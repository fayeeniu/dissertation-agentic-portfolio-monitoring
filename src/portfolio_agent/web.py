from __future__ import annotations

import hmac
import ipaddress
import json
import secrets
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from .api import create_api_router
from .bootstrap import Runtime, create_runtime
from .company_intelligence import (
    MAX_INTAKE_BYTES,
    CompanyIntakeRequest,
    CompanyIntakeValidationError,
)
from .company_research import (
    CompanyResearchError,
    profile_deck_html,
    validated_profile_content,
)
from .dashboard import (
    AttemptUsage,
    ConnectorUsage,
    ExceptionEntry,
    SnapshotUsage,
    WorkItem,
    build_activity_log,
    build_health_groups,
    build_service_calls,
    build_stage_views,
    derive_report_next_action,
    derive_run_next_action,
    derive_work_item_action,
    humanize,
    short_identifier,
    summarize_lifecycle,
)
from .enums import (
    CollectionStatus,
    DataClassification,
    IdentityCandidateStatus,
    IdentityDecisionType,
    QualityDisposition,
    ReportStatus,
    VerificationStatus,
)
from .events import events_for_run
from .identity import decide_identity_candidate, identifier_review_projection
from .importers import ImportValidationError
from .models import (
    AgentRunModel,
    ClaimModel,
    CompanyDomainDecisionModel,
    CompanyDomainModel,
    CompanyIdentifierModel,
    CompanyModel,
    CompanyResearchClaimModel,
    CompanyResearchRunModel,
    CompanyResearchSourceModel,
    CompanyResearchTaskModel,
    EvidenceItemModel,
    ExtractionAttemptModel,
    IdentityCandidateModel,
    IntakeArtifactModel,
    MetricDefinitionModel,
    ProfileVersionModel,
    QualityViolationModel,
    RawSubmissionModel,
    ReportModel,
    ResearchCaseModel,
    ReviewDecisionModel,
    SourceDefinitionModel,
    SourceSnapshotModel,
    WorkflowRunModel,
    run_evidence,
    run_source_snapshots,
)
from .reporting import ReportStateError, markdown_fragment_to_html
from .workflow import PipelineExecutionError

PACKAGE_DIR = Path(__file__).resolve().parent
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
CSRF_COOKIE = "portfolio_csrf"
ALLOWED_HOST_HEADERS = {"127.0.0.1", "localhost", "::1", "testserver"}
ALLOWED_CLIENTS = {"127.0.0.1", "::1", "testclient"}
CONTAINER_CLIENT_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7")
)

_EXCEPTION_SEVERITY_ORDER = {"danger": 0, "hold": 1, "warning": 2, "information": 3}


def _host_without_port(value: str) -> str:
    lowered = value.strip().casefold()
    if lowered.startswith("[") and "]" in lowered:
        return lowered[1 : lowered.index("]")]
    return lowered.split(":", 1)[0]


def _client_is_allowed(value: str, *, allow_container_network_clients: bool) -> bool:
    if value in ALLOWED_CLIENTS:
        return True
    if not allow_container_network_clients:
        return False
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return any(address in network for network in CONTAINER_CLIENT_NETWORKS)


def _companies_view(runtime: Runtime) -> dict[str, Any]:
    with runtime.session_factory() as session:
        companies = list(
            session.scalars(select(CompanyModel).order_by(CompanyModel.created_at.desc())).all()
        )
        identifiers_by_company: defaultdict[str, list[CompanyIdentifierModel]] = defaultdict(list)
        for identifier in session.scalars(
            select(CompanyIdentifierModel).order_by(CompanyIdentifierModel.created_at)
        ):
            identifiers_by_company[identifier.company_id].append(identifier)
        domains_by_company: defaultdict[str, list[CompanyDomainModel]] = defaultdict(list)
        for domain in session.scalars(
            select(CompanyDomainModel).order_by(CompanyDomainModel.created_at)
        ):
            domains_by_company[domain.company_id].append(domain)
        cases_by_company: defaultdict[str, list[ResearchCaseModel]] = defaultdict(list)
        for case in session.scalars(
            select(ResearchCaseModel).order_by(ResearchCaseModel.created_at.desc())
        ):
            cases_by_company[case.company_id].append(case)
        artifact_counts: dict[str, int] = {
            company_id: count
            for company_id, count in session.execute(
                select(IntakeArtifactModel.company_id, func.count(IntakeArtifactModel.id)).group_by(
                    IntakeArtifactModel.company_id
                )
            ).all()
        }

        rows: list[dict[str, Any]] = []
        attention_count = 0
        for company in companies:
            identifiers = identifiers_by_company[company.id]
            identifier_states = {
                identifier.id: identifier_review_projection(session, identifier).status.value
                for identifier in identifiers
            }
            domains = domains_by_company[company.id]
            cases = cases_by_company[company.id]
            primary_identifier = next(
                (item for item in identifiers if item.scheme == "companies_house_number"),
                identifiers[0] if identifiers else None,
            )
            verified_domain = next(
                (item for item in domains if item.status == "verified"),
                domains[0] if domains else None,
            )
            open_count = sum(
                identifier_states[item.id] == IdentityCandidateStatus.PENDING.value
                for item in identifiers
            ) + sum(item.status == "pending" for item in domains)
            if open_count or company.resolution_status != "resolved":
                attention_count += 1
            if any(
                identifier_states[item.id] == IdentityCandidateStatus.PENDING.value
                for item in identifiers
            ):
                next_action = "Review exact identifier"
            elif any(item.status == "pending" for item in domains):
                next_action = "Review domain claim"
            elif company.resolution_status != "resolved":
                next_action = "Provide exact identity evidence"
            elif cases:
                next_action = "Offline case ready"
            else:
                next_action = "No research case"
            rows.append(
                {
                    "company": company,
                    "identifier": primary_identifier,
                    "domain": verified_domain,
                    "case": cases[0] if cases else None,
                    "case_count": len(cases),
                    "artifact_count": artifact_counts.get(company.id, 0),
                    "open_count": open_count,
                    "next_action": next_action,
                }
            )
        session.expunge_all()
        return {
            "company_rows": rows,
            "company_count": len(rows),
            "attention_count": attention_count,
            "company_research_enabled": runtime.company_research is not None,
        }


