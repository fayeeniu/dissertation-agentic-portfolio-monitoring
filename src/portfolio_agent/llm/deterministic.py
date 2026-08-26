from __future__ import annotations

from portfolio_agent.ids import stable_hash
from portfolio_agent.schemas import StrictExtraction
from portfolio_agent.security import contains_prompt_injection

from .base import ExtractionRequest, ProviderAttempt, ProviderOutcome


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
            evidence_span=(str(content.get("value")) if content.get("value") is not None else None),
            abstain_reason=("source_value_is_null" if content.get("value") is None else None),
            confidence=1.0,
        )
        attempt = ProviderAttempt(
            attempt_number=1,
            provider=self.name,
            model=None,
            status="succeeded" if extraction.value is not None else "abstained",
            duration_ms=0,
            input_hash=stable_hash(
                {
                    "evidence_id": evidence.id,
                    "company": request.expected_company_name,
                    "metric": request.expected_metric_key,
                    "period": request.expected_period_label,
                }
            ),
            output_hash=stable_hash(extraction.model_dump(mode="json")),
        )
        return ProviderOutcome(
            extraction=extraction,
            provider=self.name,
            model=None,
            attempts=1,
            attempt_records=(attempt,),
        )
