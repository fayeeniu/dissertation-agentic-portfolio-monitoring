from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from pathlib import Path
from threading import Event

import httpx
import pytest
from alembic.config import Config
from sqlalchemy import select

from alembic import command
from portfolio_agent.bootstrap import Runtime, project_root
from portfolio_agent.connectors.base import (
    CollectedEvent,
    CollectedFact,
    SourceCapabilityManifest,
    SourceCollection,
    SourceFactContract,
    SourceRequest,
)
from portfolio_agent.connectors.http_client import BoundedHttpClient, HttpPolicy
from portfolio_agent.connectors.registry import (
    SourceChecksumDriftError,
    SourceContractError,
    SourceRegistry,
)
from portfolio_agent.enums import CollectionStatus, DataClassification, IdentifierScheme
from portfolio_agent.ids import sha256_bytes
from portfolio_agent.models import (
    CompanyEventModel,
    CompanyIdentifierModel,
    CompanyModel,
    EvidenceFactModel,
    SourceDefinitionModel,
    SourceSnapshotModel,
    source_snapshot_events,
)


@dataclass
class _StaticConnector:
    content: bytes = b'{"synthetic":true}'
    calls: int = 0
    classification: DataClassification = DataClassification.SYNTHETIC
    status: CollectionStatus = CollectionStatus.SUCCEEDED
    company_status: str = "active"
    manifest = SourceCapabilityManifest(
        key="companies_house",
        version="test-1",
        publisher="Synthetic Companies House transport",
        identifier_schemes=(IdentifierScheme.COMPANIES_HOUSE_NUMBER,),
        fact_contracts=tuple(
            SourceFactContract(
                fact_key=fact_key,
                metric_keys=(None,),
                extraction_method="deterministic_json_pointer",
                extraction_schema_version="test-source-fact-v2",
            )
            for fact_key in ("company_status", "sic_codes")
        ),
        event_types=("incorporated",),
        media_types=("application/json",),
        retrieval_modes=("offline_snapshot",),
        licence_reference="repository-owned synthetic fixture",
        terms_reference="local deterministic tests only",
        admission_reviewed_at=date(2026, 8, 26),
    )

    def collect_source(self, request: SourceRequest) -> SourceCollection:
        self.calls += 1
        if self.status is not CollectionStatus.SUCCEEDED:
            return SourceCollection(
                status=self.status,
                locator=f"fixture://companies-house/{request.identifier_value}",
                retrieved_at=datetime(2025, 7, 1, tzinfo=UTC),
                content=self.content,
                media_type="application/json",
                classification=self.classification,
            )
        return SourceCollection(
            status=CollectionStatus.SUCCEEDED,
            locator=f"fixture://companies-house/{request.identifier_value}",
            retrieved_at=datetime(2025, 7, 1, tzinfo=UTC),
            published_at=datetime(2025, 6, 29, tzinfo=UTC),
            content=self.content,
            media_type="application/json",
            classification=self.classification,
            facts=(
                CollectedFact(
                    fact_key="company_status",
                    value=self.company_status,
                    source_locator="#/company_status",
                    structured_locator={
                        "format": "json_pointer",
                        "pointer": "/company_status",
                    },
                    extraction_method="deterministic_json_pointer",
                    extraction_schema_version="test-source-fact-v2",
                    published_at=datetime(2025, 6, 29, tzinfo=UTC),
                ),
                CollectedFact(
                    fact_key="sic_codes",
                    value=["62020"],
                    source_locator="#/sic_codes",
                    structured_locator={
                        "format": "json_pointer",
                        "pointer": "/sic_codes",
                    },
                    extraction_method="deterministic_json_pointer",
                    extraction_schema_version="test-source-fact-v2",
                    published_at=datetime(2025, 6, 29, tzinfo=UTC),
                ),
            ),
            events=(
                CollectedEvent(
                    event_type="incorporated",
                    title="Synthetic incorporation",
                    source_locator="#/date_of_creation",
                    public_identifier="00000001:incorporated",
                    event_date=date(2020, 1, 1),
                ),
            ),
        )


