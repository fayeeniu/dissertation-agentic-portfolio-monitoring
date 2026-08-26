from __future__ import annotations

import os
import tempfile
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from portfolio_agent.cbit_contract import ADMITTED_PUBLIC_SOURCES, PeriodSemantics
from portfolio_agent.enums import (
    CollectionStatus,
    DataClassification,
    IdentifierScheme,
    ResolutionStatus,
)
from portfolio_agent.identity import normalize_identifier
from portfolio_agent.ids import new_id, sha256_bytes, stable_hash
from portfolio_agent.models import (
    CompanyEventModel,
    CompanyIdentifierModel,
    CompanyModel,
    EvidenceFactModel,
    MetricDefinitionModel,
    SourceDefinitionModel,
    SourceSnapshotModel,
    source_snapshot_events,
)

from .base import (
    CollectedEvent,
    SourceCapabilityManifest,
    SourceCollection,
    SourceConnector,
    SourceRequest,
)


class SourceContractError(ValueError):
    pass


class SourceChecksumDriftError(SourceContractError):
    pass


SOURCE_DERIVATION_CONTRACT_VERSION = "source-derivation-v2"
_LEGACY_DERIVATION_CONTRACT_VERSION = "source-derivation-v1"


@dataclass(frozen=True, slots=True)
class RegistryCollectionResult:
    snapshot_id: str
    status: CollectionStatus
    request_fingerprint: str
    sha256: str | None
    fact_count: int
    event_count: int
    replayed: bool
    error_code: str | None = None


