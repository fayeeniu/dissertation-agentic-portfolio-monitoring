from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import select

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification, ReportStatus
from portfolio_agent.models import ExtractionModel, WorkflowRunModel


@pytest.mark.e2e
def test_ingestion_to_approved_multi_format_export(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    assert pipeline.report_status is ReportStatus.PENDING_REVIEW

    lock_version = runtime.reports.approve(
        pipeline.report_id,
        actor="Synthetic E2E Reviewer",
        reason="Explicit approval in a deterministic end-to-end test.",
        expected_lock_version=1,
    )
    bundle = runtime.reports.export(pipeline.report_id, expected_lock_version=lock_version)

    artifact = json.loads(bundle.json_path.read_text(encoding="utf-8"))
    markdown = bundle.markdown_path.read_text(encoding="utf-8")
    html = bundle.html_path.read_text(encoding="utf-8")
    assert artifact["schema_version"] == "portfolio-report-v1"
    assert artifact["claims"]
    assert all(claim["verifications"] for claim in artifact["claims"])
    assert f"Dataset ID: `{imported.dataset_id}`" in markdown
    assert "<!doctype html>" in html
    assert "<main>" in html

    with runtime.session_factory() as session:
        extractions = list(session.scalars(select(ExtractionModel)))
        persisted_run = session.get(WorkflowRunModel, pipeline.run_id)
    assert extractions
    assert persisted_run is not None
    assert persisted_run.evidence_contract_version == "uk-public-evidence-v2"
    assert all(row.schema_version == "strict-extraction-v2" for row in extractions)
    assert all(row.evidence_span for row in extractions if row.extracted_value_json is not None)
    assert all(row.abstain_reason for row in extractions if row.extracted_value_json is None)
