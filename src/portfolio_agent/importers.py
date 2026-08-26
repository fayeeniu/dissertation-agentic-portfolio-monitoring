from __future__ import annotations

import csv
import io
import json
import os
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from .catalogue import MetricCatalogue, seed_catalogue
from .enums import DataClassification, ResolutionStatus
from .ids import dataset_id_for, sha256_bytes
from .models import (
    CompanyModel,
    MetricDefinitionModel,
    ObservationModel,
    RawSubmissionModel,
    ReportingPeriodModel,
)
from .normalization import normalize_value
from .schemas import ImportIssue, ImportResult


class ImportValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ParsedMetric:
    label: str
    value: Any
    location: str | None


@dataclass(frozen=True, slots=True)
class ParsedCompany:
    name: str
    external_id: str | None
    metrics: tuple[ParsedMetric, ...]


def normalize_company_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKC", name).casefold().strip()
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def _safe_filename(filename: str) -> str:
    basename = Path(filename).name
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", basename).strip("._")
    return safe or "submission.bin"


def _date_or_none(value: Any) -> date | None:
    if value in {None, ""}:
        return None
    if not isinstance(value, str):
        raise ImportValidationError("Reporting-period dates must use ISO 8601 strings.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ImportValidationError(f"Invalid reporting-period date: {value}") from exc


class PortfolioImporter:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        raw_data_dir: Path,
        catalogue: MetricCatalogue | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._raw_data_dir = raw_data_dir.resolve()
        self._catalogue = catalogue or MetricCatalogue()

    def import_file(
        self,
        path: Path,
        *,
        period_label: str | None = None,
        classification: DataClassification = DataClassification.RESTRICTED,
    ) -> ImportResult:
        payload = path.read_bytes()
        return self.import_bytes(
            payload,
            filename=path.name,
            period_label=period_label,
            classification=classification,
        )

    def import_bytes(
        self,
        payload: bytes,
        *,
        filename: str,
        period_label: str | None = None,
        classification: DataClassification = DataClassification.RESTRICTED,
    ) -> ImportResult:
        suffix = Path(filename).suffix.lower().lstrip(".")
        if suffix not in {"xlsx", "csv", "json"}:
            raise ImportValidationError("Only XLSX, CSV, and JSON submissions are supported.")

        parsed_period_label = period_label
        start_date: date | None = None
        end_date: date | None = None
        if suffix == "json":
            parsed, parsed_period_label, start_date, end_date = self._parse_json(
                payload, period_label
            )
        else:
            if not parsed_period_label or not parsed_period_label.strip():
                raise ImportValidationError(
                    "A reporting-period label is required for XLSX and CSV."
                )
            parsed = self._parse_xlsx(payload) if suffix == "xlsx" else self._parse_csv(payload)

        assert parsed_period_label is not None
        parsed_period_label = parsed_period_label.strip()
        content_hash = sha256_bytes(payload)
        dataset_id = dataset_id_for(payload, parsed_period_label)
        issues: list[ImportIssue] = []

        with self._session_factory.begin() as session:
            seed_catalogue(session, self._catalogue)
            session.flush()
            period = self._get_or_create_period(
                session, parsed_period_label, start_date=start_date, end_date=end_date
            )
            existing = session.scalar(
                select(RawSubmissionModel).where(
                    RawSubmissionModel.sha256 == content_hash,
                    RawSubmissionModel.reporting_period_id == period.id,
                )
            )
            if existing is not None:
                company_count, observation_count = self._existing_counts(session, existing.id)
                return ImportResult(
                    dataset_id=existing.dataset_id,
                    raw_submission_id=existing.id,
                    reporting_period_id=period.id,
                    company_count=company_count,
                    observation_count=observation_count,
                    reused_existing=True,
                )

            snapshot_path = self._write_snapshot(dataset_id, filename, payload, content_hash)
            raw = RawSubmissionModel(
                dataset_id=dataset_id,
                reporting_period_id=period.id,
                source_format=suffix,
                original_filename=_safe_filename(filename),
                sha256=content_hash,
                snapshot_path=str(snapshot_path),
                classification=classification.value,
            )
            session.add(raw)
            session.flush()

            definitions = {
                row.key: row for row in session.scalars(select(MetricDefinitionModel)).all()
            }
            seen_observations: set[tuple[str, str]] = set()
            imported_company_ids: set[str] = set()
            observation_count = 0
            for parsed_company in parsed:
                company, resolution_issue = self._resolve_company(
                    session,
                    name=parsed_company.name,
                    external_id=parsed_company.external_id,
                    classification=classification,
                )
                if resolution_issue is not None:
                    issues.append(resolution_issue)
                if company is None:
                    continue
                imported_company_ids.add(company.id)
                for parsed_metric in parsed_company.metrics:
                    metric = self._catalogue.resolve(parsed_metric.label)
                    if metric is None:
                        if parsed_metric.value not in {None, ""}:
                            issues.append(
                                ImportIssue(
                                    severity="warning",
                                    code="unknown_metric",
                                    message=f"Unmapped metric label: {parsed_metric.label}",
                                    location=parsed_metric.location,
                                )
                            )
                        continue
                    key = (company.id, metric.key)
                    if key in seen_observations:
                        issues.append(
                            ImportIssue(
                                severity="error",
                                code="duplicate_observation",
                                message=(
                                    f"Duplicate value for {metric.key}; "
                                    "later value was not imported."
                                ),
                                location=parsed_metric.location,
                            )
                        )
                        continue
                    seen_observations.add(key)
                    normalized = normalize_value(parsed_metric.value, metric)
                    definition = definitions[metric.key]
                    session.add(
                        ObservationModel(
                            company_id=company.id,
                            metric_definition_id=definition.id,
                            reporting_period_id=period.id,
                            raw_submission_id=raw.id,
                            original_value_json=parsed_metric.value,
                            normalized_value_json=normalized.value,
                            missing_state=normalized.missing_state.value,
                            unit=normalized.unit,
                            currency=normalized.currency,
                            source_cell=parsed_metric.location,
                            normalization_issue_code=normalized.issue_code,
                            normalization_issue_message=normalized.issue_message,
                        )
                    )
                    observation_count += 1

            return ImportResult(
                dataset_id=dataset_id,
                raw_submission_id=raw.id,
                reporting_period_id=period.id,
                company_count=len(imported_company_ids),
                observation_count=observation_count,
                issues=tuple(issues),
            )

    def _write_snapshot(
        self, dataset_id: str, filename: str, payload: bytes, expected_hash: str
    ) -> Path:
        target_dir = self._raw_data_dir / dataset_id
        target_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        target = target_dir / _safe_filename(filename)
        if target.exists():
            if sha256_bytes(target.read_bytes()) != expected_hash:
                raise ImportValidationError(
                    "Immutable snapshot path already contains different bytes."
                )
            return target
        with target.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        target.chmod(0o600)
        return target

    @staticmethod
    def _get_or_create_period(
        session: Session,
        label: str,
        *,
        start_date: date | None,
        end_date: date | None,
    ) -> ReportingPeriodModel:
        period = session.scalar(
            select(ReportingPeriodModel).where(ReportingPeriodModel.label == label)
        )
        if period is not None:
            if (start_date and period.start_date and start_date != period.start_date) or (
                end_date and period.end_date and end_date != period.end_date
            ):
                raise ImportValidationError("Reporting-period label conflicts with stored dates.")
            return period
        if start_date and end_date and start_date > end_date:
            raise ImportValidationError("Reporting-period start date must not follow its end date.")
        period = ReportingPeriodModel(label=label, start_date=start_date, end_date=end_date)
        session.add(period)
        session.flush()
        return period

    @staticmethod
    def _resolve_company(
        session: Session,
        *,
        name: str,
        external_id: str | None,
        classification: DataClassification,
    ) -> tuple[CompanyModel | None, ImportIssue | None]:
        clean_name = name.strip()
        normalized_name = normalize_company_name(clean_name)
        if not normalized_name:
            return None, ImportIssue(
                severity="error",
                code="missing_company_name",
                message="Company row has no usable identity and was skipped.",
            )
        if external_id:
            by_external = session.scalar(
                select(CompanyModel).where(CompanyModel.external_id == external_id.strip())
            )
            if by_external is not None:
                if by_external.normalized_name != normalized_name:
                    by_external.resolution_status = ResolutionStatus.AMBIGUOUS.value
                    return None, ImportIssue(
                        severity="error",
                        code="identity_conflict",
                        message=(
                            "External company identifier conflicts with the stored canonical name."
                        ),
                        location=external_id,
                    )
                return by_external, None
        by_name = session.scalar(
            select(CompanyModel).where(CompanyModel.normalized_name == normalized_name)
        )
        if by_name is not None:
            if external_id and by_name.external_id and by_name.external_id != external_id.strip():
                by_name.resolution_status = ResolutionStatus.AMBIGUOUS.value
                return None, ImportIssue(
                    severity="error",
                    code="ambiguous_company_identity",
                    message="Exact company name maps to a different external identifier.",
                    location=clean_name,
                )
            if external_id and not by_name.external_id:
                by_name.external_id = external_id.strip()
            return by_name, None
        company = CompanyModel(
            canonical_name=clean_name,
            normalized_name=normalized_name,
            external_id=external_id.strip() if external_id else None,
            classification=classification.value,
            resolution_status=ResolutionStatus.RESOLVED.value,
        )
        session.add(company)
        session.flush()
        return company, None

    @staticmethod
    def _existing_counts(session: Session, raw_submission_id: str) -> tuple[int, int]:
        company_count = session.scalar(
            select(func.count(func.distinct(ObservationModel.company_id))).where(
                ObservationModel.raw_submission_id == raw_submission_id
            )
        )
        observation_count = session.scalar(
            select(func.count(ObservationModel.id)).where(
                ObservationModel.raw_submission_id == raw_submission_id
            )
        )
        return int(company_count or 0), int(observation_count or 0)

    @staticmethod
    def _parse_json(
        payload: bytes, override_period: str | None
    ) -> tuple[tuple[ParsedCompany, ...], str, date | None, date | None]:
        try:
            document = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ImportValidationError("Submission is not valid UTF-8 JSON.") from exc
        if not isinstance(document, dict):
            raise ImportValidationError("JSON submission must be an object.")
        period = document.get("reporting_period")
        if not isinstance(period, dict):
            period = {}
        embedded_label = period.get("label")
        label = override_period or embedded_label
        if not isinstance(label, str) or not label.strip():
            raise ImportValidationError("JSON submission requires reporting_period.label.")
        if override_period and embedded_label and override_period != embedded_label:
            raise ImportValidationError("Requested period conflicts with embedded JSON period.")
        companies = document.get("companies")
        if not isinstance(companies, list) or not companies:
            raise ImportValidationError("JSON submission requires a non-empty companies array.")
        parsed: list[ParsedCompany] = []
        for index, item in enumerate(companies):
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                raise ImportValidationError(f"companies[{index}] requires a string name.")
            metrics = item.get("metrics")
            if not isinstance(metrics, dict):
                raise ImportValidationError(f"companies[{index}].metrics must be an object.")
            external_id = item.get("external_id")
            if external_id is not None and not isinstance(external_id, str):
                raise ImportValidationError(f"companies[{index}].external_id must be a string.")
            parsed.append(
                ParsedCompany(
                    name=item["name"],
                    external_id=external_id,
                    metrics=tuple(
                        ParsedMetric(
                            label=str(key), value=value, location=f"companies[{index}].{key}"
                        )
                        for key, value in metrics.items()
                    ),
                )
            )
        return (
            tuple(parsed),
            label,
            _date_or_none(period.get("start_date")),
            _date_or_none(period.get("end_date")),
        )

    @staticmethod
    def _parse_xlsx(payload: bytes) -> tuple[ParsedCompany, ...]:
        try:
            workbook = load_workbook(io.BytesIO(payload), read_only=True, data_only=False)
        except Exception as exc:
            raise ImportValidationError("Workbook could not be opened as XLSX.") from exc
        try:
            worksheet = workbook.active
            rows = list(worksheet.iter_rows(values_only=True))
            return PortfolioImporter._parse_matrix_rows(rows, location_style="xlsx")
        finally:
            workbook.close()

    @staticmethod
    def _parse_csv(payload: bytes) -> tuple[ParsedCompany, ...]:
        try:
            decoded = payload.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ImportValidationError("CSV submission must use UTF-8 encoding.") from exc
        rows = list(csv.reader(io.StringIO(decoded)))
        return PortfolioImporter._parse_matrix_rows(rows, location_style="csv")

    @staticmethod
    def _parse_matrix_rows(
        rows: Iterable[Iterable[Any]], *, location_style: str
    ) -> tuple[ParsedCompany, ...]:
        materialized = [list(row) for row in rows]
        if not materialized or len(materialized[0]) < 2:
            raise ImportValidationError(
                "Matrix submission requires metric labels in column A and companies across row 1."
            )
        headers = materialized[0]
        companies: list[tuple[int, str]] = []
        for column_index, header in enumerate(headers[1:], start=2):
            if header is None or not str(header).strip():
                continue
            companies.append((column_index, str(header).strip()))
        if not companies:
            raise ImportValidationError("Matrix submission has no company columns.")
        parsed: list[ParsedCompany] = []
        for column_index, company_name in companies:
            metrics: list[ParsedMetric] = []
            for row_index, row in enumerate(materialized[1:], start=2):
                if not row or row[0] is None or not str(row[0]).strip():
                    continue
                value = row[column_index - 1] if column_index - 1 < len(row) else None
                location = (
                    f"{get_column_letter(column_index)}{row_index}"
                    if location_style == "xlsx"
                    else f"row {row_index}, column {column_index}"
                )
                metrics.append(
                    ParsedMetric(label=str(row[0]).strip(), value=value, location=location)
                )
            parsed.append(
                ParsedCompany(name=company_name, external_id=None, metrics=tuple(metrics))
            )
        return tuple(parsed)
