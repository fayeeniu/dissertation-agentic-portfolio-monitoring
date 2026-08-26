from __future__ import annotations

import time
from collections import Counter, defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import insert, select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from .connectors.base import Connector, ConnectorQuery
from .enums import (
    DataClassification,
    MetricDataType,
    MissingState,
    ReportStatus,
    ResolutionStatus,
    RunStatus,
    Sourceability,
    VerificationStatus,
    WorkflowStage,
)
from .ids import stable_hash
from .llm.base import ExtractionProvider, ExtractionRequest
from .models import (
    AgentRunModel,
    ClaimModel,
    CompanyModel,
    EvidenceItemModel,
    ExtractionModel,
    MetricDefinitionModel,
    ObservationModel,
    RawSubmissionModel,
    ReportingPeriodModel,
    ReportModel,
    ReportSectionModel,
    VerificationModel,
    WorkflowRunModel,
    run_evidence,
)
from .normalization import normalize_value
from .schemas import EvidenceItem, MetricDefinition, PipelineResult
from .verification import VerificationEvidence, verify_claim

StageFunction = Callable[[Session, WorkflowRunModel], dict[str, Any]]


class PipelineExecutionError(RuntimeError):
    pass


def _metric_contract(row: MetricDefinitionModel) -> MetricDefinition:
    return MetricDefinition(
        key=row.key,
        category=row.category,
        label=row.label,
        data_type=MetricDataType(row.data_type),
        sourceability=Sourceability(row.sourceability),
        unit=row.unit,
        aliases=tuple(row.aliases_json),
        description=row.description,
    )


def _evidence_contract(row: EvidenceItemModel) -> EvidenceItem:
    return EvidenceItem(
        id=row.id,
        company_id=row.company_id,
        metric_key=row.metric_definition.key if row.metric_definition else None,
        source_type=row.source_type,
        connector=row.connector,
        locator=row.locator,
        publisher=row.publisher,
        retrieved_at=row.retrieved_at,
        published_at=row.published_at,
        content=row.content_json,
        checksum=row.checksum,
        connector_version=row.connector_version,
        classification=DataClassification(row.classification),
        is_untrusted=row.is_untrusted,
    )


def _claim_text(
    company: CompanyModel,
    metric: MetricDefinitionModel,
    value: Any,
    currency: str | None,
    period_label: str,
) -> str:
    unit = currency or metric.unit or ""
    suffix = f" {unit}" if unit else ""
    return f"{company.canonical_name}: {metric.label} was {value}{suffix} for {period_label}."


