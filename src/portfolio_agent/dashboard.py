from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .enums import ReportStatus, RunStatus, WorkflowStage
from .models import AgentRunModel, ReportModel, WorkflowRunModel


@dataclass(frozen=True, slots=True)
class StageDefinition:
    key: str
    label: str
    purpose: str
    boundary: str


@dataclass(frozen=True, slots=True)
class SummaryItem:
    label: str
    value: int


@dataclass(frozen=True, slots=True)
class ConnectorUsage:
    """Evidence produced for one run by one admitted connector version."""

    connector: str
    version: str
    publisher: str | None
    source_type: str
    item_count: int
    untrusted_count: int
    stale_count: int


@dataclass(frozen=True, slots=True)
class SnapshotUsage:
    """Recorded retrieval outcomes for one admitted source key."""

    source_key: str
    version: str
    publisher: str | None
    status_counts: Mapping[str, int]


@dataclass(frozen=True, slots=True)
class AttemptUsage:
    """Recorded provider attempts for one extraction provider and model."""

    provider: str
    model: str | None
    status_counts: Mapping[str, int]
    max_attempt_number: int
    escalation_count: int
    duration_ms: int


@dataclass(frozen=True, slots=True)
class ServiceCall:
    """One recorded call from a bounded stage out to a tool, source, or model provider."""

    kind: str
    name: str
    detail: str
    status_key: str
    status_label: str
    invocations: int
    outcomes: tuple[SummaryItem, ...]
    duration_ms: int | None
    note: str | None


@dataclass(frozen=True, slots=True)
class StageView:
    key: str
    label: str
    purpose: str
    boundary: str
    role: str
    persisted_status: str | None
    display_status: str
    status_key: str
    is_current: bool
    is_human: bool
    started_at: datetime | None
    finished_at: datetime | None
    duration_ms: int | None
    attempts: int | None
    model: str | None
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: str | None
    input_hash: str | None
    output_hash: str | None
    safe_summary: tuple[SummaryItem, ...]
    error_summary: str | None
    prior_label: str | None
    next_label: str | None
    services: tuple[ServiceCall, ...]
    order: int


@dataclass(frozen=True, slots=True)
class ActivityEntry:
    occurred_at: datetime | None
    stage_key: str
    role: str
    display_status: str
    transition: str
    safe_output: str
    next_step: str
    status_key: str
    duration_ms: int | None
    duration_share: float
    offset_share: float
    services: tuple[ServiceCall, ...]


@dataclass(frozen=True, slots=True)
class HealthRow:
    key: str
    label: str
    count: int
    denominator: int


@dataclass(frozen=True, slots=True)
class HealthGroup:
    key: str
    label: str
    rows: tuple[HealthRow, ...]
    denominator: int


@dataclass(frozen=True, slots=True)
class ExceptionEntry:
    severity: str
    stage: str
    subject: str
    reason: str
    evidence_state: str
    next_action: str


@dataclass(frozen=True, slots=True)
class NextAction:
    state: str
    heading: str
    detail: str
    label: str | None
    href: str | None


@dataclass(frozen=True, slots=True)
class LifecycleSummary:
    """Counts of persisted lifecycle states used for the circuit legend."""

    complete: int
    working: int
    waiting: int
    attention: int
    total: int


@dataclass(frozen=True, slots=True)
class WorkItem:
    occurred_at: datetime
    kind: str
    title: str
    status: str
    context: str
    action_label: str
    href: str


