from __future__ import annotations

import hmac
import secrets
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .bootstrap import Runtime, create_runtime
from .enums import DataClassification, IdentityDecisionType, ReportStatus
from .events import events_for_run
from .identity import decide_identity_candidate
from .importers import ImportValidationError
from .models import (
    AgentRunModel,
    ClaimModel,
    EvidenceItemModel,
    IdentityCandidateModel,
    QualityViolationModel,
    RawSubmissionModel,
    ReportModel,
    ReviewDecisionModel,
    WorkflowRunModel,
    run_evidence,
)
from .reporting import ReportStateError, markdown_fragment_to_html
from .workflow import PipelineExecutionError

PACKAGE_DIR = Path(__file__).resolve().parent
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
CSRF_COOKIE = "portfolio_csrf"
ALLOWED_HOST_HEADERS = {"127.0.0.1", "localhost", "::1", "testserver"}
ALLOWED_CLIENTS = {"127.0.0.1", "::1", "testclient"}


def _host_without_port(value: str) -> str:
    lowered = value.strip().casefold()
    if lowered.startswith("[") and "]" in lowered:
        return lowered[1 : lowered.index("]")]
    return lowered.split(":", 1)[0]


def _report_view(runtime: Runtime, report_id: str) -> dict[str, Any]:
    with runtime.session_factory() as session:
        report = session.scalar(
            select(ReportModel)
            .where(ReportModel.id == report_id)
            .options(joinedload(ReportModel.sections))
        )
        if report is None:
            raise HTTPException(status_code=404, detail="Unknown report ID.")
        sections = sorted(
            (section for section in report.sections if section.is_current),
            key=lambda section: section.order_index,
        )
        claims = list(
            session.scalars(
                select(ClaimModel)
                .where(ClaimModel.run_id == report.run_id)
                .options(
                    joinedload(ClaimModel.company),
                    joinedload(ClaimModel.metric_definition),
                    joinedload(ClaimModel.evidence_items),
                    joinedload(ClaimModel.verifications),
                )
                .order_by(ClaimModel.company_id, ClaimModel.metric_definition_id)
            ).unique()
        )
        decisions = list(
            session.scalars(
                select(ReviewDecisionModel)
                .where(ReviewDecisionModel.report_id == report.id)
                .order_by(ReviewDecisionModel.created_at.desc())
            ).all()
        )
        quality_findings = list(
            session.scalars(
                select(QualityViolationModel)
                .where(QualityViolationModel.run_id == report.run_id)
                .order_by(QualityViolationModel.disposition, QualityViolationModel.rule_key)
            ).all()
        )
        events = list(events_for_run(session, run_id=report.run_id))
        evidence_items = list(
            session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(run_evidence.c.run_id == report.run_id)
            ).all()
        )
        temporal_by_evidence = {
            evidence_id: {
                "reporting_cutoff": cutoff,
                "status": status,
                "reason": reason,
            }
            for evidence_id, cutoff, status, reason in session.execute(
                select(
                    run_evidence.c.evidence_item_id,
                    run_evidence.c.reporting_cutoff,
                    run_evidence.c.temporal_status,
                    run_evidence.c.temporal_reason,
                ).where(run_evidence.c.run_id == report.run_id)
            ).all()
        }
        visual_summary = {
            "Verification": dict(
                sorted(Counter(claim.verification_status for claim in claims).items())
            ),
            "Evidence sources": dict(
                sorted(Counter(item.source_type for item in evidence_items).items())
            ),
            "Quality dispositions": dict(
                sorted(Counter(item.disposition for item in quality_findings).items())
            ),
            "Event types": dict(sorted(Counter(item.event_type for item in events).items())),
        }
        session.expunge_all()
        return {
            "report": report,
            "sections": sections,
            "claims": claims,
            "decisions": decisions,
            "quality_findings": quality_findings,
            "events": events,
            "temporal_by_evidence": temporal_by_evidence,
            "visual_summary": visual_summary,
        }


