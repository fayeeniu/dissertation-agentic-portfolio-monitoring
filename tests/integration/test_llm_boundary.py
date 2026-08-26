from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from portfolio_agent.bootstrap import create_runtime
from portfolio_agent.config import Settings
from portfolio_agent.enums import DataClassification
from portfolio_agent.llm.base import ExtractionProviderError, ExtractionRequest
from portfolio_agent.llm.openai_provider import OpenAIStructuredExtractionProvider
from portfolio_agent.schemas import EvidenceItem, StrictExtraction


@dataclass
class _FakeResponse:
    output_text: str
    usage: Any = field(default_factory=lambda: SimpleNamespace(input_tokens=11, output_tokens=7))


class _FakeResponses:
    def __init__(self, outputs: list[str]) -> None:
        self._outputs = outputs
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> _FakeResponse:
        self.calls.append(kwargs)
        return _FakeResponse(self._outputs.pop(0))


class _FakeClient:
    def __init__(self, outputs: list[str]) -> None:
        self.responses = _FakeResponses(outputs)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        project_root=tmp_path,
        database_url=f"sqlite:///{tmp_path / 'llm.db'}",
        raw_data_dir=tmp_path / "raw",
        allow_external_llm=True,
        openai_model="gpt-5.4-mini",
        openai_escalation_model="gpt-5.4",
    )


def _request(classification: DataClassification) -> ExtractionRequest:
    evidence = EvidenceItem(
        id="ev-public",
        company_id="co-public",
        metric_key="grant_funding",
        source_type="synthetic_public_fixture",
        connector="mock",
        locator="fixture://public/exact",
        publisher="Synthetic publisher",
        retrieved_at="2025-06-30T12:00:00Z",
        published_at="2025-06-20T12:00:00Z",
        content={
            "company_name": "Public Synthetic Ltd",
            "metric_key": "grant_funding",
            "period_label": "2025-Q2",
            "value": "GBP 100",
        },
        checksum="abc",
        connector_version="test",
        classification=classification,
    )
    return ExtractionRequest(
        evidence=evidence,
        expected_company_name="Public Synthetic Ltd",
        expected_metric_key="grant_funding",
        expected_period_label="2025-Q2",
    )


def _valid_output() -> str:
    return json.dumps(
        {
            "company_name": "Public Synthetic Ltd",
            "metric_key": "grant_funding",
            "value": "100",
            "unit": "currency_units",
            "currency": "GBP",
            "period_label": "2025-Q2",
            "evidence_locator": "fixture://public/exact",
            "evidence_span": "GBP 100",
            "abstain_reason": None,
            "confidence": 0.9,
        }
    )


def test_restricted_content_is_rejected_before_client_invocation(tmp_path: Path) -> None:
    client = _FakeClient([_valid_output()])
    provider = OpenAIStructuredExtractionProvider(_settings(tmp_path), client=client)

    with pytest.raises(PermissionError, match="cannot be sent"):
        provider.extract(_request(DataClassification.RESTRICTED))
    assert client.responses.calls == []


@pytest.mark.parametrize(
    ("model", "escalation_model"),
    (
        ("unapproved-model", "gpt-5.4"),
        ("gpt-5.4", "gpt-5.4-mini"),
        ("gpt-5.4-mini", "gpt-5.4-mini"),
    ),
)
def test_external_provider_rejects_unapproved_model_sequence(
    tmp_path: Path,
    model: str,
    escalation_model: str,
) -> None:
    settings = replace(
        _settings(tmp_path),
        openai_model=model,
        openai_escalation_model=escalation_model,
    )
    with pytest.raises(ValueError, match="approved model sequence"):
        OpenAIStructuredExtractionProvider(settings, client=_FakeClient([_valid_output()]))