STAGES: tuple[StageDefinition, ...] = (
    StageDefinition(
        WorkflowStage.PLAN.value,
        "Plan work",
        "Define bounded tasks and source requirements",
        "Plans work only; it does not collect evidence or approve output.",
    ),
    StageDefinition(
        WorkflowStage.RESOLVE.value,
        "Resolve identity",
        "Confirm exact company identity or create a decision hold",
        "Exact identifiers and named human decisions control ambiguous matches.",
    ),
    StageDefinition(
        WorkflowStage.COLLECT.value,
        "Gather evidence",
        "Retrieve admitted evidence with provenance and cutoff rules",
        "Collects admitted sources only; it does not decide claim support.",
    ),
    StageDefinition(
        WorkflowStage.EXTRACT.value,
        "Extract facts",
        "Return explicit structured facts or abstain",
        "Uses strict schemas and abstains instead of filling unavailable values.",
    ),
    StageDefinition(
        WorkflowStage.NORMALIZE.value,
        "Normalize values",
        "Apply typed units, currencies, and missing-state rules",
        "Preserves units, currencies, and explicit missing states.",
    ),
    StageDefinition(
        WorkflowStage.VERIFY.value,
        "Verify claims",
        "Independently classify every candidate claim",
        "Verification remains separate from extraction and composition.",
    ),
    StageDefinition(
        WorkflowStage.COMPOSE.value,
        "Compose report",
        "Build versioned tables, exceptions, and context",
        "Composes evidence states without changing their verification outcome.",
    ),
    StageDefinition(
        WorkflowStage.HUMAN_REVIEW.value,
        "Human review",
        "Stop for a named decision; never simulate approval",
        "A named human owns approval of the current report version.",
    ),
)

_STATUS_MAPPING: dict[str, tuple[str, str]] = {
    RunStatus.PENDING.value: ("Queued", "queued"),
    RunStatus.RUNNING.value: ("Working", "working"),
    RunStatus.SUCCEEDED.value: ("Complete", "complete"),
    RunStatus.FAILED.value: ("Failed", "failed"),
    RunStatus.SKIPPED.value: ("Skipped", "skipped"),
}

_HEALTH_LABELS: dict[str, dict[str, str]] = {
    "verification": {
        "supported": "Supported",
        "contradicted": "Contradicted",
        "insufficient_evidence": "Insufficient evidence",
        "stale": "Stale",
        "rejected_untrusted": "Rejected untrusted",
    },
    "quality": {
        "pass": "Pass",
        "warn": "Warn",
        "hold": "Hold",
        "exclude": "Exclude",
    },
    "collection": {
        "succeeded": "Succeeded",
        "no_record": "No record",
        "source_unavailable": "Source unavailable",
        "failed": "Failed",
    },
}


def humanize(value: str) -> str:
    return value.replace("_", " ").strip().capitalize()


def short_identifier(value: str | None, *, width: int = 12) -> str:
    if not value:
        return "Not recorded"
    return value if len(value) <= width else f"{value[:width]}…"


def safe_metadata_summary(metadata: Mapping[str, Any]) -> tuple[SummaryItem, ...]:
    """Return count-only stage metadata, never raw source values or provider text."""

    items: list[SummaryItem] = []
    for key in sorted(metadata):
        value = metadata[key]
        if key.endswith("_count") and isinstance(value, int) and not isinstance(value, bool):
            items.append(SummaryItem(humanize(key.removesuffix("_count")), max(value, 0)))
            continue
        if not isinstance(value, Mapping) or not key.endswith(("_counts", "_issues", "_models")):
            continue
        for child_key in sorted(value):
            child_value = value[child_key]
            if isinstance(child_value, int) and not isinstance(child_value, bool):
                items.append(
                    SummaryItem(
                        f"{humanize(key)} · {humanize(str(child_key))}", max(child_value, 0)
                    )
                )
    return tuple(items)


def _safe_error(error: str | None) -> str | None:
    if not error:
        return None
    category = error.split(":", 1)[0].strip()
    return f"{category or 'Stage error'} recorded; raw detail is withheld from the trace."


_SERVICE_OUTCOME_LABELS: dict[str, str] = {
    "succeeded": "Succeeded",
    "no_record": "No record",
    "source_unavailable": "Source unavailable",
    "failed": "Failed",
    "abstained": "Abstained",
    "rejected": "Rejected",
}


_RESOLVED_OUTCOMES = frozenset({"succeeded"})
_UNRESOLVED_OUTCOMES = frozenset({"source_unavailable", "rejected", "no_record", "abstained"})
_FAILED_OUTCOMES = frozenset({"failed"})


