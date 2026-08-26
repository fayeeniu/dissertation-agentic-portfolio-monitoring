from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from portfolio_agent.schemas import EvidenceItem, StrictExtraction


@dataclass(frozen=True, slots=True)
class ExtractionRequest:
    evidence: EvidenceItem
    expected_company_name: str
    expected_metric_key: str
    expected_period_label: str


@dataclass(frozen=True, slots=True)
class ProviderOutcome:
    extraction: StrictExtraction
    provider: str
    model: str | None
    attempts: int
    input_tokens: int | None = None
    output_tokens: int | None = None


class ExtractionProvider(Protocol):
    name: str

    def extract(self, request: ExtractionRequest) -> ProviderOutcome: ...
