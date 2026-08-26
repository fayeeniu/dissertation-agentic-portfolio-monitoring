from __future__ import annotations

import json
from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification, IdentifierScheme, VerificationStatus
from portfolio_agent.events import events_for_run
from portfolio_agent.models import (
    ClaimModel,
    CompanyIdentifierModel,
    EvidenceItemModel,
    ExtractionModel,
    MetricDefinitionModel,
    ObservationModel,
    RawSubmissionModel,
    ReportSectionModel,
    SourceSnapshotModel,
    WorkflowRunModel,
    run_evidence,
    run_source_snapshots,
)
from portfolio_agent.temporal import TemporalEvidence, TemporalWindow, temporal_eligibility
from portfolio_agent.web import create_app


def _payload(*, period: str, start: date, end: date, classification: str = "synthetic") -> bytes:
    return json.dumps(
        {
            "schema_version": "1.0",
            "classification": classification,
            "reporting_period": {
                "label": period,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
            "companies": [
                {
                    "name": "Source Synthetic Ltd",
                    "external_id": "SOURCE-WORKFLOW-001",
                    "programme_start_date": "2024-10-01",
                    "metrics": {
                        "grant_funding": None,
                        "jobs_created": 2,
                    },
                }
            ],
        }
    ).encode()


def _attach_reviewed_public_identifiers(
    runtime: Runtime,
    dataset_id: str,
    *,
    ukri_organisation_id: str = "SYN-UKRI-ORG-COMPLETE",
) -> str:
    with runtime.session_factory.begin() as session:
        company_id = session.scalar(
            select(ObservationModel.company_id)
            .join(ObservationModel.raw_submission)
            .where(ObservationModel.raw_submission.has(dataset_id=dataset_id))
        )
        assert company_id is not None
        session.add_all(
            (
                CompanyIdentifierModel(
                    company_id=company_id,
                    scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER.value,
                    value="00000001",
                    normalized_value="00000001",
                    source_key="companies_house",
                    reviewed=True,
                ),
                CompanyIdentifierModel(
                    company_id=company_id,
                    scheme=IdentifierScheme.UKRI_ORGANISATION_ID.value,
                    value=ukri_organisation_id,
                    normalized_value=ukri_organisation_id,
                    source_key="ukri_gtr",
                    reviewed=True,
                ),
            )
        )
        return company_id


def test_source_v2_snapshots_feed_run_relative_evidence_events_and_report(
    runtime: Runtime,
) -> None:
    imported = runtime.importer.import_bytes(
        _payload(
            period="SOURCE-WORKFLOW-2025-Q2",
            start=date(2025, 4, 1),
            end=date(2025, 6, 30),
        ),
        filename="source-workflow-q2.json",
        classification=DataClassification.SYNTHETIC,
    )
    _attach_reviewed_public_identifiers(runtime, imported.dataset_id)
    pipeline = runtime.workflow.run(imported.dataset_id)

    with runtime.session_factory() as session:
        snapshots = list(
            session.scalars(
                select(SourceSnapshotModel)
                .join(
                    run_source_snapshots,
                    run_source_snapshots.c.source_snapshot_id == SourceSnapshotModel.id,
                )
                .where(run_source_snapshots.c.run_id == pipeline.run_id)
            ).all()
        )
        public_evidence = list(
            session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(
                    run_evidence.c.run_id == pipeline.run_id,
                    EvidenceItemModel.source_snapshot_id.is_not(None),
                )
            ).all()
        )
        temporal_rows = session.execute(
            select(
                run_evidence.c.reporting_cutoff,
                run_evidence.c.temporal_status,
                run_evidence.c.temporal_reason,
            ).where(run_evidence.c.run_id == pipeline.run_id)
        ).all()
        grant_claim = session.scalar(
            select(ClaimModel)
            .join(ClaimModel.metric_definition)
            .where(
                ClaimModel.run_id == pipeline.run_id,
                ClaimModel.metric_definition.has(key="grant_funding"),
            )
        )
        sections = {
            section.section_key: section.body_markdown
            for section in session.scalars(
                select(ReportSectionModel).where(
                    ReportSectionModel.report_id == pipeline.report_id,
                    ReportSectionModel.is_current.is_(True),
                )
            ).all()
        }
        events = events_for_run(session, run_id=pipeline.run_id)

    assert {(snapshot.source_key, snapshot.status) for snapshot in snapshots} == {
        ("companies_house", "succeeded"),
        ("ukri_gtr", "succeeded"),
    }
    assert {snapshot.programme_start_date for snapshot in snapshots} == {date(2024, 10, 1)}
    assert len(public_evidence) >= 10
    grant_evidence = [
        item
        for item in public_evidence
        if item.content_json["fact_key"] == "ukri_total_explicit_award_amount"
    ]
    assert len(grant_evidence) == 1
    assert grant_evidence[0].connector == "ukri_gtr"
    assert grant_evidence[0].content_json["period_label"] == ("from 2024-10-01 through 2025-06-30")
    assert all(item.content_json["structured_locator"] for item in public_evidence)
    assert all(item.content_json["extraction_method"] for item in public_evidence)
    assert temporal_rows
    assert all(cutoff == date(2025, 6, 30) for cutoff, _, _ in temporal_rows)
    assert all(status for _, status, _ in temporal_rows)
    assert any(status == "eligible" for _, status, _ in temporal_rows)
    assert all(reason for _, _, reason in temporal_rows)
    assert grant_claim is not None
    assert grant_claim.verification_status == VerificationStatus.SUPPORTED.value
    assert "cumulatively from 2024-10-01 through 2025-06-30" in grant_claim.text
    assert "for SOURCE-WORKFLOW-2025-Q2" not in grant_claim.text
    assert "companies_house" in sections["source-coverage"]
    assert "ukri_gtr" in sections["source-coverage"]
    assert "filing_not_due" in sections["quality-contract"]
    assert "Synthetic annual accounts filed" in sections["event-timeline"]
    assert "Synthetic public outcome" in sections["event-timeline"]
    assert {event.source_key for event in events} == {"companies_house", "ukri_gtr"}