def _service_status(counts: Mapping[str, int]) -> tuple[str, str]:
    """Grade one service by its worst recorded outcome, never by an optimistic default."""

    total = sum(counts.values())
    if total == 0:
        return "idle", "No call recorded"
    known = _RESOLVED_OUTCOMES | _UNRESOLVED_OUTCOMES | _FAILED_OUTCOMES
    if any(key not in known for key in counts):
        return "unavailable", "Status unavailable"
    if any(counts.get(key, 0) for key in _FAILED_OUTCOMES):
        return "failed", "Recorded failure"
    unresolved = sum(counts.get(key, 0) for key in _UNRESOLVED_OUTCOMES)
    if unresolved == total:
        return "empty", "Returned no usable record"
    if unresolved:
        return "partial", "Partially resolved"
    return "complete", "Resolved"


def build_service_calls(
    *,
    evidence_connectors: Sequence[ConnectorUsage] = (),
    source_snapshots: Sequence[SnapshotUsage] = (),
    extraction_attempts: Sequence[AttemptUsage] = (),
) -> dict[str, tuple[ServiceCall, ...]]:
    """Describe the recorded outward calls each bounded stage made, using safe counts only."""

    collect: list[ServiceCall] = []
    for connector_usage in sorted(
        evidence_connectors, key=lambda item: (item.connector, item.version)
    ):
        notes: list[str] = []
        if connector_usage.untrusted_count:
            notes.append(f"{connector_usage.untrusted_count} marked untrusted")
        if connector_usage.stale_count:
            notes.append(f"{connector_usage.stale_count} marked stale")
        collect.append(
            ServiceCall(
                kind="connector",
                name=connector_usage.connector,
                detail=(
                    f"v{connector_usage.version} · "
                    f"{connector_usage.publisher or 'Publisher not recorded'}"
                ),
                status_key="partial"
                if connector_usage.untrusted_count or connector_usage.stale_count
                else "complete",
                status_label="Evidence admitted",
                invocations=connector_usage.item_count,
                outcomes=(
                    SummaryItem(humanize(connector_usage.source_type), connector_usage.item_count),
                ),
                duration_ms=None,
                note=" · ".join(notes) or None,
            )
        )
    for snapshot_usage in sorted(source_snapshots, key=lambda item: item.source_key):
        status_key, status_label = _service_status(snapshot_usage.status_counts)
        collect.append(
            ServiceCall(
                kind="source",
                name=snapshot_usage.source_key,
                detail=(
                    f"v{snapshot_usage.version} · "
                    f"{snapshot_usage.publisher or 'Publisher not recorded'}"
                ),
                status_key=status_key,
                status_label=status_label,
                invocations=sum(snapshot_usage.status_counts.values()),
                outcomes=tuple(
                    SummaryItem(_SERVICE_OUTCOME_LABELS.get(key, humanize(key)), value)
                    for key, value in sorted(snapshot_usage.status_counts.items())
                ),
                duration_ms=None,
                note=(
                    None
                    if snapshot_usage.status_counts
                    else "Admitted in the source register; this run recorded no snapshot."
                ),
            )
        )

    extract: list[ServiceCall] = []
    for attempt_usage in sorted(
        extraction_attempts, key=lambda item: (item.provider, item.model or "")
    ):
        status_key, status_label = _service_status(attempt_usage.status_counts)
        notes = []
        if attempt_usage.max_attempt_number > 1:
            notes.append(f"{attempt_usage.max_attempt_number} attempts on one item")
        if attempt_usage.escalation_count:
            notes.append(f"{attempt_usage.escalation_count} escalated")
        extract.append(
            ServiceCall(
                kind="model",
                name=attempt_usage.model or attempt_usage.provider,
                detail=(
                    "Model identifier not recorded"
                    if attempt_usage.model is None
                    else attempt_usage.provider
                ),
                status_key=status_key,
                status_label=status_label,
                invocations=sum(attempt_usage.status_counts.values()),
                outcomes=tuple(
                    SummaryItem(_SERVICE_OUTCOME_LABELS.get(key, humanize(key)), value)
                    for key, value in sorted(attempt_usage.status_counts.items())
                ),
                duration_ms=attempt_usage.duration_ms or None,
                note=" · ".join(notes) or None,
            )
        )

    calls = {
        WorkflowStage.COLLECT.value: tuple(collect),
        WorkflowStage.EXTRACT.value: tuple(extract),
    }
    return {key: value for key, value in calls.items() if value}