def create_app(runtime: Runtime | None = None) -> FastAPI:
    selected = runtime or create_runtime()
    templates = Jinja2Templates(directory=str(PACKAGE_DIR / "templates"))
    templates.env.filters["safe_markdown"] = markdown_fragment_to_html
    app = FastAPI(
        title="Portfolio evidence review",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.runtime = selected
    app.state.csrf_token = secrets.token_urlsafe(32)
    app.mount("/static", StaticFiles(directory=str(PACKAGE_DIR / "static")), name="static")

    @app.middleware("http")
    async def security_headers(request: Request, call_next: Any) -> Any:
        client_host = request.client.host if request.client is not None else ""
        host_header = _host_without_port(request.headers.get("host", ""))
        if client_host not in ALLOWED_CLIENTS or host_header not in ALLOWED_HOST_HEADERS:
            return PlainTextResponse("Local loopback access only.", status_code=403)
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; img-src 'self'; form-action 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Frame-Options"] = "DENY"
        if request.cookies.get(CSRF_COOKIE) != app.state.csrf_token:
            response.set_cookie(
                CSRF_COOKIE,
                app.state.csrf_token,
                httponly=True,
                samesite="strict",
                secure=False,
                path="/",
            )
        return response

    def template_context(context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            **(context or {}),
            "csrf_token": app.state.csrf_token,
            "reviewer_name": selected.settings.reviewer_name,
        }

    def require_csrf(request: Request, submitted: str) -> None:
        cookie = request.cookies.get(CSRF_COOKIE, "")
        expected = app.state.csrf_token
        if not (hmac.compare_digest(submitted, expected) and hmac.compare_digest(cookie, expected)):
            raise HTTPException(status_code=403, detail="CSRF validation failed.")

    def reviewer_identity() -> str:
        reviewer = (selected.settings.reviewer_name or "").strip()
        if len(reviewer) < 2:
            raise HTTPException(
                status_code=403,
                detail="Set PORTFOLIO_REVIEWER_NAME before using review mutations.",
            )
        return reviewer

    @app.exception_handler(ImportValidationError)
    @app.exception_handler(PipelineExecutionError)
    @app.exception_handler(ReportStateError)
    async def domain_error(request: Request, exc: Exception) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context=template_context({"message": str(exc)}),
            status_code=422,
        )

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok", "external_llm": "disabled-by-default"}

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        with selected.session_factory() as session:
            datasets = list(
                session.scalars(
                    select(RawSubmissionModel)
                    .options(joinedload(RawSubmissionModel.reporting_period))
                    .order_by(RawSubmissionModel.created_at.desc())
                ).all()
            )
            runs = list(
                session.scalars(
                    select(WorkflowRunModel).order_by(WorkflowRunModel.started_at.desc()).limit(20)
                ).all()
            )
            reports = list(
                session.scalars(
                    select(ReportModel).order_by(ReportModel.generated_at.desc()).limit(20)
                ).all()
            )
            identity_candidates = list(
                session.scalars(
                    select(IdentityCandidateModel)
                    .where(IdentityCandidateModel.status == "pending")
                    .order_by(IdentityCandidateModel.created_at)
                ).all()
            )
            session.expunge_all()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=template_context(
                {
                    "datasets": datasets,
                    "runs": runs,
                    "reports": reports,
                    "identity_candidates": identity_candidates,
                }
            ),
        )

    @app.post("/imports")
    async def import_submission(
        request: Request,
        file: Annotated[UploadFile, File()],
        csrf_token: Annotated[str, Form()] = "",
        period_label: Annotated[str, Form()] = "",
        reporting_cutoff: Annotated[str, Form()] = "",
        classification: Annotated[str, Form()] = DataClassification.RESTRICTED.value,
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        payload = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(payload) > MAX_UPLOAD_BYTES:
            raise ImportValidationError("Upload exceeds the 20 MiB local prototype limit.")
        if classification not in {
            DataClassification.RESTRICTED.value,
            DataClassification.INTERNAL.value,
            DataClassification.SYNTHETIC.value,
        }:
            raise ImportValidationError("Unsupported data classification.")
        cutoff: date | None = None
        if reporting_cutoff.strip():
            try:
                cutoff = date.fromisoformat(reporting_cutoff.strip())
            except ValueError as exc:
                raise ImportValidationError("Reporting cutoff must use YYYY-MM-DD format.") from exc
        result = selected.importer.import_bytes(
            payload,
            filename=file.filename or "submission.bin",
            period_label=period_label or None,
            reporting_cutoff=cutoff,
            classification=DataClassification(classification),
        )
        return RedirectResponse(url=f"/?dataset={result.dataset_id}", status_code=303)

    @app.post("/runs")
    def run_dataset(
        request: Request,
        dataset_id: Annotated[str, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        result = selected.workflow.run(dataset_id)
        return RedirectResponse(url=f"/runs/{result.run_id}", status_code=303)

    @app.get("/runs/{run_id}", response_class=HTMLResponse)
    def run_detail(request: Request, run_id: str) -> HTMLResponse:
        with selected.session_factory() as session:
            run = session.get(WorkflowRunModel, run_id)
            if run is None:
                raise HTTPException(status_code=404, detail="Unknown run ID.")
            agent_runs = list(
                session.scalars(
                    select(AgentRunModel)
                    .where(AgentRunModel.run_id == run_id)
                    .order_by(AgentRunModel.started_at)
                ).all()
            )
            report = session.scalar(select(ReportModel).where(ReportModel.run_id == run_id))
            session.expunge_all()
        return templates.TemplateResponse(
            request=request,
            name="run.html",
            context=template_context({"run": run, "agent_runs": agent_runs, "report": report}),
        )

    @app.get("/reports/{report_id}", response_class=HTMLResponse)
    def report_detail(request: Request, report_id: str) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="report.html",
            context=template_context(_report_view(selected, report_id)),
        )

    @app.post("/reports/{report_id}/approve")
    def approve_report(
        request: Request,
        report_id: str,
        reason: Annotated[str, Form()],
        expected_lock_version: Annotated[int, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        selected.reports.approve(
            report_id,
            actor=reviewer_identity(),
            reason=reason,
            expected_lock_version=expected_lock_version,
        )
        return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

    @app.post("/reports/{report_id}/reject")
    def reject_report(
        request: Request,
        report_id: str,
        reason: Annotated[str, Form()],
        expected_lock_version: Annotated[int, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        selected.reports.reject(
            report_id,
            actor=reviewer_identity(),
            reason=reason,
            expected_lock_version=expected_lock_version,
        )
        return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

    @app.post("/reports/{report_id}/sections/{section_key}/edit")
    def edit_section(
        request: Request,
        report_id: str,
        section_key: str,
        body_markdown: Annotated[str, Form()],
        reason: Annotated[str, Form()],
        expected_lock_version: Annotated[int, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        selected.reports.edit_section(
            report_id,
            section_key,
            body_markdown=body_markdown,
            actor=reviewer_identity(),
            reason=reason,
            expected_lock_version=expected_lock_version,
        )
        return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

    @app.post("/reports/{report_id}/export")
    def export_report(
        request: Request,
        report_id: str,
        expected_lock_version: Annotated[int, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        reviewer_identity()
        selected.reports.export(report_id, expected_lock_version=expected_lock_version)
        return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

    @app.post("/identity-candidates/{candidate_id}/decide")
    def decide_identity(
        request: Request,
        candidate_id: str,
        decision: Annotated[str, Form()],
        reason: Annotated[str, Form()],
        company_id: Annotated[str, Form()] = "",
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        try:
            selected_decision = IdentityDecisionType(decision)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Unknown identity decision.") from exc
        with selected.session_factory.begin() as session:
            decide_identity_candidate(
                session,
                candidate_id=candidate_id,
                decision=selected_decision,
                actor=reviewer_identity(),
                reason=reason,
                company_id=company_id.strip() or None,
            )
        return RedirectResponse(url="/", status_code=303)

    @app.get("/reports/{report_id}/download/{format_name}")
    def download_report(report_id: str, format_name: str) -> FileResponse:
        if format_name not in {"json", "md", "html"}:
            raise HTTPException(status_code=404, detail="Unknown export format.")
        with selected.session_factory() as session:
            report = session.get(ReportModel, report_id)
            if report is None:
                raise HTTPException(status_code=404, detail="Unknown report ID.")
            if report.status != ReportStatus.EXPORTED.value:
                raise HTTPException(status_code=409, detail="Report has not been exported.")
            lock_version = report.lock_version
        bundle = selected.reports.export(report_id, expected_lock_version=lock_version)
        paths = {
            "json": bundle.json_path,
            "md": bundle.markdown_path,
            "html": bundle.html_path,
        }
        path = paths[format_name]
        media_type = {
            "json": "application/json",
            "md": "text/markdown",
            "html": "text/html",
        }[format_name]
        return FileResponse(path, media_type=media_type, filename=path.name)

    return app
