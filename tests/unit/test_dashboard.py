from __future__ import annotations

from datetime import UTC, datetime, timedelta

from portfolio_agent.dashboard import (
    AttemptUsage,
    ConnectorUsage,
    SnapshotUsage,
    SummaryItem,
    build_activity_log,
    build_health_groups,
    build_service_calls,
    build_stage_views,
    derive_report_next_action,
    derive_run_next_action,
    derive_work_item_action,
    safe_metadata_summary,
    summarize_lifecycle,
)
from portfolio_agent.enums import ReportStatus, RunStatus, WorkflowStage
from portfolio_agent.models import AgentRunModel, ReportModel, WorkflowRunModel


def _run(*, status: str = RunStatus.RUNNING.value, stage: str = "extract") -> WorkflowRunModel:
    return WorkflowRunModel(
        id="run_test",
        dataset_id="ds_test",
        reporting_period_id="period_test",
        status=status,
        stage=stage,
        configuration_json={},
    )


def _agent(stage: str, status: str, **overrides: object) -> AgentRunModel:
    values: dict[str, object] = {
        "id": f"ar_{stage}",
        "run_id": "run_test",
        "stage": stage,
        "role": f"{stage}_role",
        "status": status,
        "input_hash": "a" * 64,
        "output_hash": "b" * 64 if status == RunStatus.SUCCEEDED.value else None,
        "metadata_json": {},
        "started_at": datetime(2025, 7, 1, tzinfo=UTC),
    }
    values.update(overrides)
    return AgentRunModel(**values)


def _report(status: str) -> ReportModel:
    return ReportModel(
        id="rep_test",
        run_id="run_test",
        dataset_id="ds_test",
        reporting_period_id="period_test",
        title="Synthetic review",
        status=status,
    )


def test_stage_views_map_every_persisted_status_and_future_waiting_state() -> None:
    stages = build_stage_views(
        _run(stage=WorkflowStage.EXTRACT.value),
        (
            _agent("plan", RunStatus.PENDING.value),
            _agent("resolve", RunStatus.RUNNING.value),
            _agent("collect", RunStatus.SUCCEEDED.value),
            _agent("extract", RunStatus.FAILED.value, error="ValueError: private raw value"),
            _agent("normalize", RunStatus.SKIPPED.value),
        ),
    )

    assert [(stage.key, stage.display_status) for stage in stages] == [
        ("plan", "Queued"),
        ("resolve", "Working"),
        ("collect", "Complete"),
        ("extract", "Failed"),
        ("normalize", "Skipped"),
        ("verify", "Waiting"),
        ("compose", "Waiting"),
        ("human_review", "Waiting"),
    ]
    assert stages[3].is_current
    assert stages[3].error_summary == "ValueError recorded; raw detail is withheld from the trace."
    assert "private raw value" not in stages[3].error_summary
    assert stages[-1].is_human


def test_human_checkpoint_uses_report_state_without_hiding_stage_completion() -> None:
    stages = build_stage_views(
        _run(status=RunStatus.SUCCEEDED.value, stage=WorkflowStage.HUMAN_REVIEW.value),
        (_agent("human_review", RunStatus.SUCCEEDED.value),),
        report=_report(ReportStatus.PENDING_REVIEW.value),
    )

    human = stages[-1]
    assert human.persisted_status == RunStatus.SUCCEEDED.value
    assert human.display_status == "Needs human review"
    assert human.status_key == "needs-review"
    assert "no approval was simulated" in build_activity_log(stages)[0].next_step


def test_stage_summary_allowlists_counts_and_omits_raw_metadata() -> None:
    summary = safe_metadata_summary(
        {
            "observation_count": 9,
            "verification_counts": {"supported": 4, "contradicted": 2},
            "provider_models": {"deterministic": 3},
            "raw_value": "restricted source text",
            "prompt": "ignore prior instructions",
            "token": "secret",
            "report_id": "rep_private",
            "automatic_export": False,
        }
    )

    rendered = " ".join(f"{item.label} {item.value}" for item in summary)
    assert "Observation 9" in rendered
    assert "Supported 4" in rendered
    assert "Deterministic 3" in rendered
    assert "restricted source text" not in rendered
    assert "ignore prior instructions" not in rendered
    assert "secret" not in rendered
    assert "rep_private" not in rendered