def summarize_lifecycle(stages: Sequence[StageView]) -> LifecycleSummary:
    """Count persisted lifecycle states so the circuit legend never invents progress."""

    attention_states = {"failed", "held", "needs-review", "rejected", "unavailable"}
    working_states = {"working", "queued"}
    complete_states = {"complete", "approved", "exported"}
    return LifecycleSummary(
        complete=sum(stage.status_key in complete_states for stage in stages),
        working=sum(stage.status_key in working_states for stage in stages),
        waiting=sum(stage.status_key in {"waiting", "skipped"} for stage in stages),
        attention=sum(stage.status_key in attention_states for stage in stages),
        total=len(stages),
    )


def build_stage_views(
    run: WorkflowRunModel,
    agent_runs: Sequence[AgentRunModel],
    *,
    report: ReportModel | None = None,
    services: Mapping[str, tuple[ServiceCall, ...]] | None = None,
) -> tuple[StageView, ...]:
    by_stage = {agent.stage: agent for agent in agent_runs}
    views: list[StageView] = []
    for index, definition in enumerate(STAGES):
        agent = by_stage.get(definition.key)
        if agent is None:
            display_status, status_key = "Waiting", "waiting"
        else:
            display_status, status_key = _STATUS_MAPPING.get(
                agent.status, ("Status unavailable", "unavailable")
            )
        if definition.key == WorkflowStage.HUMAN_REVIEW.value and report is not None:
            report_mapping = {
                ReportStatus.PENDING_REVIEW.value: ("Needs human review", "needs-review"),
                ReportStatus.APPROVED.value: ("Approved", "approved"),
                ReportStatus.EXPORTED.value: ("Exported", "exported"),
                ReportStatus.REJECTED.value: ("Rejected", "rejected"),
            }
            display_status, status_key = report_mapping.get(
                report.status, (display_status, status_key)
            )
        views.append(
            StageView(
                key=definition.key,
                label=definition.label,
                purpose=definition.purpose,
                boundary=definition.boundary,
                role=agent.role if agent is not None else "Not started",
                persisted_status=agent.status if agent is not None else None,
                display_status=display_status,
                status_key=status_key,
                is_current=(run.status == RunStatus.RUNNING.value and run.stage == definition.key),
                is_human=definition.key == WorkflowStage.HUMAN_REVIEW.value,
                started_at=agent.started_at if agent is not None else None,
                finished_at=agent.finished_at if agent is not None else None,
                duration_ms=agent.duration_ms if agent is not None else None,
                attempts=agent.attempts if agent is not None else None,
                model=agent.model if agent is not None else None,
                input_tokens=agent.input_tokens if agent is not None else None,
                output_tokens=agent.output_tokens if agent is not None else None,
                cost_usd=(
                    str(agent.cost_usd)
                    if agent is not None and agent.cost_usd is not None
                    else None
                ),
                input_hash=agent.input_hash if agent is not None else None,
                output_hash=agent.output_hash if agent is not None else None,
                safe_summary=(
                    safe_metadata_summary(agent.metadata_json) if agent is not None else ()
                ),
                error_summary=_safe_error(agent.error if agent is not None else None),
                prior_label=STAGES[index - 1].label if index > 0 else None,
                next_label=STAGES[index + 1].label if index + 1 < len(STAGES) else None,
                services=(services or {}).get(definition.key, ()),
                order=index + 1,
            )
        )
    return tuple(views)


