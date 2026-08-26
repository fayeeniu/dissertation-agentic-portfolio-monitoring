from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import func, select

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification, ReportStatus
from portfolio_agent.models import ReportExportModel, ReportModel
from portfolio_agent.reporting import ReportStateError


def test_export_is_blocked_until_audited_human_approval(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)

    with pytest.raises(ReportStateError, match="approval"):
        runtime.reports.export(pipeline.report_id, expected_lock_version=1)

    lock_version = runtime.reports.approve(
        pipeline.report_id,
        actor="Synthetic Test Reviewer",
        reason="Reviewed all synthetic verification states.",
        expected_lock_version=1,
    )
    bundle = runtime.reports.export(pipeline.report_id, expected_lock_version=lock_version)

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
        expected_lock_version=1,
    )
    assert new_version == 2
    with pytest.raises(ReportStateError, match="approval"):
        runtime.reports.export(pipeline.report_id, expected_lock_version=2)


def test_stale_report_mutation_is_rejected(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    runtime.reports.edit_section(
        pipeline.report_id,
        "methodology",
        body_markdown="First reviewed edit.",
        actor="Synthetic Test Reviewer",
        reason="First versioned edit.",
        expected_lock_version=1,
    )
    with pytest.raises(ReportStateError, match="changed after"):
        runtime.reports.edit_section(
            pipeline.report_id,
            "methodology",
            body_markdown="Stale edit must not win.",
            actor="Synthetic Test Reviewer",
            reason="Stale competing edit.",
            expected_lock_version=1,
        )


def test_failed_export_never_becomes_final(
    runtime: Runtime,
    synthetic_portfolio_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    lock_version = runtime.reports.approve(
        pipeline.report_id,
        actor="Synthetic Test Reviewer",
        reason="Approved for atomic failure-path proof.",
        expected_lock_version=1,
    )
    original_write = runtime.reports._atomic_write

    def fail_on_markdown(path: Path, content: str) -> None:
        if path.name == "report.md":
            raise OSError("synthetic write failure")
        original_write(path, content)

    monkeypatch.setattr(runtime.reports, "_atomic_write", fail_on_markdown)
    with pytest.raises(ReportStateError, match="atomically"):
        runtime.reports.export(pipeline.report_id, expected_lock_version=lock_version)
    with runtime.session_factory() as session:
        report = session.get(ReportModel, pipeline.report_id)
        export_record = session.scalar(
            select(ReportExportModel).where(ReportExportModel.report_id == pipeline.report_id)
        )
    assert report is not None and report.status == ReportStatus.APPROVED.value
    assert export_record is not None and export_record.status == "failed"
    assert not Path(export_record.artifact_root).exists()

    monkeypatch.setattr(runtime.reports, "_atomic_write", original_write)
    bundle = runtime.reports.export(pipeline.report_id, expected_lock_version=3)
    with runtime.session_factory() as session:
        retried_report = session.get(ReportModel, pipeline.report_id)
        retried_export = session.scalar(
            select(ReportExportModel).where(ReportExportModel.report_id == pipeline.report_id)
        )
        export_count = session.scalar(
            select(func.count())
            .select_from(ReportExportModel)
            .where(ReportExportModel.report_id == pipeline.report_id)
        )
    assert bundle.json_path.is_file()
    assert retried_report is not None and retried_report.status == ReportStatus.EXPORTED.value
    assert retried_export is not None and retried_export.status == "finalized"
    assert retried_export.error is None
    assert export_count == 1


def test_report_cannot_be_edited_while_export_is_in_progress(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    with runtime.session_factory.begin() as session:
        report = session.get(ReportModel, pipeline.report_id)
        assert report is not None
        report.status = ReportStatus.EXPORTING.value

    with pytest.raises(ReportStateError, match="pending-review or approved"):
        runtime.reports.edit_section(
            pipeline.report_id,
            "methodology",
            body_markdown="This edit must remain blocked.",
            actor="Synthetic Test Reviewer",
            reason="Concurrent export mutation proof.",
            expected_lock_version=1,
        )


def test_finalized_export_is_reverified_before_reuse(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    lock_version = runtime.reports.approve(
        pipeline.report_id,
        actor="Synthetic Test Reviewer",
        reason="Approved for immutable export verification proof.",
        expected_lock_version=1,
    )
    bundle = runtime.reports.export(pipeline.report_id, expected_lock_version=lock_version)
    bundle.json_path.write_text("{}", encoding="utf-8")

    with pytest.raises(ReportStateError, match="checksum failed"):
        runtime.reports.export(pipeline.report_id, expected_lock_version=3)
