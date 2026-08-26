from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification
from portfolio_agent.models import ReviewDecisionModel
from portfolio_agent.web import create_app


def test_server_rendered_review_pages_and_security_headers(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    client = TestClient(create_app(runtime))

    health = client.get("/healthz")
    index = client.get("/")
    run = client.get(f"/runs/{pipeline.run_id}")
    report = client.get(f"/reports/{pipeline.report_id}")

    assert health.json() == {"status": "ok", "external_llm": "disabled-by-default"}
    assert index.status_code == run.status_code == report.status_code == 200
    assert "Content-Security-Policy" in report.headers
    assert "Skip to main content" in index.text
    assert 'name="reporting_cutoff"' in index.text
    assert "Independent verification" not in report.text
    assert "Claim verification and provenance" in report.text


def test_web_approval_then_export(runtime: Runtime, synthetic_portfolio_path: Path) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    app = create_app(runtime)
    client = TestClient(app)
    token = app.state.csrf_token
    client.get(f"/reports/{pipeline.report_id}")

    approval = client.post(
        f"/reports/{pipeline.report_id}/approve",
        data={
            "reason": "Checked fixture evidence.",
            "expected_lock_version": "1",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    export = client.post(
        f"/reports/{pipeline.report_id}/export",
        data={"expected_lock_version": "2", "csrf_token": token},
        follow_redirects=False,
    )
    download = client.get(f"/reports/{pipeline.report_id}/download/json")

    assert approval.status_code == 303
    assert export.status_code == 303
    assert download.status_code == 200
    assert download.json()["report"]["id"] == pipeline.report_id

    bundle = runtime.reports.export(pipeline.report_id, expected_lock_version=3)
    bundle.json_path.write_text("{}", encoding="utf-8")
    tampered_download = client.get(f"/reports/{pipeline.report_id}/download/json")
    assert tampered_download.status_code == 422
    assert "checksum failed" in tampered_download.text


def test_web_rejects_csrf_host_forgery_and_form_actor(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    app = create_app(runtime)
    client = TestClient(app)
    client.get(f"/reports/{pipeline.report_id}")

    missing_csrf = client.post(
        f"/reports/{pipeline.report_id}/approve",
        data={"reason": "No token.", "expected_lock_version": "1"},
    )
    forged_host = client.get("/", headers={"host": "attacker.example"})
    approved = client.post(
        f"/reports/{pipeline.report_id}/approve",
        data={
            "actor": "Self asserted attacker",
            "reason": "Configured reviewer identity must own this decision.",
            "expected_lock_version": "1",
            "csrf_token": app.state.csrf_token,
        },
        follow_redirects=False,
    )

    assert missing_csrf.status_code == 403
    assert forged_host.status_code == 403
    assert approved.status_code == 303
    with runtime.session_factory() as session:
        decision = session.scalar(
            select(ReviewDecisionModel).where(ReviewDecisionModel.report_id == pipeline.report_id)
        )
    assert decision is not None
    assert decision.actor == "Synthetic Test Reviewer"


def test_web_import_validates_and_accepts_reporting_cutoff(runtime: Runtime) -> None:
    app = create_app(runtime)
    client = TestClient(app)
    index = client.get("/")
    token = app.state.csrf_token
    invalid = client.post(
        "/imports",
        data={
            "csrf_token": token,
            "period_label": "SYN-2025-Q2",
            "reporting_cutoff": "30-06-2025",
            "classification": "synthetic",
        },
        files={"file": ("synthetic.csv", b"metric,Synthetic Ltd\nemployees,2\n")},
    )
    accepted = client.post(
        "/imports",
        data={
            "csrf_token": token,
            "period_label": "SYN-2025-Q2",
            "reporting_cutoff": "2025-06-30",
            "classification": "synthetic",
        },
        files={"file": ("synthetic.csv", b"metric,Synthetic Ltd\nemployees,2\n")},
        follow_redirects=False,
    )

    assert index.status_code == 200
    assert invalid.status_code == 422
    assert "YYYY-MM-DD" in invalid.text
    assert accepted.status_code == 303
