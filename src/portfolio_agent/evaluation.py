from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .catalogue import MetricCatalogue
from .enums import (
    EvaluationCondition,
    MetricDataType,
    MissingState,
    TemporalEligibilityStatus,
    VerificationStatus,
)
from .evaluation_datasets import EvaluationCase, load_evaluation_dataset
from .normalization import normalize_value
from .schemas import EvaluationCaseResult, EvaluationSummary
from .verification import VerificationEvidence, verify_claim


@dataclass(frozen=True, slots=True)
class _Prediction:
    emit: bool
    status: str
    provenance_complete: bool
    normalization_correct: bool


def _candidate(case: EvaluationCase, catalogue: MetricCatalogue) -> tuple[Any, str | None, bool]:
    metric = catalogue.get(case.metric_key)
    normalized = normalize_value(case.candidate_value, metric)
    eligible = normalized.missing_state in {MissingState.OBSERVED, MissingState.ZERO}
    return normalized.value, normalized.currency or case.candidate_currency, eligible


def _single_agent_prediction(case: EvaluationCase, catalogue: MetricCatalogue) -> _Prediction:
    normalized_value, _, eligible = _candidate(case, catalogue)
    if case.precondition == "ambiguous_identity":
        return _Prediction(False, "identity_hold", False, True)
    if not eligible:
        return _Prediction(False, "no_claim", False, normalized_value is None)
    provenance_complete = bool(case.evidence) and all(
        evidence.locator and evidence.checksum for evidence in case.evidence
    )
    return _Prediction(True, "unverified", provenance_complete, True)


def _multi_agent_prediction(case: EvaluationCase, catalogue: MetricCatalogue) -> _Prediction:
    normalized_value, currency, eligible = _candidate(case, catalogue)
    if case.precondition == "ambiguous_identity":
        return _Prediction(False, "identity_hold", False, True)
    if not eligible:
        return _Prediction(False, "no_claim", False, normalized_value is None)
    evidence = tuple(
        VerificationEvidence(
            evidence_id=item.id,
            source_type=item.source_type,
            value=item.value,
            currency=item.currency,
            period_label=item.period_label,
            expected_period_label="SYN-PERIOD",
            publisher=item.publisher,
            locator=item.locator,
            checksum=item.checksum,
            is_untrusted=item.is_untrusted,
            temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
        )
        for item in case.evidence
    )
    outcome = verify_claim(
        candidate_value=normalized_value,
        candidate_currency=currency,
        sourceability=case.sourceability,
        evidence=evidence,
        require_currency=catalogue.get(case.metric_key).data_type is MetricDataType.CURRENCY,
    )
    emit = outcome.status is VerificationStatus.SUPPORTED
    provenance_complete = emit and bool(outcome.supporting_evidence_ids)
    return _Prediction(emit, outcome.status.value, provenance_complete, True)


def _case_result(
    case: EvaluationCase,
    condition: EvaluationCondition,
    prediction: _Prediction,
    duration_ms: int,
) -> EvaluationCaseResult:
    expected = case.expected_emit
    return EvaluationCaseResult(
        case_id=case.case_id,
        condition=condition,
        true_positive=int(prediction.emit and expected),
        false_positive=int(prediction.emit and not expected),
        false_negative=int(not prediction.emit and expected),
        true_negative=int(not prediction.emit and not expected),
        supported_claims=int(prediction.emit and prediction.status == VerificationStatus.SUPPORTED),
        unsupported_claims=int(prediction.emit and not expected),
        provenance_complete_claims=int(prediction.emit and prediction.provenance_complete),
        total_claims=int(prediction.emit),
        schema_valid=True,
        normalization_correct=prediction.normalization_correct,
        verification_correct=(
            prediction.emit == case.expected_emit
            and (
                condition is EvaluationCondition.DETERMINISTIC_SINGLE_AGENT
                or prediction.status == case.expected_status
            )
        ),
        identity_correct=None,
        extraction_correct=None,
        temporal_correct=None,
        quality_correct=None,
        contradiction_correct=(
            (case.expected_status == VerificationStatus.CONTRADICTED.value)
            == (prediction.status == VerificationStatus.CONTRADICTED.value)
            if case.expected_status == VerificationStatus.CONTRADICTED.value
            or prediction.status == VerificationStatus.CONTRADICTED.value
            else None
        ),
        abstention_correct=prediction.emit == case.expected_emit,
        event_correct=None,
        report_correct=None,
        reviewer_utility=None,
        duration_ms=duration_ms,
    )


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def _summary(
    condition: EvaluationCondition,
    results: tuple[EvaluationCaseResult, ...],
    repeat_consistency: float,
) -> EvaluationSummary:
    tp = sum(result.true_positive for result in results)
    fp = sum(result.false_positive for result in results)
    fn = sum(result.false_negative for result in results)
    precision = _safe_ratio(tp, tp + fp)
    recall = _safe_ratio(tp, tp + fn)
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None and recall is not None and precision + recall
        else None
    )
    total_claims = sum(result.total_claims for result in results)

    def accuracy(field: str) -> float | None:
        values = [getattr(result, field) for result in results]
        observed = [value for value in values if value is not None]
        return _safe_ratio(sum(bool(value) for value in observed), len(observed))

    return EvaluationSummary(
        condition=condition,
        case_count=len(results),
        precision=precision,
        recall=recall,
        f1=f1,
        claim_support_rate=_safe_ratio(tp, total_claims),
        hallucination_rate=_safe_ratio(fp, total_claims),
        provenance_completeness=_safe_ratio(
            sum(result.provenance_complete_claims for result in results), total_claims
        ),
        schema_validity_rate=_safe_ratio(
            sum(result.schema_valid for result in results), len(results)
        ),
        normalization_accuracy=_safe_ratio(
            sum(result.normalization_correct for result in results), len(results)
        ),
        verification_accuracy=_safe_ratio(
            sum(result.verification_correct for result in results), len(results)
        ),
        identity_accuracy=accuracy("identity_correct"),
        extraction_accuracy=accuracy("extraction_correct"),
        temporal_accuracy=accuracy("temporal_correct"),
        quality_accuracy=accuracy("quality_correct"),
        contradiction_accuracy=accuracy("contradiction_correct"),
        abstention_accuracy=accuracy("abstention_correct"),
        event_accuracy=accuracy("event_correct"),
        report_accuracy=accuracy("report_correct"),
        reviewer_utility=None,
        repeat_consistency=repeat_consistency,
        mean_duration_ms=_safe_ratio(sum(result.duration_ms for result in results), len(results)),
        llm_cost_usd="0",
        notes=(
            "Measured on labelled synthetic cases only; no participant or production claims.",
            "LLM cost is zero because this condition uses the deterministic local path.",
        ),
    )


