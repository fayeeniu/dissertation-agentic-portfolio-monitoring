from __future__ import annotations

import json
from pathlib import Path

import pytest

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification
from portfolio_agent.reporting import ReportStateError


def test_export_is_blocked_until_audited_human_approval(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)

    with pytest.raises(ReportStateError, match="approval"):
        runtime.reports.export(pipeline.report_id)

    runtime.reports.approve(
        pipeline.report_id,
        actor="Synthetic Test Reviewer",
        reason="Reviewed all synthetic verification states.",
    )
    bundle = runtime.reports.export(pipeline.report_id)

    assert bundle.json_path.is_file()
    assert bundle.markdown_path.is_file()
    assert bundle.html_path.is_file()
    artifact = json.loads(bundle.json_path.read_text(encoding="utf-8"))
    assert artifact["report"]["dataset_id"] == imported.dataset_id
    assert artifact["review_decisions"][0]["decision"] == "approve"
    assert all("provenance" in claim for claim in artifact["claims"])


def test_section_edit_creates_version_and_requires_reapproval(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    new_version = runtime.reports.edit_section(
        pipeline.report_id,
        "methodology",
        body_markdown="Reviewed synthetic methodology section.",
        actor="Synthetic Test Reviewer",
        reason="Clarified the synthetic evidence boundary.",
    )
    assert new_version == 2
    with pytest.raises(ReportStateError, match="approval"):
        runtime.reports.export(pipeline.report_id)