def test_validation_failure_escalates_once_and_retains_attempt_telemetry(
    tmp_path: Path,
) -> None:
    wrong_locator = json.loads(_valid_output())
    wrong_locator["evidence_locator"] = "fixture://invented"
    client = _FakeClient([json.dumps(wrong_locator), _valid_output()])
    provider = OpenAIStructuredExtractionProvider(_settings(tmp_path), client=client)

    outcome = provider.extract(_request(DataClassification.SYNTHETIC))

    assert [call["model"] for call in client.responses.calls] == ["gpt-5.4-mini", "gpt-5.4"]
    assert all(call["store"] is False for call in client.responses.calls)
    assert outcome.attempts == 2
    assert [attempt.status for attempt in outcome.attempt_records] == ["failed", "succeeded"]
    assert outcome.attempt_records[1].escalation_cause == "first_model_validation_failure"
    assert outcome.input_tokens == 11
    assert outcome.output_tokens == 7


def test_two_invalid_responses_fail_without_unbounded_retry(tmp_path: Path) -> None:
    client = _FakeClient(["not-json", "still-not-json"])
    provider = OpenAIStructuredExtractionProvider(_settings(tmp_path), client=client)

    with pytest.raises(ExtractionProviderError) as caught:
        provider.extract(_request(DataClassification.PUBLIC))

    assert len(client.responses.calls) == 2
    assert len(caught.value.attempt_records) == 2
    assert all(attempt.status == "failed" for attempt in caught.value.attempt_records)


def test_hallucinated_value_or_span_cannot_pass_strict_validation(tmp_path: Path) -> None:
    wrong_value = json.loads(_valid_output())
    wrong_value["value"] = "200"
    missing_span = json.loads(_valid_output())
    missing_span["evidence_span"] = "not present in evidence"
    client = _FakeClient([json.dumps(wrong_value), json.dumps(missing_span)])
    provider = OpenAIStructuredExtractionProvider(_settings(tmp_path), client=client)

    with pytest.raises(ExtractionProviderError) as caught:
        provider.extract(_request(DataClassification.SYNTHETIC))
    assert len(caught.value.attempt_records) == 2
    assert all(attempt.status == "failed" for attempt in caught.value.attempt_records)


def test_truncated_structured_numeric_span_is_rejected() -> None:
    request = _request(DataClassification.SYNTHETIC)
    request.evidence.content["value"] = "1000"
    extraction = StrictExtraction.model_validate(
        {
            **json.loads(_valid_output()),
            "value": "100",
            "unit": None,
            "currency": None,
            "evidence_span": "100",
        }
    )
    with pytest.raises(ValueError, match="complete structured source value"):
        OpenAIStructuredExtractionProvider._validate_extraction(extraction, request)


@pytest.mark.parametrize(
    ("source", "value", "currency", "unit"),
    (
        ("1000", "1000", None, None),
        ("-100", "-100", None, None),
        ("GBP 2 million", "2000000", "GBP", "currency_units"),
        ("12%", "12", None, "percentage_points"),
        ("£100", "100", "GBP", "currency_units"),
    ),
)
def test_complete_signed_scaled_percentage_and_currency_spans_are_grounded(
    source: str,
    value: str,
    currency: str | None,
    unit: str | None,
) -> None:
    request = _request(DataClassification.SYNTHETIC)
    request.evidence.content["value"] = source
    extraction = StrictExtraction.model_validate(
        {
            **json.loads(_valid_output()),
            "value": value,
            "currency": currency,
            "unit": unit,
            "evidence_span": source,
        }
    )
    OpenAIStructuredExtractionProvider._validate_extraction(extraction, request)


def test_model_currency_requires_grounding_in_span_or_structured_sibling() -> None:
    request = _request(DataClassification.SYNTHETIC)
    request.evidence.content["value"] = "100"
    extraction = StrictExtraction.model_validate(
        {
            **json.loads(_valid_output()),
            "value": "100",
            "currency": "GBP",
            "unit": "currency_units",
            "evidence_span": "100",
        }
    )

    with pytest.raises(ValueError, match="currency is not grounded"):
        OpenAIStructuredExtractionProvider._validate_extraction(extraction, request)

    request.evidence.content["currency"] = "GBP"
    request.evidence.content["unit"] = "currency_units"
    OpenAIStructuredExtractionProvider._validate_extraction(extraction, request)


