from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification
from portfolio_agent.models import (
    AgentRunModel,
    EvidenceItemModel,
    ExtractionAttemptModel,
    ReviewDecisionModel,
    run_evidence,
)
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
    assert "script-src 'self'" in run.headers["Content-Security-Policy"]
    assert "Skip to main content" in index.text
    assert 'name="reporting_cutoff"' in index.text
    assert "Runtime and approval boundary" in index.text
    assert "Recent work" in index.text
    assert "Evidence control room" in run.text
    assert "Eight bounded roles" in run.text
    assert '<ol class="agent-rail" data-agent-rail>' in run.text
    assert "Recorded state, not live activity" in run.text
    assert "Stage contracts and trace" in run.text
    assert "Needs human review" in run.text
    assert "Persisted stage status" in run.text
    assert "Recorded tool, source, and model calls" in run.text
    assert "Recorded outward calls" in run.text
    assert "fixture_connector" in run.text
    assert "companies_house" in run.text
    assert pipeline.run_id in run.text
    assert imported.dataset_id in run.text
    assert pipeline.report_id in report.text
    assert 'data-inspector-target="plan"' in run.text
    assert "/static/control-room.js" in run.text
    assert len(re.findall(r'<details[^>]+class="stage-inspector"[^>]+ open>', run.text)) == 8
    assert "Exceptions ledger" in run.text
    assert "Independent verification" not in report.text
    assert "Claim verification and provenance" in report.text
    assert "Human review desk" in report.text
    assert 'id="decision-dock"' in report.text
    assert "A complete stage does not make a claim supported" in report.text
    assert f'href="/runs/{pipeline.run_id}#exceptions"' in report.text


def test_run_trace_renders_recorded_service_fan_out_without_inventing_calls(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    """The collect and extract fan-out must come from persisted rows, not from the stage list."""

    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)

    page = TestClient(create_app(runtime)).get(f"/runs/{pipeline.run_id}")

    with runtime.session_factory() as session:
        attempts = list(
            session.scalars(
                select(ExtractionAttemptModel).where(
                    ExtractionAttemptModel.run_id == pipeline.run_id
                )
            ).all()
        )
        evidence_connectors = {
            item.connector
            for item in session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(run_evidence.c.run_id == pipeline.run_id)
            ).all()
        }

    assert page.status_code == 200
    assert attempts, "the synthetic workflow must persist provider attempts to fan out"
    assert 'data-parent="collect"' in page.text
    assert 'data-parent="extract"' in page.text
    for connector in evidence_connectors:
        assert connector in page.text
    assert f"{len(attempts)}&#215;" in page.text
    # Stages with no persisted outward call must not be drawn with a branch.
    assert 'data-parent="plan"' not in page.text
    assert 'data-parent="verify"' not in page.text


def test_run_trace_omits_unallowlisted_stage_metadata_and_raw_error_detail(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    pipeline = runtime.workflow.run(imported.dataset_id)
    with runtime.session_factory.begin() as session:
        agent = session.scalar(
            select(AgentRunModel).where(
                AgentRunModel.run_id == pipeline.run_id,
                AgentRunModel.stage == "extract",
            )
        )
        assert agent is not None
        agent.metadata_json = {
            **agent.metadata_json,
            "raw_value": "RESTRICTED-WORKBOOK-CONTENT",
            "prompt": "UNTRUSTED-PROVIDER-TEXT",
            "safe_fixture_count": 3,
        }
        agent.error = "ProviderError: SECRET-RAW-DETAIL"

    page = TestClient(create_app(runtime)).get(f"/runs/{pipeline.run_id}")

    assert page.status_code == 200
    assert "Safe fixture" in page.text
    assert "RESTRICTED-WORKBOOK-CONTENT" not in page.text
    assert "UNTRUSTED-PROVIDER-TEXT" not in page.text
    assert "SECRET-RAW-DETAIL" not in page.text
    assert "ProviderError recorded; raw detail is withheld" in page.text


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


def test_container_local_mode_accepts_only_private_container_clients(runtime: Runtime) -> None:
    private_client = ("172.18.0.1", 50000)
    public_client = ("8.8.8.8", 50000)

    default_response = TestClient(create_app(runtime), client=private_client).get(
        "/healthz", headers={"host": "localhost:8000"}
    )
    container_response = TestClient(
        create_app(runtime, allow_container_network_clients=True), client=private_client
    ).get("/healthz", headers={"host": "localhost:8000"})
    public_response = TestClient(
        create_app(runtime, allow_container_network_clients=True), client=public_client
    ).get("/healthz", headers={"host": "localhost:8000"})
    forged_host_response = TestClient(
        create_app(runtime, allow_container_network_clients=True), client=private_client
    ).get("/healthz", headers={"host": "attacker.example"})

    assert default_response.status_code == 403
    assert container_response.status_code == 200
    assert public_response.status_code == 403
    assert forged_host_response.status_code == 403


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