def test_activity_log_only_claims_handoffs_to_persisted_downstream_stages() -> None:
    stages = build_stage_views(
        _run(status=RunStatus.FAILED.value, stage=WorkflowStage.FAILED.value),
        (
            _agent("plan", RunStatus.SUCCEEDED.value, metadata_json={"task_count": 2}),
            _agent("resolve", RunStatus.FAILED.value, error="ValueError: hidden name"),
        ),
    )
    activity = build_activity_log(stages)

    assert "orchestrator handed" in activity[0].next_step
    assert "workflow stopped" in activity[1].next_step
    assert all("hidden name" not in entry.safe_output for entry in activity)


def test_health_groups_use_exact_counts_and_denominators() -> None:
    groups = build_health_groups(
        verification={"supported": 7, "contradicted": 2},
        quality={"hold": 1},
        collection={"succeeded": 3, "no_record": 1},
        evidence_sources={"portfolio_submission": 4},
        evidence_classifications={"synthetic": 4},
    )

    assert groups[0].denominator == 9
    assert [(row.key, row.count, row.denominator) for row in groups[0].rows[:2]] == [
        ("supported", 7, 9),
        ("contradicted", 2, 9),
    ]
    assert groups[1].denominator == 1
    assert groups[2].denominator == 4


def test_health_groups_hide_empty_scaffolding_and_surface_unknown_statuses() -> None:
    groups = build_health_groups(
        verification={"supported": 2, "future_state": 3},
        quality={},
        collection={},
        evidence_sources={},
        evidence_classifications={},
    )

    verification = groups[0]
    assert verification.denominator == 5
    assert sum(row.count for row in verification.rows) == 5
    assert verification.rows[-1].label == "Status unavailable · Future state"
    assert groups[1].rows == ()
    assert groups[2].rows == ()


def test_next_action_prioritises_earliest_blocker_then_named_review_and_export() -> None:
    running = _run()
    pending = _report(ReportStatus.PENDING_REVIEW.value)
    approved = _report(ReportStatus.APPROVED.value)
    exported = _report(ReportStatus.EXPORTED.value)

    identity = derive_run_next_action(running, pending, identity_hold_count=2, exception_count=4)
    exceptions = derive_run_next_action(
        _run(status=RunStatus.SUCCEEDED.value, stage="human_review"),
        pending,
        identity_hold_count=0,
        exception_count=4,
    )
    approval = derive_run_next_action(
        _run(status=RunStatus.SUCCEEDED.value, stage="approve_export"),
        approved,
        identity_hold_count=0,
        exception_count=0,
    )
    complete = derive_run_next_action(
        _run(status=RunStatus.SUCCEEDED.value, stage="complete"),
        exported,
        identity_hold_count=0,
        exception_count=0,
    )

    assert identity.heading == "Resolve 2 company identities"
    assert exceptions.heading == "Inspect 4 evidence exceptions"
    assert approval.label == "Open export decision"
    assert complete.state == "complete"
    pending_exceptions = derive_report_next_action(pending, exception_count=4)
    assert pending_exceptions.label == "Inspect evidence exceptions"
    assert pending_exceptions.href == "/runs/run_test#exceptions"
    assert derive_report_next_action(pending, exception_count=0).href == "#decision-dock"
    assert derive_report_next_action(exported, exception_count=0).state == "complete"


def test_work_item_actions_describe_the_actual_persisted_state() -> None:
    assert derive_work_item_action(_run(status=RunStatus.FAILED.value), None) == (
        "Inspect failed trace",
        "/runs/run_test",
    )
    for status in (RunStatus.PENDING.value, RunStatus.RUNNING.value):
        assert derive_work_item_action(_run(status=status), None)[0] == (
            "View current persisted state"
        )
    assert derive_work_item_action(
        _run(status=RunStatus.SUCCEEDED.value),
        _report(ReportStatus.PENDING_REVIEW.value),
    ) == ("Continue to report review", "/reports/rep_test")
    for status in (ReportStatus.APPROVED.value, ReportStatus.EXPORTED.value):
        assert derive_work_item_action(_run(status=RunStatus.SUCCEEDED.value), _report(status)) == (
            "Open report record",
            "/reports/rep_test",
        )
    assert derive_work_item_action(_run(status=RunStatus.SUCCEEDED.value), None)[0] == (
        "View completed trace"
    )


