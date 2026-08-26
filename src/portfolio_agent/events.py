from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session

from .enums import CollectionStatus, DataClassification, EventType, MissingState
from .ids import stable_hash
from .models import (
    CompanyEventModel,
    ObservationModel,
    RawSubmissionModel,
    SourceSnapshotModel,
    WorkflowRunModel,
    run_source_snapshots,
    source_snapshot_events,
)
from .temporal import (
    TemporalEvidence,
    TemporalWindow,
    restore_persisted_utc,
    temporal_eligibility,
)

UKRI_LIFECYCLE_STAGES = ("opportunity", "decision", "award", "project", "outcome")


@dataclass(frozen=True, slots=True)
class LifecycleCoverage:
    stage_counts: dict[str, int]
    covered_stage_count: int
    expected_stage_count: int
    completeness: float
    missing_stages: tuple[str, ...]


def lifecycle_coverage(stages: tuple[str | None, ...]) -> LifecycleCoverage:
    counts = Counter(stage for stage in stages if stage is not None)
    covered = sum(stage in counts for stage in UKRI_LIFECYCLE_STAGES)
    return LifecycleCoverage(
        stage_counts=dict(sorted(counts.items())),
        covered_stage_count=covered,
        expected_stage_count=len(UKRI_LIFECYCLE_STAGES),
        completeness=covered / len(UKRI_LIFECYCLE_STAGES),
        missing_stages=tuple(stage for stage in UKRI_LIFECYCLE_STAGES if stage not in counts),
    )


def events_for_run(session: Session, *, run_id: str) -> tuple[CompanyEventModel, ...]:
    """Return only events explicitly bound and temporally eligible for one workflow run."""

    run = session.get(WorkflowRunModel, run_id)
    if run is None or run.reporting_cutoff is None:
        return ()
    raw_submission_id = session.scalar(
        select(RawSubmissionModel.id).where(RawSubmissionModel.dataset_id == run.dataset_id)
    )
    private_events = (
        list(
            session.scalars(
                select(CompanyEventModel).where(
                    CompanyEventModel.raw_submission_id == raw_submission_id,
                    CompanyEventModel.source_key == "portfolio_submission",
                )
            ).all()
        )
        if raw_submission_id is not None
        else []
    )
    public_rows = session.execute(
        select(CompanyEventModel, SourceSnapshotModel)
        .join(
            source_snapshot_events,
            source_snapshot_events.c.company_event_id == CompanyEventModel.id,
        )
        .join(
            SourceSnapshotModel,
            SourceSnapshotModel.id == source_snapshot_events.c.source_snapshot_id,
        )
        .join(
            run_source_snapshots,
            run_source_snapshots.c.source_snapshot_id == SourceSnapshotModel.id,
        )
        .where(
            run_source_snapshots.c.run_id == run.id,
            run_source_snapshots.c.reporting_cutoff == run.reporting_cutoff,
            SourceSnapshotModel.status == CollectionStatus.SUCCEEDED.value,
        )
    ).all()
    eligible: dict[str, CompanyEventModel] = {}
    for event in private_events:
        if event.event_date is not None and event.event_date <= run.reporting_cutoff:
            eligible[event.id] = event
    for event, snapshot in public_rows:
        decision = temporal_eligibility(
            TemporalEvidence(
                published_at=restore_persisted_utc(snapshot.published_at),
                effective_from=event.event_date,
            ),
            TemporalWindow(reporting_cutoff=run.reporting_cutoff),
        )
        if decision.eligible:
            eligible[event.id] = event
    return tuple(
        sorted(
            eligible.values(),
            key=lambda event: (
                event.event_date or run.reporting_cutoff,
                event.event_type,
                event.public_identifier or event.id,
            ),
        )
    )


def persist_private_funding_events(
    session: Session,
    *,
    observations: tuple[ObservationModel, ...],
) -> int:
    """Convert submission funding into restricted events without public inference."""

    created = 0
    for observation in observations:
        if (
            observation.metric_definition.key != "private_funding"
            or observation.missing_state
            not in {MissingState.OBSERVED.value, MissingState.ZERO.value}
        ):
            continue
        fingerprint = stable_hash(
            {
                "raw_submission_id": observation.raw_submission_id,
                "company_id": observation.company_id,
                "observation_id": observation.id,
                "event_type": EventType.PRIVATE_FUNDING_REPORTED.value,
            }
        )
        if session.scalar(
            select(CompanyEventModel.id).where(CompanyEventModel.event_fingerprint == fingerprint)
        ):
            continue
        amount: Decimal | None = None
        if observation.currency and observation.normalized_value_json is not None:
            try:
                amount = Decimal(str(observation.normalized_value_json))
            except InvalidOperation:
                amount = None
        session.add(
            CompanyEventModel(
                event_fingerprint=fingerprint,
                company_id=observation.company_id,
                source_snapshot_id=None,
                raw_submission_id=observation.raw_submission_id,
                source_key="portfolio_submission",
                event_type=EventType.PRIVATE_FUNDING_REPORTED.value,
                lifecycle_stage=None,
                public_identifier=None,
                event_date=observation.raw_submission.reporting_period.end_date,
                amount=amount,
                currency=observation.currency,
                title="Private funding reported in restricted submission",
                details_json={
                    "source_cell": observation.source_cell,
                    "causal_attribution": False,
                    "publicly_verified": False,
                },
                source_locator=(
                    f"submission://{observation.raw_submission.dataset_id}"
                    f"#{observation.source_cell or observation.id}"
                ),
                classification=DataClassification.RESTRICTED.value,
            )
        )
        created += 1
    return created
