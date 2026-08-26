from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from portfolio_agent.bootstrap import Runtime, project_root
from portfolio_agent.connectors.base import SourceRequest
from portfolio_agent.connectors.companies_house import CompaniesHouseConnector
from portfolio_agent.connectors.registry import SourceContractError, SourceRegistry
from portfolio_agent.enums import CollectionStatus, DataClassification, IdentifierScheme
from portfolio_agent.models import CompanyIdentifierModel, CompanyModel


def _request(company_id: str, number: str = "00000001") -> SourceRequest:
    return SourceRequest(
        source_key="companies_house",
        company_id=company_id,
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value=number,
        reporting_cutoff=date(2025, 6, 30),
    )


def test_companies_house_exact_replay_preserves_dates_and_expected_missingness(
    runtime: Runtime,
) -> None:
    connector = CompaniesHouseConnector(
        local_snapshot_path=(
            project_root() / "fixtures" / "evidence" / "companies_house_synthetic.json"
        )
    )
    with runtime.session_factory.begin() as session:
        company = CompanyModel(
            canonical_name="Source Synthetic Ltd",
            normalized_name="source synthetic ltd",
            external_id="00000001",
            resolution_status="resolved",
            classification="synthetic",
        )
        session.add(company)
        session.flush()
        session.add(
            CompanyIdentifierModel(
                company_id=company.id,
                scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER.value,
                value="00000001",
                normalized_value="00000001",
                source_key="companies_house",
                reviewed=True,
            )
        )
        company_id = company.id

    collection = connector.collect_source(_request(company_id))
    assert collection.status is CollectionStatus.SUCCEEDED
    fact_keys = {fact.fact_key for fact in collection.facts}
    assert "accounts_missing_state" in fact_keys
    assert (
        next(fact.value for fact in collection.facts if fact.fact_key == "accounts_missing_state")
        == "filing_not_due"
    )
    assert not {"valuation", "private_funding", "dilution"} & fact_keys
    company_name_fact = next(fact for fact in collection.facts if fact.fact_key == "company_name")
    assert company_name_fact.structured_locator == {
        "format": "json_pointer",
        "pointer": "/records/0/company_name",
    }
    assert company_name_fact.extraction_schema_version == "companies-house-source-fact-v3"
    assert connector.manifest.version == "1.4.0"
    event_ids = {event.public_identifier for event in collection.events}
    assert "SYN-FILING-001" in event_ids
    assert "SYN-FUTURE-FILING" not in event_ids
    assert all(
        event.event_date is None or event.event_date <= date(2025, 6, 30)
        for event in collection.events
    )

    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "source-snapshots",
        (connector,),
    )
    persisted = registry.collect(_request(company_id))
    assert persisted.fact_count == len(collection.facts)
    assert persisted.event_count == len(collection.events)


def test_companies_house_no_record_invalid_id_and_live_gate(runtime: Runtime) -> None:
    connector = CompaniesHouseConnector(
        local_snapshot_path=(
            project_root() / "fixtures" / "evidence" / "companies_house_synthetic.json"
        )
    )
    no_record = connector.collect_source(_request("co_missing", "00000999"))
    assert no_record.status is CollectionStatus.NO_RECORD
    assert no_record.classification is DataClassification.SYNTHETIC

    with pytest.raises(ValueError, match="validation"):
        connector.collect_source(_request("co_invalid", "INVALID"))

    live_request = SourceRequest(
        source_key="companies_house",
        company_id="co_live",
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
        mode="read_only_api",
    )
    with pytest.raises(ValueError, match="disabled"):
        connector.collect_source(live_request)


def test_public_offline_snapshot_no_record_cannot_be_mislabeled_or_persisted(
    runtime: Runtime, tmp_path: Path
) -> None:
    source = project_root() / "fixtures" / "evidence" / "companies_house_synthetic.json"
    document = json.loads(source.read_text(encoding="utf-8"))
    document["classification"] = "public"
    public_snapshot = tmp_path / "public-companies-house.json"
    public_snapshot.write_text(json.dumps(document), encoding="utf-8")
    connector = CompaniesHouseConnector(local_snapshot_path=public_snapshot)
    with runtime.session_factory.begin() as session:
        company = CompanyModel(
            canonical_name="Held Public Source Synthetic Ltd",
            normalized_name="held public source synthetic ltd",
            external_id="00000999",
            resolution_status="resolved",
            classification="synthetic",
        )
        session.add(company)
        session.flush()
        session.add(
            CompanyIdentifierModel(
                company_id=company.id,
                scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER.value,
                value="00000999",
                normalized_value="00000999",
                source_key="companies_house",
                reviewed=True,
            )
        )
        company_id = company.id

    collection = connector.collect_source(_request(company_id, "00000999"))
    assert collection.status is CollectionStatus.NO_RECORD
    assert collection.classification is DataClassification.PUBLIC
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "held-public-company-house",
        (connector,),
    )
    with pytest.raises(SourceContractError, match="held until"):
        registry.collect(_request(company_id, "00000999"))