def test_service_calls_grade_by_worst_recorded_outcome_and_stay_count_only() -> None:
    calls = build_service_calls(
        evidence_connectors=(
            ConnectorUsage(
                connector="fixture_connector",
                version="1.0.0",
                publisher="Synthetic Register",
                source_type="synthetic_public_fixture",
                item_count=10,
                untrusted_count=1,
                stale_count=1,
            ),
        ),
        source_snapshots=(
            SnapshotUsage(
                source_key="companies_house",
                version="1.4.0",
                publisher="Companies House",
                status_counts={"succeeded": 2, "source_unavailable": 1},
            ),
            SnapshotUsage(
                source_key="ukri_gtr",
                version="1.3.0",
                publisher="UKRI",
                status_counts={},
            ),
            SnapshotUsage(
                source_key="broken_source",
                version="0.1.0",
                publisher=None,
                status_counts={"succeeded": 1, "failed": 1},
            ),
        ),
        extraction_attempts=(
            AttemptUsage(
                provider="openai_structured",
                model="gpt-test",
                status_counts={"succeeded": 3, "abstained": 1},
                max_attempt_number=2,
                escalation_count=1,
                duration_ms=412,
            ),
        ),
    )

    collect = {call.name: call for call in calls["collect"]}
    extract = {call.name: call for call in calls["extract"]}

    assert collect["fixture_connector"].status_key == "partial"
    assert collect["fixture_connector"].note == "1 marked untrusted · 1 marked stale"
    assert collect["companies_house"].status_key == "partial"
    assert collect["companies_house"].invocations == 3
    assert collect["ukri_gtr"].status_key == "idle"
    assert collect["ukri_gtr"].invocations == 0
    assert "this run recorded no snapshot" in (collect["ukri_gtr"].note or "")
    assert collect["broken_source"].status_key == "failed"
    assert collect["broken_source"].detail == "v0.1.0 · Publisher not recorded"

    assert extract["gpt-test"].status_key == "partial"
    assert extract["gpt-test"].note == "2 attempts on one item · 1 escalated"
    assert extract["gpt-test"].duration_ms == 412
    assert all(isinstance(item.value, int) for item in extract["gpt-test"].outcomes)


def test_service_calls_refuse_to_grade_an_unknown_outcome_as_resolved() -> None:
    calls = build_service_calls(
        source_snapshots=(
            SnapshotUsage(
                source_key="future_source",
                version="2.0.0",
                publisher="Registry",
                status_counts={"quarantined": 4},
            ),
        )
    )

    call = calls["collect"][0]
    assert call.status_key == "unavailable"
    assert call.status_label == "Status unavailable"
    assert call.outcomes == (SummaryItem("Quarantined", 4),)


def test_service_calls_omit_stages_with_no_recorded_outward_call() -> None:
    assert build_service_calls() == {}
    assert set(
        build_service_calls(
            extraction_attempts=(
                AttemptUsage(
                    provider="deterministic",
                    model=None,
                    status_counts={"succeeded": 1},
                    max_attempt_number=1,
                    escalation_count=0,
                    duration_ms=0,
                ),
            )
        )
    ) == {"extract"}


def test_activity_log_shares_come_from_persisted_timings() -> None:
    origin = datetime(2025, 7, 1, 12, 0, 0, tzinfo=UTC)
    stages = build_stage_views(
        _run(status=RunStatus.SUCCEEDED.value, stage=WorkflowStage.COMPOSE.value),
        (
            _agent(
                "plan",
                RunStatus.SUCCEEDED.value,
                started_at=origin,
                finished_at=origin + timedelta(milliseconds=10),
                duration_ms=10,
            ),
            _agent(
                "collect",
                RunStatus.SUCCEEDED.value,
                started_at=origin + timedelta(milliseconds=50),
                finished_at=origin + timedelta(milliseconds=90),
                duration_ms=40,
            ),
        ),
        services={"collect": ()},
    )

    entries = build_activity_log(stages, run_started_at=origin)

    assert [entry.duration_share for entry in entries] == [0.25, 1.0]
    assert entries[0].offset_share == 0.0
    assert round(entries[1].offset_share, 4) == round(50 / 90, 4)
    assert entries[1].display_status == "Complete"
    assert entries[0].stage_key == "plan"


def test_lifecycle_summary_never_counts_an_unstarted_stage_as_progress() -> None:
    stages = build_stage_views(
        _run(stage=WorkflowStage.EXTRACT.value),
        (
            _agent("plan", RunStatus.SUCCEEDED.value),
            _agent("resolve", RunStatus.SUCCEEDED.value),
            _agent("collect", RunStatus.RUNNING.value),
            _agent("extract", RunStatus.FAILED.value),
        ),
    )

    summary = summarize_lifecycle(stages)

    assert (summary.complete, summary.working, summary.attention, summary.total) == (2, 1, 1, 8)
    assert summary.waiting == 4
    assert summary.complete + summary.working + summary.attention + summary.waiting == summary.total
