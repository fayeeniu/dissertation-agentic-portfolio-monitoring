from __future__ import annotations

import json
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from portfolio_agent.bootstrap import Runtime, project_root
from portfolio_agent.connectors.base import SourceRequest
from portfolio_agent.connectors.registry import SourceRegistry
from portfolio_agent.connectors.ukri import UkriConnector
from portfolio_agent.enums import CollectionStatus, DataClassification, IdentifierScheme
from portfolio_agent.events import lifecycle_coverage, persist_private_funding_events
from portfolio_agent.models import (
    CompanyEventModel,
    CompanyIdentifierModel,
    CompanyModel,
    ObservationModel,
    RawSubmissionModel,
)


def _request(
    company_id: str,
    organisation_id: str = "SYN-UKRI-ORG-001",
    *,
    programme_start_date: date | None = None,
    reporting_cutoff: date = date(2025, 6, 30),
) -> SourceRequest:
    return SourceRequest(
        source_key="ukri_gtr",
        company_id=company_id,
        identifier_scheme=IdentifierScheme.UKRI_ORGANISATION_ID,
        identifier_value=organisation_id,
        reporting_cutoff=reporting_cutoff,
        programme_start_date=programme_start_date,
    )


def test_ukri_lifecycle_uses_latest_correction_and_preserves_missing_amount(
    runtime: Runtime,
) -> None:
    connector = UkriConnector(project_root() / "fixtures" / "evidence" / "ukri_synthetic.json")
    with runtime.session_factory.begin() as session:
        company = CompanyModel(
            canonical_name="Source Synthetic Ltd",
            normalized_name="source synthetic ltd",
            external_id="SYN-UKRI-ORG-001",
            resolution_status="resolved",
            classification="synthetic",
        )
        session.add(company)
        session.flush()
        session.add(
            CompanyIdentifierModel(
                company_id=company.id,
                scheme=IdentifierScheme.UKRI_ORGANISATION_ID.value,
                value="SYN-UKRI-ORG-001",
                normalized_value="SYN-UKRI-ORG-001",
                source_key="ukri_gtr",
                reviewed=True,
            )
        )
        company_id = company.id

    collection = connector.collect_source(_request(company_id))
    assert collection.status is CollectionStatus.SUCCEEDED
    project_ids = next(
        fact.value for fact in collection.facts if fact.fact_key == "ukri_project_ids"
    )
    assert project_ids == ["SYN-PROJECT-001", "SYN-PROJECT-002"]
    assert (
        next(
            fact.value for fact in collection.facts if fact.fact_key == "ukri_awards_missing_amount"
        )
        == 1
    )
    assert (
        next(
            fact.value
            for fact in collection.facts
            if fact.fact_key == "ukri_total_explicit_award_amount"
        )
        == "125000"
    )
    total_fact = next(
        fact for fact in collection.facts if fact.fact_key == "ukri_total_explicit_award_amount"
    )
    assert total_fact.metric_key is None
    assert total_fact.period_start is None
    assert total_fact.structured_locator["award_date_through"] == "2025-06-30"
    event_ids = {event.public_identifier for event in collection.events}
    assert "SYN-FUTURE-OUTCOME" not in event_ids
    assert "SYN-FUTURE-PROJECT" not in event_ids
    assert all(
        event.details is None or event.details.get("causal_attribution") is False
        for event in collection.events
    )
    coverage = lifecycle_coverage(tuple(event.lifecycle_stage for event in collection.events))
    assert coverage.completeness == 1.0

    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "source-snapshots",
        (connector,),
    )
    persisted = registry.collect(_request(company_id))
    assert persisted.event_count == len(collection.events)


def test_ukri_cumulative_metric_uses_explicit_programme_window(runtime: Runtime) -> None:
    connector = UkriConnector(project_root() / "fixtures" / "evidence" / "ukri_synthetic.json")
    collection = connector.collect_source(
        _request("co_window", programme_start_date=date(2025, 1, 1))
    )
    total = next(
        fact for fact in collection.facts if fact.fact_key == "ukri_total_explicit_award_amount"
    )
    missing = next(
        fact.value for fact in collection.facts if fact.fact_key == "ukri_awards_missing_amount"
    )
    assert total.value == "0"
    missing_state = next(
        fact.value for fact in collection.facts if fact.fact_key == "ukri_award_total_missing_state"
    )
    assert total.metric_key is None
    assert total.period_start == date(2025, 1, 1)
    assert total.period_end == date(2025, 6, 30)
    assert missing == 1
    assert missing_state == "not_reported"