@pytest.mark.parametrize(
    ("leaf", "truncated"),
    (
        ("The award was 1000 GBP.", "100"),
        ("The award was -1000 GBP.", "1000"),
        ("The award was 100 million GBP.", "100"),
        ("The margin was 100%.", "100"),
    ),
)
def test_free_text_numeric_spans_require_complete_tokens(leaf: str, truncated: str) -> None:
    request = _request(DataClassification.SYNTHETIC)
    request.evidence.content = {"statement": leaf}
    extraction = StrictExtraction.model_validate(
        {
            **json.loads(_valid_output()),
            "value": truncated,
            "unit": None,
            "currency": None,
            "evidence_span": truncated,
        }
    )
    with pytest.raises(ValueError, match="eligible evidence leaf"):
        OpenAIStructuredExtractionProvider._validate_extraction(extraction, request)


@pytest.mark.parametrize("source", ("NaN", "Infinity", "-Infinity"))
def test_non_finite_model_values_require_abstention(source: str) -> None:
    request = _request(DataClassification.SYNTHETIC)
    request.evidence.content["value"] = source
    extraction = StrictExtraction.model_validate(
        {
            **json.loads(_valid_output()),
            "value": source,
            "unit": None,
            "currency": None,
            "evidence_span": source,
        }
    )
    with pytest.raises(ValueError, match="Non-finite"):
        OpenAIStructuredExtractionProvider._validate_extraction(extraction, request)


def test_metadata_number_cannot_ground_a_missing_source_value(tmp_path: Path) -> None:
    request = _request(DataClassification.SYNTHETIC)
    request.evidence.content["value"] = None
    fabricated = json.loads(_valid_output())
    fabricated["value"] = "2025"
    fabricated["unit"] = None
    fabricated["currency"] = None
    fabricated["evidence_span"] = "2025-Q2"
    client = _FakeClient([json.dumps(fabricated), json.dumps(fabricated)])
    provider = OpenAIStructuredExtractionProvider(_settings(tmp_path), client=client)

    with pytest.raises(ExtractionProviderError):
        provider.extract(request)


def test_envelope_cutoff_cannot_ground_value_when_source_value_key_is_absent(
    tmp_path: Path,
) -> None:
    request = _request(DataClassification.SYNTHETIC)
    del request.evidence.content["value"]
    request.evidence.content["reporting_cutoff"] = "2025-06-30"
    fabricated = json.loads(_valid_output())
    fabricated["value"] = "2025"
    fabricated["unit"] = None
    fabricated["currency"] = None
    fabricated["evidence_span"] = "2025"
    provider = OpenAIStructuredExtractionProvider(
        _settings(tmp_path),
        client=_FakeClient([json.dumps(fabricated), json.dumps(fabricated)]),
    )

    with pytest.raises(ExtractionProviderError):
        provider.extract(request)


def test_valid_model_abstention_is_audited_as_abstained(tmp_path: Path) -> None:
    request = _request(DataClassification.SYNTHETIC)
    request.evidence.content["value"] = None
    abstention = json.loads(_valid_output())
    abstention.update(
        {
            "value": None,
            "unit": None,
            "currency": None,
            "evidence_span": None,
            "abstain_reason": "source_value_is_null",
        }
    )
    provider = OpenAIStructuredExtractionProvider(
        _settings(tmp_path), client=_FakeClient([json.dumps(abstention)])
    )

    outcome = provider.extract(request)

    assert outcome.attempt_records[0].status == "abstained"


def test_default_runtime_refuses_open_external_gates_before_database_creation(
    tmp_path: Path,
) -> None:
    external_settings = _settings(tmp_path)
    with pytest.raises(RuntimeError, match="Gate G4"):
        create_runtime(external_settings)
    assert not (tmp_path / "llm.db").exists()

    live_settings = replace(
        external_settings,
        allow_external_llm=False,
        allow_live_public_retrieval=True,
    )
    with pytest.raises(RuntimeError, match="Gate G2"):
        create_runtime(live_settings)
    assert not (tmp_path / "llm.db").exists()