def _protocol_only_summary(condition: EvaluationCondition, note: str) -> EvaluationSummary:
    return EvaluationSummary(
        condition=condition,
        case_count=0,
        precision=None,
        recall=None,
        f1=None,
        claim_support_rate=None,
        hallucination_rate=None,
        provenance_completeness=None,
        schema_validity_rate=None,
        normalization_accuracy=None,
        verification_accuracy=None,
        identity_accuracy=None,
        extraction_accuracy=None,
        temporal_accuracy=None,
        quality_accuracy=None,
        contradiction_accuracy=None,
        abstention_accuracy=None,
        event_accuracy=None,
        report_accuracy=None,
        reviewer_utility=None,
        repeat_consistency=None,
        mean_duration_ms=None,
        llm_cost_usd=None,
        notes=(note,),
    )


def run_evaluation(manifest_path: Path, *, repeats: int = 3) -> dict[str, Any]:
    if repeats < 2:
        raise ValueError("At least two repeats are required for consistency measurement.")
    dataset = load_evaluation_dataset(manifest_path, tier="D0")
    document = dataset.document
    catalogue = MetricCatalogue()
    condition_functions = {
        EvaluationCondition.DETERMINISTIC_SINGLE_AGENT: _single_agent_prediction,
        EvaluationCondition.MULTI_AGENT_VERIFICATION: _multi_agent_prediction,
    }
    summaries: list[EvaluationSummary] = [
        _protocol_only_summary(
            EvaluationCondition.MANUAL,
            "Protocol defined but not executed: manual cycle time and quality require "
            "authorised users.",
        )
    ]
    all_results: list[EvaluationCaseResult] = []
    for condition, prediction_function in condition_functions.items():
        repeat_vectors: list[tuple[tuple[bool, str], ...]] = []
        first_results: tuple[EvaluationCaseResult, ...] | None = None
        for repeat_index in range(repeats):
            current_results: list[EvaluationCaseResult] = []
            vector: list[tuple[bool, str]] = []
            for case in document.cases:
                start = time.perf_counter()
                prediction = prediction_function(case, catalogue)
                duration_ms = int((time.perf_counter() - start) * 1000)
                vector.append((prediction.emit, prediction.status))
                current_results.append(_case_result(case, condition, prediction, duration_ms))
            repeat_vectors.append(tuple(vector))
            if repeat_index == 0:
                first_results = tuple(current_results)
        assert first_results is not None
        first_vector = repeat_vectors[0]
        consistent = sum(vector == first_vector for vector in repeat_vectors) / len(repeat_vectors)
        summaries.append(_summary(condition, first_results, consistent))
        all_results.extend(first_results)
    summaries.append(
        _protocol_only_summary(
            EvaluationCondition.MULTI_AGENT_HITL,
            "Workflow implemented, but usability, edits, and human time require ethics "
            "approval and authorised participant data; no synthetic human result is reported.",
        )
    )
    return {
        "schema_version": "evaluation-output-v2",
        "generated_at": datetime.now(UTC).isoformat(),
        "source": {
            "manifest_path": str(dataset.manifest_path),
            "manifest_sha256": dataset.manifest_sha256,
            "dataset_sha256": dataset.dataset_sha256,
            "tier": dataset.entry.tier,
            "namespace": dataset.entry.namespace,
            "source_version": dataset.entry.source_version,
            "partition_policy": dataset.entry.partition_policy,
            "classification": document.classification,
            "case_count": len(document.cases),
        },
        "condition_parity": {
            "shared_core": ["catalogue", "normalization", "input_cases"],
            "deterministic_single_agent_ablation": ["independent_verification"],
            "multi_agent_verification_addition": ["independent_verifier"],
        },
        "repeats": repeats,
        "summaries": [summary.model_dump(mode="json") for summary in summaries],
        "case_results": [result.model_dump(mode="json") for result in all_results],
        "evidence_boundary": (
            "These measurements are automated synthetic-fixture results, not dissertation findings "
            "about real portfolio operations or human users."
        ),
    }


def write_evaluation(result: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
