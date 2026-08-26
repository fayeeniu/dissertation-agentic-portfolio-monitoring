from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification
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
    assert "Independent verification" not in report.text
    assert "Claim verification and provenance" in report.text


def test_web_approval_then_export(runtime: Runtime, synthetic_portfolio_path: Path) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    client = TestClient(create_app(runtime))

    approval = client.post(
        f"/reports/{pipeline.report_id}/approve",
        data={"actor": "Synthetic Web Reviewer", "reason": "Checked fixture evidence."},
        follow_redirects=False,
    )
    export = client.post(f"/reports/{pipeline.report_id}/export", follow_redirects=False)
    download = client.get(f"/reports/{pipeline.report_id}/download/json")

    assert approval.status_code == 303
    assert export.status_code == 303
    assert download.status_code == 200
    assert download.json()["report"]["id"] == pipeline.report_id