def _company(
    runtime: Runtime,
    *,
    number: str = "00000001",
    name: str = "Source Synthetic Ltd",
    reviewed: bool = True,
    source_key: str = "companies_house",
    valid_to: date | None = None,
) -> str:
    with runtime.session_factory.begin() as session:
        company = CompanyModel(
            canonical_name=name,
            normalized_name=name.casefold(),
            external_id=number,
            resolution_status="resolved",
            classification="synthetic",
        )
        session.add(company)
        session.flush()
        session.add(
            CompanyIdentifierModel(
                company_id=company.id,
                scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER.value,
                value=number,
                normalized_value=number,
                source_key=source_key,
                valid_to=valid_to,
                reviewed=reviewed,
            )
        )
        return company.id


class _ReturnedCollectionConnector:
    manifest = _StaticConnector.manifest

    def __init__(self, collection: SourceCollection) -> None:
        self.collection = collection
        self.calls = 0

    def collect_source(self, request: SourceRequest) -> SourceCollection:
        self.calls += 1
        return self.collection


def test_registry_persists_multiple_facts_and_replays_idempotently(
    runtime: Runtime,
) -> None:
    connector = _StaticConnector()
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "source-snapshots",
        (connector,),
    )
    company_id = _company(runtime)
    request = SourceRequest(
        source_key="companies_house",
        company_id=company_id,
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
        fact_keys=("company_status", "sic_codes"),
    )

    first = registry.collect(request)
    second = registry.collect(request)

    assert first.fact_count == 2
    assert first.event_count == 1
    assert not first.replayed
    assert second.replayed
    assert second.snapshot_id == first.snapshot_id
    assert connector.calls == 1
    with runtime.session_factory() as session:
        snapshots = list(session.scalars(select(SourceSnapshotModel)).all())
        facts = list(session.scalars(select(EvidenceFactModel)).all())
        definition = session.scalar(
            select(SourceDefinitionModel).where(SourceDefinitionModel.key == "companies_house")
        )
    assert len(snapshots) == 1
    assert len(facts) == 2
    assert snapshots[0].derivation_sha256 is not None
    assert snapshots[0].derivation_contract_version == "source-derivation-v2"
    assert all(fact.structured_locator_json for fact in facts)
    assert all(fact.extraction_method == "deterministic_json_pointer" for fact in facts)
    assert all(fact.extraction_schema_version == "test-source-fact-v2" for fact in facts)
    assert definition is not None and not definition.admitted


def test_registry_rejects_cross_metric_fact_binding_before_persistence(
    runtime: Runtime,
) -> None:
    connector = _ReturnedCollectionConnector(
        SourceCollection(
            status=CollectionStatus.SUCCEEDED,
            locator="fixture://companies-house/00000001",
            retrieved_at=datetime(2025, 7, 1, tzinfo=UTC),
            published_at=datetime(2025, 6, 29, tzinfo=UTC),
            content=b'{"company_status":"100"}',
            media_type="application/json",
            classification=DataClassification.SYNTHETIC,
            facts=(
                CollectedFact(
                    fact_key="company_status",
                    value="100",
                    metric_key="grant_funding",
                    source_locator="#/company_status",
                    structured_locator={
                        "format": "json_pointer",
                        "pointer": "/company_status",
                    },
                    extraction_method="deterministic_json_pointer",
                    extraction_schema_version="test-source-fact-v2",
                    published_at=datetime(2025, 6, 29, tzinfo=UTC),
                ),
            ),
        )
    )
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "cross-metric-binding",
        (connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
        programme_start_date=date(2024, 1, 1),
    )

    with pytest.raises(SourceContractError, match="metric binding"):
        registry.collect(request)
    with runtime.session_factory() as session:
        assert session.scalar(select(SourceSnapshotModel.id)) is None
        assert session.scalar(select(EvidenceFactModel.id)) is None