def build_activity_log(
    stages: Sequence[StageView],
    *,
    run_started_at: datetime | None = None,
) -> tuple[ActivityEntry, ...]:
    """Return the chronological trace: complete as text, proportional as a waterfall."""

    recorded = [stage for stage in stages if stage.status_key != "waiting"]
    longest = max((stage.duration_ms or 0) for stage in recorded) if recorded else 0
    origin = run_started_at or next(
        (stage.started_at for stage in recorded if stage.started_at is not None), None
    )
    span_ms = 0.0
    if origin is not None:
        ends = [
            (stage.finished_at - origin).total_seconds() * 1000
            for stage in recorded
            if stage.finished_at is not None
        ]
        span_ms = max(ends) if ends else 0.0

    entries: list[ActivityEntry] = []
    for index, stage in enumerate(recorded):
        output = ", ".join(f"{item.label}: {item.value}" for item in stage.safe_summary[:3]) or (
            f"Output hash {short_identifier(stage.output_hash)}"
            if stage.output_hash
            else "No safe output summary recorded"
        )
        next_stage = recorded[index + 1] if index + 1 < len(recorded) else None
        if stage.status_key == "complete" and next_stage is not None:
            next_step = f"The orchestrator handed the recorded output to {next_stage.label}."
        elif stage.status_key == "needs-review":
            next_step = "The workflow stopped for a named decision; no approval was simulated."
        elif stage.status_key == "failed":
            next_step = "The workflow stopped; no downstream handoff was recorded."
        elif stage.status_key == "working":
            next_step = "This persisted stage has not recorded a downstream handoff."
        else:
            next_step = "No later persisted stage is recorded."
        offset_share = 0.0
        if origin is not None and span_ms > 0 and stage.started_at is not None:
            offset = (stage.started_at - origin).total_seconds() * 1000
            offset_share = min(max(offset / span_ms, 0.0), 1.0)
        entries.append(
            ActivityEntry(
                occurred_at=stage.finished_at or stage.started_at,
                stage_key=stage.key,
                role=stage.label,
                display_status=stage.display_status,
                transition=f"Stage state persisted as {stage.display_status}.",
                safe_output=output,
                next_step=next_step,
                status_key=stage.status_key,
                duration_ms=stage.duration_ms,
                duration_share=(
                    min(max((stage.duration_ms or 0) / longest, 0.0), 1.0) if longest else 0.0
                ),
                offset_share=offset_share,
                services=stage.services,
            )
        )
    return tuple(entries)


def build_health_groups(
    *,
    verification: Mapping[str, int],
    quality: Mapping[str, int],
    collection: Mapping[str, int],
    evidence_sources: Mapping[str, int],
    evidence_classifications: Mapping[str, int],
) -> tuple[HealthGroup, ...]:
    groups: list[HealthGroup] = []
    for key, counts in (
        ("verification", verification),
        ("quality", quality),
        ("collection", collection),
    ):
        labels = _HEALTH_LABELS[key]
        denominator = sum(counts.values())
        if counts:
            known_rows = [
                HealthRow(item_key, label, counts.get(item_key, 0), denominator)
                for item_key, label in labels.items()
            ]
            unknown_rows = [
                HealthRow(
                    item_key,
                    f"Status unavailable · {humanize(item_key)}",
                    value,
                    denominator,
                )
                for item_key, value in sorted(counts.items())
                if item_key not in labels
            ]
            rows = tuple(known_rows + unknown_rows)
        else:
            rows = ()
        groups.append(HealthGroup(key, humanize(key), rows, denominator))
    for key, counts in (
        ("evidence_sources", evidence_sources),
        ("evidence_classifications", evidence_classifications),
    ):
        denominator = sum(counts.values())
        rows = tuple(
            HealthRow(item_key, humanize(item_key), value, denominator)
            for item_key, value in sorted(counts.items())
        )
        groups.append(HealthGroup(key, humanize(key), rows, denominator))
    return tuple(groups)


