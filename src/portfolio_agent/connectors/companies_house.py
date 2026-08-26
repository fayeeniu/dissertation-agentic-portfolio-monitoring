from __future__ import annotations

import base64
import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Literal
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict

from portfolio_agent.document_extraction import DocumentFieldRequest, extract_document
from portfolio_agent.enums import CollectionStatus, DataClassification, EventType, IdentifierScheme
from portfolio_agent.identity import is_valid_companies_house_number, normalize_identifier

from .base import (
    CollectedEvent,
    CollectedFact,
    SourceCapabilityManifest,
    SourceCollection,
    SourceFactContract,
    SourceRequest,
)
from .http_client import BoundedHttpClient


class _Accounts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    next_due: date | None = None
    period_end: date | None = None
    last_filed_at: date | None = None
    overdue: bool = False
    dormant: bool = False


class _Filing(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str
    category: str
    filed_at: date
    period_start: date | None = None
    period_end: date | None = None
    description: str


class _Charge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    charge_id: str
    created_at: date
    status: str


class _CompanyRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_number: str
    company_name: str
    company_status: str
    date_of_creation: date | None = None
    date_of_cessation: date | None = None
    sic_codes: tuple[str, ...] = ()
    registered_office_postcode: str | None = None
    published_at: datetime
    accounts: _Accounts
    filings: tuple[_Filing, ...] = ()
    charges: tuple[_Charge, ...] = ()


class _SnapshotDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    classification: Literal["synthetic", "public"]
    publisher: str
    records: tuple[_CompanyRecord, ...]


class CompaniesHouseConnector:
    manifest = SourceCapabilityManifest(
        key="companies_house",
        version="1.4.0",
        publisher="Companies House",
        identifier_schemes=(IdentifierScheme.COMPANIES_HOUSE_NUMBER,),
        fact_contracts=tuple(
            SourceFactContract(
                fact_key=fact_key,
                metric_keys=(None,),
                extraction_method=(
                    "deterministic_json_rule"
                    if fact_key == "accounts_missing_state"
                    else "deterministic_json_pointer"
                ),
                extraction_schema_version="companies-house-source-fact-v3",
            )
            for fact_key in (
                "company_number",
                "company_name",
                "company_status",
                "incorporation_date",
                "dissolution_date",
                "sic_codes",
                "registered_office_postcode",
                "accounts_next_due",
                "accounts_period_end",
                "accounts_overdue",
                "accounts_dormant",
                "accounts_missing_state",
            )
        ),
        event_types=(
            EventType.INCORPORATED.value,
            EventType.DISSOLVED.value,
            EventType.ACCOUNTS_FILED.value,
            EventType.CHARGE_REGISTERED.value,
        ),
        media_types=("application/json",),
        retrieval_modes=("offline_snapshot", "read_only_api"),
        licence_reference="G2:EVIDENCE_REQUIRED",
        terms_reference="G2:EVIDENCE_REQUIRED",
        live_retrieval_admitted=False,
    )

    def __init__(
        self,
        *,
        local_snapshot_path: Path | None = None,
        http_client: BoundedHttpClient | None = None,
        api_key: str | None = None,
        allow_live_api: bool = False,
        api_base_url: str = "https://api.company-information.service.gov.uk",
    ) -> None:
        self._local_snapshot_path = local_snapshot_path
        self._http_client = http_client
        self._api_key = api_key
        self._allow_live_api = allow_live_api
        self._api_base_url = api_base_url.rstrip("/")

    def collect_source(self, request: SourceRequest) -> SourceCollection:
        if request.identifier_scheme is not IdentifierScheme.COMPANIES_HOUSE_NUMBER:
            raise ValueError("Companies House requires its exact registry-number scheme.")
        normalized_number = normalize_identifier(
            IdentifierScheme.COMPANIES_HOUSE_NUMBER, request.identifier_value
        )
        if not is_valid_companies_house_number(normalized_number):
            raise ValueError("Companies House number failed structural validation.")
        if request.mode == "offline_snapshot":
            return self._collect_offline(request, normalized_number)
        if request.mode == "read_only_api":
            return self._collect_api(request, normalized_number)
        raise ValueError("Unsupported Companies House retrieval mode.")

    def _collect_offline(self, request: SourceRequest, normalized_number: str) -> SourceCollection:
        if self._local_snapshot_path is None:
            return SourceCollection(
                status=CollectionStatus.SOURCE_UNAVAILABLE,
                locator="fixture://companies-house/unconfigured",
                retrieved_at=datetime.now(UTC),
                error_code="offline_snapshot_unconfigured",
                error_message="No immutable local Companies House snapshot was configured.",
            )
        content = self._local_snapshot_path.read_bytes()
        document = _SnapshotDocument.model_validate_json(content)
        classification = DataClassification(document.classification)
        records = [
            (record_index, record)
            for record_index, record in enumerate(document.records)
            if normalize_identifier(IdentifierScheme.COMPANIES_HOUSE_NUMBER, record.company_number)
            == normalized_number
        ]
        locator = f"fixture://companies-house/{normalized_number}"
        if not records:
            return SourceCollection(
                status=CollectionStatus.NO_RECORD,
                locator=locator,
                retrieved_at=datetime.now(UTC),
                content=content,
                media_type="application/json",
                classification=classification,
                http_status=404,
                error_code="no_exact_company_number",
            )
        if len(records) != 1:
            raise ValueError("Companies House snapshot contains a duplicate registry number.")
        return self._collection_for_record(
            request,
            record=records[0][1],
            content=content,
            locator=locator,
            classification=classification,
            document_pointer_prefix=f"/records/{records[0][0]}",
        )

    def _collect_api(self, request: SourceRequest, normalized_number: str) -> SourceCollection:
        if not self._allow_live_api:
            raise ValueError("Live Companies House retrieval is disabled by policy.")
        if self._http_client is None or not self._api_key:
            raise ValueError("Live Companies House retrieval requires a configured client key.")
        token = base64.b64encode(f"{self._api_key}:".encode()).decode()
        url = f"{self._api_base_url}/company/{normalized_number}"
        response = self._http_client.get(url, headers={"authorization": f"Basic {token}"})
        if response.status is not CollectionStatus.SUCCEEDED:
            return SourceCollection(
                status=response.status,
                locator=url,
                retrieved_at=datetime.now(UTC),
                http_status=response.http_status,
                error_code=response.error_code,
                error_message=response.error_message,
            )
        assert response.content is not None
        payload = json.loads(response.content)
        if not isinstance(payload, dict):
            raise ValueError("Companies House API response must be a JSON object.")
        record = _CompanyRecord.model_validate(
            {
                "company_number": payload.get("company_number"),
                "company_name": payload.get("company_name"),
                "company_status": payload.get("company_status"),
                "date_of_creation": payload.get("date_of_creation"),
                "date_of_cessation": payload.get("date_of_cessation"),
                "sic_codes": payload.get("sic_codes", []),
                "registered_office_postcode": (
                    payload.get("registered_office_address", {}).get("postal_code")
                    if isinstance(payload.get("registered_office_address"), dict)
                    else None
                ),
                "published_at": datetime.now(UTC),
                "accounts": {
                    "next_due": payload.get("accounts", {}).get("next_due")
                    if isinstance(payload.get("accounts"), dict)
                    else None,
                    "overdue": payload.get("accounts", {}).get("overdue", False)
                    if isinstance(payload.get("accounts"), dict)
                    else False,
                    "dormant": False,
                },
                "filings": [],
                "charges": [],
            }
        )
        return self._collection_for_record(
            request,
            record=record,
            content=response.content,
            locator=url,
            classification=DataClassification.PUBLIC,
            http_status=response.http_status,
            document_pointer_prefix="",
        )

    @staticmethod
    def _collection_for_record(
        request: SourceRequest,
        *,
        record: _CompanyRecord,
        content: bytes,
        locator: str,
        classification: DataClassification,
        document_pointer_prefix: str,
        http_status: int | None = 200,
    ) -> SourceCollection:
        base_facts = (
            ("company_number", record.company_number, "/company_number"),
            ("company_name", record.company_name, "/company_name"),
            ("company_status", record.company_status, "/company_status"),
            (
                "incorporation_date",
                record.date_of_creation.isoformat() if record.date_of_creation else None,
                "/date_of_creation",
            ),
            (
                "dissolution_date",
                record.date_of_cessation.isoformat() if record.date_of_cessation else None,
                "/date_of_cessation",
            ),
            ("sic_codes", list(record.sic_codes), "/sic_codes"),
            (
                "registered_office_postcode",
                record.registered_office_postcode,
                "/registered_office_postcode",
            ),
            (
                "accounts_next_due",
                record.accounts.next_due.isoformat() if record.accounts.next_due else None,
                "/accounts/next_due",
            ),
            (
                "accounts_period_end",
                record.accounts.period_end.isoformat() if record.accounts.period_end else None,
                "/accounts/period_end",
            ),
            ("accounts_overdue", record.accounts.overdue, "/accounts/overdue"),
            ("accounts_dormant", record.accounts.dormant, "/accounts/dormant"),
        )
        for key, expected_value, relative_pointer in base_facts:
            if key not in {"company_number", "company_name", "company_status"}:
                continue
            pointer = f"{document_pointer_prefix}{relative_pointer}"
            extracted = extract_document(
                content,
                media_type="application/json",
                request=DocumentFieldRequest(
                    field_key=key,
                    aliases=(key.replace("_", " "),),
                    json_pointers=(pointer,),
                ),
            )
            if extracted.abstain_reason is not None or extracted.value != expected_value:
                raise ValueError(
                    f"Companies House document extraction disagrees with validated field {key}."
                )
        missing_state: str | None = None
        if record.accounts.dormant:
            missing_state = "dormant"
        elif record.accounts.next_due and record.accounts.next_due > request.reporting_cutoff:
            missing_state = "filing_not_due"
        facts = [
            CollectedFact(
                fact_key=key,
                value=value,
                source_locator=f"{locator}#{document_pointer_prefix}{pointer}",
                structured_locator={
                    "format": "json_pointer",
                    "pointer": f"{document_pointer_prefix}{pointer}",
                },
                extraction_method="deterministic_json_pointer",
                extraction_schema_version="companies-house-source-fact-v3",
                published_at=record.published_at,
                period_end=(record.accounts.period_end if key == "accounts_period_end" else None),
            )
            for key, value, pointer in base_facts
            if not request.fact_keys or key in request.fact_keys
        ]
        if missing_state and (
            not request.fact_keys or "accounts_missing_state" in request.fact_keys
        ):
            facts.append(
                CollectedFact(
                    fact_key="accounts_missing_state",
                    value=missing_state,
                    source_locator=f"{locator}#{document_pointer_prefix}/accounts",
                    structured_locator={
                        "format": "json_pointer",
                        "pointer": f"{document_pointer_prefix}/accounts",
                    },
                    extraction_method="deterministic_json_rule",
                    extraction_schema_version="companies-house-source-fact-v3",
                    published_at=record.published_at,
                )
            )

        events: list[CollectedEvent] = []
        if record.date_of_creation and record.date_of_creation <= request.reporting_cutoff:
            events.append(
                CollectedEvent(
                    event_type=EventType.INCORPORATED.value,
                    title="Company incorporated",
                    source_locator=f"{locator}#/date_of_creation",
                    public_identifier=f"{record.company_number}:incorporated",
                    event_date=record.date_of_creation,
                )
            )
        if record.date_of_cessation and record.date_of_cessation <= request.reporting_cutoff:
            events.append(
                CollectedEvent(
                    event_type=EventType.DISSOLVED.value,
                    title="Company dissolved",
                    source_locator=f"{locator}#/date_of_cessation",
                    public_identifier=f"{record.company_number}:dissolved",
                    event_date=record.date_of_cessation,
                )
            )
        events.extend(
            CollectedEvent(
                event_type=EventType.ACCOUNTS_FILED.value,
                title=filing.description,
                source_locator=(
                    f"{locator}#/filings/by-transaction/{quote(filing.transaction_id, safe='')}"
                ),
                public_identifier=filing.transaction_id,
                event_date=filing.filed_at,
                details={
                    "category": filing.category,
                    "period_start": filing.period_start.isoformat()
                    if filing.period_start
                    else None,
                    "period_end": filing.period_end.isoformat() if filing.period_end else None,
                },
            )
            for filing in record.filings
            if filing.filed_at <= request.reporting_cutoff
        )
        events.extend(
            CollectedEvent(
                event_type=EventType.CHARGE_REGISTERED.value,
                title="Charge registered",
                source_locator=f"{locator}#/charges/by-id/{quote(charge.charge_id, safe='')}",
                public_identifier=charge.charge_id,
                event_date=charge.created_at,
                details={"status": charge.status},
            )
            for charge in record.charges
            if charge.created_at <= request.reporting_cutoff
        )
        return SourceCollection(
            status=CollectionStatus.SUCCEEDED,
            locator=locator,
            retrieved_at=datetime.now(UTC),
            content=content,
            media_type="application/json",
            published_at=record.published_at,
            http_status=http_status,
            facts=tuple(facts),
            events=tuple(events),
            classification=classification,
        )
