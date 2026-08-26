from __future__ import annotations

import time
from collections import Counter, defaultdict
from collections.abc import Callable
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import insert, select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from .cbit_contract import PeriodSemantics
from .connectors.base import Connector, ConnectorQuery, SourceRequest
from .connectors.registry import SourceRegistry
from .context import compare_with_prior_periods, derive_context_statistics
from .enums import (
    CollectionStatus,
    DataClassification,
    ExtractionAttemptStatus,
    IdentifierScheme,
    MetricDataType,
    MissingState,
    ReportStatus,
    ResolutionStatus,
    RunStatus,
    Sourceability,
    TemporalEligibilityStatus,
    VerificationStatus,
    WorkflowStage,
)
from .events import events_for_run, persist_private_funding_events
from .ids import stable_hash
from .llm.base import (
    ExtractionProvider,
    ExtractionProviderError,
    ExtractionRequest,
    ProviderAttempt,
)
from .models import (
    AgentRunModel,
    ClaimModel,
    CompanyIdentifierModel,
    CompanyModel,
    CompanyProgrammeMembershipModel,
    EvidenceFactModel,
    EvidenceItemModel,
    ExtractionAttemptModel,
    ExtractionModel,
    MetricDefinitionModel,
    ObservationModel,
    QualityViolationModel,
    RawSubmissionModel,
    ReportingPeriodModel,
    ReportModel,
    ReportSectionModel,
    SourceSnapshotModel,
    VerificationModel,
    WorkflowRunModel,
    run_evidence,
    run_source_snapshots,
)
from .normalization import normalize_value
from .quality import (
    QUALITY_CONTRACT_VERSION,
    QualityRecord,
    evaluate_quality,
    persist_quality_evaluation,
)
from .schemas import EvidenceItem, MetricDefinition, PipelineResult
from .temporal import (
    TemporalDecision,
    TemporalEvidence,
    TemporalWindow,
    restore_persisted_utc,
    temporal_eligibility,
)
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
        period_semantics=PeriodSemantics(row.period_semantics or PeriodSemantics.NONE.value),
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