def derive_run_next_action(
    run: WorkflowRunModel,
    report: ReportModel | None,
    *,
    identity_hold_count: int,
    exception_count: int,
) -> NextAction:
    if identity_hold_count:
        return NextAction(
            "blocked",
            f"Resolve {identity_hold_count} company identities",
            "Collection cannot continue until a named reviewer records each decision "
            "and rationale.",
            "Resolve identities",
            "/#identity-holds",
        )
    if run.status == RunStatus.FAILED.value:
        return NextAction(
            "blocked",
            f"This run failed during {humanize(run.stage)}",
            "Inspect the recorded stage error and recovery guidance; no downstream "
            "advance is shown.",
            "Open recorded exception",
            "#exceptions",
        )
    if report is not None and report.status == ReportStatus.PENDING_REVIEW.value:
        if exception_count:
            return NextAction(
                "action",
                f"Inspect {exception_count} evidence exceptions",
                "Review contradictions, stale evidence, insufficiency, and holds before "
                "deciding this version.",
                "Inspect exceptions",
                "#exceptions",
            )
        return NextAction(
            "action",
            "The current report version needs named human review",
            "The workflow has stopped at its normal human checkpoint.",
            "Open report review",
            f"/reports/{report.id}",
        )
    if report is not None and report.status == ReportStatus.APPROVED.value:
        return NextAction(
            "action",
            "The current report version is approved and ready to export",
            "Export remains an explicit named-reviewer action.",
            "Open export decision",
            f"/reports/{report.id}",
        )
    if report is not None and report.status == ReportStatus.EXPORTED.value:
        return NextAction(
            "complete",
            "No action required",
            "This trace is complete and its approved report was explicitly exported.",
            "View verified downloads",
            f"/reports/{report.id}",
        )
    return NextAction(
        "informational",
        "No safe action is currently available",
        "The page reflects the last persisted workflow state.",
        None,
        None,
    )


def derive_report_next_action(report: ReportModel, *, exception_count: int) -> NextAction:
    if report.status == ReportStatus.PENDING_REVIEW.value:
        if exception_count:
            return NextAction(
                "action",
                "Named human review required",
                f"Inspect {exception_count} unresolved evidence exceptions before recording "
                "a decision.",
                "Inspect evidence exceptions",
                f"/runs/{report.run_id}#exceptions",
            )
        return NextAction(
            "action",
            "Named human review required",
            "Review the current version and its provenance before recording a decision.",
            "Open decision dock",
            "#decision-dock",
        )
    if report.status == ReportStatus.APPROVED.value:
        return NextAction(
            "action",
            "Current version approved",
            "Approval applies only to this content version; export is still explicit.",
            "Open export action",
            "#decision-dock",
        )
    if report.status == ReportStatus.EXPORTED.value:
        return NextAction(
            "complete",
            "Approved export is complete",
            "Verified immutable artifacts are available in the decision dock.",
            "View downloads",
            "#decision-dock",
        )
    if report.status == ReportStatus.REJECTED.value:
        return NextAction(
            "blocked",
            "This report candidate is closed",
            "The recorded rejection ended this candidate; no export action is available.",
            None,
            None,
        )
    return NextAction(
        "informational",
        humanize(report.status),
        "The page reflects the last persisted report state.",
        None,
        None,
    )


def derive_work_item_action(run: WorkflowRunModel, report: ReportModel | None) -> tuple[str, str]:
    if run.status == RunStatus.FAILED.value:
        return "Inspect failed trace", f"/runs/{run.id}"
    if run.status in {RunStatus.PENDING.value, RunStatus.RUNNING.value}:
        return "View current persisted state", f"/runs/{run.id}"
    if report is not None and report.status == ReportStatus.PENDING_REVIEW.value:
        return "Continue to report review", f"/reports/{report.id}"
    if report is not None:
        return "Open report record", f"/reports/{report.id}"
    if run.status == RunStatus.SUCCEEDED.value:
        return "View completed trace", f"/runs/{run.id}"
    return "View recorded trace", f"/runs/{run.id}"
