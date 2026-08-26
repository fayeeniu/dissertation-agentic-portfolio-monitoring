from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload, sessionmaker

from .enums import ReportStatus, ReviewDecisionType, RunStatus, WorkflowStage
from .events import events_for_run
from .ids import stable_hash
from .models import (
    ClaimModel,
    EvidenceItemModel,
    QualityViolationModel,
    ReportExportModel,
    ReportModel,
    ReportSectionModel,
    ReviewDecisionModel,
    WorkflowRunModel,
    run_evidence,
)


class ReportStateError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ExportBundle:
    report_id: str
    version: int
    json_path: Path
    markdown_path: Path
    html_path: Path
    content_hash: str


def _require_audit_text(actor: str, reason: str) -> tuple[str, str]:
    clean_actor = actor.strip()
    clean_reason = reason.strip()
    if not clean_actor or len(clean_actor) > 255:
        raise ReportStateError("Reviewer identity must be between 1 and 255 characters.")
    if len(clean_reason) < 3 or len(clean_reason) > 2000:
        raise ReportStateError("Review rationale must be between 3 and 2,000 characters.")
    return clean_actor, clean_reason


def _inline_markdown(value: str) -> str:
    escaped = html.escape(value)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def markdown_fragment_to_html(value: str) -> str:
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    table_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f"<p>{_inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            items = "".join(f"<li>{_inline_markdown(item)}</li>" for item in list_items)
            blocks.append(f"<ul>{items}</ul>")
            list_items.clear()

    def flush_table() -> None:
        if not table_lines:
            return
        rows = [
            [cell.strip() for cell in line.strip().strip("|").split("|")] for line in table_lines
        ]
        separator = rows[1] if len(rows) > 1 else []
        is_table = bool(separator) and all(
            re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in separator
        )
        if is_table:
            header = "".join(f'<th scope="col">{_inline_markdown(cell)}</th>' for cell in rows[0])
            body = "".join(
                "<tr>" + "".join(f"<td>{_inline_markdown(cell)}</td>" for cell in row) + "</tr>"
                for row in rows[2:]
            )
            blocks.append(
                '<div class="table-wrap"><table><thead><tr>'
                f"{header}</tr></thead><tbody>{body}</tbody></table></div>"
            )
        else:
            paragraph.extend(table_lines)
        table_lines.clear()

    for line in value.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            flush_list()
            table_lines.append(stripped)
        elif stripped.startswith("- "):
            flush_table()
            flush_paragraph()
            list_items.append(stripped[2:])
        elif not stripped:
            flush_table()
            flush_paragraph()
            flush_list()
        else:
            flush_table()
            flush_list()
            paragraph.append(stripped)
    flush_table()
    flush_paragraph()
    flush_list()
    return "".join(blocks)


