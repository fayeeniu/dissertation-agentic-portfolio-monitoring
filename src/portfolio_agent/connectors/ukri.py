from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict

from portfolio_agent.enums import CollectionStatus, DataClassification, EventType, IdentifierScheme
from portfolio_agent.events import lifecycle_coverage

from .base import (
    CollectedEvent,
    CollectedFact,
    SourceCapabilityManifest,
    SourceCollection,
    SourceFactContract,
    SourceRequest,
)


class _Opportunity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: str
    title: str
    opened_at: date | None = None


class _Outcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome_id: str
    title: str
    published_at: date


class _Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    record_version: int
    updated_at: datetime
    application_id: str | None = None
    decision_id: str | None = None
    decision_date: date | None = None
    award_id: str | None = None
    award_date: date | None = None
    title: str
    funder: str
    organisation_role: str
    start_date: date | None = None
    end_date: date | None = None
    amount: str | None = None
    currency: str | None = None
    opportunity: _Opportunity | None = None
    outcomes: tuple[_Outcome, ...] = ()


class _OrganisationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organisation_id: str
    organisation_name: str
    published_at: datetime
    projects: tuple[_Project, ...]


class _SnapshotDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    classification: Literal["synthetic", "public"]
    publisher: str
    records: tuple[_OrganisationRecord, ...]


