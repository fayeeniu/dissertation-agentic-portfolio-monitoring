from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from portfolio_agent.enums import DataClassification
from portfolio_agent.ids import sha256_bytes
from portfolio_agent.schemas import EvidenceItem
from portfolio_agent.security import contains_prompt_injection

from .base import ConnectorQuery


class _FixtureEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    company_name: str
    external_id: str | None = None
    metric_key: str
    period_label: str
    value: str | int | bool | None
    unit: str | None = None
    currency: str | None = None
    publisher: str
    published_at: datetime | None = None
    locator: str
    narrative: str
    marked_untrusted: bool = False


class _FixtureDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    evidence: tuple[_FixtureEvidence, ...]


class FixtureConnector:
    name = "fixture_connector"
    version = "1.0.0"

    def __init__(self, document: _FixtureDocument) -> None:
        self._document = document

    @classmethod
    def from_path(cls, path: Path) -> FixtureConnector:
        return cls(_FixtureDocument.model_validate_json(path.read_text(encoding="utf-8")))

    def collect(self, query: ConnectorQuery) -> tuple[EvidenceItem, ...]:
        matches: list[EvidenceItem] = []
        for record in self._document.evidence:
            identity_match = (
                query.external_id is not None
                and record.external_id is not None
                and query.external_id == record.external_id
            ) or query.company_name.casefold().strip() == record.company_name.casefold().strip()
            if not identity_match or record.metric_key != query.metric_key:
                continue
            content: dict[str, Any] = {
                "company_name": record.company_name,
                "external_id": record.external_id,
                "metric_key": record.metric_key,
                "period_label": record.period_label,
                "value": record.value,
                "unit": record.unit,
                "currency": record.currency,
                "narrative": record.narrative,
            }
            canonical = json.dumps(content, sort_keys=True, default=str).encode()
            is_untrusted = record.marked_untrusted or contains_prompt_injection(content)
            matches.append(
                EvidenceItem(
                    id=record.id,
                    company_id=query.company_id,
                    metric_key=query.metric_key,
                    source_type="synthetic_public_fixture",
                    connector=self.name,
                    locator=record.locator,
                    publisher=record.publisher,
                    retrieved_at=datetime.now(UTC),
                    published_at=record.published_at,
                    content=content,
                    checksum=sha256_bytes(canonical),
                    connector_version=self.version,
                    classification=DataClassification.SYNTHETIC,
                    is_untrusted=is_untrusted,
                )
            )
        return tuple(matches)
