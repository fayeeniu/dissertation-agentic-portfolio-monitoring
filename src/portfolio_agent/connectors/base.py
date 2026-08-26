from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Protocol

from portfolio_agent.enums import CollectionStatus, DataClassification, IdentifierScheme
from portfolio_agent.schemas import EvidenceItem


@dataclass(frozen=True, slots=True)
class ConnectorQuery:
    """Legacy metric-oriented query retained for the v1 workflow adapter."""

    company_id: str
    company_name: str
    external_id: str | None
    metric_key: str
    period_label: str
    reporting_cutoff: date | None = None


class Connector(Protocol):
    name: str
    version: str

    def collect(self, query: ConnectorQuery) -> tuple[EvidenceItem, ...]: ...


@dataclass(frozen=True, slots=True)
class SourceFactContract:
    """Exact semantic binding for one connector-produced fact."""

    fact_key: str
    metric_keys: tuple[str | None, ...]
    extraction_method: str
    extraction_schema_version: str
    unit: str | None = None
    currency: str | None = None


@dataclass(frozen=True, slots=True)
class SourceCapabilityManifest:
    key: str
    version: str
    publisher: str
    identifier_schemes: tuple[IdentifierScheme, ...]
    fact_contracts: tuple[SourceFactContract, ...]
    event_types: tuple[str, ...]
    media_types: tuple[str, ...]
    retrieval_modes: tuple[str, ...]
    public_only: bool = True
    licence_reference: str | None = None
    terms_reference: str | None = None
    admission_reviewed_at: date | None = None
    live_retrieval_admitted: bool = False

    @property
    def fact_keys(self) -> tuple[str, ...]:
        return tuple(contract.fact_key for contract in self.fact_contracts)


@dataclass(frozen=True, slots=True)
class SourceRequest:
    source_key: str
    company_id: str
    identifier_scheme: IdentifierScheme
    identifier_value: str
    reporting_cutoff: date
    programme_start_date: date | None = None
    fact_keys: tuple[str, ...] = ()
    mode: str = "offline_snapshot"


@dataclass(frozen=True, slots=True)
class CollectedFact:
    fact_key: str
    value: Any
    source_locator: str
    structured_locator: dict[str, Any] = field(default_factory=dict)
    extraction_method: str = ""
    extraction_schema_version: str = ""
    unit: str | None = None
    currency: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    effective_at: datetime | None = None
    published_at: datetime | None = None
    metric_key: str | None = None


@dataclass(frozen=True, slots=True)
class CollectedEvent:
    event_type: str
    title: str
    source_locator: str
    public_identifier: str | None = None
    lifecycle_stage: str | None = None
    event_date: date | None = None
    amount: str | int | None = None
    currency: str | None = None
    details: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class SourceCollection:
    status: CollectionStatus
    locator: str
    retrieved_at: datetime
    content: bytes | None = None
    media_type: str | None = None
    published_at: datetime | None = None
    http_status: int | None = None
    facts: tuple[CollectedFact, ...] = ()
    events: tuple[CollectedEvent, ...] = ()
    classification: DataClassification = DataClassification.PUBLIC
    error_code: str | None = None
    error_message: str | None = None


class SourceConnector(Protocol):
    manifest: SourceCapabilityManifest

    def collect_source(self, request: SourceRequest) -> SourceCollection: ...
