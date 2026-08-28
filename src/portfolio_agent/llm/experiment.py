from __future__ import annotations

from portfolio_agent.enums import DataClassification

from .base import ExtractionProvider, ExtractionRequest, ProviderOutcome
from .deterministic import DeterministicExtractionProvider
from .openai_provider import OpenAIStructuredExtractionProvider

SYNTHETIC_EXPERIMENT_EVIDENCE_ID = "ev_syn_aster_products_narrative"
SYNTHETIC_EXPERIMENT_EVIDENCE_SHA256 = (
    "eb4e91485aa5460fd4470574988126d6d4907243f451a7686ff822f8744daf0f"
)


class SyntheticOpenAIExperimentProvider:
    """Route one checksum-pinned synthetic item externally and keep all others local."""

    name = "bounded_synthetic_openai_experiment"

    def __init__(
        self,
        live_provider: OpenAIStructuredExtractionProvider,
        fallback_provider: ExtractionProvider | None = None,
    ) -> None:
        self._live_provider = live_provider
        self._fallback_provider = fallback_provider or DeterministicExtractionProvider()

    def extract(self, request: ExtractionRequest) -> ProviderOutcome:
        evidence = request.evidence
        if evidence.id != SYNTHETIC_EXPERIMENT_EVIDENCE_ID:
            return self._fallback_provider.extract(request)
        if evidence.classification != DataClassification.SYNTHETIC:
            raise PermissionError("The live smoke path accepts synthetic evidence only.")
        if (
            evidence.source_type != "synthetic_public_fixture"
            or evidence.connector != "fixture_connector"
        ):
            raise PermissionError("The live smoke path accepts the checked-in fixture only.")
        if evidence.checksum != SYNTHETIC_EXPERIMENT_EVIDENCE_SHA256:
            raise PermissionError("The selected synthetic evidence checksum has changed.")
        return self._live_provider.extract(request)
