from __future__ import annotations

import json
from pathlib import Path

import pytest

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification, ReportStatus


@pytest.mark.e2e
def test_ingestion_to_approved_multi_format_export(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    assert pipeline.report_status is ReportStatus.PENDING_REVIEW

    runtime.reports.approve(
        pipeline.report_id,
        actor="Synthetic E2E Reviewer",
        reason="Explicit approval in a deterministic end-to-end test.",
    )
    bundle = runtime.reports.export(pipeline.report_id)

    artifact = json.loads(bundle.json_path.read_text(encoding="utf-8"))
    markdown = bundle.markdown_path.read_text(encoding="utf-8")
    html = bundle.html_path.read_text(encoding="utf-8")
    assert artifact["schema_version"] == "portfolio-report-v1"
    assert artifact["claims"]
    assert all(claim["verifications"] for claim in artifact["claims"])
    assert f"Dataset ID: `{imported.dataset_id}`" in markdown
    assert "<!doctype html>" in html
    assert "<main>" in html