class PortfolioWorkflow:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        connector: Connector,
        extraction_provider: ExtractionProvider,
    ) -> None:
        self._session_factory = session_factory
        self._connector = connector
        self._extraction_provider = extraction_provider

    def run(self, dataset_id: str) -> PipelineResult:
        with self._session_factory.begin() as session:
            raw = session.scalar(
                select(RawSubmissionModel).where(RawSubmissionModel.dataset_id == dataset_id)
            )
            if raw is None:
                raise PipelineExecutionError(f"Unknown dataset ID: {dataset_id}")
            workflow_run = WorkflowRunModel(
                dataset_id=dataset_id,
                reporting_period_id=raw.reporting_period_id,
                stage=WorkflowStage.PLAN.value,
                status=RunStatus.RUNNING.value,
                configuration_json={
                    "connector": self._connector.name,
                    "connector_version": self._connector.version,
                    "extraction_provider": self._extraction_provider.name,
                    "completed_stages": [],
                },
            )
            session.add(workflow_run)
            session.flush()
            run_id = workflow_run.id

        stages: tuple[tuple[WorkflowStage, str, StageFunction], ...] = (
            (WorkflowStage.PLAN, "planner", self._plan),
            (WorkflowStage.RESOLVE, "identity_resolver", self._resolve),
            (WorkflowStage.COLLECT, "evidence_collector", self._collect),
            (WorkflowStage.EXTRACT, "structured_extractor", self._extract),
            (WorkflowStage.NORMALIZE, "normalizer", self._normalize),
            (WorkflowStage.VERIFY, "independent_verifier", self._verify),
            (WorkflowStage.COMPOSE, "report_composer", self._compose),
            (WorkflowStage.HUMAN_REVIEW, "human_review_gate", self._human_review_gate),
        )
        try:
            for stage, role, function in stages:
                self._execute_stage(run_id, stage, role, function)
        except Exception as exc:
            with self._session_factory.begin() as session:
                failed_run = session.get(WorkflowRunModel, run_id)
                if failed_run is not None:
                    failed_run.stage = WorkflowStage.FAILED.value
                    failed_run.status = RunStatus.FAILED.value
                    failed_run.finished_at = datetime.now(UTC)
                    failed_run.error = f"{type(exc).__name__}: {exc}"
            raise PipelineExecutionError(f"Pipeline {run_id} failed at a bounded stage.") from exc

        with self._session_factory.begin() as session:
            completed_run = session.get(WorkflowRunModel, run_id)
            assert completed_run is not None
            completed_run.status = RunStatus.SUCCEEDED.value
            completed_run.finished_at = datetime.now(UTC)
            report = session.scalar(select(ReportModel).where(ReportModel.run_id == run_id))
            assert report is not None
            counts = Counter(
                session.scalars(
                    select(ClaimModel.verification_status).where(ClaimModel.run_id == run_id)
                ).all()
            )
            return PipelineResult(
                run_id=run_id,
                dataset_id=dataset_id,
                report_id=report.id,
                report_status=ReportStatus(report.status),
                final_stage=WorkflowStage.HUMAN_REVIEW,
                claim_counts=dict(sorted(counts.items())),
            )

    def _execute_stage(
        self,
        run_id: str,
        stage: WorkflowStage,
        role: str,
        function: StageFunction,
    ) -> None:
        started = datetime.now(UTC)
        start_clock = time.perf_counter()
        input_summary = {"run_id": run_id, "stage": stage.value}
        with self._session_factory.begin() as session:
            agent_run = AgentRunModel(
                run_id=run_id,
                stage=stage.value,
                role=role,
                status=RunStatus.RUNNING.value,
                input_hash=stable_hash(input_summary),
                attempts=1,
                started_at=started,
                metadata_json={},
            )
            session.add(agent_run)
            session.flush()
            agent_run_id = agent_run.id
        try:
            with self._session_factory.begin() as session:
                workflow_run = session.get(WorkflowRunModel, run_id)
                assert workflow_run is not None
                summary = function(session, workflow_run)
                finished = datetime.now(UTC)
                stored_agent_run = session.get(AgentRunModel, agent_run_id)
                assert stored_agent_run is not None
                stored_agent_run.status = RunStatus.SUCCEEDED.value
                stored_agent_run.output_hash = stable_hash(summary)
                stored_agent_run.duration_ms = int((time.perf_counter() - start_clock) * 1000)
                stored_agent_run.finished_at = finished
                stored_agent_run.metadata_json = summary
                workflow_run.stage = stage.value
                config = dict(workflow_run.configuration_json)
                completed = list(config.get("completed_stages", []))
                completed.append(stage.value)
                config["completed_stages"] = completed
                workflow_run.configuration_json = config
        except Exception as exc:
            with self._session_factory.begin() as session:
                failed_agent_run = session.get(AgentRunModel, agent_run_id)
                if failed_agent_run is not None:
                    failed_agent_run.status = RunStatus.FAILED.value
                    failed_agent_run.error = f"{type(exc).__name__}: {exc}"
                    failed_agent_run.duration_ms = int((time.perf_counter() - start_clock) * 1000)
                    failed_agent_run.finished_at = datetime.now(UTC)
            raise

    @staticmethod
    def _dataset_observations(session: Session, dataset_id: str) -> list[ObservationModel]:
        return list(
            session.scalars(
                select(ObservationModel)
                .join(RawSubmissionModel)
                .where(RawSubmissionModel.dataset_id == dataset_id)
                .options(
                    joinedload(ObservationModel.company),
                    joinedload(ObservationModel.metric_definition),
                    joinedload(ObservationModel.raw_submission).joinedload(
                        RawSubmissionModel.reporting_period
                    ),
                )
            ).all()
        )

    def _plan(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        observations = self._dataset_observations(session, run.dataset_id)
        public_tasks = sum(
            observation.metric_definition.sourceability
            in {Sourceability.PUBLICLY_SOURCEABLE.value, Sourceability.MIXED.value}
            for observation in observations
        )
        config = dict(run.configuration_json)
        config["plan"] = {
            "observation_count": len(observations),
            "public_collection_task_count": public_tasks,
        }
        run.configuration_json = config
        return {
            "observation_count": len(observations),
            "public_collection_task_count": public_tasks,
        }

    def _resolve(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        observations = self._dataset_observations(session, run.dataset_id)
        companies = {observation.company.id: observation.company for observation in observations}
        unresolved = [
            company.id
            for company in companies.values()
            if company.resolution_status != ResolutionStatus.RESOLVED.value
        ]
        if unresolved:
            raise ValueError(
                "Ambiguous company identities require human resolution before collection."
            )
        return {"resolved_company_count": len(companies), "unresolved_company_count": 0}

    def _link_evidence(self, session: Session, run_id: str, evidence_id: str) -> None:
        existing = session.execute(
            select(run_evidence).where(
                run_evidence.c.run_id == run_id,
                run_evidence.c.evidence_item_id == evidence_id,
            )
        ).first()
        if existing is None:
            session.execute(
                insert(run_evidence).values(run_id=run_id, evidence_item_id=evidence_id)
            )

    def _collect(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        observations = self._dataset_observations(session, run.dataset_id)
        internal_count = 0
        external_count = 0
        untrusted_count = 0
        for observation in observations:
            internal_content = {
                "company_name": observation.company.canonical_name,
                "metric_key": observation.metric_definition.key,
                "period_label": observation.raw_submission.reporting_period.label,
                "value": observation.normalized_value_json,
                "unit": observation.unit,
                "currency": observation.currency,
                "missing_state": observation.missing_state,
            }
            internal_locator = (
                f"submission://{run.dataset_id}#{observation.source_cell or observation.id}"
            )
            internal_checksum = stable_hash(
                {
                    "raw_sha256": observation.raw_submission.sha256,
                    "locator": internal_locator,
                    "content": internal_content,
                }
            )
            internal = session.scalar(
                select(EvidenceItemModel).where(
                    EvidenceItemModel.raw_submission_id == observation.raw_submission_id,
                    EvidenceItemModel.company_id == observation.company_id,
                    EvidenceItemModel.metric_definition_id == observation.metric_definition_id,
                )
            )
            if internal is None:
                internal = EvidenceItemModel(
                    company_id=observation.company_id,
                    metric_definition_id=observation.metric_definition_id,
                    raw_submission_id=observation.raw_submission_id,
                    source_type="portfolio_submission",
                    connector="immutable_submission",
                    locator=internal_locator,
                    publisher=None,
                    retrieved_at=observation.raw_submission.created_at,
                    published_at=None,
                    content_json=internal_content,
                    checksum=internal_checksum,
                    connector_version="1.0.0",
                    classification=observation.raw_submission.classification,
                    is_untrusted=False,
                    is_stale=False,
                )
                session.add(internal)
                session.flush()
            self._link_evidence(session, run.id, internal.id)
            internal_count += 1

            if observation.metric_definition.sourceability not in {
                Sourceability.PUBLICLY_SOURCEABLE.value,
                Sourceability.MIXED.value,
            }:
                continue
            query = ConnectorQuery(
                company_id=observation.company.id,
                company_name=observation.company.canonical_name,
                external_id=observation.company.external_id,
                metric_key=observation.metric_definition.key,
                period_label=observation.raw_submission.reporting_period.label,
            )
            for evidence in self._connector.collect(query):
                stored = session.get(EvidenceItemModel, evidence.id)
                if stored is None:
                    stored = EvidenceItemModel(
                        id=evidence.id,
                        company_id=evidence.company_id,
                        metric_definition_id=observation.metric_definition_id,
                        raw_submission_id=None,
                        source_type=evidence.source_type,
                        connector=evidence.connector,
                        locator=evidence.locator,
                        publisher=evidence.publisher,
                        retrieved_at=evidence.retrieved_at,
                        published_at=evidence.published_at,
                        content_json=evidence.content,
                        checksum=evidence.checksum,
                        connector_version=evidence.connector_version,
                        classification=evidence.classification.value,
                        is_untrusted=evidence.is_untrusted,
                        is_stale=evidence.content.get("period_label")
                        != observation.raw_submission.reporting_period.label,
                    )
                    session.add(stored)
                    session.flush()
                elif (
                    stored.checksum != evidence.checksum
                    or stored.company_id != evidence.company_id
                    or stored.metric_definition_id != observation.metric_definition_id
                ):
                    raise ValueError(
                        "Fixture evidence ID collision with different immutable content."
                    )
                self._link_evidence(session, run.id, stored.id)
                external_count += 1
                untrusted_count += int(stored.is_untrusted)
        return {
            "internal_evidence_count": internal_count,
            "external_evidence_count": external_count,
            "untrusted_evidence_count": untrusted_count,
        }

    def _run_evidence(self, session: Session, run_id: str) -> list[EvidenceItemModel]:
        return list(
            session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(run_evidence.c.run_id == run_id)
                .options(joinedload(EvidenceItemModel.metric_definition))
            ).all()
        )

    def _extract(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        evidence_items = self._run_evidence(session, run.id)
        period = session.get(ReportingPeriodModel, run.reporting_period_id)
        assert period is not None
        extracted = 0
        rejected_untrusted = 0
        provider_models: Counter[str] = Counter()
        for evidence in evidence_items:
            if evidence.source_type == "portfolio_submission":
                continue
            if evidence.is_untrusted:
                rejected_untrusted += 1
                continue
            assert evidence.company_id is not None
            assert evidence.metric_definition_id is not None
            metric_definition = evidence.metric_definition
            assert metric_definition is not None
            company = session.get(CompanyModel, evidence.company_id)
            assert company is not None
            existing = session.scalar(
                select(ExtractionModel).where(
                    ExtractionModel.run_id == run.id,
                    ExtractionModel.evidence_item_id == evidence.id,
                )
            )
            if existing is not None:
                continue
            outcome = self._extraction_provider.extract(
                ExtractionRequest(
                    evidence=_evidence_contract(evidence),
                    expected_company_name=company.canonical_name,
                    expected_metric_key=metric_definition.key,
                    expected_period_label=period.label,
                )
            )
            extraction = outcome.extraction
            if extraction.metric_key != metric_definition.key:
                raise ValueError("Extraction metric does not match the planned metric.")
            if (
                extraction.company_name.casefold().strip()
                != company.canonical_name.casefold().strip()
            ):
                raise ValueError("Extraction company identity does not match the resolved company.")
            session.add(
                ExtractionModel(
                    run_id=run.id,
                    evidence_item_id=evidence.id,
                    company_id=company.id,
                    metric_definition_id=evidence.metric_definition_id,
                    extracted_value_json=extraction.value,
                    normalized_value_json=None,
                    missing_state=None,
                    unit=extraction.unit,
                    currency=extraction.currency,
                    period_label=extraction.period_label,
                    provider=outcome.provider,
                    model=outcome.model,
                    schema_version="strict-extraction-v1",
                )
            )
            extracted += 1
            provider_models[outcome.model or "deterministic"] += 1
        return {
            "extraction_count": extracted,
            "rejected_untrusted_count": rejected_untrusted,
            "provider_models": dict(sorted(provider_models.items())),
        }

    def _normalize(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        extractions = list(
            session.scalars(
                select(ExtractionModel)
                .where(ExtractionModel.run_id == run.id)
                .options(joinedload(ExtractionModel.metric_definition))
            ).all()
        )
        issue_counts: Counter[str] = Counter()
        for extraction in extractions:
            normalized = normalize_value(
                extraction.extracted_value_json,
                _metric_contract(extraction.metric_definition),
            )
            extraction.normalized_value_json = normalized.value
            extraction.missing_state = normalized.missing_state.value
            extraction.unit = normalized.unit
            extraction.currency = normalized.currency or extraction.currency
            extraction.normalization_issue_code = normalized.issue_code
            if normalized.issue_code:
                issue_counts[normalized.issue_code] += 1
        return {
            "normalized_extraction_count": len(extractions),
            "normalization_issues": dict(sorted(issue_counts.items())),
        }

    def _verify(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        observations = self._dataset_observations(session, run.dataset_id)
        extractions = list(
            session.scalars(
                select(ExtractionModel)
                .where(ExtractionModel.run_id == run.id)
                .options(
                    joinedload(ExtractionModel.metric_definition),
                    joinedload(ExtractionModel.evidence_item),
                )
            ).all()
        )
        evidence_items = self._run_evidence(session, run.id)
        evidence_by_pair: dict[tuple[str, str], list[EvidenceItemModel]] = defaultdict(list)
        for item in evidence_items:
            if item.company_id and item.metric_definition_id:
                evidence_by_pair[(item.company_id, item.metric_definition_id)].append(item)
        extraction_by_pair: dict[tuple[str, str], list[ExtractionModel]] = defaultdict(list)
        for extraction in extractions:
            extraction_by_pair[(extraction.company_id, extraction.metric_definition_id)].append(
                extraction
            )
        observation_by_pair = {
            (observation.company_id, observation.metric_definition_id): observation
            for observation in observations
        }
        all_pairs = set(observation_by_pair) | set(extraction_by_pair)
        status_counts: Counter[str] = Counter()
        for company_id, metric_id in sorted(all_pairs):
            observation = observation_by_pair.get((company_id, metric_id))
            candidates = extraction_by_pair.get((company_id, metric_id), [])
            metric = (
                observation.metric_definition
                if observation is not None
                else candidates[0].metric_definition
            )
            company = session.get(CompanyModel, company_id)
            assert company is not None
            period = session.get(ReportingPeriodModel, run.reporting_period_id)
            assert period is not None

            candidate_value: Any = None
            candidate_currency: str | None = None
            if observation is not None and observation.missing_state in {
                MissingState.OBSERVED.value,
                MissingState.ZERO.value,
            }:
                candidate_value = observation.normalized_value_json
                candidate_currency = observation.currency
            else:
                eligible = [
                    extraction
                    for extraction in candidates
                    if extraction.missing_state
                    in {MissingState.OBSERVED.value, MissingState.ZERO.value}
                    and extraction.period_label == period.label
                ]
                if eligible and metric.sourceability in {
                    Sourceability.PUBLICLY_SOURCEABLE.value,
                    Sourceability.MIXED.value,
                }:
                    candidate_value = eligible[0].normalized_value_json
                    candidate_currency = eligible[0].currency
            if candidate_value is None:
                continue

            extracted_by_evidence = {
                extraction.evidence_item_id: extraction for extraction in candidates
            }
            verification_evidence: list[VerificationEvidence] = []
            for item in evidence_by_pair[(company_id, metric_id)]:
                if item.source_type == "portfolio_submission":
                    value = item.content_json.get("value")
                    currency = item.content_json.get("currency")
                    period_label = item.content_json.get("period_label")
                else:
                    evidence_extraction = extracted_by_evidence.get(item.id)
                    value = (
                        evidence_extraction.normalized_value_json if evidence_extraction else None
                    )
                    currency = evidence_extraction.currency if evidence_extraction else None
                    period_label = (
                        evidence_extraction.period_label
                        if evidence_extraction
                        else item.content_json.get("period_label")
                    )
                verification_evidence.append(
                    VerificationEvidence(
                        evidence_id=item.id,
                        source_type=item.source_type,
                        value=value,
                        currency=currency if isinstance(currency, str) else None,
                        period_label=period_label if isinstance(period_label, str) else None,
                        expected_period_label=period.label,
                        publisher=item.publisher,
                        locator=item.locator,
                        checksum=item.checksum,
                        is_untrusted=item.is_untrusted,
                    )
                )
            outcome = verify_claim(
                candidate_value=candidate_value,
                candidate_currency=candidate_currency,
                sourceability=Sourceability(metric.sourceability),
                evidence=tuple(verification_evidence),
            )
            claim = ClaimModel(
                run_id=run.id,
                company_id=company_id,
                metric_definition_id=metric_id,
                reporting_period_id=period.id,
                text=_claim_text(
                    company, metric, candidate_value, candidate_currency, period.label
                ),
                normalized_value_json=candidate_value,
                verification_status=outcome.status.value,
            )
            claim.evidence_items = [
                item
                for item in evidence_by_pair[(company_id, metric_id)]
                if item.id in outcome.supporting_evidence_ids
            ]
            session.add(claim)
            session.flush()
            session.add(
                VerificationModel(
                    claim_id=claim.id,
                    status=outcome.status.value,
                    rationale=outcome.rationale,
                    verifier_role="independent_verifier",
                )
            )
            status_counts[outcome.status.value] += 1
        return {
            "claim_count": sum(status_counts.values()),
            "verification_statuses": dict(sorted(status_counts.items())),
        }

    def _compose(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        period = session.get(ReportingPeriodModel, run.reporting_period_id)
        assert period is not None
        claims = list(
            session.scalars(
                select(ClaimModel)
                .where(ClaimModel.run_id == run.id)
                .options(
                    joinedload(ClaimModel.company),
                    joinedload(ClaimModel.metric_definition),
                    joinedload(ClaimModel.verifications),
                )
                .order_by(ClaimModel.company_id, ClaimModel.metric_definition_id)
            ).unique()
        )
        observations = self._dataset_observations(session, run.dataset_id)
        report = ReportModel(
            run_id=run.id,
            dataset_id=run.dataset_id,
            reporting_period_id=period.id,
            title=f"Portfolio report — {period.label}",
            version=1,
            status=ReportStatus.DRAFT.value,
        )
        session.add(report)
        session.flush()

        status_counts = Counter(claim.verification_status for claim in claims)
        missing_counts = Counter(observation.missing_state for observation in observations)
        sections: list[ReportSectionModel] = []
        executive = ReportSectionModel(
            report_id=report.id,
            section_key="executive-summary",
            heading="Executive summary",
            order_index=10,
            body_markdown=(
                f"Reporting period: **{period.label}**.\n\n"
                "The verified workflow produced "
                f"{status_counts[VerificationStatus.SUPPORTED.value]} supported claims. "
                "Claims with conflicts or insufficient evidence are excluded from the "
                "supported narrative and shown in the verification exceptions section."
            ),
            version=1,
            is_current=True,
        )
        sections.append(executive)

        claims_by_company: dict[str, list[ClaimModel]] = defaultdict(list)
        for claim in claims:
            claims_by_company[claim.company_id].append(claim)
        order = 20
        for company_id, company_claims in sorted(
            claims_by_company.items(), key=lambda item: item[1][0].company.canonical_name.casefold()
        ):
            company = company_claims[0].company
            supported = [
                claim
                for claim in company_claims
                if claim.verification_status == VerificationStatus.SUPPORTED.value
            ]
            exceptions = [
                claim
                for claim in company_claims
                if claim.verification_status != VerificationStatus.SUPPORTED.value
            ]
            lines = ["Supported claims:"]
            lines.extend(f"- {claim.text}" for claim in supported)
            if not supported:
                lines.append("- No claims met the support rule for this period.")
            if exceptions:
                lines.append("\nVerification exceptions:")
                lines.extend(
                    f"- {claim.metric_definition.label}: `{claim.verification_status}`"
                    for claim in exceptions
                )
            section = ReportSectionModel(
                report_id=report.id,
                company_id=company_id,
                section_key=f"company-{company_id}",
                heading=company.canonical_name,
                order_index=order,
                body_markdown="\n".join(lines),
                version=1,
                is_current=True,
            )
            session.add(section)
            session.flush()
            for claim in company_claims:
                claim.report_section_id = section.id
            sections.append(section)
            order += 10

        exceptions_body = "\n".join(
            [
                f"- Supported: {status_counts[VerificationStatus.SUPPORTED.value]}",
                f"- Contradicted: {status_counts[VerificationStatus.CONTRADICTED.value]}",
                "- Insufficient evidence: "
                f"{status_counts[VerificationStatus.INSUFFICIENT_EVIDENCE.value]}",
                f"- Stale: {status_counts[VerificationStatus.STALE.value]}",
                "- Rejected as untrusted: "
                f"{status_counts[VerificationStatus.REJECTED_UNTRUSTED.value]}",
            ]
        )
        sections.append(
            ReportSectionModel(
                report_id=report.id,
                section_key="verification-exceptions",
                heading="Verification outcomes",
                order_index=900,
                body_markdown=exceptions_body,
                version=1,
                is_current=True,
            )
        )
        data_quality_body = "\n".join(
            f"- {state}: {count}" for state, count in sorted(missing_counts.items())
        )
        sections.append(
            ReportSectionModel(
                report_id=report.id,
                section_key="data-quality",
                heading="Data quality and missingness",
                order_index=910,
                body_markdown=data_quality_body or "No observations were imported.",
                version=1,
                is_current=True,
            )
        )
        sections.append(
            ReportSectionModel(
                report_id=report.id,
                section_key="methodology",
                heading="Methodology and limitations",
                order_index=920,
                body_markdown=(
                    "Claims were deterministically extracted and normalized, then checked by an "
                    "independent verifier against period-bounded provenance. Missing public "
                    "evidence is represented as missing; it is never inferred. Human approval "
                    "is required before export."
                ),
                version=1,
                is_current=True,
            )
        )
        session.add_all(sections)
        session.flush()
        report.content_hash = stable_hash(
            [
                {"key": section.section_key, "body": section.body_markdown}
                for section in sorted(sections, key=lambda item: item.order_index)
            ]
        )
        report.status = ReportStatus.PENDING_REVIEW.value
        return {"report_id": report.id, "section_count": len(sections), "version": 1}

    @staticmethod
    def _human_review_gate(session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        report = session.scalar(select(ReportModel).where(ReportModel.run_id == run.id))
        if report is None or report.status != ReportStatus.PENDING_REVIEW.value:
            raise ValueError("Report did not reach the required pending-review state.")
        return {
            "report_id": report.id,
            "status": ReportStatus.PENDING_REVIEW.value,
            "automatic_export": False,
        }
