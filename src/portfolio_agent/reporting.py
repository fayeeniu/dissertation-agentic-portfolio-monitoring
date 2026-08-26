from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from .enums import ReportStatus, ReviewDecisionType, RunStatus, WorkflowStage
from .ids import stable_hash
from .models import (
    ClaimModel,
    ReportModel,
    ReportSectionModel,
    ReviewDecisionModel,
    WorkflowRunModel,
)


class ReportStateError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ExportBundle:
    report_id: str
    version: int
    json_path: Path
    markdown_path: Path
    html_path: Path
    content_hash: str


def _require_audit_text(actor: str, reason: str) -> tuple[str, str]:
    clean_actor = actor.strip()
    clean_reason = reason.strip()
    if not clean_actor or len(clean_actor) > 255:
        raise ReportStateError("Reviewer identity must be between 1 and 255 characters.")
    if len(clean_reason) < 3 or len(clean_reason) > 2000:
        raise ReportStateError("Review rationale must be between 3 and 2,000 characters.")
    return clean_actor, clean_reason


def _inline_markdown(value: str) -> str:
    escaped = html.escape(value)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def markdown_fragment_to_html(value: str) -> str:
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f"<p>{_inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            items = "".join(f"<li>{_inline_markdown(item)}</li>" for item in list_items)
            blocks.append(f"<ul>{items}</ul>")
            list_items.clear()

    for line in value.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            flush_paragraph()
            list_items.append(stripped[2:])
        elif not stripped:
            flush_paragraph()
            flush_list()
        else:
            flush_list()
            paragraph.append(stripped)
    flush_paragraph()
    flush_list()
    return "".join(blocks)