def test_registry_fails_closed_and_detects_same_cutoff_drift(runtime: Runtime) -> None:
    connector = _StaticConnector()
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "source-snapshots",
        (connector,),
    )
    company_id = _company(runtime)
    request = SourceRequest(
        source_key="companies_house",
        company_id=company_id,
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    registry.collect(request)
    connector.content = b'{"synthetic":"changed"}'
    with pytest.raises(SourceChecksumDriftError):
        registry.collect(request, force_refresh=True)

    bad_source = SourceRequest(
        source_key="not_admitted",
        company_id=company_id,
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    with pytest.raises(SourceContractError):
        registry.collect(bad_source)


def test_registry_detects_same_bytes_with_changed_fact_derivation(runtime: Runtime) -> None:
    connector = _StaticConnector()
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "derivation-drift",
        (connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    registry.collect(request)
    connector.company_status = "dissolved"

    with pytest.raises(SourceChecksumDriftError, match="derivation"):
        registry.collect(request, force_refresh=True)

    with runtime.session_factory() as session:
        facts = list(
            session.scalars(
                select(EvidenceFactModel).where(EvidenceFactModel.fact_key == "company_status")
            ).all()
        )
    assert [fact.value_json for fact in facts] == ["active"]


def test_registry_backfills_legacy_derivation_and_detects_persisted_fact_tampering(
    runtime: Runtime,
) -> None:
    connector = _StaticConnector()
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "legacy-derivation-backfill",
        (connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    first = registry.collect(request)
    with runtime.session_factory.begin() as session:
        snapshot = session.get(SourceSnapshotModel, first.snapshot_id)
        assert snapshot is not None
        snapshot.derivation_sha256 = None

    replay = registry.collect(request)
    assert replay.replayed
    with runtime.session_factory.begin() as session:
        snapshot = session.get(SourceSnapshotModel, first.snapshot_id)
        fact = session.scalar(
            select(EvidenceFactModel).where(
                EvidenceFactModel.source_snapshot_id == first.snapshot_id,
                EvidenceFactModel.fact_key == "company_status",
            )
        )
        assert snapshot is not None and snapshot.derivation_sha256 is not None
        assert fact is not None
        fact.value_json = "dissolved"

    with pytest.raises(SourceChecksumDriftError, match="derivation hash"):
        registry.collect(request)


def test_non_null_0006_derivation_hash_survives_0007_upgrade_and_detects_tampering(
    runtime: Runtime,
) -> None:
    connector = _StaticConnector()
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "legacy-v1-derivation",
        (connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    first = registry.collect(request)
    with runtime.session_factory.begin() as session:
        snapshot = session.get(SourceSnapshotModel, first.snapshot_id)
        assert snapshot is not None
        legacy_hash = registry._stored_derivation_hash(
            session,
            snapshot,
            contract_version="source-derivation-v1",
        )
        snapshot.derivation_sha256 = legacy_hash
        snapshot.derivation_contract_version = None

    runtime.engine.dispose()
    config = Config(str(project_root() / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", runtime.settings.database_url)
    command.downgrade(config, "0006")
    command.upgrade(config, "0007")

    replay = registry.collect(request)
    assert replay.replayed
    with runtime.session_factory.begin() as session:
        snapshot = session.get(SourceSnapshotModel, first.snapshot_id)
        fact = session.scalar(
            select(EvidenceFactModel).where(
                EvidenceFactModel.source_snapshot_id == first.snapshot_id,
                EvidenceFactModel.fact_key == "company_status",
            )
        )
        assert snapshot is not None
        assert snapshot.derivation_contract_version == "source-derivation-v1"
        assert snapshot.derivation_sha256 == legacy_hash
        assert fact is not None
        fact.value_json = "dissolved"

    with pytest.raises(SourceChecksumDriftError, match="derivation hash"):
        registry.collect(request)


def test_no_record_snapshot_is_terminal_and_idempotent(runtime: Runtime) -> None:
    connector = _StaticConnector(status=CollectionStatus.NO_RECORD)
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "no-record-snapshots",
        (connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )

    first = registry.collect(request)
    second = registry.collect(request)

    assert first.status is CollectionStatus.NO_RECORD
    assert not first.replayed
    assert second.replayed
    assert second.snapshot_id == first.snapshot_id
    assert connector.calls == 1
    with runtime.session_factory() as session:
        assert len(list(session.scalars(select(SourceSnapshotModel)).all())) == 1


def test_transient_failure_can_be_retried_without_becoming_terminal(
    runtime: Runtime,
) -> None:
    connector = _ReturnedCollectionConnector(
        SourceCollection(
            status=CollectionStatus.SOURCE_UNAVAILABLE,
            locator="fixture://companies-house/unavailable",
            retrieved_at=datetime(2025, 6, 30, tzinfo=UTC),
            classification=DataClassification.SYNTHETIC,
            error_code="synthetic_unavailable",
        )
    )
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "transient-retry",
        (connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )

    first = registry.collect(request)
    second = registry.collect(request)

    assert first.status is second.status is CollectionStatus.SOURCE_UNAVAILABLE
    assert first.snapshot_id != second.snapshot_id
    assert not first.replayed and not second.replayed
    assert connector.calls == 2


def test_registry_requires_licence_state_and_holds_unadmitted_public_content(
    runtime: Runtime,
) -> None:
    missing_licence = _StaticConnector()
    missing_licence.manifest = replace(missing_licence.manifest, licence_reference=None)
    with pytest.raises(SourceContractError, match="licence evidence"):
        SourceRegistry(
            runtime.session_factory,
            runtime.settings.raw_data_dir.parent / "missing-licence",
            (missing_licence,),
        )

    public_connector = _StaticConnector(classification=DataClassification.PUBLIC)
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "held-public",
        (public_connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    with pytest.raises(SourceContractError, match="held until"):
        registry.collect(request)
    with runtime.session_factory() as session:
        assert session.scalar(select(SourceSnapshotModel.id)) is None


def test_manifest_must_match_admitted_identifier_and_retrieval_policy(
    runtime: Runtime,
) -> None:
    wrong_identifier = _StaticConnector()
    wrong_identifier.manifest = replace(
        wrong_identifier.manifest,
        identifier_schemes=(IdentifierScheme.UKRI_ORGANISATION_ID,),
    )
    with pytest.raises(SourceContractError, match="identifier schemes"):
        SourceRegistry(
            runtime.session_factory,
            runtime.settings.raw_data_dir.parent / "wrong-manifest-identifier",
            (wrong_identifier,),
        )

    wrong_mode = _StaticConnector()
    wrong_mode.manifest = replace(wrong_mode.manifest, retrieval_modes=("bulk_scrape",))
    with pytest.raises(SourceContractError, match="retrieval modes"):
        SourceRegistry(
            runtime.session_factory,
            runtime.settings.raw_data_dir.parent / "wrong-manifest-mode",
            (wrong_mode,),
        )


def test_live_mode_is_blocked_before_connector_call_when_g2_is_open(runtime: Runtime) -> None:
    connector = _StaticConnector()
    connector.manifest = replace(
        connector.manifest,
        retrieval_modes=("offline_snapshot", "read_only_api"),
    )
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "held-live",
        (connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
        mode="read_only_api",
    )
    with pytest.raises(SourceContractError, match="Live retrieval is held"):
        registry.collect(request)
    assert connector.calls == 0


def test_registry_rejects_cross_company_unreviewed_and_expired_identifiers_before_io(
    runtime: Runtime,
) -> None:
    connector = _StaticConnector()
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "identity-boundary",
        (connector,),
    )
    first_company = _company(
        runtime,
        number="00000011",
        name="Identity Alpha Synthetic Ltd",
    )
    second_company = _company(
        runtime,
        number="00000012",
        name="Identity Beta Synthetic Ltd",
    )
    unreviewed_company = _company(
        runtime,
        number="00000013",
        name="Identity Unreviewed Synthetic Ltd",
        reviewed=False,
    )
    expired_company = _company(
        runtime,
        number="00000014",
        name="Identity Expired Synthetic Ltd",
        valid_to=date(2025, 6, 29),
    )

    invalid_requests = (
        SourceRequest(
            source_key="companies_house",
            company_id=second_company,
            identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
            identifier_value="00000011",
            reporting_cutoff=date(2025, 6, 30),
        ),
        SourceRequest(
            source_key="companies_house",
            company_id=unreviewed_company,
            identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
            identifier_value="00000013",
            reporting_cutoff=date(2025, 6, 30),
        ),
        SourceRequest(
            source_key="companies_house",
            company_id=expired_company,
            identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
            identifier_value="00000014",
            reporting_cutoff=date(2025, 6, 30),
        ),
    )
    for request in invalid_requests:
        with pytest.raises(SourceContractError):
            registry.collect(request)
    assert first_company != second_company
    assert connector.calls == 0


@pytest.mark.parametrize(
    "collection, expected",
    (
        (
            SourceCollection(
                status=CollectionStatus.SUCCEEDED,
                locator="fixture://invalid/media",
                retrieved_at=datetime(2025, 6, 30, tzinfo=UTC),
                content=b"{}",
                media_type="text/plain",
                classification=DataClassification.SYNTHETIC,
            ),
            "media type",
        ),
        (
            SourceCollection(
                status=CollectionStatus.SUCCEEDED,
                locator="fixture://invalid/fact",
                retrieved_at=datetime(2025, 6, 30, tzinfo=UTC),
                content=b"{}",
                media_type="application/json",
                facts=(CollectedFact("undeclared", "x", "#/x"),),
                classification=DataClassification.SYNTHETIC,
            ),
            "outside its manifest",
        ),
        (
            SourceCollection(
                status=CollectionStatus.SUCCEEDED,
                locator="fixture://invalid/provenance",
                retrieved_at=datetime(2025, 6, 30, tzinfo=UTC),
                content=b"{}",
                media_type="application/json",
                facts=(CollectedFact("company_status", "active", "#/status"),),
                classification=DataClassification.SYNTHETIC,
            ),
            "structured source locator",
        ),
        (
            SourceCollection(
                status=CollectionStatus.SUCCEEDED,
                locator="fixture://invalid/event",
                retrieved_at=datetime(2025, 6, 30, tzinfo=UTC),
                content=b"{}",
                media_type="application/json",
                events=(CollectedEvent("undeclared", "Bad event", "#/event"),),
                classification=DataClassification.SYNTHETIC,
            ),
            "outside its manifest",
        ),
        (
            SourceCollection(
                status=CollectionStatus.SUCCEEDED,
                locator="fixture://invalid/metric",
                retrieved_at=datetime(2025, 6, 30, tzinfo=UTC),
                content=b"{}",
                media_type="application/json",
                facts=(
                    CollectedFact(
                        "company_status",
                        "active",
                        "#/status",
                        structured_locator={
                            "format": "json_pointer",
                            "pointer": "/status",
                        },
                        extraction_method="deterministic_json_pointer",
                        extraction_schema_version="test-source-fact-v2",
                        metric_key="undeclared_metric",
                    ),
                ),
                classification=DataClassification.SYNTHETIC,
            ),
            "undeclared metric",
        ),
        (
            SourceCollection(
                status=CollectionStatus.NO_RECORD,
                locator="fixture://invalid/non-terminal-facts",
                retrieved_at=datetime(2025, 6, 30, tzinfo=UTC),
                facts=(CollectedFact("company_status", "active", "#/status"),),
                classification=DataClassification.SYNTHETIC,
            ),
            "Non-successful",
        ),
        (
            SourceCollection(
                status=CollectionStatus.SUCCEEDED,
                locator="fixture://invalid/timezone",
                retrieved_at=datetime(2025, 6, 30),
                content=b"{}",
                media_type="application/json",
                classification=DataClassification.SYNTHETIC,
            ),
            "timezone",
        ),
    ),
)
def test_registry_rejects_connector_output_outside_manifest_before_persistence(
    runtime: Runtime,
    collection: SourceCollection,
    expected: str,
) -> None:
    connector = _ReturnedCollectionConnector(collection)
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / f"invalid-response-{expected.replace(' ', '-')}",
        (connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    with pytest.raises(SourceContractError, match=expected):
        registry.collect(request)
    with runtime.session_factory() as session:
        assert session.scalar(select(SourceSnapshotModel.id)) is None


def test_cumulative_metric_fact_requires_request_programme_interval(runtime: Runtime) -> None:
    collection = SourceCollection(
        status=CollectionStatus.SUCCEEDED,
        locator="fixture://invalid/cumulative-window",
        retrieved_at=datetime(2025, 6, 30, tzinfo=UTC),
        content=b"{}",
        media_type="application/json",
        facts=(
            CollectedFact(
                fact_key="cumulative_total",
                value="100",
                source_locator="#/derived/total",
                structured_locator={"format": "json_pointer", "pointer": "/total"},
                extraction_method="deterministic_json_pointer",
                extraction_schema_version="test-source-fact-v2",
                metric_key="grant_funding",
            ),
        ),
        classification=DataClassification.SYNTHETIC,
    )
    connector = _ReturnedCollectionConnector(collection)
    connector.manifest = replace(
        connector.manifest,
        fact_contracts=(
            SourceFactContract(
                fact_key="cumulative_total",
                metric_keys=("grant_funding",),
                extraction_method="deterministic_json_pointer",
                extraction_schema_version="test-source-fact-v2",
            ),
        ),
    )
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "missing-cumulative-window",
        (connector,),
    )
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    with pytest.raises(SourceContractError, match="programme start"):
        registry.collect(request)


def test_repeated_events_are_canonical_and_linked_to_each_cutoff_snapshot(
    runtime: Runtime,
) -> None:
    class _CutoffConnector(_StaticConnector):
        def collect_source(self, request: SourceRequest) -> SourceCollection:
            self.calls += 1
            common = CollectedEvent(
                event_type="incorporated",
                title="Synthetic incorporation",
                source_locator="#/incorporated",
                public_identifier="00000001:incorporated",
                event_date=date(2020, 1, 1),
            )
            later = CollectedEvent(
                event_type="incorporated",
                title="Synthetic branch registration",
                source_locator="#/branch",
                public_identifier="00000001:branch",
                event_date=date(2025, 7, 1),
            )
            return SourceCollection(
                status=CollectionStatus.SUCCEEDED,
                locator=f"fixture://companies-house/{request.reporting_cutoff}",
                retrieved_at=datetime(2025, 7, 2, tzinfo=UTC),
                published_at=datetime(2025, 6, 29, tzinfo=UTC),
                content=f'{{"cutoff":"{request.reporting_cutoff}"}}'.encode(),
                media_type="application/json",
                events=(common, later)
                if request.reporting_cutoff >= date(2025, 7, 1)
                else (common,),
                classification=DataClassification.SYNTHETIC,
            )

    connector = _CutoffConnector()
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "cross-cutoff-events",
        (connector,),
    )
    company_id = _company(runtime)
    first = registry.collect(
        SourceRequest(
            source_key="companies_house",
            company_id=company_id,
            identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
            identifier_value="00000001",
            reporting_cutoff=date(2025, 6, 30),
        )
    )
    second = registry.collect(
        SourceRequest(
            source_key="companies_house",
            company_id=company_id,
            identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
            identifier_value="00000001",
            reporting_cutoff=date(2025, 7, 31),
        )
    )
    with runtime.session_factory() as session:
        events = list(session.scalars(select(CompanyEventModel)).all())
        links = session.execute(
            select(
                source_snapshot_events.c.source_snapshot_id,
                source_snapshot_events.c.company_event_id,
            )
        ).all()
    assert first.event_count == 1
    assert second.event_count == 2
    assert len(events) == 2
    assert len(links) == 3
    assert {snapshot_id for snapshot_id, _ in links} == {first.snapshot_id, second.snapshot_id}


def test_snapshot_artifact_survives_metadata_failure_and_is_reused(
    runtime: Runtime,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connector = _StaticConnector()
    snapshot_root = runtime.settings.raw_data_dir.parent / "metadata-failure-artifact"
    registry = SourceRegistry(runtime.session_factory, snapshot_root, (connector,))
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    original_seed = SourceRegistry._seed_manifest

    def fail_metadata(*_: object) -> None:
        raise RuntimeError("synthetic metadata failure")

    monkeypatch.setattr(SourceRegistry, "_seed_manifest", staticmethod(fail_metadata))
    with pytest.raises(RuntimeError, match="metadata failure"):
        registry.collect(request)
    artifacts = tuple(snapshot_root.rglob("*.bin"))
    assert len(artifacts) == 1
    assert artifacts[0].read_bytes() == connector.content

    monkeypatch.setattr(SourceRegistry, "_seed_manifest", staticmethod(original_seed))
    persisted = registry.collect(request)
    with runtime.session_factory() as session:
        snapshot = session.get(SourceSnapshotModel, persisted.snapshot_id)
        assert snapshot is not None
        assert Path(snapshot.snapshot_path or "") == artifacts[0]


def test_concurrent_snapshot_writers_publish_one_checksum_addressed_artifact(
    runtime: Runtime,
) -> None:
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / "concurrent-artifact",
        (_StaticConnector(),),
    )
    content = b'{"immutable":"same-bytes"}'

    def write_once(_: int) -> tuple[Path, bool]:
        return registry._write_snapshot(
            source_key="companies_house",
            request_fingerprint="f" * 64,
            checksum=sha256_bytes(content),
            content=content,
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = tuple(executor.map(write_once, range(8)))
    paths = {path for path, _ in results}
    assert len(paths) == 1
    path = paths.pop()
    assert path.read_bytes() == content
    assert sum(created for _, created in results) == 1
    assert tuple(path.parent.glob("*.staging")) == ()


def test_concurrent_same_request_rejects_different_derivation_winner(
    runtime: Runtime,
) -> None:
    request = SourceRequest(
        source_key="companies_house",
        company_id=_company(runtime),
        identifier_scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER,
        identifier_value="00000001",
        reporting_cutoff=date(2025, 6, 30),
    )
    winning_connector = _StaticConnector(company_status="active")
    losing_collection = _StaticConnector(company_status="dissolved").collect_source(request)
    entered = Event()
    release = Event()

    class BlockingConnector:
        manifest = _StaticConnector.manifest

        def collect_source(self, _request: SourceRequest) -> SourceCollection:
            entered.set()
            if not release.wait(timeout=5):
                raise TimeoutError("Concurrent derivation test did not release the connector.")
            return losing_collection

    snapshot_root = runtime.settings.raw_data_dir.parent / "concurrent-derivation"
    winner_registry = SourceRegistry(runtime.session_factory, snapshot_root, (winning_connector,))
    loser_registry = SourceRegistry(runtime.session_factory, snapshot_root, (BlockingConnector(),))

    with ThreadPoolExecutor(max_workers=1) as executor:
        losing_future = executor.submit(loser_registry.collect, request)
        assert entered.wait(timeout=5)
        winner = winner_registry.collect(request)
        release.set()
        with pytest.raises(SourceChecksumDriftError, match="derivation"):
            losing_future.result(timeout=5)

    with runtime.session_factory() as session:
        snapshots = list(session.scalars(select(SourceSnapshotModel)).all())
        facts = list(
            session.scalars(
                select(EvidenceFactModel).where(EvidenceFactModel.fact_key == "company_status")
            ).all()
        )
    assert [snapshot.id for snapshot in snapshots] == [winner.snapshot_id]
    assert [fact.value_json for fact in facts] == ["active"]


def test_http_client_handles_no_record_retries_and_resource_bounds() -> None:
    attempts = 0
    sleeps: list[float] = []

    def retrying_handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, headers={"retry-after": "0.1"})
        if attempts == 2:
            return httpx.Response(503)
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=b'{"ok":true}',
        )

    policy = HttpPolicy(
        allowed_origins=("https://example.test",),
        max_attempts=3,
        max_response_bytes=20,
    )
    with BoundedHttpClient(
        policy,
        transport=httpx.MockTransport(retrying_handler),
        sleeper=sleeps.append,
    ) as client:
        result = client.get("https://example.test/company/1")
    assert result.status is CollectionStatus.SUCCEEDED
    assert result.attempts == 3
    assert sleeps == [0.1, 0.5]

    cases = (
        (
            lambda _request: httpx.Response(404),
            CollectionStatus.NO_RECORD,
            None,
        ),
        (
            lambda _request: httpx.Response(
                200,
                headers={"content-type": "text/html"},
                content=b"not json",
            ),
            CollectionStatus.FAILED,
            "unexpected_content_type",
        ),
        (
            lambda _request: httpx.Response(
                200,
                headers={"content-type": "application/json", "content-length": "21"},
                content=b"{}",
            ),
            CollectionStatus.FAILED,
            "response_too_large",
        ),
    )
    for handler, expected_status, expected_error in cases:
        with BoundedHttpClient(
            policy,
            transport=httpx.MockTransport(handler),
            sleeper=lambda _seconds: None,
        ) as client:
            result = client.get("https://example.test/company/1")
        assert result.status is expected_status
        assert result.error_code == expected_error


def test_http_client_bounds_timeouts_and_rejects_unlisted_origins() -> None:
    def timeout_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("synthetic timeout", request=request)

    policy = HttpPolicy(allowed_origins=("https://example.test",), max_attempts=2)
    with BoundedHttpClient(
        policy,
        transport=httpx.MockTransport(timeout_handler),
        sleeper=lambda _seconds: None,
    ) as client:
        result = client.get("https://example.test/company/1")
        with pytest.raises(ValueError, match="allowlist"):
            client.get("https://unlisted.test/company/1")
    assert result.status is CollectionStatus.SOURCE_UNAVAILABLE
    assert result.attempts == 2
    assert result.error_code == "timeout_or_transport"


def test_http_client_retries_timeout_while_streaming_response_body() -> None:
    class FailingStream(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b'{"partial":'
            raise httpx.ReadTimeout("synthetic mid-stream timeout")

    attempts = 0
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(
                200,
                headers={"content-type": "application/json"},
                stream=FailingStream(),
                request=request,
            )
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=b'{"ok":true}',
            request=request,
        )

    with BoundedHttpClient(
        HttpPolicy(allowed_origins=("https://example.test",), max_attempts=2),
        transport=httpx.MockTransport(handler),
        sleeper=sleeps.append,
    ) as client:
        result = client.get("https://example.test/company/1")

    assert result.status is CollectionStatus.SUCCEEDED
    assert result.attempts == 2
    assert attempts == 2
    assert sleeps == [0.25]


@pytest.mark.parametrize("amount", ("NaN", "Infinity", "-Infinity"))
def test_event_amount_rejects_non_finite_literals(amount: str) -> None:
    with pytest.raises(SourceContractError, match="finite"):
        SourceRegistry._canonical_event_amount(amount)
