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
class ProviderAttempt:
    attempt_number: int
    provider: str
    model: str | None
    status: str
    duration_ms: int
    input_hash: str
    output_hash: str | None = None
    prompt_version: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    error: str | None = None
    escalation_cause: str | None = None


@dataclass(frozen=True, slots=True)
class ProviderOutcome:
    extraction: StrictExtraction
    provider: str
    model: str | None
    attempts: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    attempt_records: tuple[ProviderAttempt, ...] = ()


class ExtractionProviderError(RuntimeError):
    def __init__(self, message: str, attempts: tuple[ProviderAttempt, ...]) -> None:
        super().__init__(message)
        self.attempt_records = attempts


class ExtractionProvider(Protocol):
    name: str

    def extract(self, request: ExtractionRequest) -> ProviderOutcome: ...
