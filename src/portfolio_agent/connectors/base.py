from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from portfolio_agent.schemas import EvidenceItem


@dataclass(frozen=True, slots=True)
class ConnectorQuery:
    company_id: str
    company_name: str
    external_id: str | None
    metric_key: str
    period_label: str


class Connector(Protocol):
    name: str
    version: str

    def collect(self, query: ConnectorQuery) -> tuple[EvidenceItem, ...]: ...