def test_restricted_company_name_never_enters_public_extraction_payload(
    runtime: Runtime,
) -> None:
    restricted_name = "Restricted Portfolio Name Never For External Models Ltd"
    document = json.loads(
        _payload(
            period="RESTRICTED-SOURCE-WORKFLOW-2025-Q2",
            start=date(2025, 4, 1),
            end=date(2025, 6, 30),
            classification="restricted",
        )
    )
    document["companies"][0]["name"] = restricted_name
    imported = runtime.importer.import_bytes(
        json.dumps(document).encode(),
        filename="restricted-source-workflow-q2.json",
        classification=DataClassification.RESTRICTED,
    )
    _attach_reviewed_public_identifiers(runtime, imported.dataset_id)
    pipeline = runtime.workflow.run(imported.dataset_id)

    with runtime.session_factory() as session:
        public_evidence = list(
            session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(
                    run_evidence.c.run_id == pipeline.run_id,
                    EvidenceItemModel.source_snapshot_id.is_not(None),
                )
            ).all()
        )
        extractions = list(
            session.scalars(
                select(ExtractionModel).where(ExtractionModel.run_id == pipeline.run_id)
            ).all()
        )

    assert public_evidence
    assert extractions
    assert all(
        item.content_json["company_name"].startswith("public-evidence:") for item in public_evidence
    )
    assert all(
        restricted_name not in json.dumps(item.content_json, sort_keys=True)
        for item in public_evidence
    )
    assert all(
        extraction.company_id
        and extraction.evidence_span is not None
        and restricted_name not in extraction.evidence_span
        for extraction in extractions
    )


def test_cumulative_public_claim_abstains_without_programme_start(runtime: Runtime) -> None:
    document = json.loads(
        _payload(
            period="SOURCE-WORKFLOW-NO-PROGRAMME-START",
            start=date(2025, 4, 1),
            end=date(2025, 6, 30),
        )
    )
    document["companies"][0].pop("programme_start_date")
    imported = runtime.importer.import_bytes(
        json.dumps(document).encode(),
        filename="source-workflow-no-programme-start.json",
        classification=DataClassification.SYNTHETIC,
    )
    _attach_reviewed_public_identifiers(runtime, imported.dataset_id)
    pipeline = runtime.workflow.run(imported.dataset_id)

    with runtime.session_factory() as session:
        grant_claim = session.scalar(
            select(ClaimModel)
            .join(ClaimModel.metric_definition)
            .where(
                ClaimModel.run_id == pipeline.run_id,
                ClaimModel.metric_definition.has(key="grant_funding"),
            )
        )
        ukri_evidence = list(
            session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(
                    run_evidence.c.run_id == pipeline.run_id,
                    EvidenceItemModel.connector == "ukri_gtr",
                )
            ).all()
        )
        ukri_total = next(
            item
            for item in ukri_evidence
            if item.content_json["fact_key"] == "ukri_total_explicit_award_amount"
        )
    assert grant_claim is None
    assert ukri_total is not None
    assert ukri_total.metric_definition_id is None
    assert ukri_total.content_json["period_label"] is None


