from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .bootstrap import Runtime, create_runtime
from .enums import DataClassification, ReportStatus
from .importers import ImportValidationError
from .models import (
    AgentRunModel,
    ClaimModel,
    RawSubmissionModel,
    ReportModel,
    ReviewDecisionModel,
    WorkflowRunModel,
)
from .reporting import ReportStateError
from .workflow import PipelineExecutionError

PACKAGE_DIR = Path(__file__).resolve().parent
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


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
        session.expunge_all()
        return {
            "report": report,
            "sections": sections,
            "claims": claims,
            "decisions": decisions,
        }


def create_app(runtime: Runtime | None = None) -> FastAPI:
    selected = runtime or create_runtime()
    templates = Jinja2Templates(directory=str(PACKAGE_DIR / "templates"))
    app = FastAPI(
        title="Portfolio evidence review",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.runtime = selected
    app.mount("/static", StaticFiles(directory=str(PACKAGE_DIR / "static")), name="static")

    @app.middleware("http")
    async def security_headers(request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; img-src 'self'; form-action 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.exception_handler(ImportValidationError)
    @app.exception_handler(PipelineExecutionError)
    @app.exception_handler(ReportStateError)
    async def domain_error(request: Request, exc: Exception) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"message": str(exc)},
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
            session.expunge_all()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"datasets": datasets, "runs": runs, "reports": reports},
        )

    @app.post("/imports")
    async def import_submission(
        file: Annotated[UploadFile, File()],
        period_label: Annotated[str, Form()] = "",
        classification: Annotated[str, Form()] = DataClassification.RESTRICTED.value,
    ) -> RedirectResponse:
        payload = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(payload) > MAX_UPLOAD_BYTES:
            raise ImportValidationError("Upload exceeds the 20 MiB local prototype limit.")
        if classification not in {
            DataClassification.RESTRICTED.value,
            DataClassification.INTERNAL.value,
            DataClassification.SYNTHETIC.value,
        }:
            raise ImportValidationError("Unsupported data classification.")
        result = selected.importer.import_bytes(
            payload,
            filename=file.filename or "submission.bin",
            period_label=period_label or None,
            classification=DataClassification(classification),
        )
        return RedirectResponse(url=f"/?dataset={result.dataset_id}", status_code=303)

    @app.post("/runs")
    def run_dataset(dataset_id: Annotated[str, Form()]) -> RedirectResponse:
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
            context={"run": run, "agent_runs": agent_runs, "report": report},
        )

    @app.get("/reports/{report_id}", response_class=HTMLResponse)
    def report_detail(request: Request, report_id: str) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="report.html",
            context=_report_view(selected, report_id),
        )

    @app.post("/reports/{report_id}/approve")
    def approve_report(
        report_id: str,
        actor: Annotated[str, Form()],
        reason: Annotated[str, Form()],
    ) -> RedirectResponse:
        selected.reports.approve(report_id, actor=actor, reason=reason)
        return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

    @app.post("/reports/{report_id}/reject")
    def reject_report(
        report_id: str,
        actor: Annotated[str, Form()],
        reason: Annotated[str, Form()],
    ) -> RedirectResponse:
        selected.reports.reject(report_id, actor=actor, reason=reason)
        return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

    @app.post("/reports/{report_id}/sections/{section_key}/edit")
    def edit_section(
        report_id: str,
        section_key: str,
        body_markdown: Annotated[str, Form()],
        actor: Annotated[str, Form()],
        reason: Annotated[str, Form()],
    ) -> RedirectResponse:
        selected.reports.edit_section(
            report_id,
            section_key,
            body_markdown=body_markdown,
            actor=actor,
            reason=reason,
        )
        return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

    @app.post("/reports/{report_id}/export")
    def export_report(report_id: str) -> RedirectResponse:
        selected.reports.export(report_id)
        return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

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
            version = report.version
        extension = {"json": "json", "md": "md", "html": "html"}[format_name]
        path = (
            selected.settings.project_root
            / "var"
            / "exports"
            / report_id
            / f"v{version}"
            / f"report.{extension}"
        ).resolve()
        export_root = (selected.settings.project_root / "var" / "exports").resolve()
        if not path.is_relative_to(export_root) or not path.is_file():
            raise HTTPException(status_code=404, detail="Export artifact is unavailable.")
        media_type = {
            "json": "application/json",
            "md": "text/markdown",
            "html": "text/html",
        }[format_name]
        return FileResponse(path, media_type=media_type, filename=path.name)

    return app


app = create_app()
