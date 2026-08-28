from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy import select

from portfolio_agent.bootstrap import create_openai_experiment_runtime, create_runtime, project_root
from portfolio_agent.cli import main
from portfolio_agent.config import Settings
from portfolio_agent.enums import DataClassification
from portfolio_agent.experiments import OpenAISmokeTestError, run_openai_synthetic_smoke
from portfolio_agent.llm.base import ExtractionProviderError, ExtractionRequest
from portfolio_agent.llm.deterministic import DeterministicExtractionProvider
from portfolio_agent.llm.experiment import (
    SYNTHETIC_EXPERIMENT_EVIDENCE_ID,
    SyntheticOpenAIExperimentProvider,
)
from portfolio_agent.llm.openai_provider import OpenAIStructuredExtractionProvider
from portfolio_agent.models import ExtractionModel
from portfolio_agent.schemas import EvidenceItem, StrictExtraction


@dataclass
class _FakeResponse:
    output_text: str
    model: str
    usage: Any = field(default_factory=lambda: SimpleNamespace(input_tokens=11, output_tokens=7))


class _FakeResponses:
    def __init__(self, outputs: list[str]) -> None:
        self._outputs = outputs
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> _FakeResponse:
        self.calls.append(kwargs)
        return _FakeResponse(self._outputs.pop(0), model=kwargs["model"])


class _FakeClient:
    def __init__(self, outputs: list[str]) -> None:
        self.responses = _FakeResponses(outputs)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        project_root=tmp_path,
        database_url=f"sqlite:///{tmp_path / 'llm.db'}",
        raw_data_dir=tmp_path / "raw",
        allow_external_llm=True,
        openai_model="gpt-5.6-luna",
        openai_escalation_model="gpt-5.6-luna",
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


def _valid_product_output() -> str:
    return json.dumps(
        {
            "company_name": "Aster Analytics",
            "metric_key": "products_launched",
            "value": 2,
            "unit": "products",
            "currency": None,
            "period_label": "SYN-2025-Q2",
            "evidence_locator": "fixture://news/aster/products",
            "evidence_span": "2",
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
        ("unapproved-model", "gpt-5.6-luna"),
        ("gpt-5.6-luna", "unapproved-model"),
        ("gpt-5.4-mini", "gpt-5.4"),
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
    with pytest.raises(ValueError, match="approved model route"):
        OpenAIStructuredExtractionProvider(settings, client=_FakeClient([_valid_output()]))


def test_validation_failure_repairs_once_and_retains_attempt_telemetry(
    tmp_path: Path,
) -> None:
    wrong_locator = json.loads(_valid_output())
    wrong_locator["evidence_locator"] = "fixture://invented"
    client = _FakeClient([json.dumps(wrong_locator), _valid_output()])
    provider = OpenAIStructuredExtractionProvider(_settings(tmp_path), client=client)

    outcome = provider.extract(_request(DataClassification.SYNTHETIC))

    assert [call["model"] for call in client.responses.calls] == [
        "gpt-5.6-luna",
        "gpt-5.6-luna",
    ]
    assert all(call["store"] is False for call in client.responses.calls)
    assert all(call["max_output_tokens"] == 512 for call in client.responses.calls)
    assert all(call["reasoning"] == {"effort": "none"} for call in client.responses.calls)
    assert all(
        'JSON number 2 becomes string "2"' in call["instructions"]
        for call in client.responses.calls
    )
    for call in client.responses.calls:
        schema = call["text"]["format"]["schema"]
        assert schema["required"] == list(schema["properties"])
        assert schema["additionalProperties"] is False
        for nullable_field in (
            "unit",
            "currency",
            "period_label",
            "evidence_span",
            "abstain_reason",
        ):
            field_schema = schema["properties"][nullable_field]
            assert {variant.get("type") for variant in field_schema["anyOf"]} >= {"null"}
            assert "default" not in field_schema
    assert outcome.attempts == 2
    assert [attempt.status for attempt in outcome.attempt_records] == ["failed", "succeeded"]
    assert outcome.attempt_records[0].input_tokens == 11
    assert outcome.attempt_records[0].output_tokens == 7
    assert outcome.attempt_records[1].escalation_cause == "first_model_validation_failure"
    assert outcome.input_tokens == 11
    assert outcome.output_tokens == 7
    assert outcome.model == "gpt-5.6-luna"


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


def test_synthetic_experiment_provider_rejects_changed_target_before_live_call(
    tmp_path: Path,
) -> None:
    client = _FakeClient([_valid_product_output()])
    live = OpenAIStructuredExtractionProvider(_settings(tmp_path), client=client)
    provider = SyntheticOpenAIExperimentProvider(live, DeterministicExtractionProvider())
    request = _request(DataClassification.SYNTHETIC)
    request.evidence.id = SYNTHETIC_EXPERIMENT_EVIDENCE_ID
    request.evidence.source_type = "synthetic_public_fixture"
    request.evidence.connector = "fixture_connector"

    with pytest.raises(PermissionError, match="checksum has changed"):
        provider.extract(request)
    assert client.responses.calls == []


def test_live_smoke_requires_command_acknowledgement() -> None:
    with pytest.raises(SystemExit, match="acknowledge-synthetic-only"):
        main(["openai-smoke"])


def test_live_smoke_reads_only_private_local_key_and_uses_ephemeral_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "PORTFOLIO_REVIEWER_NAME=Ignored unquoted local value\nOPENAI_API_KEY='sk-local-test'\n",
        encoding="utf-8",
    )
    env_path.chmod(0o600)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("portfolio_agent.cli.project_root", lambda: tmp_path)
    captured: dict[str, Settings] = {}
    disposed: list[bool] = []

    def fake_runtime(settings: Settings) -> Any:
        captured["settings"] = settings
        return SimpleNamespace(engine=SimpleNamespace(dispose=lambda: disposed.append(True)))

    monkeypatch.setattr("portfolio_agent.cli.create_openai_experiment_runtime", fake_runtime)
    monkeypatch.setattr(
        "portfolio_agent.cli.run_openai_synthetic_smoke",
        lambda _runtime: {"status": "passed"},
    )

    assert main(["openai-smoke", "--acknowledge-synthetic-only"]) == 0

    settings = captured["settings"]
    assert settings.allow_external_llm is True
    assert settings.allow_live_public_retrieval is False
    assert settings.enable_synthetic_fixture_connector is True
    assert settings.database_url != f"sqlite:///{tmp_path / 'var' / 'portfolio.db'}"
    assert str(tmp_path / "var" / "experiments" / "runtimes") in settings.database_url
    assert disposed == [True]
    assert "OPENAI_API_KEY" not in os.environ


def test_live_smoke_refuses_group_readable_local_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("OPENAI_API_KEY=sk-local-test\n", encoding="utf-8")
    env_path.chmod(0o644)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("portfolio_agent.cli.project_root", lambda: tmp_path)

    with pytest.raises(RuntimeError, match="chmod 600"):
        main(["openai-smoke", "--acknowledge-synthetic-only"])


def test_experiment_runtime_requires_all_cumulative_guards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = _settings(tmp_path)
    client = _FakeClient([_valid_product_output()])
    with pytest.raises(RuntimeError, match="ALLOW_EXTERNAL_LLM"):
        create_openai_experiment_runtime(replace(base, allow_external_llm=False), client=client)
    with pytest.raises(RuntimeError, match="SYNTHETIC_FIXTURE_CONNECTOR"):
        create_openai_experiment_runtime(base, client=client)
    with pytest.raises(RuntimeError, match="cannot enable public retrieval"):
        create_openai_experiment_runtime(
            replace(
                base, enable_synthetic_fixture_connector=True, allow_live_public_retrieval=True
            ),
            client=client,
        )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="process environment"):
        create_openai_experiment_runtime(
            replace(base, enable_synthetic_fixture_connector=True),
        )
    assert not (tmp_path / "llm.db").exists()