@pytest.mark.parametrize(
    ("ukri_organisation_id", "missing_state"),
    (
        ("SYN-UKRI-ORG-001", "not_reported"),
        ("SYN-UKRI-ORG-NONGBP", "not_applicable"),
    ),
)
def test_incomplete_ukri_monetary_coverage_cannot_support_zero_or_total_claim(
    runtime: Runtime,
    ukri_organisation_id: str,
    missing_state: str,
) -> None:
    imported = runtime.importer.import_bytes(
        _payload(
            period=f"SOURCE-WORKFLOW-INCOMPLETE-{missing_state}",
            start=date(2025, 4, 1),
            end=date(2025, 6, 30),
        ),
        filename=f"source-workflow-incomplete-{missing_state}.json",
        classification=DataClassification.SYNTHETIC,
    )
    _attach_reviewed_public_identifiers(
        runtime,
        imported.dataset_id,
        ukri_organisation_id=ukri_organisation_id,
    )
    pipeline = runtime.workflow.run(imported.dataset_id)

    with runtime.session_factory() as session:
        grant_claim = session.scalar(
            select(ClaimModel)
            .join(ClaimModel.metric_definition)
            .where(
                ClaimModel.run_id == pipeline.run_id,
                ClaimModel.metric_definition.has(key="grant_funding"),
            )
        )
        ukri_evidence = list(
            session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(
                    run_evidence.c.run_id == pipeline.run_id,
                    EvidenceItemModel.connector == "ukri_gtr",
                )
            ).all()
        )
        quality_section = session.scalar(
            select(ReportSectionModel).where(
                ReportSectionModel.report_id == pipeline.report_id,
                ReportSectionModel.section_key == "quality-contract",
            )
        )

    total = next(
        item
        for item in ukri_evidence
        if item.content_json["fact_key"] == "ukri_total_explicit_award_amount"
    )
    state = next(
        item
        for item in ukri_evidence
        if item.content_json["fact_key"] == "ukri_award_total_missing_state"
    )
    assert grant_claim is None
    assert total.metric_definition_id is None
    assert state.content_json["missing_state"] == missing_state
    assert quality_section is not None
    assert missing_state in quality_section.body_markdown


def test_later_source_run_does_not_leak_future_events_into_earlier_ui_or_export(
    runtime: Runtime,
) -> None:
    earlier_import = runtime.importer.import_bytes(
        _payload(
            period="SOURCE-WORKFLOW-LEAK-Q2",
            start=date(2025, 4, 1),
            end=date(2025, 6, 30),
        ),
        filename="source-workflow-leak-q2.json",
        classification=DataClassification.SYNTHETIC,
    )
    _attach_reviewed_public_identifiers(
        runtime,
        earlier_import.dataset_id,
        ukri_organisation_id="SYN-UKRI-ORG-001",
    )
    earlier = runtime.workflow.run(earlier_import.dataset_id)

    later_import = runtime.importer.import_bytes(
        _payload(
            period="SOURCE-WORKFLOW-LEAK-Q3",
            start=date(2025, 7, 1),
            end=date(2025, 9, 30),
        ),
        filename="source-workflow-leak-q3.json",
        classification=DataClassification.SYNTHETIC,
    )
    later = runtime.workflow.run(later_import.dataset_id)

    with runtime.session_factory() as session:
        earlier_titles = {event.title for event in events_for_run(session, run_id=earlier.run_id)}
        later_titles = {event.title for event in events_for_run(session, run_id=later.run_id)}
    assert "Synthetic filing after historical cutoff" not in earlier_titles
    assert "Synthetic outcome after cutoff" not in earlier_titles
    assert "Synthetic filing after historical cutoff" in later_titles
    assert "Synthetic outcome after cutoff" in later_titles

    page = TestClient(create_app(runtime)).get(f"/reports/{earlier.report_id}")
    assert page.status_code == 200
    assert "Synthetic filing after historical cutoff" not in page.text
    assert "Synthetic outcome after cutoff" not in page.text

    lock_version = runtime.reports.approve(
        earlier.report_id,
        actor="Synthetic Test Reviewer",
        reason="Verified historical cutoff isolation before controlled export.",
        expected_lock_version=1,
    )
    bundle = runtime.reports.export(
        earlier.report_id,
        expected_lock_version=lock_version,
    )
    exported_markdown = bundle.markdown_path.read_text(encoding="utf-8")
    exported_json = json.loads(bundle.json_path.read_text(encoding="utf-8"))
    assert "Synthetic filing after historical cutoff" not in exported_markdown
    assert "Synthetic outcome after cutoff" not in exported_markdown
    assert exported_json["visual_summary"]["event_types"]["accounts_filed"] == 1