def _public_evidence_company_reference(
    *, snapshot_sha256: str | None, source_key: str, source_locator: str
) -> str:
    """Return a model-safe alias derived only from public evidence provenance."""
    return (
        "public-evidence:"
        + stable_hash(
            {
                "snapshot_sha256": snapshot_sha256,
                "source_key": source_key,
                "source_locator": source_locator,
            }
        )[:20]
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
    semantics = PeriodSemantics(metric.period_semantics or PeriodSemantics.NONE.value)
    if semantics is PeriodSemantics.SINCE_PROGRAMME_START:
        relation = f"cumulatively {period_label}"
    elif semantics in {
        PeriodSemantics.AS_AT_CUTOFF,
        PeriodSemantics.BEFORE_PROGRAMME,
    }:
        relation = period_label
    else:
        relation = f"for {period_label}"
    return f"{company.canonical_name}: {metric.label} was {value}{suffix} {relation}."


def _semantic_period_label(
    metric: MetricDefinitionModel,
    *,
    reporting_period_label: str,
    reporting_cutoff: date,
    programme_start_date: date | None,
) -> str | None:
    semantics = PeriodSemantics(metric.period_semantics or PeriodSemantics.NONE.value)
    if semantics is PeriodSemantics.SINCE_PROGRAMME_START:
        if programme_start_date is None or programme_start_date > reporting_cutoff:
            return None
        return f"from {programme_start_date.isoformat()} through {reporting_cutoff.isoformat()}"
    if semantics is PeriodSemantics.AS_AT_CUTOFF:
        return f"as at {reporting_cutoff.isoformat()}"
    if semantics is PeriodSemantics.BEFORE_PROGRAMME:
        return (
            f"before programme start {programme_start_date.isoformat()}"
            if programme_start_date is not None
            else None
        )
    if semantics is PeriodSemantics.LIFETIME:
        return f"lifetime through {reporting_cutoff.isoformat()}"
    return reporting_period_label


def _fact_period_label(fact: EvidenceFactModel) -> str | None:
    if fact.period_start is not None and fact.period_end is not None:
        return f"from {fact.period_start.isoformat()} through {fact.period_end.isoformat()}"
    return None


class PortfolioWorkflow:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        connector: Connector,
        extraction_provider: ExtractionProvider,
        source_registry: SourceRegistry | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._connector = connector
        self._extraction_provider = extraction_provider
        self._source_registry = source_registry

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
                reporting_cutoff=raw.reporting_cutoff,
                evidence_contract_version="uk-public-evidence-v2",
                quality_contract_version=QUALITY_CONTRACT_VERSION,
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
            if stage is WorkflowStage.COLLECT:
                self._prepare_source_collections(run_id)
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

    def _prepare_source_collections(self, run_id: str) -> None:
        if self._source_registry is None or not self._source_registry.manifests:
            return
        with self._session_factory() as session:
            run = session.get(WorkflowRunModel, run_id)
            if run is None or run.reporting_cutoff is None:
                raise ValueError("Source collection requires a persisted reporting cutoff.")
            company_ids = sorted(
                set(
                    session.scalars(
                        select(ObservationModel.company_id)
                        .join(RawSubmissionModel)
                        .where(RawSubmissionModel.dataset_id == run.dataset_id)
                    ).all()
                )
            )
            identifiers = list(
                session.scalars(
                    select(CompanyIdentifierModel).where(
                        CompanyIdentifierModel.company_id.in_(company_ids),
                        CompanyIdentifierModel.reviewed.is_(True),
                    )
                ).all()
            )
            programme_starts = self._programme_starts(session, run.dataset_id)
            requests: list[SourceRequest] = []
            for manifest in self._source_registry.manifests:
                if "offline_snapshot" not in manifest.retrieval_modes:
                    continue
                for company_id in company_ids:
                    active = [
                        identifier
                        for identifier in identifiers
                        if identifier.company_id == company_id
                        and identifier.source_key == manifest.key
                        and identifier.scheme
                        in {scheme.value for scheme in manifest.identifier_schemes}
                        and (
                            identifier.valid_from is None
                            or identifier.valid_from <= run.reporting_cutoff
                        )
                        and (
                            identifier.valid_to is None
                            or identifier.valid_to >= run.reporting_cutoff
                        )
                    ]
                    if len(active) > 1:
                        raise ValueError(
                            "Multiple active reviewed identifiers exist for one company/source."
                        )
                    if not active:
                        continue
                    identifier = active[0]
                    requests.append(
                        SourceRequest(
                            source_key=manifest.key,
                            company_id=company_id,
                            identifier_scheme=IdentifierScheme(identifier.scheme),
                            identifier_value=identifier.value,
                            reporting_cutoff=run.reporting_cutoff,
                            programme_start_date=programme_starts.get(company_id),
                            fact_keys=manifest.fact_keys,
                            mode="offline_snapshot",
                        )
                    )

        for request in requests:
            result = self._source_registry.collect(request)
            with self._session_factory.begin() as session:
                run = session.get(WorkflowRunModel, run_id)
                snapshot = session.get(SourceSnapshotModel, result.snapshot_id)
                if run is None or run.reporting_cutoff is None or snapshot is None:
                    raise ValueError("Collected source snapshot could not be bound to its run.")
                if (
                    snapshot.company_id != request.company_id
                    or snapshot.reporting_cutoff != run.reporting_cutoff
                ):
                    raise ValueError("Source snapshot identity or cutoff changed before run link.")
                existing = session.execute(
                    select(run_source_snapshots).where(
                        run_source_snapshots.c.run_id == run.id,
                        run_source_snapshots.c.source_snapshot_id == snapshot.id,
                    )
                ).first()
                if existing is None:
                    session.execute(
                        insert(run_source_snapshots).values(
                            run_id=run.id,
                            source_snapshot_id=snapshot.id,
                            reporting_cutoff=run.reporting_cutoff,
                            linked_at=datetime.now(UTC),
                        )
                    )

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

    @staticmethod
    def _programme_starts(session: Session, dataset_id: str) -> dict[str, date]:
        return {
            company_id: programme_start
            for company_id, programme_start in session.execute(
                select(
                    CompanyProgrammeMembershipModel.company_id,
                    CompanyProgrammeMembershipModel.programme_start_date,
                )
                .join(
                    RawSubmissionModel,
                    RawSubmissionModel.id == CompanyProgrammeMembershipModel.raw_submission_id,
                )
                .where(RawSubmissionModel.dataset_id == dataset_id)
            ).all()
        }

    def _plan(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        observations = self._dataset_observations(session, run.dataset_id)
        public_tasks = sum(
            observation.metric_definition.sourceability
            in {Sourceability.PUBLICLY_SOURCEABLE.value, Sourceability.MIXED.value}
            for observation in observations
        )
        if public_tasks and run.reporting_cutoff is None:
            raise ValueError(
                "Public evidence planning requires the immutable submission reporting cutoff."
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

    def _link_evidence(
        self,
        session: Session,
        *,
        run: WorkflowRunModel,
        evidence_id: str,
        temporal: TemporalDecision,
    ) -> None:
        if run.reporting_cutoff is None:
            raise ValueError("Run-relative evidence requires a reporting cutoff.")
        existing = session.execute(
            select(run_evidence).where(
                run_evidence.c.run_id == run.id,
                run_evidence.c.evidence_item_id == evidence_id,
            )
        ).first()
        if existing is None:
            session.execute(
                insert(run_evidence).values(
                    run_id=run.id,
                    evidence_item_id=evidence_id,
                    reporting_cutoff=run.reporting_cutoff,
                    temporal_status=temporal.status.value,
                    temporal_reason=temporal.rationale,
                    evaluated_at=datetime.now(UTC),
                )
            )
            return
        if (
            existing.reporting_cutoff != run.reporting_cutoff
            or existing.temporal_status != temporal.status.value
            or existing.temporal_reason != temporal.rationale
        ):
            raise ValueError("Run evidence link was reused with changed temporal semantics.")

    def _collect(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        observations = self._dataset_observations(session, run.dataset_id)
        period = session.get(ReportingPeriodModel, run.reporting_period_id)
        assert period is not None
        if run.reporting_cutoff is None:
            raise ValueError("Evidence collection requires a reporting cutoff.")
        private_event_count = persist_private_funding_events(
            session, observations=tuple(observations)
        )
        internal_count = 0
        external_count = 0
        untrusted_count = 0
        programme_starts = self._programme_starts(session, run.dataset_id)
        for observation in observations:
            semantic_period_label = _semantic_period_label(
                observation.metric_definition,
                reporting_period_label=observation.raw_submission.reporting_period.label,
                reporting_cutoff=run.reporting_cutoff,
                programme_start_date=programme_starts.get(observation.company_id),
            )
            internal_content = {
                "company_name": observation.company.canonical_name,
                "metric_key": observation.metric_definition.key,
                "period_label": semantic_period_label,
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
                    temporal_status="eligible",
                )
                session.add(internal)
                session.flush()
            internal_temporal = temporal_eligibility(
                TemporalEvidence(
                    published_at=None,
                    is_internal_submission=True,
                ),
                TemporalWindow(
                    reporting_cutoff=run.reporting_cutoff,
                    period_start=period.start_date,
                    period_end=period.end_date,
                ),
            )
            self._link_evidence(
                session,
                run=run,
                evidence_id=internal.id,
                temporal=internal_temporal,
            )
            internal_count += 1

            if observation.metric_definition.sourceability not in {
                Sourceability.PUBLICLY_SOURCEABLE.value,
                Sourceability.MIXED.value,
            }:
                continue
            if semantic_period_label is None:
                continue
            query = ConnectorQuery(
                company_id=observation.company.id,
                company_name=observation.company.canonical_name,
                external_id=observation.company.external_id,
                metric_key=observation.metric_definition.key,
                period_label=semantic_period_label,
                reporting_cutoff=run.reporting_cutoff,
            )
            for evidence in self._connector.collect(query):
                temporal = temporal_eligibility(
                    TemporalEvidence(published_at=evidence.published_at),
                    TemporalWindow(
                        reporting_cutoff=run.reporting_cutoff,
                        period_start=period.start_date,
                        period_end=period.end_date,
                    ),
                )
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
                        is_stale=evidence.content.get("period_label") != semantic_period_label,
                        temporal_status=temporal.status.value,
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
                self._link_evidence(
                    session,
                    run=run,
                    evidence_id=stored.id,
                    temporal=temporal,
                )
                external_count += 1
                untrusted_count += int(stored.is_untrusted)
        registry_fact_count = self._collect_registry_facts(session, run=run, period=period)
        source_snapshot_count = len(
            session.execute(
                select(run_source_snapshots.c.source_snapshot_id).where(
                    run_source_snapshots.c.run_id == run.id
                )
            ).all()
        )
        return {
            "internal_evidence_count": internal_count,
            "external_evidence_count": external_count + registry_fact_count,
            "registry_fact_evidence_count": registry_fact_count,
            "source_snapshot_count": source_snapshot_count,
            "untrusted_evidence_count": untrusted_count,
            "private_funding_event_count": private_event_count,
        }

    def _collect_registry_facts(
        self,
        session: Session,
        *,
        run: WorkflowRunModel,
        period: ReportingPeriodModel,
    ) -> int:
        reporting_cutoff = run.reporting_cutoff
        if reporting_cutoff is None:
            raise ValueError("Registry fact collection requires a reporting cutoff.")
        rows = session.execute(
            select(EvidenceFactModel, SourceSnapshotModel)
            .join(
                SourceSnapshotModel,
                SourceSnapshotModel.id == EvidenceFactModel.source_snapshot_id,
            )
            .join(
                run_source_snapshots,
                run_source_snapshots.c.source_snapshot_id == SourceSnapshotModel.id,
            )
            .where(
                run_source_snapshots.c.run_id == run.id,
            )
        ).all()
        publishers = (
            {manifest.key: manifest.publisher for manifest in self._source_registry.manifests}
            if self._source_registry is not None
            else {}
        )
        created_or_linked = 0
        for fact, snapshot in rows:
            company = session.get(CompanyModel, fact.company_id)
            metric = (
                session.get(MetricDefinitionModel, fact.metric_definition_id)
                if fact.metric_definition_id is not None
                else None
            )
            if company is None or (fact.metric_definition_id is not None and metric is None):
                raise ValueError("Source fact lost its company or metric definition.")
            published_at = restore_persisted_utc(fact.published_at) or restore_persisted_utc(
                snapshot.published_at
            )
            public_company_reference = _public_evidence_company_reference(
                snapshot_sha256=snapshot.sha256,
                source_key=snapshot.source_key,
                source_locator=fact.source_locator,
            )
            content = {
                "company_name": public_company_reference,
                "metric_key": metric.key if metric is not None else None,
                "period_label": _fact_period_label(fact),
                "value": fact.value_json,
                "unit": fact.unit,
                "currency": fact.currency,
                "fact_key": fact.fact_key,
                "period_start": fact.period_start.isoformat() if fact.period_start else None,
                "period_end": fact.period_end.isoformat() if fact.period_end else None,
                "reporting_cutoff": reporting_cutoff.isoformat(),
                "snapshot_sha256": snapshot.sha256,
                "structured_locator": fact.structured_locator_json,
                "extraction_method": fact.extraction_method,
                "extraction_schema_version": fact.extraction_schema_version,
                "missing_state": (
                    fact.value_json if fact.fact_key.endswith("_missing_state") else None
                ),
            }
            checksum = stable_hash(
                {
                    "source_snapshot_id": snapshot.id,
                    "source_sha256": snapshot.sha256,
                    "locator": fact.source_locator,
                    "content": content,
                }
            )
            evidence = session.scalar(
                select(EvidenceItemModel).where(
                    EvidenceItemModel.source_snapshot_id == snapshot.id,
                    EvidenceItemModel.metric_definition_id == fact.metric_definition_id,
                    EvidenceItemModel.locator == fact.source_locator,
                )
            )
            if evidence is None:
                evidence = EvidenceItemModel(
                    company_id=fact.company_id,
                    metric_definition_id=fact.metric_definition_id,
                    raw_submission_id=None,
                    source_snapshot_id=snapshot.id,
                    source_type="public_source_fact",
                    connector=snapshot.source_key,
                    locator=fact.source_locator,
                    publisher=publishers.get(snapshot.source_key),
                    retrieved_at=snapshot.retrieved_at,
                    published_at=published_at,
                    content_json=content,
                    checksum=checksum,
                    connector_version=snapshot.source_version,
                    classification=snapshot.classification,
                    is_untrusted=False,
                    is_stale=False,
                    temporal_status=None,
                )
                session.add(evidence)
                session.flush()
            elif evidence.checksum != checksum or evidence.company_id != fact.company_id:
                raise ValueError("Source fact evidence changed under an immutable locator.")
            temporal = temporal_eligibility(
                TemporalEvidence(
                    published_at=published_at,
                    effective_from=restore_persisted_utc(fact.effective_at) or fact.period_start,
                    effective_to=fact.period_end,
                ),
                TemporalWindow(
                    reporting_cutoff=reporting_cutoff,
                    period_start=period.start_date,
                    period_end=period.end_date,
                ),
            )
            self._link_evidence(
                session,
                run=run,
                evidence_id=evidence.id,
                temporal=temporal,
            )
            created_or_linked += 1
        return created_or_linked

    def _run_evidence(
        self, session: Session, run_id: str, *, eligible_only: bool = False
    ) -> list[EvidenceItemModel]:
        statement = (
            select(EvidenceItemModel)
            .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
            .where(run_evidence.c.run_id == run_id)
            .options(joinedload(EvidenceItemModel.metric_definition))
        )
        if eligible_only:
            statement = statement.where(
                run_evidence.c.temporal_status == TemporalEligibilityStatus.ELIGIBLE.value
            )
        return list(session.scalars(statement).all())

    @staticmethod
    def _run_temporal_decisions(session: Session, run_id: str) -> dict[str, str]:
        return {
            evidence_id: status
            for evidence_id, status in session.execute(
                select(
                    run_evidence.c.evidence_item_id,
                    run_evidence.c.temporal_status,
                ).where(run_evidence.c.run_id == run_id)
            ).all()
            if status is not None
        }

    def _extract(self, session: Session, run: WorkflowRunModel) -> dict[str, Any]:
        evidence_items = self._run_evidence(session, run.id, eligible_only=True)
        period = session.get(ReportingPeriodModel, run.reporting_period_id)
        assert period is not None
        extracted = 0
        rejected_untrusted = 0
        failed_attempts = 0
        provider_models: Counter[str] = Counter()
        for evidence in evidence_items:
            if evidence.source_type == "portfolio_submission":
                continue
            if evidence.is_untrusted:
                rejected_untrusted += 1
                continue
            if evidence.metric_definition_id is None:
                continue
            assert evidence.company_id is not None
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
            expected_period_label = evidence.content_json.get("period_label")
            if not isinstance(expected_period_label, str) or not expected_period_label:
                continue
            expected_company_reference = evidence.content_json.get("company_name")
            if not isinstance(expected_company_reference, str) or not expected_company_reference:
                raise ValueError("Public evidence is missing its model-safe company reference.")
            request = ExtractionRequest(
                evidence=_evidence_contract(evidence),
                expected_company_name=expected_company_reference,
                expected_metric_key=metric_definition.key,
                expected_period_label=expected_period_label,
            )
            try:
                outcome = self._extraction_provider.extract(request)
            except ExtractionProviderError as exc:
                self._persist_provider_attempts(
                    session,
                    run_id=run.id,
                    evidence_item_id=evidence.id,
                    extraction_id=None,
                    attempts=exc.attempt_records,
                )
                failed_attempts += len(exc.attempt_records)
                continue
            extraction = outcome.extraction
            if extraction.metric_key != metric_definition.key:
                raise ValueError("Extraction metric does not match the planned metric.")
            if (
                extraction.company_name.casefold().strip()
                != expected_company_reference.casefold().strip()
            ):
                raise ValueError("Extraction company reference does not match public evidence.")
            stored_extraction = ExtractionModel(
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
                schema_version="strict-extraction-v2",
                evidence_locator=extraction.evidence_locator,
                evidence_span=extraction.evidence_span,
                abstain_reason=extraction.abstain_reason,
                confidence=extraction.confidence,
            )
            session.add(stored_extraction)
            session.flush()
            attempts = outcome.attempt_records or (
                ProviderAttempt(
                    attempt_number=1,
                    provider=outcome.provider,
                    model=outcome.model,
                    status=ExtractionAttemptStatus.SUCCEEDED.value,
                    duration_ms=0,
                    input_hash=stable_hash(
                        {
                            "evidence_id": evidence.id,
                            "metric_key": metric_definition.key,
                        }
                    ),
                    input_tokens=outcome.input_tokens,
                    output_tokens=outcome.output_tokens,
                ),
            )
            self._persist_provider_attempts(
                session,
                run_id=run.id,
                evidence_item_id=evidence.id,
                extraction_id=stored_extraction.id,
                attempts=attempts,
            )
            extracted += 1
            provider_models[outcome.model or "deterministic"] += 1
        return {
            "extraction_count": extracted,
            "rejected_untrusted_count": rejected_untrusted,
            "failed_provider_attempt_count": failed_attempts,
            "provider_models": dict(sorted(provider_models.items())),
        }

    @staticmethod
    def _persist_provider_attempts(
        session: Session,
        *,
        run_id: str,
        evidence_item_id: str,
        extraction_id: str | None,
        attempts: tuple[ProviderAttempt, ...],
    ) -> None:
        for attempt in attempts:
            session.add(
                ExtractionAttemptModel(
                    run_id=run_id,
                    evidence_item_id=evidence_item_id,
                    extraction_id=extraction_id,
                    provider=attempt.provider,
                    model=attempt.model,
                    prompt_version=attempt.prompt_version,
                    attempt_number=attempt.attempt_number,
                    status=attempt.status,
                    input_hash=attempt.input_hash,
                    output_hash=attempt.output_hash,
                    input_tokens=attempt.input_tokens,
                    output_tokens=attempt.output_tokens,
                    cost_usd=None,
                    duration_ms=attempt.duration_ms,
                    error=attempt.error,
                    escalation_cause=attempt.escalation_cause,
                )
            )

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
        temporal_by_evidence = self._run_temporal_decisions(session, run.id)
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
        if run.reporting_cutoff is None:
            raise ValueError("Verification requires a persisted reporting cutoff.")
        programme_starts = self._programme_starts(session, run.dataset_id)
        quality_records: list[QualityRecord] = []
        for item in evidence_items:
            quality_extraction = next(
                (row for row in extractions if row.evidence_item_id == item.id),
                None,
            )
            value = (
                item.content_json.get("value")
                if item.source_type == "portfolio_submission"
                else quality_extraction.normalized_value_json
                if quality_extraction is not None
                else item.content_json.get("value")
            )
            missing_state = (
                item.content_json.get("missing_state")
                if item.source_type == "portfolio_submission"
                else quality_extraction.missing_state
                if quality_extraction is not None
                else item.content_json.get("missing_state")
            )
            period_label = (
                item.content_json.get("period_label")
                if item.source_type == "portfolio_submission"
                else quality_extraction.period_label
                if quality_extraction is not None
                else item.content_json.get("period_label")
            )
            unit = (
                item.content_json.get("unit")
                if item.source_type == "portfolio_submission"
                else quality_extraction.unit
                if quality_extraction is not None
                else item.content_json.get("unit")
            )
            currency = (
                item.content_json.get("currency")
                if item.source_type == "portfolio_submission"
                else quality_extraction.currency
                if quality_extraction is not None
                else item.content_json.get("currency")
            )
            quality_records.append(
                QualityRecord(
                    evidence_item_id=item.id,
                    source_snapshot_id=item.source_snapshot_id,
                    company_id=item.company_id,
                    metric_definition_id=item.metric_definition_id,
                    source_type=item.source_type,
                    locator=item.locator,
                    checksum=item.checksum,
                    is_untrusted=item.is_untrusted,
                    temporal_status=temporal_by_evidence[item.id],
                    value=value,
                    missing_state=(missing_state if isinstance(missing_state, str) else None),
                    period_label=(period_label if isinstance(period_label, str) else None),
                    unit=(unit if isinstance(unit, str) else None),
                    currency=(currency if isinstance(currency, str) else None),
                )
            )
        source_snapshots = list(
            session.scalars(
                select(SourceSnapshotModel)
                .join(
                    run_source_snapshots,
                    run_source_snapshots.c.source_snapshot_id == SourceSnapshotModel.id,
                )
                .where(
                    run_source_snapshots.c.run_id == run.id,
                    SourceSnapshotModel.status.in_(("no_record", "source_unavailable", "failed")),
                )
            ).all()
        )
        quality_records.extend(
            QualityRecord(
                evidence_item_id=None,
                source_snapshot_id=snapshot.id,
                company_id=snapshot.company_id,
                metric_definition_id=None,
                source_type="public_source_snapshot",
                locator=snapshot.locator,
                checksum=snapshot.derivation_sha256 or snapshot.request_fingerprint,
                is_untrusted=False,
                temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
                value={
                    "status": snapshot.status,
                    "error_code": snapshot.error_code,
                },
                missing_state=(
                    MissingState.NOT_FOUND_PUBLICLY.value
                    if snapshot.status == CollectionStatus.NO_RECORD.value
                    else MissingState.SOURCE_UNAVAILABLE.value
                    if snapshot.status == CollectionStatus.SOURCE_UNAVAILABLE.value
                    else MissingState.INVALID.value
                ),
                source_terminal_status=snapshot.status,
            )
            for snapshot in source_snapshots
        )
        quality_evaluation = evaluate_quality(tuple(quality_records))
        persist_quality_evaluation(
            session,
            run_id=run.id,
            evaluation=quality_evaluation,
        )
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
            expected_period_label = _semantic_period_label(
                metric,
                reporting_period_label=period.label,
                reporting_cutoff=run.reporting_cutoff,
                programme_start_date=programme_starts.get(company_id),
            )
            if expected_period_label is None:
                continue

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
                    and extraction.period_label == expected_period_label
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
                        expected_period_label=expected_period_label,
                        publisher=item.publisher,
                        locator=item.locator,
                        checksum=item.checksum,
                        is_untrusted=item.is_untrusted,
                        temporal_status=temporal_by_evidence[item.id],
                    )
                )
            outcome = verify_claim(
                candidate_value=candidate_value,
                candidate_currency=candidate_currency,
                sourceability=Sourceability(metric.sourceability),
                evidence=tuple(verification_evidence),
                require_currency=metric.data_type == MetricDataType.CURRENCY.value,
            )
            claim = ClaimModel(
                run_id=run.id,
                company_id=company_id,
                metric_definition_id=metric_id,
                reporting_period_id=period.id,
                text=_claim_text(
                    company,
                    metric,
                    candidate_value,
                    candidate_currency,
                    expected_period_label,
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
            "quality_dispositions": quality_evaluation.disposition_counts,
            "quality_violation_count": len(quality_evaluation.findings),
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
        evidence_items = list(
            session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(run_evidence.c.run_id == run.id)
            ).all()
        )
        source_snapshots = list(
            session.scalars(
                select(SourceSnapshotModel)
                .join(
                    run_source_snapshots,
                    run_source_snapshots.c.source_snapshot_id == SourceSnapshotModel.id,
                )
                .where(run_source_snapshots.c.run_id == run.id)
            ).all()
        )
        source_versions = {
            item.connector: item.connector_version
            for item in sorted(
                evidence_items, key=lambda row: (row.connector, row.connector_version)
            )
        }
        source_versions.update(
            {
                snapshot.source_key: snapshot.source_version
                for snapshot in sorted(
                    source_snapshots,
                    key=lambda row: (row.source_key, row.source_version),
                )
            }
        )
        context_summaries = derive_context_statistics(
            session,
            run=run,
            observations=tuple(observations),
            source_versions=source_versions,
        )
        changes = compare_with_prior_periods(session, observations=tuple(observations))
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
        change_rows = [
            "| Company | Metric | Current period | Prior period | Status | Current | Prior "
            "| Change | % change |",
            "|---|---|---|---|---|---:|---:|---:|---:|",
        ]
        for change in changes:
            change_rows.append(
                "| {company} | {metric} | {current_period} | {prior_period} | {status} | "
                "{current} | {prior} | {absolute} | {percentage} |".format(
                    company=change.company_name,
                    metric=change.metric_label,
                    current_period=change.current_period,
                    prior_period=change.prior_period or "—",
                    status=change.status,
                    current=change.current_value or "—",
                    prior=change.prior_value or "—",
                    absolute=change.absolute_change or "—",
                    percentage=(
                        f"{change.percentage_change}%" if change.percentage_change else "—"
                    ),
                )
            )
        sections.append(
            ReportSectionModel(
                report_id=report.id,
                section_key="period-change",
                heading="Period change and comparability",
                order_index=905,
                body_markdown="\n".join(change_rows),
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
        source_counts = Counter(item.connector for item in evidence_items)
        snapshot_counts = Counter(
            (snapshot.source_key, snapshot.status) for snapshot in source_snapshots
        )
        source_rows = [
            "| Connector | Version | Evidence items | Snapshots | Snapshot status |",
            "|---|---|---:|---:|---|",
        ]
        for connector in sorted(set(source_counts) | {key for key, _ in snapshot_counts}):
            statuses = [
                f"{status}: {count}"
                for (key, status), count in sorted(snapshot_counts.items())
                if key == connector
            ]
            source_rows.append(
                f"| {connector} | {source_versions[connector]} | "
                f"{source_counts[connector]} | "
                f"{sum(count for (key, _), count in snapshot_counts.items() if key == connector)} "
                f"| {', '.join(statuses) or 'not applicable'} |"
            )
        sections.append(
            ReportSectionModel(
                report_id=report.id,
                section_key="source-coverage",
                heading="Source coverage",
                order_index=912,
                body_markdown="\n".join(source_rows),
                version=1,
                is_current=True,
            )
        )
        quality_findings = list(
            session.scalars(
                select(QualityViolationModel)
                .where(QualityViolationModel.run_id == run.id)
                .order_by(QualityViolationModel.fingerprint)
            ).all()
        )
        quality_counts = Counter(finding.disposition for finding in quality_findings)
        quality_rows = [
            "| Disposition | Findings |",
            "|---|---:|",
        ]
        quality_rows.extend(
            f"| {disposition} | {count} |" for disposition, count in sorted(quality_counts.items())
        )
        if len(quality_rows) == 2:
            quality_rows.append("| pass | 0 explicit violations |")
        else:
            quality_rows.extend(
                [
                    "",
                    "| Rule | Disposition | Finding |",
                    "|---|---|---|",
                    *(
                        "| {rule} | {disposition} | {message} |".format(
                            rule=finding.rule_key,
                            disposition=finding.disposition,
                            message=finding.message.replace("|", "\\|"),
                        )
                        for finding in quality_findings
                    ),
                ]
            )
        sections.append(
            ReportSectionModel(
                report_id=report.id,
                section_key="quality-contract",
                heading="Executable quality-contract outcomes",
                order_index=914,
                body_markdown="\n".join(quality_rows),
                version=1,
                is_current=True,
            )
        )
        events = list(events_for_run(session, run_id=run.id))
        event_rows = [
            "| Date | Source | Event | Stage | Amount | Evidence locator |",
            "|---|---|---|---|---:|---|",
        ]
        event_rows.extend(
            "| {date} | {source} | {title} | {stage} | {amount} | `{locator}` |".format(
                date=event.event_date.isoformat() if event.event_date else "—",
                source=event.source_key,
                title=event.title,
                stage=event.lifecycle_stage or "—",
                amount=(
                    f"{event.amount} {event.currency or ''}".strip()
                    if event.amount is not None
                    else "—"
                ),
                locator=event.source_locator,
            )
            for event in events
        )
        if len(event_rows) == 2:
            event_rows.append("| — | — | No eligible events were recorded. | — | — | — |")
        sections.append(
            ReportSectionModel(
                report_id=report.id,
                section_key="event-timeline",
                heading="Event timeline",
                order_index=916,
                body_markdown="\n".join(event_rows),
                version=1,
                is_current=True,
            )
        )
        context_rows = [
            "| Metric | Exposure window | Status | N | Minimum N | Min | Q1 | Median | Q3 | "
            "Max | Unit / currency |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
        context_rows.extend(
            "| {metric} | {exposure} | {status} | {sample} | {minimum_sample} | {minimum} | {q1} | "
            "{median} | {q3} | {maximum} | {measure} |".format(
                metric=item.metric_label,
                exposure=item.exposure_window,
                status=item.status,
                sample=item.sample_size,
                minimum_sample=item.minimum_sample_size,
                minimum=item.minimum or "—",
                q1=item.first_quartile or "—",
                median=item.median or "—",
                q3=item.third_quartile or "—",
                maximum=item.maximum or "—",
                measure=item.currency or item.unit or "unitless",
            )
            for item in context_summaries
        )
        if len(context_rows) == 2:
            context_rows.append("| — | — | no_numeric_cohort | 0 | 3 | — | — | — | — | — | — |")
        context_rows.extend(
            [
                "",
                f"Within-portfolio cutoff: **{run.reporting_cutoff}**. Statistics describe only "
                "companies in this imported portfolio; they are not an external UK benchmark. "
                "Statistics are suppressed below N=3, and missing states are excluded rather "
                "than imputed. No ranking or recommendation is produced.",
            ]
        )
        sections.append(
            ReportSectionModel(
                report_id=report.id,
                section_key="portfolio-context",
                heading="Within-portfolio context",
                order_index=918,
                body_markdown="\n".join(context_rows),
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