def _company_view(runtime: Runtime, company_id: str) -> dict[str, Any]:
    with runtime.session_factory() as session:
        company = session.get(CompanyModel, company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Unknown company ID.")
        identifiers = list(
            session.scalars(
                select(CompanyIdentifierModel)
                .where(CompanyIdentifierModel.company_id == company_id)
                .order_by(CompanyIdentifierModel.created_at)
            ).all()
        )
        domains = list(
            session.scalars(
                select(CompanyDomainModel)
                .where(CompanyDomainModel.company_id == company_id)
                .order_by(CompanyDomainModel.created_at)
            ).all()
        )
        cases = list(
            session.scalars(
                select(ResearchCaseModel)
                .where(ResearchCaseModel.company_id == company_id)
                .order_by(ResearchCaseModel.created_at.desc())
            ).all()
        )
        artifacts = list(
            session.scalars(
                select(IntakeArtifactModel)
                .where(IntakeArtifactModel.company_id == company_id)
                .order_by(IntakeArtifactModel.created_at.desc())
            ).all()
        )
        domain_ids = [item.id for item in domains]
        case_ids = [item.id for item in cases]
        identifier_states: dict[str, str] = {}
        identifier_decisions: dict[str, list[Any]] = {}
        identifier_candidates: dict[str, list[IdentityCandidateModel]] = {}
        for identifier in identifiers:
            projection = identifier_review_projection(session, identifier)
            identifier_states[identifier.id] = projection.status.value
            identifier_decisions[identifier.id] = list(projection.decisions)
            identifier_candidates[identifier.id] = [
                candidate
                for candidate in projection.candidates
                if candidate.status == IdentityCandidateStatus.PENDING.value
            ]
        domain_decisions: defaultdict[str, list[CompanyDomainDecisionModel]] = defaultdict(list)
        if domain_ids:
            for domain_decision in session.scalars(
                select(CompanyDomainDecisionModel)
                .where(CompanyDomainDecisionModel.company_domain_id.in_(domain_ids))
                .order_by(CompanyDomainDecisionModel.created_at.desc())
            ):
                domain_decisions[domain_decision.company_domain_id].append(domain_decision)
        profile_versions = (
            list(
                session.scalars(
                    select(ProfileVersionModel)
                    .where(ProfileVersionModel.research_case_id.in_(case_ids))
                    .order_by(ProfileVersionModel.created_at.desc())
                ).all()
            )
            if case_ids
            else []
        )
        for profile in profile_versions:
            if profile.research_run_id is not None:
                validated_profile_content(profile)
        research_runs = list(
            session.scalars(
                select(CompanyResearchRunModel)
                .where(CompanyResearchRunModel.company_id == company_id)
                .order_by(CompanyResearchRunModel.created_at.desc())
            ).all()
        )
        run_ids = [item.id for item in research_runs]
        research_tasks = (
            list(
                session.scalars(
                    select(CompanyResearchTaskModel)
                    .where(CompanyResearchTaskModel.research_run_id.in_(run_ids))
                    .order_by(
                        CompanyResearchTaskModel.research_run_id,
                        CompanyResearchTaskModel.stage_order,
                    )
                ).all()
            )
            if run_ids
            else []
        )
        research_sources = (
            list(
                session.scalars(
                    select(CompanyResearchSourceModel)
                    .where(CompanyResearchSourceModel.research_run_id.in_(run_ids))
                    .order_by(CompanyResearchSourceModel.created_at)
                ).all()
            )
            if run_ids
            else []
        )
        research_claims = (
            list(
                session.scalars(
                    select(CompanyResearchClaimModel)
                    .where(CompanyResearchClaimModel.research_run_id.in_(run_ids))
                    .order_by(
                        CompanyResearchClaimModel.category,
                        CompanyResearchClaimModel.created_at,
                    )
                ).all()
            )
            if run_ids
            else []
        )
        tasks_by_run: defaultdict[str, list[CompanyResearchTaskModel]] = defaultdict(list)
        sources_by_run: defaultdict[str, list[CompanyResearchSourceModel]] = defaultdict(list)
        claims_by_run: defaultdict[str, list[CompanyResearchClaimModel]] = defaultdict(list)
        for task in research_tasks:
            tasks_by_run[task.research_run_id].append(task)
        for source in research_sources:
            sources_by_run[source.research_run_id].append(source)
        for claim in research_claims:
            claims_by_run[claim.research_run_id].append(claim)
        if any(
            identifier_states[item.id] == IdentityCandidateStatus.PENDING.value
            for item in identifiers
        ):
            next_action = "Review exact identifier"
            next_detail = "A structurally valid identifier is still a submitted claim."
        elif any(item.status == "pending" for item in domains):
            next_action = "Review domain claim"
            next_detail = "The website remains self-asserted until a named decision."
        elif any(
            identifier_states[item.id] == IdentityCandidateStatus.REJECTED.value
            for item in identifiers
        ):
            next_action = "Identifier rejected"
            next_detail = "Provide a new exact identity claim; the rejected claim is closed."
        elif company.resolution_status != "resolved":
            next_action = "Identity held"
            next_detail = "Provide exact identity evidence; do not merge by name or filename."
        elif research_runs and research_runs[0].status == "pending_review":
            next_action = "Review cited deck"
            next_detail = "The bounded public research run is complete and awaits named review."
        elif research_runs and research_runs[0].status in {"pending", "running", "failed"}:
            next_action = "Advance research run"
            next_detail = (
                "Run the next persisted stage or inspect the recorded failure before retrying."
            )
        elif cases and runtime.company_research is not None:
            next_action = "Start public research"
            next_detail = "The reviewed public case is eligible for a bounded live research run."
        elif cases:
            next_action = "Offline case ready"
            next_detail = (
                "The reviewed case remains available offline. Configure both explicit "
                "live-retrieval and external-model opt-ins to enable public research."
            )
        else:
            next_action = "No research case"
            next_detail = "Record an authorised company intake before starting offline research."
        session.expunge_all()
        return {
            "company": company,
            "identifiers": identifiers,
            "domains": domains,
            "cases": cases,
            "artifacts": artifacts,
            "identifier_decisions": dict(identifier_decisions),
            "identifier_states": identifier_states,
            "identifier_candidates": identifier_candidates,
            "domain_decisions": dict(domain_decisions),
            "profile_versions": profile_versions,
            "research_runs": research_runs,
            "tasks_by_run": dict(tasks_by_run),
            "sources_by_run": dict(sources_by_run),
            "claims_by_run": dict(claims_by_run),
            "research_sources": research_sources,
            "company_research_enabled": runtime.company_research is not None,
            "next_action": next_action,
            "next_detail": next_detail,
        }


def _run_dashboard_view(runtime: Runtime, run_id: str) -> dict[str, Any]:
    with runtime.session_factory() as session:
        run = session.get(WorkflowRunModel, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Unknown run ID.")
        raw = session.scalar(
            select(RawSubmissionModel)
            .where(RawSubmissionModel.dataset_id == run.dataset_id)
            .options(joinedload(RawSubmissionModel.reporting_period))
        )
        if raw is None:
            raise HTTPException(status_code=404, detail="Run dataset is unavailable.")
        agent_runs = list(
            session.scalars(
                select(AgentRunModel)
                .where(AgentRunModel.run_id == run_id)
                .order_by(AgentRunModel.started_at)
            ).all()
        )
        report = session.scalar(select(ReportModel).where(ReportModel.run_id == run_id))
        identity_candidates = list(
            session.scalars(
                select(IdentityCandidateModel)
                .where(
                    IdentityCandidateModel.raw_submission_id == raw.id,
                    IdentityCandidateModel.status == "pending",
                )
                .order_by(IdentityCandidateModel.created_at)
            ).all()
        )
        claims = list(
            session.scalars(
                select(ClaimModel)
                .where(ClaimModel.run_id == run_id)
                .options(
                    joinedload(ClaimModel.company),
                    joinedload(ClaimModel.metric_definition),
                )
            ).all()
        )
        quality_findings = list(
            session.scalars(
                select(QualityViolationModel)
                .where(QualityViolationModel.run_id == run_id)
                .order_by(QualityViolationModel.created_at)
            ).all()
        )
        source_snapshots = list(
            session.scalars(
                select(SourceSnapshotModel)
                .join(
                    run_source_snapshots,
                    run_source_snapshots.c.source_snapshot_id == SourceSnapshotModel.id,
                )
                .where(run_source_snapshots.c.run_id == run_id)
            ).all()
        )
        evidence_items = list(
            session.scalars(
                select(EvidenceItemModel)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(run_evidence.c.run_id == run_id)
            ).all()
        )
        company_ids = {finding.company_id for finding in quality_findings if finding.company_id}
        metric_ids = {
            finding.metric_definition_id
            for finding in quality_findings
            if finding.metric_definition_id
        }
        company_names = {
            company.id: company.canonical_name
            for company in session.scalars(
                select(CompanyModel).where(CompanyModel.id.in_(company_ids))
            ).all()
        }
        metric_keys = {
            metric.id: metric.key
            for metric in session.scalars(
                select(MetricDefinitionModel).where(MetricDefinitionModel.id.in_(metric_ids))
            ).all()
        }

        extraction_attempts = list(
            session.scalars(
                select(ExtractionAttemptModel).where(ExtractionAttemptModel.run_id == run_id)
            ).all()
        )
        source_definitions = list(session.scalars(select(SourceDefinitionModel)).all())

        verification_counts = Counter(claim.verification_status for claim in claims)
        quality_counts = Counter(finding.disposition for finding in quality_findings)
        collection_counts = Counter(snapshot.status for snapshot in source_snapshots)
        evidence_source_counts = Counter(item.source_type for item in evidence_items)
        evidence_classification_counts = Counter(item.classification for item in evidence_items)

        connector_usage: dict[tuple[str, str], ConnectorUsage] = {}
        for item in evidence_items:
            key = (item.connector, item.connector_version)
            current = connector_usage.get(key)
            connector_usage[key] = ConnectorUsage(
                connector=item.connector,
                version=item.connector_version,
                publisher=item.publisher or (current.publisher if current else None),
                source_type=item.source_type,
                item_count=(current.item_count if current else 0) + 1,
                untrusted_count=(current.untrusted_count if current else 0)
                + int(item.is_untrusted),
                stale_count=(current.stale_count if current else 0) + int(item.is_stale),
            )
        snapshot_statuses: dict[str, Counter[str]] = {
            definition.key: Counter() for definition in source_definitions
        }
        for snapshot in source_snapshots:
            snapshot_statuses.setdefault(snapshot.source_key, Counter())[snapshot.status] += 1
        definition_by_key = {definition.key: definition for definition in source_definitions}
        snapshot_usage = tuple(
            SnapshotUsage(
                source_key=source_key,
                version=(
                    definition_by_key[source_key].version
                    if source_key in definition_by_key
                    else "not recorded"
                ),
                publisher=(
                    definition_by_key[source_key].publisher
                    if source_key in definition_by_key
                    else None
                ),
                status_counts=dict(sorted(counts.items())),
            )
            for source_key, counts in sorted(snapshot_statuses.items())
        )
        attempt_usage: dict[tuple[str, str | None], AttemptUsage] = {}
        for attempt in extraction_attempts:
            attempt_key = (attempt.provider, attempt.model)
            attempt_seen = attempt_usage.get(attempt_key)
            attempt_counts: Counter[str] = Counter(
                attempt_seen.status_counts if attempt_seen else {}
            )
            attempt_counts[attempt.status] += 1
            attempt_usage[attempt_key] = AttemptUsage(
                provider=attempt.provider,
                model=attempt.model,
                status_counts=dict(sorted(attempt_counts.items())),
                max_attempt_number=max(
                    attempt.attempt_number, attempt_seen.max_attempt_number if attempt_seen else 0
                ),
                escalation_count=(attempt_seen.escalation_count if attempt_seen else 0)
                + int(bool(attempt.escalation_cause)),
                duration_ms=(attempt_seen.duration_ms if attempt_seen else 0)
                + (attempt.duration_ms or 0),
            )
        services = build_service_calls(
            evidence_connectors=tuple(connector_usage.values()),
            source_snapshots=snapshot_usage,
            extraction_attempts=tuple(attempt_usage.values()),
        )

        stages = build_stage_views(run, agent_runs, report=report, services=services)
        exceptions: list[ExceptionEntry] = []
        exceptions.extend(
            ExceptionEntry(
                "hold",
                "Resolve identity",
                candidate.submitted_name,
                humanize(candidate.reason_code),
                "Identity decision pending",
                "Record a named accept or reject decision with rationale on the work queue.",
            )
            for candidate in identity_candidates
        )
        for finding in quality_findings:
            if finding.disposition not in {
                QualityDisposition.HOLD.value,
                QualityDisposition.EXCLUDE.value,
            }:
                continue
            subject_parts = [
                (
                    company_names.get(finding.company_id, "Company not recorded")
                    if finding.company_id is not None
                    else "Company not recorded"
                ),
                (
                    metric_keys.get(finding.metric_definition_id, "Metric not recorded")
                    if finding.metric_definition_id is not None
                    else "Metric not recorded"
                ),
            ]
            exceptions.append(
                ExceptionEntry(
                    "hold" if finding.disposition == QualityDisposition.HOLD.value else "danger",
                    "Verify claims",
                    " · ".join(subject_parts),
                    finding.message,
                    humanize(finding.disposition),
                    "Inspect the quality contract finding before human review.",
                )
            )
        for claim in claims:
            if claim.verification_status == VerificationStatus.SUPPORTED.value:
                continue
            exceptions.append(
                ExceptionEntry(
                    (
                        "danger"
                        if claim.verification_status
                        in {
                            VerificationStatus.CONTRADICTED.value,
                            VerificationStatus.REJECTED_UNTRUSTED.value,
                        }
                        else "warning"
                    ),
                    "Verify claims",
                    f"{claim.company.canonical_name} · {claim.metric_definition.key}",
                    f"Claim persisted as {humanize(claim.verification_status)}.",
                    humanize(claim.verification_status),
                    "Open the report provenance ledger and inspect linked evidence.",
                )
            )
        for snapshot in source_snapshots:
            if snapshot.status == CollectionStatus.SUCCEEDED.value:
                continue
            exceptions.append(
                ExceptionEntry(
                    "danger" if snapshot.status == CollectionStatus.FAILED.value else "warning",
                    "Gather evidence",
                    humanize(snapshot.source_key),
                    humanize(snapshot.error_code or snapshot.status),
                    humanize(snapshot.status),
                    "Inspect the admitted source state; do not infer unavailable evidence.",
                )
            )
        for stage in stages:
            if stage.status_key == "failed":
                exceptions.append(
                    ExceptionEntry(
                        "danger",
                        stage.label,
                        "Bounded stage",
                        stage.error_summary or "A stage failure was persisted.",
                        "Failed",
                        "Correct the recorded input or contract failure, then start a new run.",
                    )
                )
        exceptions.sort(
            key=lambda item: (
                _EXCEPTION_SEVERITY_ORDER[item.severity],
                item.stage,
                item.subject,
            )
        )
        next_action = derive_run_next_action(
            run,
            report,
            identity_hold_count=len(identity_candidates),
            exception_count=len(exceptions),
        )
        provider = run.configuration_json.get("extraction_provider")
        recorded_models = tuple(sorted({stage.model for stage in stages if stage.model}))
        finished_at = run.finished_at
        duration_ms = (
            int((finished_at - run.started_at).total_seconds() * 1000)
            if finished_at is not None
            else None
        )
        context = {
            "run": run,
            "report": report,
            "raw": raw,
            "period": raw.reporting_period,
            "stages": stages,
            "lifecycle": summarize_lifecycle(stages),
            "activity_log": build_activity_log(stages, run_started_at=run.started_at),
            "health_groups": build_health_groups(
                verification=verification_counts,
                quality=quality_counts,
                collection=collection_counts,
                evidence_sources=evidence_source_counts,
                evidence_classifications=evidence_classification_counts,
            ),
            "exceptions": tuple(exceptions),
            "next_action": next_action,
            "duration_ms": duration_ms,
            "provider": provider if isinstance(provider, str) and provider else None,
            "recorded_models": recorded_models,
        }
        session.expunge_all()
        return context


def _report_view(runtime: Runtime, report_id: str) -> dict[str, Any]:
    with runtime.session_factory() as session:
        report = session.scalar(
            select(ReportModel)
            .where(ReportModel.id == report_id)
            .options(joinedload(ReportModel.sections))
        )
        if report is None:
            raise HTTPException(status_code=404, detail="Unknown report ID.")
        run = session.get(WorkflowRunModel, report.run_id)
        raw = session.scalar(
            select(RawSubmissionModel)
            .where(RawSubmissionModel.dataset_id == report.dataset_id)
            .options(joinedload(RawSubmissionModel.reporting_period))
        )
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
        source_snapshots = list(
            session.scalars(
                select(SourceSnapshotModel)
                .join(
                    run_source_snapshots,
                    run_source_snapshots.c.source_snapshot_id == SourceSnapshotModel.id,
                )
                .where(run_source_snapshots.c.run_id == report.run_id)
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
        exception_count = (
            sum(claim.verification_status != VerificationStatus.SUPPORTED.value for claim in claims)
            + sum(
                finding.disposition
                in {QualityDisposition.HOLD.value, QualityDisposition.EXCLUDE.value}
                for finding in quality_findings
            )
            + sum(
                snapshot.status != CollectionStatus.SUCCEEDED.value for snapshot in source_snapshots
            )
        )
        health_groups = build_health_groups(
            verification=Counter(claim.verification_status for claim in claims),
            quality=Counter(item.disposition for item in quality_findings),
            collection=Counter(item.status for item in source_snapshots),
            evidence_sources=Counter(item.source_type for item in evidence_items),
            evidence_classifications=Counter(item.classification for item in evidence_items),
        )
        latest_approval = next(
            (
                decision
                for decision in decisions
                if decision.decision == "approve" and decision.report_version == report.version
            ),
            None,
        )
        session.expunge_all()
        return {
            "report": report,
            "run": run,
            "raw": raw,
            "period": raw.reporting_period if raw is not None else None,
            "sections": sections,
            "claims": claims,
            "decisions": decisions,
            "quality_findings": quality_findings,
            "events": events,
            "temporal_by_evidence": temporal_by_evidence,
            "visual_summary": visual_summary,
            "health_groups": health_groups,
            "exception_count": exception_count,
            "next_action": derive_report_next_action(report, exception_count=exception_count),
            "latest_approval": latest_approval,
        }


def create_app(
    runtime: Runtime | None = None, *, allow_container_network_clients: bool = False
) -> FastAPI:
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
        if (
            not _client_is_allowed(
                client_host,
                allow_container_network_clients=allow_container_network_clients,
            )
            or host_header not in ALLOWED_HOST_HEADERS
        ):
            return PlainTextResponse("Local loopback access only.", status_code=403)
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
            "form-action 'self'; frame-ancestors 'none'"
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
            "short_id": short_identifier,
            "humanize": humanize,
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
    @app.exception_handler(CompanyIntakeValidationError)
    @app.exception_handler(CompanyResearchError)
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
        return {
            "status": "ok",
            "external_llm": "enabled"
            if selected.company_research is not None
            else "disabled-by-default",
        }

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
            report_by_run = {report.run_id: report for report in reports}
            recent_work: list[WorkItem] = []
            for run in runs:
                linked_report = report_by_run.get(run.id)
                action_label, href = derive_work_item_action(run, linked_report)
                recent_work.append(
                    WorkItem(
                        occurred_at=run.started_at,
                        kind="Workflow run",
                        title=f"Run {short_identifier(run.id)}",
                        status=run.status,
                        context=f"Current stage: {humanize(run.stage)}",
                        action_label=action_label,
                        href=href,
                    )
                )
            recent_work.extend(
                WorkItem(
                    occurred_at=report.generated_at,
                    kind="Report",
                    title=report.title,
                    status=report.status,
                    context=f"Version {report.version}",
                    action_label=(
                        "Continue to report review"
                        if report.status == ReportStatus.PENDING_REVIEW.value
                        else "Open report record"
                    ),
                    href=f"/reports/{report.id}",
                )
                for report in reports
            )
            recent_work.sort(key=lambda item: item.occurred_at, reverse=True)
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
                    "recent_work": tuple(recent_work[:30]),
                    "external_model_state": (
                        "Explicit opt-in enabled"
                        if selected.settings.allow_external_llm
                        else "Disabled; deterministic local path"
                    ),
                }
            ),
        )

    @app.get("/companies", response_class=HTMLResponse)
    def companies(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="companies.html",
            context=template_context(_companies_view(selected)),
        )

    @app.get("/companies/{company_id}", response_class=HTMLResponse)
    def company_detail(request: Request, company_id: str) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="company.html",
            context=template_context(_company_view(selected, company_id)),
        )

    @app.post("/company-intakes")
    async def create_company_intake(
        request: Request,
        csrf_token: Annotated[str, Form()] = "",
        intake_mode: Annotated[str, Form()] = "single",
        purpose: Annotated[str, Form()] = "",
        classification: Annotated[str, Form()] = DataClassification.RESTRICTED.value,
        companies_house_number: Annotated[str, Form()] = "",
        website: Annotated[str, Form()] = "",
        company_name: Annotated[str, Form()] = "",
        jurisdiction: Annotated[str, Form()] = "",
        file: Annotated[UploadFile | None, File()] = None,
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        try:
            selected_classification = DataClassification(classification)
        except ValueError as exc:
            raise CompanyIntakeValidationError("Unsupported data classification.") from exc
        actor = reviewer_identity()
        payload = None
        if file is not None and file.filename:
            payload = await file.read(MAX_INTAKE_BYTES + 1)
            if len(payload) > MAX_INTAKE_BYTES:
                raise CompanyIntakeValidationError(
                    "Upload exceeds the 20 MiB local prototype limit."
                )
        if intake_mode == "bulk":
            if payload is None or file is None or not file.filename:
                raise CompanyIntakeValidationError("Bulk intake requires a CSV or XLSX file.")
            selected.intakes.create_bulk(
                payload,
                filename=file.filename,
                actor=actor,
                purpose=purpose,
                classification=selected_classification,
            )
            return RedirectResponse(url="/companies", status_code=303)
        if intake_mode != "single":
            raise CompanyIntakeValidationError("Unknown company intake mode.")
        result = selected.intakes.create(
            CompanyIntakeRequest(
                actor=actor,
                purpose=purpose,
                classification=selected_classification,
                companies_house_number=companies_house_number or None,
                website=website or None,
                company_name=company_name or None,
                jurisdiction=jurisdiction or None,
                document_bytes=payload,
                document_filename=file.filename
                if payload is not None and file is not None
                else None,
                declared_mime=file.content_type
                if payload is not None and file is not None
                else None,
            )
        )
        return RedirectResponse(url=f"/companies/{result.company_id}", status_code=303)

    @app.post("/company-identifiers/{identifier_id}/decide")
    def decide_company_identifier(
        request: Request,
        identifier_id: str,
        decision: Annotated[str, Form()],
        reason: Annotated[str, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        with selected.session_factory() as session:
            identifier = session.get(CompanyIdentifierModel, identifier_id)
            if identifier is None:
                raise HTTPException(status_code=404, detail="Unknown company identifier.")
            company_id = identifier.company_id
        try:
            selected_decision = IdentityDecisionType(decision)
        except ValueError as exc:
            raise CompanyIntakeValidationError("Unknown identifier decision.") from exc
        selected.intakes.decide_identifier(
            identifier_id=identifier_id,
            decision=selected_decision,
            actor=reviewer_identity(),
            reason=reason,
        )
        return RedirectResponse(url=f"/companies/{company_id}", status_code=303)

    @app.post("/company-domains/{domain_id}/decide")
    def decide_company_domain(
        request: Request,
        domain_id: str,
        decision: Annotated[str, Form()],
        reason: Annotated[str, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        with selected.session_factory() as session:
            domain = session.get(CompanyDomainModel, domain_id)
            if domain is None:
                raise HTTPException(status_code=404, detail="Unknown company domain.")
            company_id = domain.company_id
        try:
            selected_decision = IdentityDecisionType(decision)
        except ValueError as exc:
            raise CompanyIntakeValidationError("Unknown domain decision.") from exc
        selected.intakes.decide_domain(
            domain_id=domain_id,
            decision=selected_decision,
            actor=reviewer_identity(),
            reason=reason,
        )
        return RedirectResponse(url=f"/companies/{company_id}", status_code=303)

    @app.post("/research-cases/{research_case_id}/runs")
    def start_company_research(
        request: Request,
        research_case_id: str,
        csrf_token: Annotated[str, Form()] = "",
        reporting_cutoff: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        if selected.company_research is None:
            raise CompanyResearchError("Live company research is disabled.")
        cutoff = date.today()
        if reporting_cutoff.strip():
            try:
                cutoff = date.fromisoformat(reporting_cutoff.strip())
            except ValueError as exc:
                raise CompanyResearchError("Research cutoff must use YYYY-MM-DD.") from exc
        run = selected.company_research.start(
            research_case_id,
            actor=reviewer_identity(),
            cutoff=cutoff,
        )
        with selected.session_factory() as session:
            persisted_case = session.get(ResearchCaseModel, research_case_id)
            if persisted_case is None:
                raise CompanyResearchError("Research case is unavailable.")
            company_id = persisted_case.company_id
        return RedirectResponse(
            url=f"/companies/{company_id}#research-run-{run.id}", status_code=303
        )

    @app.post("/company-research-runs/{run_id}/advance")
    def advance_company_research(
        request: Request,
        run_id: str,
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        if selected.company_research is None:
            raise CompanyResearchError("Live company research is disabled.")
        with selected.session_factory() as session:
            run = session.get(CompanyResearchRunModel, run_id)
            if run is None:
                raise CompanyResearchError("Unknown company research run.")
            company_id = run.company_id
        selected.company_research.advance(run_id)
        return RedirectResponse(
            url=f"/companies/{company_id}#research-run-{run_id}", status_code=303
        )

    @app.post("/company-research-runs/{run_id}/cancel")
    def cancel_company_research(
        request: Request,
        run_id: str,
        reason: Annotated[str, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        if selected.company_research is None:
            raise CompanyResearchError("Live company research is disabled.")
        with selected.session_factory() as session:
            run = session.get(CompanyResearchRunModel, run_id)
            if run is None:
                raise CompanyResearchError("Unknown company research run.")
            company_id = run.company_id
        selected.company_research.cancel(run_id, actor=reviewer_identity(), reason=reason)
        return RedirectResponse(
            url=f"/companies/{company_id}#research-run-{run_id}", status_code=303
        )

    @app.post("/company-research-runs/{run_id}/recover")
    def recover_company_research(
        request: Request,
        run_id: str,
        reason: Annotated[str, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        if selected.company_research is None:
            raise CompanyResearchError("Live company research is disabled.")
        with selected.session_factory() as session:
            run = session.get(CompanyResearchRunModel, run_id)
            if run is None:
                raise CompanyResearchError("Unknown company research run.")
            company_id = run.company_id
        selected.company_research.recover_interrupted(
            run_id,
            actor=reviewer_identity(),
            reason=reason,
        )
        return RedirectResponse(
            url=f"/companies/{company_id}#research-run-{run_id}", status_code=303
        )

    @app.post("/profile-versions/{profile_id}/decide")
    def decide_company_profile(
        request: Request,
        profile_id: str,
        decision: Annotated[str, Form()],
        reason: Annotated[str, Form()],
        expected_lock_version: Annotated[int, Form()],
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        if selected.company_research is None:
            raise CompanyResearchError("Live company research is disabled.")
        if decision not in {"approve", "reject"}:
            raise CompanyResearchError("Unknown profile decision.")
        with selected.session_factory() as session:
            profile = session.get(ProfileVersionModel, profile_id)
            if profile is None:
                raise CompanyResearchError("Unknown profile version.")
            case = session.get(ResearchCaseModel, profile.research_case_id)
            if case is None:
                raise CompanyResearchError("Profile research case is unavailable.")
            company_id = case.company_id
        selected.company_research.review_profile(
            profile_id,
            approve=decision == "approve",
            actor=reviewer_identity(),
            reason=reason,
            expected_lock_version=expected_lock_version,
        )
        return RedirectResponse(url=f"/companies/{company_id}#research-state", status_code=303)

    @app.get("/profile-versions/{profile_id}/deck/{format_name}", response_model=None)
    def download_company_profile(
        profile_id: str, format_name: str
    ) -> HTMLResponse | PlainTextResponse:
        if selected.company_research is None:
            raise CompanyResearchError("Live company research is disabled.")
        profile = selected.company_research.validated_profile(profile_id, require_approved=True)
        content = validated_profile_content(profile, require_approved=True)
        if format_name == "json":
            payload = json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
            response: HTMLResponse | PlainTextResponse = PlainTextResponse(
                payload, media_type="application/json"
            )
        elif format_name == "html":
            response = HTMLResponse(profile_deck_html(profile))
        else:
            raise HTTPException(status_code=404, detail="Unknown company deck format.")
        response.headers["Content-Disposition"] = (
            f'attachment; filename="company-deck-{profile_id}.{format_name}"'
        )
        return response

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
        return templates.TemplateResponse(
            request=request,
            name="run.html",
            context=template_context(_run_dashboard_view(selected, run_id)),
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
        return_company_id: Annotated[str, Form()] = "",
        csrf_token: Annotated[str, Form()] = "",
    ) -> RedirectResponse:
        require_csrf(request, csrf_token)
        try:
            selected_decision = IdentityDecisionType(decision)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Unknown identity decision.") from exc
        redirect_url = "/"
        try:
            with selected.session_factory.begin() as session:
                candidate = session.get(IdentityCandidateModel, candidate_id)
                if candidate is None:
                    raise HTTPException(status_code=404, detail="Unknown identity candidate.")
                clean_return_company_id = return_company_id.strip()
                allowed_company_ids = {
                    candidate.imported_company_id,
                    candidate.candidate_company_id,
                }
                if clean_return_company_id:
                    if clean_return_company_id not in allowed_company_ids:
                        raise HTTPException(
                            status_code=422, detail="Invalid identity return target."
                        )
                    redirect_url = f"/companies/{clean_return_company_id}"
                decide_identity_candidate(
                    session,
                    candidate_id=candidate_id,
                    decision=selected_decision,
                    actor=reviewer_identity(),
                    reason=reason,
                    company_id=company_id.strip() or None,
                )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return RedirectResponse(url=redirect_url, status_code=303)

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

    app.include_router(
        create_api_router(
            selected,
            csrf_token=app.state.csrf_token,
            csrf_cookie=CSRF_COOKIE,
        )
    )

    return app