class ReportService:
    def __init__(self, session_factory: sessionmaker[Session], export_root: Path) -> None:
        self._session_factory = session_factory
        self._export_root = export_root.resolve()

    @property
    def export_root(self) -> Path:
        return self._export_root

    def approve(
        self,
        report_id: str,
        *,
        actor: str,
        reason: str,
        expected_lock_version: int,
    ) -> int:
        clean_actor, clean_reason = _require_audit_text(actor, reason)
        with self._session_factory.begin() as session:
            report = self._report_for_update(session, report_id)
            if report.status != ReportStatus.PENDING_REVIEW.value:
                raise ReportStateError("Only a pending-review report can be approved.")
            self._assert_approval_ready(session, report)
            self._acquire_version(session, report, expected_lock_version)
            report.status = ReportStatus.APPROVED.value
            report.approved_at = datetime.now(UTC)
            session.add(
                ReviewDecisionModel(
                    report_id=report.id,
                    section_id=None,
                    actor=clean_actor,
                    decision=ReviewDecisionType.APPROVE.value,
                    reason=clean_reason,
                    report_version=report.version,
                )
            )
            run = session.get(WorkflowRunModel, report.run_id)
            if run is not None:
                run.stage = WorkflowStage.APPROVE_EXPORT.value
            return report.lock_version

    def reject(
        self,
        report_id: str,
        *,
        actor: str,
        reason: str,
        expected_lock_version: int,
    ) -> int:
        clean_actor, clean_reason = _require_audit_text(actor, reason)
        with self._session_factory.begin() as session:
            report = self._report_for_update(session, report_id)
            if report.status not in {
                ReportStatus.PENDING_REVIEW.value,
                ReportStatus.APPROVED.value,
            }:
                raise ReportStateError("This report cannot be rejected in its current state.")
            self._acquire_version(session, report, expected_lock_version)
            report.status = ReportStatus.REJECTED.value
            report.approved_at = None
            session.add(
                ReviewDecisionModel(
                    report_id=report.id,
                    section_id=None,
                    actor=clean_actor,
                    decision=ReviewDecisionType.REJECT.value,
                    reason=clean_reason,
                    report_version=report.version,
                )
            )
            return report.lock_version

    def edit_section(
        self,
        report_id: str,
        section_key: str,
        *,
        body_markdown: str,
        actor: str,
        reason: str,
        expected_lock_version: int,
    ) -> int:
        clean_actor, clean_reason = _require_audit_text(actor, reason)
        clean_body = body_markdown.strip()
        if not clean_body or len(clean_body) > 50_000:
            raise ReportStateError("Section body must be between 1 and 50,000 characters.")
        with self._session_factory.begin() as session:
            report = self._report_for_update(session, report_id)
            if report.status not in {
                ReportStatus.PENDING_REVIEW.value,
                ReportStatus.APPROVED.value,
            }:
                raise ReportStateError("Only pending-review or approved reports can be edited.")
            self._acquire_version(session, report, expected_lock_version)
            current = session.scalar(
                select(ReportSectionModel).where(
                    ReportSectionModel.report_id == report.id,
                    ReportSectionModel.section_key == section_key,
                    ReportSectionModel.is_current.is_(True),
                )
            )
            if current is None:
                raise ReportStateError("Unknown report section.")
            current.is_current = False
            new_version = current.version + 1
            replacement = ReportSectionModel(
                report_id=report.id,
                company_id=current.company_id,
                section_key=current.section_key,
                heading=current.heading,
                order_index=current.order_index,
                body_markdown=clean_body,
                version=new_version,
                is_current=True,
            )
            session.add(replacement)
            session.flush()
            report.version += 1
            report.status = ReportStatus.PENDING_REVIEW.value
            report.approved_at = None
            current_sections = self._current_sections(session, report.id)
            current_sections.append(replacement)
            report.content_hash = stable_hash(
                [
                    {"key": section.section_key, "body": section.body_markdown}
                    for section in sorted(
                        {section.section_key: section for section in current_sections}.values(),
                        key=lambda item: item.order_index,
                    )
                ]
            )
            session.add(
                ReviewDecisionModel(
                    report_id=report.id,
                    section_id=replacement.id,
                    actor=clean_actor,
                    decision=ReviewDecisionType.REQUEST_EDIT.value,
                    reason=clean_reason,
                    report_version=report.version,
                )
            )
            return report.version

    def export(self, report_id: str, *, expected_lock_version: int) -> ExportBundle:
        with self._session_factory.begin() as session:
            report = self._report_for_update(session, report_id)
            if report.lock_version != expected_lock_version:
                raise ReportStateError(
                    "This report changed after the page was loaded; refresh before retrying."
                )
            if report.status == ReportStatus.EXPORTED.value:
                return self._existing_export(session, report)
            if report.status != ReportStatus.APPROVED.value:
                raise ReportStateError("Human approval is required before export.")
            self._acquire_version(session, report, expected_lock_version)
            artifact = self._artifact(session, report)
            markdown = self._markdown(artifact)
            html_document = self._html(artifact)
            json_document = json.dumps(
                artifact, indent=2, sort_keys=True, ensure_ascii=False, default=str
            )
            content_hash = stable_hash(
                {"json": json_document, "markdown": markdown, "html": html_document}
            )
            target = self._export_target(report.id, report.version)
            manifest = {
                "schema_version": "portfolio-export-manifest-v1",
                "report_id": report.id,
                "report_version": report.version,
                "content_hash": content_hash,
                "files": {
                    "report.json": hashlib.sha256(json_document.encode()).hexdigest(),
                    "report.md": hashlib.sha256(markdown.encode()).hexdigest(),
                    "report.html": hashlib.sha256(html_document.encode()).hexdigest(),
                },
            }
            manifest_sha256 = stable_hash(manifest)
            export_record = session.scalar(
                select(ReportExportModel).where(
                    ReportExportModel.report_id == report.id,
                    ReportExportModel.report_version == report.version,
                )
            )
            if export_record is None:
                export_record = ReportExportModel(
                    report_id=report.id,
                    report_version=report.version,
                    status="pending",
                    artifact_root=str(target),
                    manifest_json=manifest,
                    manifest_sha256=manifest_sha256,
                )
                session.add(export_record)
            elif export_record.status == "failed":
                export_record.status = "pending"
                export_record.artifact_root = str(target)
                export_record.manifest_json = manifest
                export_record.manifest_sha256 = manifest_sha256
                export_record.error = None
                export_record.finalized_at = None
            else:
                raise ReportStateError("An export attempt already exists for this report version.")
            report.status = ReportStatus.EXPORTING.value
            session.flush()
            export_id = export_record.id
            export_lock_version = report.lock_version

        try:
            self._write_export_bundle(
                report_id=report_id,
                version=artifact["report"]["version"],
                target=target,
                json_document=json_document,
                markdown=markdown,
                html_document=html_document,
                manifest=manifest,
                content_hash=content_hash,
            )
            bundle = self._verified_export_bundle(
                report_id=report_id,
                version=artifact["report"]["version"],
                target=target,
                manifest=manifest,
                manifest_sha256=manifest_sha256,
            )
        except Exception as exc:
            self._remove_export_target(target)
            self._mark_export_failed(
                export_id=export_id,
                report_id=report_id,
                export_lock_version=export_lock_version,
                error=exc,
            )
            raise ReportStateError("Export could not be finalized atomically.") from exc

        try:
            with self._session_factory.begin() as session:
                report = self._report_for_update(session, report_id)
                if (
                    report.lock_version != export_lock_version
                    or report.status != ReportStatus.EXPORTING.value
                ):
                    raise ReportStateError(
                        "Report state changed while the export was being finalized."
                    )
                finalized_export = session.get(ReportExportModel, export_id)
                if finalized_export is None or finalized_export.status != "pending":
                    raise ReportStateError(
                        "The pending export manifest is unavailable for finalization."
                    )
                finalized_export.status = "finalized"
                finalized_export.finalized_at = datetime.now(UTC)
                report.status = ReportStatus.EXPORTED.value
                report.exported_at = datetime.now(UTC)
                run = session.get(WorkflowRunModel, report.run_id)
                if run is not None:
                    run.stage = WorkflowStage.COMPLETE.value
                    run.status = RunStatus.SUCCEEDED.value
                    run.finished_at = datetime.now(UTC)
        except Exception as exc:
            try:
                if self._export_is_finalized(export_id, report_id):
                    return bundle
            except Exception as recovery_error:
                raise ReportStateError(
                    "Export finalization outcome could not be confirmed; artifacts were retained."
                ) from recovery_error
            self._remove_export_target(target)
            self._mark_export_failed(
                export_id=export_id,
                report_id=report_id,
                export_lock_version=export_lock_version,
                error=exc,
            )
            raise ReportStateError("Export finalization state could not be committed.") from exc
        return bundle

    def _export_is_finalized(self, export_id: str, report_id: str) -> bool:
        with self._session_factory() as session:
            export_record = session.get(ReportExportModel, export_id)
            report = session.get(ReportModel, report_id)
            if (
                export_record is None
                or report is None
                or export_record.status != "finalized"
                or report.status != ReportStatus.EXPORTED.value
            ):
                return False
            self._verified_export_bundle(
                report_id=report.id,
                version=report.version,
                target=Path(export_record.artifact_root),
                manifest=export_record.manifest_json,
                manifest_sha256=export_record.manifest_sha256,
            )
            return True

    def _export_target(self, report_id: str, version: int) -> Path:
        target = (self._export_root / report_id / f"v{version}").resolve()
        if not target.is_relative_to(self._export_root):
            raise ReportStateError("Export target falls outside the configured export root.")
        return target

    def _mark_export_failed(
        self,
        *,
        export_id: str,
        report_id: str,
        export_lock_version: int,
        error: Exception,
    ) -> None:
        with self._session_factory.begin() as session:
            failed_export = session.get(ReportExportModel, export_id)
            if failed_export is not None and failed_export.status != "finalized":
                failed_export.status = "failed"
                failed_export.error = f"{type(error).__name__}: {error}"[:2000]
            failed_report = session.get(ReportModel, report_id)
            if (
                failed_report is not None
                and failed_report.lock_version == export_lock_version
                and failed_report.status == ReportStatus.EXPORTING.value
            ):
                failed_report.status = ReportStatus.APPROVED.value

    def _remove_export_target(self, target: Path) -> None:
        resolved = target.resolve()
        if resolved.is_relative_to(self._export_root) and resolved.exists():
            shutil.rmtree(resolved)

    @staticmethod
    def _report_for_update(session: Session, report_id: str) -> ReportModel:
        report = session.get(ReportModel, report_id)
        if report is None:
            raise ReportStateError("Unknown report ID.")
        return report

    @staticmethod
    def _acquire_version(session: Session, report: ReportModel, expected_lock_version: int) -> None:
        if expected_lock_version < 1:
            raise ReportStateError("Invalid report version token.")
        result = session.connection().execute(
            update(ReportModel)
            .where(
                ReportModel.id == report.id,
                ReportModel.lock_version == expected_lock_version,
            )
            .values(lock_version=expected_lock_version + 1)
        )
        if result.rowcount != 1:
            raise ReportStateError(
                "This report changed after the page was loaded; refresh before retrying."
            )
        report.lock_version = expected_lock_version + 1

    def _existing_export(self, session: Session, report: ReportModel) -> ExportBundle:
        export_record = session.scalar(
            select(ReportExportModel).where(
                ReportExportModel.report_id == report.id,
                ReportExportModel.report_version == report.version,
                ReportExportModel.status == "finalized",
            )
        )
        if export_record is None:
            raise ReportStateError("Export state exists without a finalized manifest.")
        return self._verified_export_bundle(
            report_id=report.id,
            version=report.version,
            target=Path(export_record.artifact_root),
            manifest=export_record.manifest_json,
            manifest_sha256=export_record.manifest_sha256,
        )

    def _verified_export_bundle(
        self,
        *,
        report_id: str,
        version: int,
        target: Path,
        manifest: dict[str, Any],
        manifest_sha256: str,
    ) -> ExportBundle:
        resolved_target = target.resolve()
        if not resolved_target.is_relative_to(self._export_root):
            raise ReportStateError("Export manifest points outside the configured export root.")
        if stable_hash(manifest) != manifest_sha256:
            raise ReportStateError("Persisted export manifest checksum does not match its content.")
        if (
            manifest.get("schema_version") != "portfolio-export-manifest-v1"
            or manifest.get("report_id") != report_id
            or manifest.get("report_version") != version
        ):
            raise ReportStateError("Export manifest identity or schema is invalid.")
        expected_files = manifest.get("files")
        filenames = {"report.json", "report.md", "report.html"}
        if not isinstance(expected_files, dict) or set(expected_files) != filenames:
            raise ReportStateError("Export manifest file inventory is invalid.")

        verified_paths: dict[str, Path] = {}
        file_bytes: dict[str, bytes] = {}
        for filename in sorted(filenames):
            artifact_path = (resolved_target / filename).resolve()
            if not artifact_path.is_relative_to(resolved_target) or not artifact_path.is_file():
                raise ReportStateError("Finalized export artifacts are unavailable.")
            payload = artifact_path.read_bytes()
            expected_sha256 = expected_files.get(filename)
            if (
                not isinstance(expected_sha256, str)
                or hashlib.sha256(payload).hexdigest() != expected_sha256
            ):
                raise ReportStateError(f"Export artifact checksum failed for {filename}.")
            verified_paths[filename] = artifact_path
            file_bytes[filename] = payload

        manifest_path = (resolved_target / "manifest.json").resolve()
        if not manifest_path.is_relative_to(resolved_target) or not manifest_path.is_file():
            raise ReportStateError("Export manifest artifact is unavailable.")
        try:
            disk_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            documents = {
                "json": file_bytes["report.json"].decode("utf-8"),
                "markdown": file_bytes["report.md"].decode("utf-8"),
                "html": file_bytes["report.html"].decode("utf-8"),
            }
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReportStateError("Export artifacts are not valid UTF-8 or JSON.") from exc
        if disk_manifest != manifest:
            raise ReportStateError("Export manifest artifact differs from the persisted manifest.")
        content_hash = manifest.get("content_hash")
        if not isinstance(content_hash, str) or stable_hash(documents) != content_hash:
            raise ReportStateError("Export bundle content hash is invalid.")
        return ExportBundle(
            report_id=report_id,
            version=version,
            json_path=verified_paths["report.json"],
            markdown_path=verified_paths["report.md"],
            html_path=verified_paths["report.html"],
            content_hash=content_hash,
        )

    def _write_export_bundle(
        self,
        *,
        report_id: str,
        version: int,
        target: Path,
        json_document: str,
        markdown: str,
        html_document: str,
        manifest: dict[str, Any],
        content_hash: str,
    ) -> ExportBundle:
        target_parent = target.parent
        target_parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if target.exists():
            raise ReportStateError("An untracked export directory already exists for this version.")
        staging = Path(tempfile.mkdtemp(prefix=f".staging-v{version}-", dir=target_parent))
        staging.chmod(0o700)
        try:
            self._atomic_write(staging / "report.json", json_document)
            self._atomic_write(staging / "report.md", markdown)
            self._atomic_write(staging / "report.html", html_document)
            self._atomic_write(
                staging / "manifest.json",
                json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            )
            staging.replace(target)
        except Exception:
            if staging.exists():
                shutil.rmtree(staging)
            raise
        return ExportBundle(
            report_id=report_id,
            version=version,
            json_path=target / "report.json",
            markdown_path=target / "report.md",
            html_path=target / "report.html",
            content_hash=content_hash,
        )

    @staticmethod
    def _current_sections(session: Session, report_id: str) -> list[ReportSectionModel]:
        return list(
            session.scalars(
                select(ReportSectionModel)
                .where(
                    ReportSectionModel.report_id == report_id,
                    ReportSectionModel.is_current.is_(True),
                )
                .order_by(ReportSectionModel.order_index)
            ).all()
        )

    def _assert_approval_ready(self, session: Session, report: ReportModel) -> None:
        sections = self._current_sections(session, report.id)
        if not sections or any(not section.body_markdown.strip() for section in sections):
            raise ReportStateError("Every current report section must contain reviewable content.")
        claims = list(
            session.scalars(
                select(ClaimModel)
                .where(ClaimModel.run_id == report.run_id)
                .options(joinedload(ClaimModel.verifications))
            ).unique()
        )
        if any(not claim.verifications for claim in claims):
            raise ReportStateError("Every claim must have an independent verification record.")

    def _artifact(self, session: Session, report: ReportModel) -> dict[str, Any]:
        sections = self._current_sections(session, report.id)
        claims = list(
            session.scalars(
                select(ClaimModel)
                .where(ClaimModel.run_id == report.run_id)
                .options(
                    joinedload(ClaimModel.company),
                    joinedload(ClaimModel.metric_definition),
                    joinedload(ClaimModel.evidence_items),
                    joinedload(ClaimModel.verifications),
                )
                .order_by(ClaimModel.id)
            ).unique()
        )
        decisions = list(
            session.scalars(
                select(ReviewDecisionModel)
                .where(ReviewDecisionModel.report_id == report.id)
                .order_by(ReviewDecisionModel.created_at)
            ).all()
        )
        evidence_items = list(
            session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(run_evidence.c.run_id == report.run_id)
            ).all()
        )
        temporal_by_evidence = {
            evidence_id: {
                "reporting_cutoff": cutoff.isoformat() if cutoff else None,
                "status": status,
                "reason": reason,
            }
            for evidence_id, cutoff, status, reason in session.execute(
                select(
                    run_evidence.c.evidence_item_id,
                    run_evidence.c.reporting_cutoff,
                    run_evidence.c.temporal_status,
                    run_evidence.c.temporal_reason,
                ).where(run_evidence.c.run_id == report.run_id)
            ).all()
        }
        quality_dispositions = Counter(
            session.scalars(
                select(QualityViolationModel.disposition).where(
                    QualityViolationModel.run_id == report.run_id
                )
            ).all()
        )
        event_types = Counter(
            event.event_type for event in events_for_run(session, run_id=report.run_id)
        )
        return {
            "schema_version": "portfolio-report-v1",
            "report": {
                "id": report.id,
                "run_id": report.run_id,
                "dataset_id": report.dataset_id,
                "reporting_period_id": report.reporting_period_id,
                "title": report.title,
                "version": report.version,
                "status_at_export": report.status,
                "generated_at": report.generated_at.isoformat(),
                "approved_at": report.approved_at.isoformat() if report.approved_at else None,
                "content_hash": report.content_hash,
            },
            "sections": [
                {
                    "key": section.section_key,
                    "heading": section.heading,
                    "order": section.order_index,
                    "version": section.version,
                    "body_markdown": section.body_markdown,
                }
                for section in sections
            ],
            "visual_summary": {
                "verification_statuses": dict(
                    sorted(Counter(claim.verification_status for claim in claims).items())
                ),
                "evidence_sources": dict(
                    sorted(Counter(item.source_type for item in evidence_items).items())
                ),
                "quality_dispositions": dict(sorted(quality_dispositions.items())),
                "event_types": dict(sorted(event_types.items())),
            },
            "claims": [
                {
                    "id": claim.id,
                    "company": claim.company.canonical_name,
                    "metric_key": claim.metric_definition.key,
                    "text": claim.text,
                    "normalized_value": claim.normalized_value_json,
                    "verification_status": claim.verification_status,
                    "verifications": [
                        {
                            "status": verification.status,
                            "rationale": verification.rationale,
                            "verifier_role": verification.verifier_role,
                            "verified_at": verification.verified_at.isoformat(),
                        }
                        for verification in claim.verifications
                    ],
                    "provenance": [
                        {
                            "evidence_id": evidence.id,
                            "source_type": evidence.source_type,
                            "publisher": evidence.publisher,
                            "locator": evidence.locator,
                            "checksum": evidence.checksum,
                            "retrieved_at": evidence.retrieved_at.isoformat(),
                            "temporal": temporal_by_evidence[evidence.id],
                        }
                        for evidence in claim.evidence_items
                    ],
                }
                for claim in claims
            ],
            "review_decisions": [
                {
                    "id": decision.id,
                    "decision": decision.decision,
                    "actor": decision.actor,
                    "reason": decision.reason,
                    "report_version": decision.report_version,
                    "created_at": decision.created_at.isoformat(),
                }
                for decision in decisions
            ],
        }

    @staticmethod
    def _markdown(artifact: dict[str, Any]) -> str:
        report = artifact["report"]
        lines = [
            f"# {report['title']}",
            "",
            f"Report ID: `{report['id']}`  ",
            f"Run ID: `{report['run_id']}`  ",
            f"Dataset ID: `{report['dataset_id']}`  ",
            f"Version: {report['version']}",
            "",
        ]
        for section in artifact["sections"]:
            lines.extend([f"## {section['heading']}", "", section["body_markdown"], ""])
        lines.extend(["## Visual summary data", ""])
        for heading, values in artifact["visual_summary"].items():
            lines.extend([f"### {heading.replace('_', ' ').title()}", ""])
            lines.extend(f"- {key}: {value}" for key, value in values.items())
            lines.append("")
        lines.extend(["## Claim provenance", ""])
        for claim in artifact["claims"]:
            lines.append(
                f"- `{claim['id']}` — {claim['verification_status']} — {claim['metric_key']}"
            )
            for evidence in claim["provenance"]:
                lines.append(
                    f"  - `{evidence['evidence_id']}` — {evidence['locator']} — "
                    f"SHA-256 `{evidence['checksum']}`"
                )
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _html(artifact: dict[str, Any]) -> str:
        report = artifact["report"]
        sections = "".join(
            '<section aria-labelledby="section-{index}">'
            '<h2 id="section-{index}">{heading}</h2>{body}</section>'.format(
                index=index,
                heading=html.escape(section["heading"]),
                body=markdown_fragment_to_html(section["body_markdown"]),
            )
            for index, section in enumerate(artifact["sections"], start=1)
        )
        visual_groups = "".join(
            '<section class="visual-card" aria-labelledby="visual-{index}">'
            '<h2 id="visual-{index}">{heading}</h2>{rows}</section>'.format(
                index=index,
                heading=html.escape(heading.replace("_", " ").title()),
                rows="".join(
                    '<label>{label}<progress max="{maximum}" value="{value}">{value} of '
                    "{maximum}</progress><strong>{value}</strong></label>".format(
                        label=html.escape(label.replace("_", " ").title()),
                        value=value,
                        maximum=max(sum(values.values()), 1),
                    )
                    for label, value in values.items()
                )
                or "<p>No observations.</p>",
            )
            for index, (heading, values) in enumerate(artifact["visual_summary"].items(), start=1)
        )
        return (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{html.escape(report['title'])}</title>"
            "<style>body{font:16px/1.55 system-ui;max-width:70rem;margin:auto;padding:2rem;}"
            "h1,h2{line-height:1.2}section{border-top:1px solid #bbb;margin-top:2rem;}"
            "code{overflow-wrap:anywhere}.visual-grid{display:grid;grid-template-columns:"
            "repeat(auto-fit,minmax(16rem,1fr));gap:1rem}.visual-card{padding:1rem;"
            "border:1px solid "
            "#bbb}.visual-card label{display:grid;grid-template-columns:1fr 3fr auto;gap:.5rem;"
            "align-items:center;margin:.5rem 0}progress{width:100%}.table-wrap{overflow-x:auto}"
            "table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #bbb;"
            "padding:.5rem;text-align:left}</style></head><body><main>"
            f"<h1>{html.escape(report['title'])}</h1>"
            f"<p>Report <code>{html.escape(report['id'])}</code>, version "
            f'{report["version"]}.</p><section aria-labelledby="visual-summary"><h2 '
            f'id="visual-summary">Visual summary</h2><div class="visual-grid">'
            f"{visual_groups}</div></section>{sections}</main></body></html>"
        )

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(0o600)
        temporary.replace(path)