def test_same_evidence_item_has_independent_temporal_decisions_per_run(
    runtime: Runtime,
) -> None:
    first_import = runtime.importer.import_bytes(
        _payload(
            period="TEMPORAL-ASSOCIATION-Q2",
            start=date(2025, 4, 1),
            end=date(2025, 6, 30),
        ),
        filename="temporal-association-q2.json",
        classification=DataClassification.SYNTHETIC,
    )
    second_import = runtime.importer.import_bytes(
        _payload(
            period="TEMPORAL-ASSOCIATION-Q3",
            start=date(2025, 7, 1),
            end=date(2025, 9, 30),
        ),
        filename="temporal-association-q3.json",
        classification=DataClassification.SYNTHETIC,
    )
    with runtime.session_factory.begin() as session:
        first_raw = session.scalar(
            select(RawSubmissionModel).where(
                RawSubmissionModel.dataset_id == first_import.dataset_id
            )
        )
        second_raw = session.scalar(
            select(RawSubmissionModel).where(
                RawSubmissionModel.dataset_id == second_import.dataset_id
            )
        )
        company_id = session.scalar(
            select(ObservationModel.company_id).where(
                ObservationModel.raw_submission_id == first_import.raw_submission_id
            )
        )
        metric = session.scalar(
            select(MetricDefinitionModel).where(MetricDefinitionModel.key == "grant_funding")
        )
        assert first_raw is not None and second_raw is not None
        assert company_id is not None and metric is not None
        evidence = EvidenceItemModel(
            company_id=company_id,
            metric_definition_id=metric.id,
            source_type="synthetic_public_fixture",
            connector="temporal-test",
            locator="fixture://temporal/shared",
            publisher="Synthetic temporal publisher",
            retrieved_at=datetime(2025, 7, 2, tzinfo=UTC),
            published_at=datetime(2025, 7, 1, tzinfo=UTC),
            content_json={
                "company_name": "Source Synthetic Ltd",
                "metric_key": "grant_funding",
                "period_label": "TEMPORAL-ASSOCIATION-Q3",
                "value": "10",
            },
            checksum="a" * 64,
            connector_version="test-1",
            classification=DataClassification.SYNTHETIC.value,
            is_untrusted=False,
            is_stale=False,
            temporal_status=None,
        )
        first_run = WorkflowRunModel(
            dataset_id=first_raw.dataset_id,
            reporting_period_id=first_raw.reporting_period_id,
            reporting_cutoff=date(2025, 6, 30),
            stage="collect",
            status="running",
        )
        second_run = WorkflowRunModel(
            dataset_id=second_raw.dataset_id,
            reporting_period_id=second_raw.reporting_period_id,
            reporting_cutoff=date(2025, 9, 30),
            stage="collect",
            status="running",
        )
        session.add_all((evidence, first_run, second_run))
        session.flush()
        first_decision = temporal_eligibility(
            TemporalEvidence(published_at=datetime(2025, 7, 1, tzinfo=UTC)),
            TemporalWindow(reporting_cutoff=date(2025, 6, 30)),
        )
        second_decision = temporal_eligibility(
            TemporalEvidence(published_at=datetime(2025, 7, 1, tzinfo=UTC)),
            TemporalWindow(reporting_cutoff=date(2025, 9, 30)),
        )
        runtime.workflow._link_evidence(
            session,
            run=first_run,
            evidence_id=evidence.id,
            temporal=first_decision,
        )
        runtime.workflow._link_evidence(
            session,
            run=second_run,
            evidence_id=evidence.id,
            temporal=second_decision,
        )
        first_run_id = first_run.id
        second_run_id = second_run.id
        evidence_id = evidence.id

    with runtime.session_factory() as session:
        decisions = {
            run_id: status
            for run_id, status in session.execute(
                select(run_evidence.c.run_id, run_evidence.c.temporal_status).where(
                    run_evidence.c.evidence_item_id == evidence_id
                )
            ).all()
        }
        first_eligible = runtime.workflow._run_evidence(session, first_run_id, eligible_only=True)
        second_eligible = runtime.workflow._run_evidence(session, second_run_id, eligible_only=True)
    assert decisions == {
        first_run_id: "future_published",
        second_run_id: "eligible",
    }
    assert first_eligible == []
    assert [item.id for item in second_eligible] == [evidence_id]
