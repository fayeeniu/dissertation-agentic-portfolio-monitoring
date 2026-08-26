from __future__ import annotations

from portfolio_agent.schemas import StrictExtraction
from portfolio_agent.security import contains_prompt_injection

from .base import ExtractionRequest, ProviderOutcome


class DeterministicExtractionProvider:
    name = "deterministic_structured_extractor"

    def extract(self, request: ExtractionRequest) -> ProviderOutcome:
        evidence = request.evidence
        if evidence.is_untrusted or contains_prompt_injection(evidence.content):
            raise ValueError("Untrusted evidence is not eligible for extraction.")
        content = evidence.content
        company_name = content.get("company_name")
        metric_key = content.get("metric_key")
        period_label = content.get("period_label")
        if not all(isinstance(item, str) for item in (company_name, metric_key, period_label)):
            raise ValueError("Structured evidence is missing identity, metric, or period fields.")
        extraction = StrictExtraction(
            company_name=company_name,
            metric_key=metric_key,
            value=content.get("value"),
            unit=content.get("unit") if isinstance(content.get("unit"), str) else None,
            currency=(
                content.get("currency") if isinstance(content.get("currency"), str) else None
            ),
            period_label=period_label,
            evidence_locator=evidence.locator,
            confidence=1.0,
        )
        return ProviderOutcome(
            extraction=extraction,
            provider=self.name,
            model=None,
            attempts=1,
        )