def test_real_workflow_experiment_routes_exactly_one_synthetic_item_to_openai(
    tmp_path: Path,
) -> None:
    settings = replace(
        _settings(tmp_path),
        project_root=project_root(),
        enable_synthetic_fixture_connector=True,
    )
    client = _FakeClient([_valid_product_output()])
    runtime = create_openai_experiment_runtime(settings, client=client)

    result = run_openai_synthetic_smoke(runtime, output_dir=tmp_path / "manifests")

    assert result["status"] == "passed"
    assert result["external_model_attempt_count"] == 1
    assert result["models"] == ["gpt-5.6-luna"]
    assert len(client.responses.calls) == 1
    with runtime.session_factory() as session:
        extractions = list(
            session.scalars(
                select(ExtractionModel).where(ExtractionModel.run_id == result["run_id"])
            ).all()
        )
    live_extractions = [
        row for row in extractions if row.provider == "openai_responses_structured_extractor"
    ]
    assert [row.evidence_item_id for row in live_extractions] == [SYNTHETIC_EXPERIMENT_EVIDENCE_ID]
    assert all(
        row.provider == "deterministic_structured_extractor"
        for row in extractions
        if row.evidence_item_id != SYNTHETIC_EXPERIMENT_EVIDENCE_ID
    )


def test_live_smoke_writes_failure_manifest_and_fails_closed(tmp_path: Path) -> None:
    settings = replace(
        _settings(tmp_path),
        project_root=project_root(),
        enable_synthetic_fixture_connector=True,
    )
    runtime = create_openai_experiment_runtime(
        settings,
        client=_FakeClient(["not-json", "still-not-json"]),
    )
    output_dir = tmp_path / "manifests"

    with pytest.raises(OpenAISmokeTestError, match="did not produce"):
        run_openai_synthetic_smoke(runtime, output_dir=output_dir)

    manifests = list(output_dir.glob("openai-smoke-*.json"))
    assert len(manifests) == 1
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))["manifest"]
    assert manifest["strict_extraction_persisted"] is False
    assert len(manifest["external_model_attempts"]) == 2
    serialized = json.dumps(manifest)
    assert "Aster Analytics" not in serialized
    assert "fictional company announced" not in serialized