def test_ukri_complete_gbp_window_is_metric_bound_but_non_gbp_window_abstains(
    runtime: Runtime,
) -> None:
    connector = UkriConnector(project_root() / "fixtures" / "evidence" / "ukri_synthetic.json")
    complete = connector.collect_source(
        _request(
            "co_complete",
            "SYN-UKRI-ORG-COMPLETE",
            programme_start_date=date(2024, 10, 1),
        )
    )
    complete_total = next(
        fact for fact in complete.facts if fact.fact_key == "ukri_total_explicit_award_amount"
    )
    assert complete_total.value == "125000"
    assert complete_total.metric_key == "grant_funding"
    assert not any(fact.fact_key.endswith("_missing_state") for fact in complete.facts)

    non_gbp = connector.collect_source(
        _request(
            "co_non_gbp",
            "SYN-UKRI-ORG-NONGBP",
            programme_start_date=date(2025, 1, 1),
        )
    )
    non_gbp_total = next(
        fact for fact in non_gbp.facts if fact.fact_key == "ukri_total_explicit_award_amount"
    )
    assert non_gbp_total.value == "0"
    assert non_gbp_total.metric_key is None
    assert next(fact.value for fact in non_gbp.facts if fact.fact_key == "ukri_awards_non_gbp") == 1
    assert (
        next(
            fact.value
            for fact in non_gbp.facts
            if fact.fact_key == "ukri_award_total_missing_state"
        )
        == "not_applicable"
    )


def test_ukri_later_cutoff_snapshot_replays_with_stable_event_locators(
    runtime: Runtime,
) -> None:
    connector = UkriConnector(project_root() / "fixtures" / "evidence" / "ukri_synthetic.json")
    with runtime.session_factory.begin() as session:
        company = CompanyModel(
            canonical_name="UKRI Replay Synthetic Ltd",
            normalized_name="ukri replay synthetic ltd",
            external_id="SYN-UKRI-ORG-001",
            resolution_status="resolved",
            classification="synthetic",
        )
        session.add(company)
        session.flush()
        session.add(
            CompanyIdentifierModel(
                company_id=company.id,
                scheme=IdentifierScheme.UKRI_ORGANISATION_ID.value,
                value="SYN-UKRI-ORG-001",
                normalized_value="SYN-UKRI-ORG-001",
                source_key="ukri_gtr",
                reviewed=True,
            )
        )
        company_id = company.id
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "ukri-cross-cutoff-replay",
        (connector,),
    )
    registry.collect(_request(company_id))
    later_request = _request(company_id, reporting_cutoff=date(2025, 12, 31))
    later = registry.collect(later_request)
    replay = registry.collect(later_request)

    assert not later.replayed
    assert replay.replayed
    assert replay.snapshot_id == later.snapshot_id


def test_ukri_requires_exact_identifier_and_reports_unmatched(runtime: Runtime) -> None:
    connector = UkriConnector(project_root() / "fixtures" / "evidence" / "ukri_synthetic.json")
    no_record = connector.collect_source(_request("co_none", "SYN-UKRI-NOT-FOUND"))
    assert no_record.status is CollectionStatus.NO_RECORD
    assert no_record.error_code == "no_exact_ukri_organisation_id"
    assert no_record.classification is DataClassification.SYNTHETIC

    wrong_scheme = SourceRequest(
        source_key="ukri_gtr",
        company_id="co_wrong",
        identifier_scheme=IdentifierScheme.LEGACY,
        identifier_value="Source Synthetic Ltd",
        reporting_cutoff=date(2025, 6, 30),
    )
    with pytest.raises(ValueError, match="exact UKRI"):
        connector.collect_source(wrong_scheme)


def test_private_funding_becomes_restricted_submission_event(runtime: Runtime) -> None:
    payload = {
        "reporting_period": {
            "label": "PRIVATE-FUNDING-2025-Q2",
            "start_date": "2025-04-01",
            "end_date": "2025-06-30",
        },
        "companies": [
            {
                "name": "Funding Synthetic Ltd",
                "external_id": "SYN-FUNDING",
                "metrics": {"private_funding": "GBP 75000"},
            }
        ],
    }
    result = runtime.importer.import_bytes(
        json.dumps(payload).encode(),
        filename="private-funding.json",
        classification=DataClassification.RESTRICTED,
    )
    with runtime.session_factory.begin() as session:
        observations = tuple(
            session.scalars(
                select(ObservationModel)
                .where(ObservationModel.raw_submission_id == result.raw_submission_id)
                .options(
                    joinedload(ObservationModel.metric_definition),
                    joinedload(ObservationModel.raw_submission).joinedload(
                        RawSubmissionModel.reporting_period
                    ),
                )
            ).all()
        )
        assert persist_private_funding_events(session, observations=observations) == 1
    with runtime.session_factory() as session:
        event = session.scalar(select(CompanyEventModel))
        assert event is not None
        assert event.classification == DataClassification.RESTRICTED.value
        assert event.source_key == "portfolio_submission"
        assert event.details_json["causal_attribution"] is False