class UkriConnector:
    manifest = SourceCapabilityManifest(
        key="ukri_gtr",
        version="1.3.0",
        publisher="UK Research and Innovation Gateway to Research",
        identifier_schemes=(IdentifierScheme.UKRI_ORGANISATION_ID,),
        fact_contracts=tuple(
            SourceFactContract(
                fact_key=fact_key,
                metric_keys=(None, "grant_funding")
                if fact_key == "ukri_total_explicit_award_amount"
                else (None,),
                extraction_method="deterministic_json_aggregation",
                extraction_schema_version="ukri-gtr-source-fact-v2",
                unit=("currency_units" if fact_key == "ukri_total_explicit_award_amount" else None),
                currency=("GBP" if fact_key == "ukri_total_explicit_award_amount" else None),
            )
            for fact_key in (
                "ukri_project_ids",
                "ukri_award_count",
                "ukri_total_explicit_award_amount",
                "ukri_awards_missing_amount",
                "ukri_awards_non_gbp",
                "ukri_award_total_missing_state",
                "ukri_lifecycle_coverage",
            )
        ),
        event_types=(
            EventType.UKRI_OPPORTUNITY.value,
            EventType.UKRI_DECISION.value,
            EventType.UKRI_AWARD.value,
            EventType.UKRI_PROJECT.value,
            EventType.UKRI_OUTCOME.value,
        ),
        media_types=("application/json",),
        retrieval_modes=("offline_snapshot",),
        licence_reference="G2:EVIDENCE_REQUIRED",
        terms_reference="G2:EVIDENCE_REQUIRED",
        live_retrieval_admitted=False,
    )

    def __init__(self, local_snapshot_path: Path) -> None:
        self._local_snapshot_path = local_snapshot_path

    def collect_source(self, request: SourceRequest) -> SourceCollection:
        if request.identifier_scheme is not IdentifierScheme.UKRI_ORGANISATION_ID:
            raise ValueError("UKRI collection requires an exact UKRI organisation identifier.")
        if request.mode != "offline_snapshot":
            raise ValueError("Only immutable UKRI snapshot replay is enabled.")
        content = self._local_snapshot_path.read_bytes()
        document = _SnapshotDocument.model_validate_json(content)
        classification = DataClassification(document.classification)
        matches = [
            record
            for record in document.records
            if record.organisation_id == request.identifier_value.strip()
        ]
        locator = f"fixture://ukri/{request.identifier_value.strip()}"
        if not matches:
            return SourceCollection(
                status=CollectionStatus.NO_RECORD,
                locator=locator,
                retrieved_at=datetime.now(UTC),
                content=content,
                media_type="application/json",
                classification=classification,
                error_code="no_exact_ukri_organisation_id",
            )
        if len(matches) != 1:
            raise ValueError("UKRI snapshot contains duplicate organisation identifiers.")
        record = matches[0]
        projects = self._latest_project_versions(record.projects, request.reporting_cutoff)
        events = self._events(projects, locator, request.reporting_cutoff)
        facts = self._facts(
            projects,
            events,
            locator,
            record.published_at,
            request.fact_keys,
            programme_start_date=request.programme_start_date,
            reporting_cutoff=request.reporting_cutoff,
        )
        return SourceCollection(
            status=CollectionStatus.SUCCEEDED,
            locator=locator,
            retrieved_at=datetime.now(UTC),
            content=content,
            media_type="application/json",
            published_at=record.published_at,
            facts=facts,
            events=events,
            classification=classification,
        )

    @staticmethod
    def _latest_project_versions(
        projects: tuple[_Project, ...], cutoff: date
    ) -> tuple[_Project, ...]:
        by_id: dict[str, list[_Project]] = defaultdict(list)
        for project in projects:
            if project.updated_at.date() <= cutoff:
                by_id[project.project_id].append(project)
        return tuple(
            max(versions, key=lambda project: (project.record_version, project.updated_at))
            for _, versions in sorted(by_id.items())
        )

    @staticmethod
    def _events(
        projects: tuple[_Project, ...], locator: str, cutoff: date
    ) -> tuple[CollectedEvent, ...]:
        events: list[CollectedEvent] = []
        for project in projects:
            base = (
                f"{locator}#/projects/by-id/{quote(project.project_id, safe='')}"
                f"/versions/{project.record_version}"
            )
            common_details = {
                "funder": project.funder,
                "organisation_role": project.organisation_role,
                "association_basis": "exact_ukri_organisation_id",
                "causal_attribution": False,
                "record_version": project.record_version,
            }
            if (
                project.opportunity is not None
                and project.opportunity.opened_at is not None
                and project.opportunity.opened_at <= cutoff
            ):
                events.append(
                    CollectedEvent(
                        event_type=EventType.UKRI_OPPORTUNITY.value,
                        lifecycle_stage="opportunity",
                        title=project.opportunity.title,
                        source_locator=f"{base}/opportunity",
                        public_identifier=project.opportunity.opportunity_id,
                        event_date=project.opportunity.opened_at,
                        details=common_details,
                    )
                )
            if project.decision_id and project.decision_date and project.decision_date <= cutoff:
                events.append(
                    CollectedEvent(
                        event_type=EventType.UKRI_DECISION.value,
                        lifecycle_stage="decision",
                        title="UKRI decision recorded",
                        source_locator=f"{base}/decision_id",
                        public_identifier=project.decision_id,
                        event_date=project.decision_date,
                        details=common_details,
                    )
                )
            if project.award_id and project.award_date and project.award_date <= cutoff:
                events.append(
                    CollectedEvent(
                        event_type=EventType.UKRI_AWARD.value,
                        lifecycle_stage="award",
                        title="UKRI award associated with organisation",
                        source_locator=f"{base}/award_id",
                        public_identifier=project.award_id,
                        event_date=project.award_date,
                        amount=project.amount,
                        currency=project.currency,
                        details=common_details,
                    )
                )
            if project.start_date and project.start_date <= cutoff:
                events.append(
                    CollectedEvent(
                        event_type=EventType.UKRI_PROJECT.value,
                        lifecycle_stage="project",
                        title=project.title,
                        source_locator=f"{base}/project_id",
                        public_identifier=project.project_id,
                        event_date=project.start_date,
                        details={
                            **common_details,
                            "application_id": project.application_id,
                            "end_date": project.end_date.isoformat() if project.end_date else None,
                        },
                    )
                )
            events.extend(
                CollectedEvent(
                    event_type=EventType.UKRI_OUTCOME.value,
                    lifecycle_stage="outcome",
                    title=outcome.title,
                    source_locator=(f"{base}/outcomes/by-id/{quote(outcome.outcome_id, safe='')}"),
                    public_identifier=outcome.outcome_id,
                    event_date=outcome.published_at,
                    details=common_details,
                )
                for outcome in project.outcomes
                if outcome.published_at <= cutoff
            )
        return tuple(
            sorted(
                events,
                key=lambda event: (
                    event.event_date or date.min,
                    event.event_type,
                    event.public_identifier or "",
                ),
            )
        )

    @staticmethod
    def _facts(
        projects: tuple[_Project, ...],
        events: tuple[CollectedEvent, ...],
        locator: str,
        published_at: datetime,
        requested_fact_keys: tuple[str, ...],
        *,
        programme_start_date: date | None,
        reporting_cutoff: date,
    ) -> tuple[CollectedFact, ...]:
        award_projects = [
            project
            for project in projects
            if project.award_id
            and project.award_date is not None
            and project.award_date <= reporting_cutoff
            and (programme_start_date is None or project.award_date >= programme_start_date)
        ]
        explicit_amounts: list[Decimal] = []
        missing_amount_count = 0
        non_gbp_count = 0
        for project in award_projects:
            if project.amount is None:
                missing_amount_count += 1
                continue
            if project.currency != "GBP":
                non_gbp_count += 1
                continue
            amount = Decimal(project.amount)
            if not amount.is_finite():
                raise ValueError("UKRI award amounts must be finite numeric literals.")
            explicit_amounts.append(amount)
        coverage = lifecycle_coverage(tuple(event.lifecycle_stage for event in events))
        total_is_complete = missing_amount_count == 0 and non_gbp_count == 0
        values: dict[str, object] = {
            "ukri_project_ids": [project.project_id for project in projects],
            "ukri_award_count": len(award_projects),
            "ukri_total_explicit_award_amount": str(sum(explicit_amounts, Decimal("0"))),
            "ukri_awards_missing_amount": missing_amount_count,
            "ukri_awards_non_gbp": non_gbp_count,
            "ukri_lifecycle_coverage": {
                "covered_stage_count": coverage.covered_stage_count,
                "expected_stage_count": coverage.expected_stage_count,
                "completeness": coverage.completeness,
                "missing_stages": list(coverage.missing_stages),
            },
        }
        if not total_is_complete:
            values["ukri_award_total_missing_state"] = (
                "not_reported" if missing_amount_count else "not_applicable"
            )
        period_start = programme_start_date
        period_end = reporting_cutoff if programme_start_date is not None else None
        return tuple(
            CollectedFact(
                fact_key=key,
                value=value,
                source_locator=f"{locator}#/derived/{key}",
                structured_locator={
                    "format": "deterministic_json_aggregation",
                    "record_pointer": "/records/*/projects",
                    "fact_key": key,
                    "award_date_from": (
                        programme_start_date.isoformat() if programme_start_date else None
                    ),
                    "award_date_through": reporting_cutoff.isoformat(),
                },
                extraction_method="deterministic_json_aggregation",
                extraction_schema_version="ukri-gtr-source-fact-v2",
                published_at=published_at,
                period_start=period_start,
                period_end=period_end,
                unit=("currency_units" if key == "ukri_total_explicit_award_amount" else None),
                currency=("GBP" if key == "ukri_total_explicit_award_amount" else None),
                metric_key=(
                    "grant_funding"
                    if key == "ukri_total_explicit_award_amount"
                    and programme_start_date is not None
                    and total_is_complete
                    else None
                ),
            )
            for key, value in values.items()
            if not requested_fact_keys or key in requested_fact_keys
        )