class SourceRegistry:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        snapshot_root: Path,
        connectors: tuple[SourceConnector, ...] = (),
    ) -> None:
        self._session_factory = session_factory
        self._snapshot_root = snapshot_root.resolve()
        for connector in connectors:
            self._validate_manifest(connector.manifest)
        self._connectors = {connector.manifest.key: connector for connector in connectors}
        if len(self._connectors) != len(connectors):
            raise SourceContractError("Duplicate source connector key.")
        admitted = {source.key for source in ADMITTED_PUBLIC_SOURCES}
        if not set(self._connectors).issubset(admitted):
            raise SourceContractError("Connector key is not admitted by the source policy.")

    @property
    def manifests(self) -> tuple[SourceCapabilityManifest, ...]:
        return tuple(
            connector.manifest
            for _, connector in sorted(self._connectors.items(), key=lambda item: item[0])
        )

    def seed_manifests(self) -> None:
        with self._session_factory.begin() as session:
            for connector in self._connectors.values():
                self._seed_manifest(session, connector.manifest)

    def collect(
        self,
        request: SourceRequest,
        *,
        force_refresh: bool = False,
    ) -> RegistryCollectionResult:
        connector = self._connectors.get(request.source_key)
        if connector is None:
            raise SourceContractError("Requested source is not admitted and configured.")
        normalized_identifier = self._validate_request(request, connector.manifest)
        request_fingerprint = stable_hash(
            {
                "source_key": request.source_key,
                "source_version": connector.manifest.version,
                "company_id": request.company_id,
                "identifier_scheme": request.identifier_scheme.value,
                "identifier_value": normalized_identifier,
                "reporting_cutoff": request.reporting_cutoff.isoformat(),
                "programme_start_date": (
                    request.programme_start_date.isoformat()
                    if request.programme_start_date is not None
                    else None
                ),
                "fact_keys": sorted(request.fact_keys),
                "mode": request.mode,
            }
        )
        existing = self._replayable_snapshot(request.source_key, request_fingerprint)
        if existing is not None and not force_refresh:
            self._assert_allowed_classification(existing.classification, connector.manifest)
            self._verify_stored_snapshot(existing)
            self._verify_stored_derivation(existing)
            return self._result_for_existing(existing)

        collected = connector.collect_source(request)
        self._validate_collection(collected, request, connector.manifest)
        self._assert_allowed_classification(collected.classification, connector.manifest)
        content_hash = sha256_bytes(collected.content) if collected.content is not None else None
        derivation_hash = self._collection_derivation_hash(
            collection=collected,
            content_hash=content_hash,
            request=request,
            source_version=connector.manifest.version,
        )
        if existing is not None and collected.status in {
            CollectionStatus.SUCCEEDED,
            CollectionStatus.NO_RECORD,
        }:
            self._assert_incoming_matches_snapshot(
                existing,
                status=collected.status,
                content_hash=content_hash,
                derivation_hash=derivation_hash,
            )
            self._verify_stored_snapshot(existing)
            return self._result_for_existing(existing)
        snapshot_id = new_id("snap")
        snapshot_path: Path | None = None
        if collected.content is not None and content_hash is not None:
            snapshot_path, _ = self._write_snapshot(
                source_key=request.source_key,
                request_fingerprint=request_fingerprint,
                checksum=content_hash,
                content=collected.content,
            )
        try:
            with self._session_factory.begin() as session:
                self._seed_manifest(session, connector.manifest)
                snapshot = SourceSnapshotModel(
                    id=snapshot_id,
                    source_key=request.source_key,
                    source_version=connector.manifest.version,
                    request_fingerprint=request_fingerprint,
                    company_id=request.company_id,
                    identifier_scheme=request.identifier_scheme.value,
                    identifier_value=normalized_identifier,
                    programme_start_date=request.programme_start_date,
                    reporting_cutoff=request.reporting_cutoff,
                    status=collected.status.value,
                    http_status=collected.http_status,
                    locator=collected.locator,
                    media_type=collected.media_type,
                    byte_size=len(collected.content) if collected.content is not None else None,
                    sha256=content_hash,
                    derivation_contract_version=SOURCE_DERIVATION_CONTRACT_VERSION,
                    derivation_sha256=derivation_hash,
                    snapshot_path=str(snapshot_path) if snapshot_path else None,
                    retrieved_at=collected.retrieved_at,
                    published_at=collected.published_at,
                    classification=collected.classification.value,
                    error_code=collected.error_code,
                    error_message=collected.error_message,
                )
                session.add(snapshot)
                session.flush()
                definitions = {
                    row.key: row for row in session.scalars(select(MetricDefinitionModel)).all()
                }
                for fact in collected.facts:
                    metric_id = (
                        definitions[fact.metric_key].id
                        if fact.metric_key and fact.metric_key in definitions
                        else None
                    )
                    session.add(
                        EvidenceFactModel(
                            source_snapshot_id=snapshot.id,
                            company_id=request.company_id,
                            metric_definition_id=metric_id,
                            fact_key=fact.fact_key,
                            value_json=fact.value,
                            unit=fact.unit,
                            currency=fact.currency,
                            period_start=fact.period_start,
                            period_end=fact.period_end,
                            effective_at=fact.effective_at,
                            published_at=fact.published_at,
                            source_locator=fact.source_locator,
                            structured_locator_json=dict(fact.structured_locator),
                            extraction_method=fact.extraction_method,
                            extraction_schema_version=fact.extraction_schema_version,
                            temporal_status=None,
                        )
                    )
                for event in collected.events:
                    stored_event = self._persist_event(
                        session,
                        snapshot=snapshot,
                        company_id=request.company_id,
                        source_key=request.source_key,
                        event=event,
                        classification=collected.classification,
                    )
                    session.execute(
                        insert(source_snapshot_events).values(
                            source_snapshot_id=snapshot.id,
                            company_event_id=stored_event.id,
                        )
                    )
                return RegistryCollectionResult(
                    snapshot_id=snapshot.id,
                    status=collected.status,
                    request_fingerprint=request_fingerprint,
                    sha256=content_hash,
                    fact_count=len(collected.facts),
                    event_count=len(collected.events),
                    replayed=False,
                    error_code=collected.error_code,
                )
        except IntegrityError:
            winner = self._replayable_snapshot(request.source_key, request_fingerprint)
            if winner is None:
                raise
            self._assert_allowed_classification(winner.classification, connector.manifest)
            self._verify_stored_snapshot(winner)
            self._assert_incoming_matches_snapshot(
                winner,
                status=collected.status,
                content_hash=content_hash,
                derivation_hash=derivation_hash,
            )
            return self._result_for_existing(winner)

    def _replayable_snapshot(
        self, source_key: str, request_fingerprint: str
    ) -> SourceSnapshotModel | None:
        with self._session_factory() as session:
            snapshot = session.scalar(
                select(SourceSnapshotModel)
                .where(
                    SourceSnapshotModel.source_key == source_key,
                    SourceSnapshotModel.request_fingerprint == request_fingerprint,
                    SourceSnapshotModel.status.in_(
                        (
                            CollectionStatus.SUCCEEDED.value,
                            CollectionStatus.NO_RECORD.value,
                        )
                    ),
                )
                .order_by(SourceSnapshotModel.created_at)
            )
            if snapshot is not None:
                session.expunge(snapshot)
            return snapshot

    def _result_for_existing(self, snapshot: SourceSnapshotModel) -> RegistryCollectionResult:
        with self._session_factory() as session:
            fact_count = len(
                session.scalars(
                    select(EvidenceFactModel.id).where(
                        EvidenceFactModel.source_snapshot_id == snapshot.id
                    )
                ).all()
            )
            event_count = len(
                session.scalars(
                    select(source_snapshot_events.c.company_event_id).where(
                        source_snapshot_events.c.source_snapshot_id == snapshot.id
                    )
                ).all()
            )
        return RegistryCollectionResult(
            snapshot_id=snapshot.id,
            status=CollectionStatus(snapshot.status),
            request_fingerprint=snapshot.request_fingerprint,
            sha256=snapshot.sha256,
            fact_count=fact_count,
            event_count=event_count,
            replayed=True,
            error_code=snapshot.error_code,
        )

    def _assert_incoming_matches_snapshot(
        self,
        snapshot: SourceSnapshotModel,
        *,
        status: CollectionStatus,
        content_hash: str | None,
        derivation_hash: str,
    ) -> None:
        stored_derivation_hash = self._verify_stored_derivation(snapshot)
        if (
            snapshot.status != status.value
            or snapshot.sha256 != content_hash
            or stored_derivation_hash != derivation_hash
        ):
            raise SourceChecksumDriftError(
                "The same source request and cutoff returned a different terminal result or "
                "derivation."
            )

    @classmethod
    def _collection_derivation_hash(
        cls,
        *,
        collection: SourceCollection,
        content_hash: str | None,
        request: SourceRequest,
        source_version: str,
    ) -> str:
        facts = [
            cls._fact_derivation_payload(
                company_id=request.company_id,
                fact_key=fact.fact_key,
                value=fact.value,
                source_locator=fact.source_locator,
                unit=fact.unit,
                currency=fact.currency,
                period_start=fact.period_start,
                period_end=fact.period_end,
                effective_at=fact.effective_at,
                published_at=fact.published_at,
                metric_key=fact.metric_key,
                structured_locator=fact.structured_locator,
                extraction_method=fact.extraction_method,
                extraction_schema_version=fact.extraction_schema_version,
                contract_version=SOURCE_DERIVATION_CONTRACT_VERSION,
            )
            for fact in collection.facts
        ]
        events = [
            cls._event_derivation_payload(
                event_fingerprint=cls._event_fingerprint(
                    company_id=request.company_id,
                    source_key=request.source_key,
                    event=event,
                ),
                company_id=request.company_id,
                source_key=request.source_key,
                event_type=event.event_type,
                title=event.title,
                source_locator=event.source_locator,
                public_identifier=event.public_identifier,
                lifecycle_stage=event.lifecycle_stage,
                event_date=event.event_date,
                amount=event.amount,
                currency=event.currency,
                details=event.details or {},
                classification=collection.classification.value,
            )
            for event in collection.events
        ]
        return cls._derivation_hash(
            source_key=request.source_key,
            source_version=source_version,
            company_id=request.company_id,
            identifier_scheme=request.identifier_scheme.value,
            identifier_value=normalize_identifier(
                request.identifier_scheme, request.identifier_value
            ),
            reporting_cutoff=request.reporting_cutoff,
            programme_start_date=request.programme_start_date,
            status=collection.status.value,
            http_status=collection.http_status,
            locator=collection.locator,
            media_type=collection.media_type,
            content_hash=content_hash,
            byte_size=len(collection.content) if collection.content is not None else None,
            published_at=collection.published_at,
            classification=collection.classification.value,
            error_code=collection.error_code,
            error_message=collection.error_message,
            facts=facts,
            events=events,
            contract_version=SOURCE_DERIVATION_CONTRACT_VERSION,
        )

    def _verify_stored_derivation(self, snapshot: SourceSnapshotModel) -> str:
        with self._session_factory.begin() as session:
            stored = session.get(SourceSnapshotModel, snapshot.id)
            if stored is None:
                raise SourceContractError("Stored source snapshot metadata is unavailable.")
            contract_version = (
                SOURCE_DERIVATION_CONTRACT_VERSION
                if stored.derivation_sha256 is None
                else stored.derivation_contract_version or _LEGACY_DERIVATION_CONTRACT_VERSION
            )
            calculated = self._stored_derivation_hash(
                session, stored, contract_version=contract_version
            )
            if stored.derivation_sha256 is None:
                # Revision 0006 is nullable so databases produced by earlier prototype
                # revisions can be upgraded without fabricating a hash in SQL. The first
                # verified replay derives it from the persisted snapshot/fact/event state.
                stored.derivation_sha256 = calculated
                stored.derivation_contract_version = contract_version
                snapshot.derivation_sha256 = calculated
                snapshot.derivation_contract_version = contract_version
            elif stored.derivation_sha256 != calculated:
                raise SourceChecksumDriftError(
                    "Persisted source facts or events no longer match their derivation hash."
                )
            return calculated

    @classmethod
    def _stored_derivation_hash(
        cls,
        session: Session,
        snapshot: SourceSnapshotModel,
        *,
        contract_version: str,
    ) -> str:
        if contract_version not in {
            _LEGACY_DERIVATION_CONTRACT_VERSION,
            SOURCE_DERIVATION_CONTRACT_VERSION,
        }:
            raise SourceContractError("Stored source derivation contract is unsupported.")
        metric_keys = {
            metric_id: key
            for metric_id, key in session.execute(
                select(MetricDefinitionModel.id, MetricDefinitionModel.key)
            ).all()
        }
        stored_facts = list(
            session.scalars(
                select(EvidenceFactModel).where(EvidenceFactModel.source_snapshot_id == snapshot.id)
            ).all()
        )
        stored_events = list(
            session.scalars(
                select(CompanyEventModel)
                .join(
                    source_snapshot_events,
                    source_snapshot_events.c.company_event_id == CompanyEventModel.id,
                )
                .where(source_snapshot_events.c.source_snapshot_id == snapshot.id)
            ).all()
        )
        facts = [
            cls._fact_derivation_payload(
                company_id=fact.company_id,
                fact_key=fact.fact_key,
                value=fact.value_json,
                source_locator=fact.source_locator,
                unit=fact.unit,
                currency=fact.currency,
                period_start=fact.period_start,
                period_end=fact.period_end,
                effective_at=fact.effective_at,
                published_at=fact.published_at,
                metric_key=metric_keys.get(fact.metric_definition_id),
                structured_locator=fact.structured_locator_json or {},
                extraction_method=fact.extraction_method or "",
                extraction_schema_version=fact.extraction_schema_version or "",
                contract_version=contract_version,
            )
            for fact in stored_facts
        ]
        events = [
            cls._event_derivation_payload(
                event_fingerprint=event.event_fingerprint,
                company_id=event.company_id,
                source_key=event.source_key,
                event_type=event.event_type,
                title=event.title,
                source_locator=event.source_locator,
                public_identifier=event.public_identifier,
                lifecycle_stage=event.lifecycle_stage,
                event_date=event.event_date,
                amount=event.amount,
                currency=event.currency,
                details=event.details_json,
                classification=event.classification,
            )
            for event in stored_events
        ]
        return cls._derivation_hash(
            source_key=snapshot.source_key,
            source_version=snapshot.source_version,
            company_id=snapshot.company_id,
            identifier_scheme=snapshot.identifier_scheme,
            identifier_value=snapshot.identifier_value,
            reporting_cutoff=snapshot.reporting_cutoff,
            programme_start_date=snapshot.programme_start_date,
            status=snapshot.status,
            http_status=snapshot.http_status,
            locator=snapshot.locator,
            media_type=snapshot.media_type,
            content_hash=snapshot.sha256,
            byte_size=snapshot.byte_size,
            published_at=snapshot.published_at,
            classification=snapshot.classification,
            error_code=snapshot.error_code,
            error_message=snapshot.error_message,
            facts=facts,
            events=events,
            contract_version=contract_version,
        )

    @classmethod
    def _derivation_hash(
        cls,
        *,
        source_key: str,
        source_version: str,
        company_id: str | None,
        identifier_scheme: str,
        identifier_value: str,
        reporting_cutoff: date,
        programme_start_date: date | None,
        status: str,
        http_status: int | None,
        locator: str,
        media_type: str | None,
        content_hash: str | None,
        byte_size: int | None,
        published_at: datetime | None,
        classification: str,
        error_code: str | None,
        error_message: str | None,
        facts: list[dict[str, object]],
        events: list[dict[str, object]],
        contract_version: str,
    ) -> str:
        payload: dict[str, object] = {
            "source_key": source_key,
            "source_version": source_version,
            "company_id": company_id,
            "identifier_scheme": identifier_scheme,
            "identifier_value": identifier_value,
            "reporting_cutoff": reporting_cutoff.isoformat(),
            "status": status,
            "http_status": http_status,
            "locator": locator,
            "media_type": media_type,
            "content_sha256": content_hash,
            "byte_size": byte_size,
            # retrieved_at identifies a collection attempt, not the semantic result;
            # including it would make identical forced refreshes appear to drift.
            "published_at": cls._canonical_datetime(published_at),
            "classification": classification,
            "error_code": error_code,
            "error_message": error_message,
            "facts": sorted(facts, key=stable_hash),
            "events": sorted(events, key=stable_hash),
        }
        if contract_version == SOURCE_DERIVATION_CONTRACT_VERSION:
            payload.update(
                {
                    "contract_version": contract_version,
                    "programme_start_date": (
                        programme_start_date.isoformat() if programme_start_date else None
                    ),
                }
            )
        return stable_hash(payload)

    @classmethod
    def _fact_derivation_payload(
        cls,
        *,
        company_id: str,
        fact_key: str,
        value: object,
        source_locator: str,
        unit: str | None,
        currency: str | None,
        period_start: date | None,
        period_end: date | None,
        effective_at: datetime | None,
        published_at: datetime | None,
        metric_key: str | None,
        structured_locator: Mapping[str, object],
        extraction_method: str,
        extraction_schema_version: str,
        contract_version: str,
    ) -> dict[str, object]:
        payload: dict[str, object] = {
            "company_id": company_id,
            "fact_key": fact_key,
            "value": value,
            "source_locator": source_locator,
            "unit": unit,
            "currency": currency,
            "period_start": period_start.isoformat() if period_start else None,
            "period_end": period_end.isoformat() if period_end else None,
            "effective_at": cls._canonical_datetime(effective_at),
            "published_at": cls._canonical_datetime(published_at),
            "metric_key": metric_key,
        }
        if contract_version == SOURCE_DERIVATION_CONTRACT_VERSION:
            payload.update(
                {
                    "structured_locator": dict(structured_locator),
                    "extraction_method": extraction_method,
                    "extraction_schema_version": extraction_schema_version,
                }
            )
        return payload

    @classmethod
    def _event_derivation_payload(
        cls,
        *,
        event_fingerprint: str,
        company_id: str,
        source_key: str,
        event_type: str,
        title: str,
        source_locator: str,
        public_identifier: str | None,
        lifecycle_stage: str | None,
        event_date: date | None,
        amount: object,
        currency: str | None,
        details: Mapping[str, object],
        classification: str,
    ) -> dict[str, object]:
        return {
            "event_fingerprint": event_fingerprint,
            "company_id": company_id,
            "source_key": source_key,
            "event_type": event_type,
            "title": title,
            "source_locator": source_locator,
            "public_identifier": public_identifier,
            "lifecycle_stage": lifecycle_stage,
            "event_date": event_date.isoformat() if event_date else None,
            "amount": cls._canonical_event_amount(amount),
            "currency": currency,
            "details": dict(details),
            "classification": classification,
        }

    @staticmethod
    def _canonical_datetime(value: datetime | None) -> str | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()

    @staticmethod
    def _canonical_event_amount(value: object) -> str | None:
        if value is None:
            return None
        raw = Decimal(str(value))
        if not raw.is_finite():
            raise SourceContractError("Event amount must be finite.")
        canonical = raw.quantize(Decimal("0.0001"))
        if canonical != raw:
            raise SourceContractError(
                "Event amount exceeds the canonical four-decimal storage precision."
            )
        return format(canonical, "f")

    def _verify_stored_snapshot(self, snapshot: SourceSnapshotModel) -> None:
        if snapshot.snapshot_path is None and snapshot.sha256 is None:
            if snapshot.status != CollectionStatus.SUCCEEDED.value:
                return
            raise SourceContractError("Successful snapshot is missing its immutable artifact.")
        if snapshot.snapshot_path is None or snapshot.sha256 is None:
            raise SourceContractError("Snapshot artifact metadata is incomplete.")
        path = Path(snapshot.snapshot_path).resolve()
        if not path.is_relative_to(self._snapshot_root) or not path.is_file():
            raise SourceContractError("Stored source snapshot is outside the registry or missing.")
        if sha256_bytes(path.read_bytes()) != snapshot.sha256:
            raise SourceChecksumDriftError("Stored source snapshot checksum verification failed.")

    def _validate_request(self, request: SourceRequest, manifest: SourceCapabilityManifest) -> str:
        if request.source_key != manifest.key:
            raise SourceContractError("Request source key does not match connector manifest.")
        if not request.company_id or not request.identifier_value.strip():
            raise SourceContractError("Source collection requires an exact company and identifier.")
        if request.company_id.startswith("benchmark:"):
            raise SourceContractError(
                "Benchmark identifiers cannot be attached to operational source snapshots."
            )
        if request.identifier_scheme not in manifest.identifier_schemes:
            raise SourceContractError("Identifier scheme is unsupported by this source.")
        if request.mode not in manifest.retrieval_modes:
            raise SourceContractError("Retrieval mode is unsupported by this source.")
        if request.mode != "offline_snapshot" and not manifest.live_retrieval_admitted:
            raise SourceContractError(
                "Live retrieval is held until licence, terms, and admission review are recorded."
            )
        unsupported_facts = set(request.fact_keys) - set(manifest.fact_keys)
        if unsupported_facts:
            raise SourceContractError("Request includes facts outside the source capability.")
        if (
            request.programme_start_date is not None
            and request.programme_start_date > request.reporting_cutoff
        ):
            raise SourceContractError("Programme start date must not follow the reporting cutoff.")
        normalized_identifier = normalize_identifier(
            request.identifier_scheme, request.identifier_value
        )
        with self._session_factory() as session:
            company = session.get(CompanyModel, request.company_id)
            identifier = session.scalar(
                select(CompanyIdentifierModel).where(
                    CompanyIdentifierModel.company_id == request.company_id,
                    CompanyIdentifierModel.scheme == request.identifier_scheme.value,
                    CompanyIdentifierModel.normalized_value == normalized_identifier,
                    CompanyIdentifierModel.source_key == request.source_key,
                    CompanyIdentifierModel.reviewed.is_(True),
                )
            )
            if company is None:
                raise SourceContractError("Source request references an unknown company.")
            if company.resolution_status != ResolutionStatus.RESOLVED.value:
                raise SourceContractError(
                    "Source collection requires a human-resolved company identity."
                )
            if identifier is None:
                raise SourceContractError(
                    "Source request identifier is not an exact reviewed identifier for this "
                    "company and source."
                )
            if (
                identifier.valid_from is not None
                and identifier.valid_from > request.reporting_cutoff
            ):
                raise SourceContractError(
                    "Source identifier was not valid by the reporting cutoff."
                )
            if identifier.valid_to is not None and identifier.valid_to < request.reporting_cutoff:
                raise SourceContractError("Source identifier expired before the reporting cutoff.")
        return normalized_identifier

    def _validate_collection(
        self,
        collection: SourceCollection,
        request: SourceRequest,
        manifest: SourceCapabilityManifest,
    ) -> None:
        self._require_aware(collection.retrieved_at, "collection retrieved_at")
        if collection.published_at is not None:
            self._require_aware(collection.published_at, "collection published_at")
        if not collection.locator.strip():
            raise SourceContractError("Source collection requires a non-empty locator.")
        if collection.status is CollectionStatus.SUCCEEDED:
            if not collection.content or not collection.media_type:
                raise SourceContractError(
                    "Successful collection requires non-empty snapshot bytes and a media type."
                )
            if collection.error_code or collection.error_message:
                raise SourceContractError("Successful collection cannot carry terminal errors.")
        elif collection.facts or collection.events:
            raise SourceContractError("Non-successful collection cannot contain facts or events.")
        if collection.status in {
            CollectionStatus.SOURCE_UNAVAILABLE,
            CollectionStatus.FAILED,
        } and (collection.content is not None or collection.media_type is not None):
            raise SourceContractError(
                "Transient source failures must not persist response bodies as evidence."
            )
        if (collection.content is None) != (collection.media_type is None):
            raise SourceContractError(
                "Snapshot content and media type must either both be present or both be absent."
            )
        if collection.media_type is not None and collection.media_type not in manifest.media_types:
            raise SourceContractError("Collection media type is outside the source manifest.")

        fact_contracts = {contract.fact_key: contract for contract in manifest.fact_contracts}
        returned_fact_keys = {fact.fact_key for fact in collection.facts}
        if not returned_fact_keys.issubset(manifest.fact_keys):
            raise SourceContractError("Connector returned a fact outside its manifest.")
        if request.fact_keys and not returned_fact_keys.issubset(request.fact_keys):
            raise SourceContractError("Connector returned a fact that was not requested.")
        returned_event_types = {event.event_type for event in collection.events}
        if not returned_event_types.issubset(manifest.event_types):
            raise SourceContractError("Connector returned an event outside its manifest.")

        with self._session_factory() as session:
            metric_definitions = {
                row.key: row for row in session.scalars(select(MetricDefinitionModel)).all()
            }
        fact_identities: set[tuple[str, str]] = set()
        for fact in collection.facts:
            if not fact.fact_key.strip() or not fact.source_locator.strip():
                raise SourceContractError("Collected facts require keys and evidence locators.")
            if not fact.structured_locator or not isinstance(fact.structured_locator, dict):
                raise SourceContractError("Collected facts require a structured source locator.")
            if not fact.extraction_method.strip() or not fact.extraction_schema_version.strip():
                raise SourceContractError(
                    "Collected facts require extraction method and schema provenance."
                )
            if fact.metric_key is not None and fact.metric_key not in metric_definitions:
                raise SourceContractError("Connector returned an undeclared metric key.")
            contract = fact_contracts[fact.fact_key]
            if fact.metric_key not in contract.metric_keys:
                raise SourceContractError(
                    "Connector fact metric binding is outside its source-fact contract."
                )
            if fact.extraction_method != contract.extraction_method:
                raise SourceContractError(
                    "Connector fact extraction method is outside its source-fact contract."
                )
            if fact.extraction_schema_version != contract.extraction_schema_version:
                raise SourceContractError(
                    "Connector fact extraction schema is outside its source-fact contract."
                )
            if fact.unit != contract.unit or fact.currency != contract.currency:
                raise SourceContractError(
                    "Connector fact unit or currency is outside its source-fact contract."
                )
            identity = (fact.fact_key, fact.source_locator)
            if identity in fact_identities:
                raise SourceContractError("Connector returned a duplicate fact locator.")
            fact_identities.add(identity)
            if fact.metric_key is not None and (
                (fact.period_start is None) != (fact.period_end is None)
            ):
                raise SourceContractError("Collected fact periods require both interval bounds.")
            if fact.period_start is not None and fact.period_end is not None:
                if fact.period_start > fact.period_end:
                    raise SourceContractError("Collected fact period has reversed bounds.")
                if fact.period_end > request.reporting_cutoff:
                    raise SourceContractError(
                        "Collected fact period extends beyond the reporting cutoff."
                    )
            if fact.metric_key is not None:
                metric = metric_definitions[fact.metric_key]
                if metric.period_semantics == PeriodSemantics.SINCE_PROGRAMME_START.value:
                    if request.programme_start_date is None:
                        raise SourceContractError(
                            "Cumulative public metric facts require a programme start date."
                        )
                    if (
                        fact.period_start != request.programme_start_date
                        or fact.period_end != request.reporting_cutoff
                    ):
                        raise SourceContractError(
                            "Cumulative public metric fact interval does not match its request."
                        )
            if fact.published_at is not None:
                self._require_aware(fact.published_at, "fact published_at")
            if fact.effective_at is not None:
                self._require_aware(fact.effective_at, "fact effective_at")

        event_identities: set[str] = set()
        for event in collection.events:
            if (
                not event.event_type.strip()
                or not event.title.strip()
                or not event.source_locator.strip()
            ):
                raise SourceContractError("Collected events require a type, title, and locator.")
            event_fingerprint = self._event_fingerprint(
                company_id=request.company_id,
                source_key=request.source_key,
                event=event,
            )
            if event_fingerprint in event_identities:
                raise SourceContractError("Connector returned a duplicate canonical event.")
            event_identities.add(event_fingerprint)

    @staticmethod
    def _require_aware(value: datetime, field: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise SourceContractError(f"{field} must include a timezone.")

    @staticmethod
    def _validate_manifest(manifest: SourceCapabilityManifest) -> None:
        policy = next(
            (source for source in ADMITTED_PUBLIC_SOURCES if source.key == manifest.key), None
        )
        if policy is None:
            raise SourceContractError("Connector key is not admitted by the source policy.")
        expected_scheme = IdentifierScheme(policy.identifier_scheme)
        if set(manifest.identifier_schemes) != {expected_scheme}:
            raise SourceContractError(
                "Connector identifier schemes do not match the admitted source policy."
            )
        if not manifest.fact_contracts:
            raise SourceContractError("Source manifest requires explicit fact contracts.")
        fact_keys = [contract.fact_key for contract in manifest.fact_contracts]
        if any(not key.strip() for key in fact_keys) or len(fact_keys) != len(set(fact_keys)):
            raise SourceContractError("Source fact-contract keys must be unique and non-empty.")
        for contract in manifest.fact_contracts:
            if not contract.metric_keys or len(contract.metric_keys) != len(
                set(contract.metric_keys)
            ):
                raise SourceContractError(
                    "Source fact contracts require unique allowed metric bindings."
                )
            if (
                not contract.extraction_method.strip()
                or not contract.extraction_schema_version.strip()
            ):
                raise SourceContractError(
                    "Source fact contracts require extraction method and schema."
                )
        if not manifest.retrieval_modes or not set(manifest.retrieval_modes).issubset(
            policy.retrieval_modes
        ):
            raise SourceContractError(
                "Connector retrieval modes do not match the admitted source policy."
            )
        if manifest.public_only != policy.public_only:
            raise SourceContractError(
                "Connector public-only boundary does not match the admitted source policy."
            )
        for label, values in (
            ("fact keys", manifest.fact_keys),
            ("event types", manifest.event_types),
            ("media types", manifest.media_types),
            ("retrieval modes", manifest.retrieval_modes),
        ):
            if len(values) != len(set(values)) or any(not value.strip() for value in values):
                raise SourceContractError(f"Source manifest has invalid or duplicate {label}.")
        if not manifest.licence_reference or not manifest.licence_reference.strip():
            raise SourceContractError("Source manifest is missing its licence evidence state.")
        if not manifest.terms_reference or not manifest.terms_reference.strip():
            raise SourceContractError("Source manifest is missing its terms evidence state.")
        if manifest.live_retrieval_admitted:
            if manifest.admission_reviewed_at is None:
                raise SourceContractError(
                    "A live-admitted source requires a dated admission review."
                )
            if any(
                "EVIDENCE_REQUIRED" in reference
                for reference in (manifest.licence_reference, manifest.terms_reference)
            ):
                raise SourceContractError(
                    "A live-admitted source cannot retain an evidence-required marker."
                )

    @staticmethod
    def _event_fingerprint(*, company_id: str, source_key: str, event: CollectedEvent) -> str:
        details = event.details or {}
        return stable_hash(
            {
                "company_id": company_id,
                "source_key": source_key,
                "event_type": event.event_type,
                "public_identifier": event.public_identifier or event.source_locator,
                "event_date": event.event_date.isoformat() if event.event_date else None,
                "record_version": details.get("record_version"),
            }
        )

    @classmethod
    def _persist_event(
        cls,
        session: Session,
        *,
        snapshot: SourceSnapshotModel,
        company_id: str,
        source_key: str,
        event: CollectedEvent,
        classification: DataClassification,
    ) -> CompanyEventModel:
        fingerprint = cls._event_fingerprint(
            company_id=company_id,
            source_key=source_key,
            event=event,
        )
        canonical_amount = cls._canonical_event_amount(event.amount)
        amount = Decimal(canonical_amount) if canonical_amount is not None else None
        canonical = {
            "company_id": company_id,
            "source_key": source_key,
            "event_type": event.event_type,
            "lifecycle_stage": event.lifecycle_stage,
            "public_identifier": event.public_identifier,
            "event_date": event.event_date,
            "amount": amount,
            "currency": event.currency,
            "title": event.title,
            "source_locator": event.source_locator,
            "details": event.details or {},
            "classification": classification.value,
        }
        stored = session.scalar(
            select(CompanyEventModel).where(CompanyEventModel.event_fingerprint == fingerprint)
        )
        if stored is not None:
            cls._assert_event_matches(stored, canonical)
            return stored
        stored = CompanyEventModel(
            event_fingerprint=fingerprint,
            company_id=company_id,
            source_snapshot_id=snapshot.id,
            raw_submission_id=None,
            source_key=source_key,
            event_type=event.event_type,
            lifecycle_stage=event.lifecycle_stage,
            public_identifier=event.public_identifier,
            event_date=event.event_date,
            amount=amount,
            currency=event.currency,
            title=event.title,
            details_json=event.details or {},
            source_locator=event.source_locator,
            classification=classification.value,
        )
        try:
            with session.begin_nested():
                session.add(stored)
                session.flush()
            return stored
        except IntegrityError:
            winner = session.scalar(
                select(CompanyEventModel).where(CompanyEventModel.event_fingerprint == fingerprint)
            )
            if winner is None:
                raise
            cls._assert_event_matches(winner, canonical)
            return winner

    @staticmethod
    def _assert_event_matches(stored: CompanyEventModel, canonical: Mapping[str, object]) -> None:
        persisted = {
            "company_id": stored.company_id,
            "source_key": stored.source_key,
            "event_type": stored.event_type,
            "lifecycle_stage": stored.lifecycle_stage,
            "public_identifier": stored.public_identifier,
            "event_date": stored.event_date,
            "amount": stored.amount,
            "currency": stored.currency,
            "title": stored.title,
            "source_locator": stored.source_locator,
            "details": stored.details_json,
            "classification": stored.classification,
        }
        if stable_hash(persisted) != stable_hash(canonical):
            raise SourceChecksumDriftError(
                "A canonical event fingerprint was reused with changed event content."
            )

    @staticmethod
    def _assert_allowed_classification(
        classification: DataClassification | str,
        manifest: SourceCapabilityManifest,
    ) -> None:
        try:
            resolved = DataClassification(classification)
        except ValueError as exc:
            raise SourceContractError("Source content has an unsupported classification.") from exc
        if resolved is DataClassification.PUBLIC:
            if not manifest.live_retrieval_admitted:
                raise SourceContractError(
                    "Public source content is held until its live admission is approved."
                )
        elif resolved is not DataClassification.SYNTHETIC:
            raise SourceContractError(
                "Source connectors may persist only public or synthetic evidence."
            )

    @staticmethod
    def _seed_manifest(session: Session, manifest: SourceCapabilityManifest) -> None:
        payload = asdict(manifest)
        payload["identifier_schemes"] = [scheme.value for scheme in manifest.identifier_schemes]
        payload["admission_reviewed_at"] = (
            manifest.admission_reviewed_at.isoformat()
            if manifest.admission_reviewed_at is not None
            else None
        )
        manifest_hash = stable_hash(payload)
        existing = session.scalar(
            select(SourceDefinitionModel).where(
                SourceDefinitionModel.key == manifest.key,
                SourceDefinitionModel.version == manifest.version,
            )
        )
        if existing is None:
            session.execute(
                update(SourceDefinitionModel)
                .where(
                    SourceDefinitionModel.key == manifest.key,
                    SourceDefinitionModel.version != manifest.version,
                )
                .values(active=False)
            )
            session.add(
                SourceDefinitionModel(
                    key=manifest.key,
                    version=manifest.version,
                    publisher=manifest.publisher,
                    manifest_json=payload,
                    manifest_sha256=manifest_hash,
                    admitted=manifest.live_retrieval_admitted,
                    active=True,
                )
            )
        elif existing.manifest_sha256 != manifest_hash:
            raise SourceContractError("Source manifest version was reused with changed semantics.")
        else:
            existing.active = True

    def _write_snapshot(
        self,
        *,
        source_key: str,
        request_fingerprint: str,
        checksum: str,
        content: bytes,
    ) -> tuple[Path, bool]:
        target_dir = self._snapshot_root / source_key / request_fingerprint
        target_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        target = target_dir / f"{checksum}.bin"
        if target.exists():
            if sha256_bytes(target.read_bytes()) != checksum:
                raise SourceChecksumDriftError(
                    "Immutable source snapshot path contains different bytes."
                )
            return target, False
        descriptor, staging_name = tempfile.mkstemp(
            prefix=f".{checksum}.", suffix=".staging", dir=target_dir
        )
        staging = Path(staging_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            staging.chmod(0o600)
            try:
                os.link(staging, target)
                created = True
            except FileExistsError:
                created = False
            if sha256_bytes(target.read_bytes()) != checksum:
                raise SourceChecksumDriftError(
                    "Immutable source snapshot path contains different bytes."
                )
            return target, created
        finally:
            staging.unlink(missing_ok=True)

    @staticmethod
    def replay_collection(
        *,
        content: bytes,
        locator: str,
        media_type: str,
        published_at: datetime | None = None,
    ) -> SourceCollection:
        return SourceCollection(
            status=CollectionStatus.SUCCEEDED,
            locator=locator,
            retrieved_at=datetime.now(UTC),
            content=content,
            media_type=media_type,
            published_at=published_at,
        )