class ReportService:
    def __init__(self, session_factory: sessionmaker[Session], export_root: Path) -> None:
        self._session_factory = session_factory
        self._export_root = export_root.resolve()

    def approve(self, report_id: str, *, actor: str, reason: str) -> None:
        clean_actor, clean_reason = _require_audit_text(actor, reason)
        with self._session_factory.begin() as session:
            report = self._report_for_update(session, report_id)
            if report.status != ReportStatus.PENDING_REVIEW.value:
                raise ReportStateError("Only a pending-review report can be approved.")
            self._assert_approval_ready(session, report)
            report.status = ReportStatus.APPROVED.value
            report.approved_at = datetime.now(UTC)
            session.add(
                ReviewDecisionModel(
                    report_id=report.id,
                    section_id=None,
                    actor=clean_actor,
                    decision=ReviewDecisionType.APPROVE.value,
                    reason=clean_reason,
                    report_version=report.version,
                )
            )
            run = session.get(WorkflowRunModel, report.run_id)
            if run is not None:
                run.stage = WorkflowStage.APPROVE_EXPORT.value

    def reject(self, report_id: str, *, actor: str, reason: str) -> None:
        clean_actor, clean_reason = _require_audit_text(actor, reason)
        with self._session_factory.begin() as session:
            report = self._report_for_update(session, report_id)
            if report.status not in {
                ReportStatus.PENDING_REVIEW.value,
                ReportStatus.APPROVED.value,
            }:
                raise ReportStateError("This report cannot be rejected in its current state.")
            report.status = ReportStatus.REJECTED.value
            report.approved_at = None
            session.add(
                ReviewDecisionModel(
                    report_id=report.id,
                    section_id=None,
                    actor=clean_actor,
                    decision=ReviewDecisionType.REJECT.value,
                    reason=clean_reason,
                    report_version=report.version,
                )
            )

    def edit_section(
        self,
        report_id: str,
        section_key: str,
        *,
        body_markdown: str,
        actor: str,
        reason: str,
    ) -> int:
        clean_actor, clean_reason = _require_audit_text(actor, reason)
        clean_body = body_markdown.strip()
        if not clean_body or len(clean_body) > 50_000:
            raise ReportStateError("Section body must be between 1 and 50,000 characters.")
        with self._session_factory.begin() as session:
            report = self._report_for_update(session, report_id)
            if report.status in {ReportStatus.EXPORTED.value, ReportStatus.REJECTED.value}:
                raise ReportStateError("Exported or rejected reports are immutable.")
            current = session.scalar(
                select(ReportSectionModel).where(
                    ReportSectionModel.report_id == report.id,
                    ReportSectionModel.section_key == section_key,
                    ReportSectionModel.is_current.is_(True),
                )
            )
            if current is None:
                raise ReportStateError("Unknown report section.")
            current.is_current = False
            new_version = current.version + 1
            replacement = ReportSectionModel(
                report_id=report.id,
                company_id=current.company_id,
                section_key=current.section_key,
                heading=current.heading,
                order_index=current.order_index,
                body_markdown=clean_body,
                version=new_version,
                is_current=True,
            )
            session.add(replacement)
            session.flush()
            report.version += 1
            report.status = ReportStatus.PENDING_REVIEW.value
            report.approved_at = None
            current_sections = self._current_sections(session, report.id)
            current_sections.append(replacement)
            report.content_hash = stable_hash(
                [
                    {"key": section.section_key, "body": section.body_markdown}
                    for section in sorted(
                        {section.section_key: section for section in current_sections}.values(),
                        key=lambda item: item.order_index,
                    )
                ]
            )
            session.add(
                ReviewDecisionModel(
                    report_id=report.id,
                    section_id=replacement.id,
                    actor=clean_actor,
                    decision=ReviewDecisionType.REQUEST_EDIT.value,
                    reason=clean_reason,
                    report_version=report.version,
                )
            )
            return report.version

    def export(self, report_id: str) -> ExportBundle:
        with self._session_factory.begin() as session:
            report = self._report_for_update(session, report_id)
            if report.status not in {
                ReportStatus.APPROVED.value,
                ReportStatus.EXPORTED.value,
            }:
                raise ReportStateError("Human approval is required before export.")
            artifact = self._artifact(session, report)
            markdown = self._markdown(artifact)
            html_document = self._html(artifact)
            json_document = json.dumps(
                artifact, indent=2, sort_keys=True, ensure_ascii=False, default=str
            )
            content_hash = stable_hash(
                {"json": json_document, "markdown": markdown, "html": html_document}
            )
            target = self._export_root / report.id / f"v{report.version}"
            target.mkdir(parents=True, exist_ok=True, mode=0o700)
            json_path = target / "report.json"
            markdown_path = target / "report.md"
            html_path = target / "report.html"
            self._atomic_write(json_path, json_document)
            self._atomic_write(markdown_path, markdown)
            self._atomic_write(html_path, html_document)
            report.status = ReportStatus.EXPORTED.value
            report.exported_at = datetime.now(UTC)
            run = session.get(WorkflowRunModel, report.run_id)
            if run is not None:
                run.stage = WorkflowStage.COMPLETE.value
                run.status = RunStatus.SUCCEEDED.value
                run.finished_at = datetime.now(UTC)
            return ExportBundle(
                report_id=report.id,
                version=report.version,
                json_path=json_path,
                markdown_path=markdown_path,
                html_path=html_path,
                content_hash=content_hash,
            )

    @staticmethod
    def _report_for_update(session: Session, report_id: str) -> ReportModel:
        report = session.get(ReportModel, report_id)
        if report is None:
            raise ReportStateError("Unknown report ID.")
        return report

    @staticmethod
    def _current_sections(session: Session, report_id: str) -> list[ReportSectionModel]:
        return list(
            session.scalars(
                select(ReportSectionModel)
                .where(
                    ReportSectionModel.report_id == report_id,
                    ReportSectionModel.is_current.is_(True),
                )
                .order_by(ReportSectionModel.order_index)
            ).all()
        )

    def _assert_approval_ready(self, session: Session, report: ReportModel) -> None:
        sections = self._current_sections(session, report.id)
        if not sections or any(not section.body_markdown.strip() for section in sections):
            raise ReportStateError("Every current report section must contain reviewable content.")
        claims = list(
            session.scalars(
                select(ClaimModel)
                .where(ClaimModel.run_id == report.run_id)
                .options(joinedload(ClaimModel.verifications))
            ).unique()
        )
        if any(not claim.verifications for claim in claims):
            raise ReportStateError("Every claim must have an independent verification record.")

    def _artifact(self, session: Session, report: ReportModel) -> dict[str, Any]:
        sections = self._current_sections(session, report.id)
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
                .order_by(ClaimModel.id)
            ).unique()
        )
        decisions = list(
            session.scalars(
                select(ReviewDecisionModel)
                .where(ReviewDecisionModel.report_id == report.id)
                .order_by(ReviewDecisionModel.created_at)
            ).all()
        )
        return {
            "schema_version": "portfolio-report-v1",
            "report": {
                "id": report.id,
                "run_id": report.run_id,
                "dataset_id": report.dataset_id,
                "reporting_period_id": report.reporting_period_id,
                "title": report.title,
                "version": report.version,
                "status_at_export": report.status,
                "generated_at": report.generated_at.isoformat(),
                "approved_at": report.approved_at.isoformat() if report.approved_at else None,
                "content_hash": report.content_hash,
            },
            "sections": [
                {
                    "key": section.section_key,
                    "heading": section.heading,
                    "order": section.order_index,
                    "version": section.version,
                    "body_markdown": section.body_markdown,
                }
                for section in sections
            ],
            "claims": [
                {
                    "id": claim.id,
                    "company": claim.company.canonical_name,
                    "metric_key": claim.metric_definition.key,
                    "text": claim.text,
                    "normalized_value": claim.normalized_value_json,
                    "verification_status": claim.verification_status,
                    "verifications": [
                        {
                            "status": verification.status,
                            "rationale": verification.rationale,
                            "verifier_role": verification.verifier_role,
                            "verified_at": verification.verified_at.isoformat(),
                        }
                        for verification in claim.verifications
                    ],
                    "provenance": [
                        {
                            "evidence_id": evidence.id,
                            "source_type": evidence.source_type,
                            "publisher": evidence.publisher,
                            "locator": evidence.locator,
                            "checksum": evidence.checksum,
                            "retrieved_at": evidence.retrieved_at.isoformat(),
                        }
                        for evidence in claim.evidence_items
                    ],
                }
                for claim in claims
            ],
            "review_decisions": [
                {
                    "id": decision.id,
                    "decision": decision.decision,
                    "actor": decision.actor,
                    "reason": decision.reason,
                    "report_version": decision.report_version,
                    "created_at": decision.created_at.isoformat(),
                }
                for decision in decisions
            ],
        }

    @staticmethod
    def _markdown(artifact: dict[str, Any]) -> str:
        report = artifact["report"]
        lines = [
            f"# {report['title']}",
            "",
            f"Report ID: `{report['id']}`  ",
            f"Run ID: `{report['run_id']}`  ",
            f"Dataset ID: `{report['dataset_id']}`  ",
            f"Version: {report['version']}",
            "",
        ]
        for section in artifact["sections"]:
            lines.extend([f"## {section['heading']}", "", section["body_markdown"], ""])
        lines.extend(["## Claim provenance", ""])
        for claim in artifact["claims"]:
            lines.append(
                f"- `{claim['id']}` — {claim['verification_status']} — {claim['metric_key']}"
            )
            for evidence in claim["provenance"]:
                lines.append(
                    f"  - `{evidence['evidence_id']}` — {evidence['locator']} — "
                    f"SHA-256 `{evidence['checksum']}`"
                )
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _html(artifact: dict[str, Any]) -> str:
        report = artifact["report"]
        sections = "".join(
            '<section aria-labelledby="section-{index}">'
            '<h2 id="section-{index}">{heading}</h2>{body}</section>'.format(
                index=index,
                heading=html.escape(section["heading"]),
                body=markdown_fragment_to_html(section["body_markdown"]),
            )
            for index, section in enumerate(artifact["sections"], start=1)
        )
        return (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{html.escape(report['title'])}</title>"
            "<style>body{font:16px/1.55 system-ui;max-width:70rem;margin:auto;padding:2rem;}"
            "h1,h2{line-height:1.2}section{border-top:1px solid #bbb;margin-top:2rem;}"
            "code{overflow-wrap:anywhere}</style></head><body><main>"
            f"<h1>{html.escape(report['title'])}</h1>"
            f"<p>Report <code>{html.escape(report['id'])}</code>, version "
            f"{report['version']}.</p>{sections}</main></body></html>"
        )

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(0o600)
        temporary.replace(path)
