from __future__ import annotations

from datetime import UTC, date, datetime
from itertools import permutations

from portfolio_agent.enums import (
    MissingState,
    QualityDisposition,
    Sourceability,
    TemporalEligibilityStatus,
    VerificationStatus,
)
from portfolio_agent.quality import QualityRecord, evaluate_quality
from portfolio_agent.temporal import (
    TemporalEvidence,
    TemporalWindow,
    reporting_cutoff_instant,
    temporal_eligibility,
)
from portfolio_agent.verification import VerificationEvidence, verify_claim


def test_uk_cutoff_is_dst_aware_and_inclusive() -> None:
    cutoff = date(2025, 6, 30)
    assert reporting_cutoff_instant(cutoff) == datetime(2025, 6, 30, 22, 59, 59, 999999, tzinfo=UTC)
    eligible = temporal_eligibility(
        TemporalEvidence(published_at=datetime(2025, 6, 30, 22, 59, tzinfo=UTC)),
        TemporalWindow(cutoff),
    )
    future = temporal_eligibility(
        TemporalEvidence(published_at=datetime(2025, 6, 30, 23, 0, tzinfo=UTC)),
        TemporalWindow(cutoff),
    )
    assert eligible.eligible
    assert future.status is TemporalEligibilityStatus.FUTURE_PUBLISHED


def test_public_missing_timestamp_fails_closed_but_internal_submission_is_eligible() -> None:
    window = TemporalWindow(date(2025, 6, 30))
    public = temporal_eligibility(TemporalEvidence(published_at=None), window)
    internal = temporal_eligibility(
        TemporalEvidence(published_at=None, is_internal_submission=True), window
    )
    assert public.status is TemporalEligibilityStatus.MISSING_PUBLISHED_AT
    assert not public.eligible
    assert internal.eligible


def test_expected_missingness_is_not_a_quality_defect() -> None:
    expected_missing = QualityRecord(
        evidence_item_id="ev-expected",
        source_snapshot_id=None,
        company_id="company",
        metric_definition_id="metric",
        source_type="companies_house",
        locator="source://record",
        checksum="abc",
        is_untrusted=False,
        temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
        value=None,
        missing_state=MissingState.FILING_NOT_DUE.value,
    )
    unavailable = QualityRecord(
        evidence_item_id="ev-unavailable",
        source_snapshot_id=None,
        company_id="company",
        metric_definition_id="metric",
        source_type="companies_house",
        locator="source://record",
        checksum="abc",
        is_untrusted=False,
        temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
        value=None,
        missing_state=MissingState.SOURCE_UNAVAILABLE.value,
    )
    expected_result = evaluate_quality((expected_missing,))
    unavailable_result = evaluate_quality((unavailable,))
    assert len(expected_result.findings) == 1
    assert expected_result.findings[0].disposition is QualityDisposition.WARN
    assert "not a data-quality defect" in expected_result.findings[0].message
    assert len(unavailable_result.findings) == 1
    assert unavailable_result.findings[0].disposition is QualityDisposition.WARN


def test_public_quality_record_without_temporal_decision_is_excluded() -> None:
    record = QualityRecord(
        evidence_item_id="ev-not-evaluated",
        source_snapshot_id="snap-not-evaluated",
        company_id="company",
        metric_definition_id="metric",
        source_type="companies_house",
        locator="source://record",
        checksum="abc",
        is_untrusted=False,
        temporal_status=None,
        value=10,
    )
    result = evaluate_quality((record,))
    assert result.eligible_record_count == 0
    assert len(result.findings) == 1
    assert result.findings[0].rule_key == "claim_relative_time"
    assert result.findings[0].disposition is QualityDisposition.EXCLUDE


def test_expected_missingness_does_not_suppress_independent_quality_failures() -> None:
    untrusted = QualityRecord(
        evidence_item_id="ev-untrusted-missing",
        source_snapshot_id="snap-untrusted-missing",
        company_id="company",
        metric_definition_id="metric",
        source_type="companies_house",
        locator="source://record",
        checksum="abc",
        is_untrusted=True,
        temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
        value=None,
        missing_state=MissingState.DORMANT.value,
    )
    incomplete = QualityRecord(
        evidence_item_id="ev-incomplete-missing",
        source_snapshot_id="snap-incomplete-missing",
        company_id="company",
        metric_definition_id="metric",
        source_type="companies_house",
        locator="",
        checksum="",
        is_untrusted=False,
        temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
        value=None,
        missing_state=MissingState.NOT_REQUIRED.value,
    )
    future = QualityRecord(
        evidence_item_id="ev-future-missing",
        source_snapshot_id="snap-future-missing",
        company_id="company",
        metric_definition_id="metric",
        source_type="companies_house",
        locator="source://record",
        checksum="abc",
        is_untrusted=False,
        temporal_status=TemporalEligibilityStatus.FUTURE_PUBLISHED.value,
        value=None,
        missing_state=MissingState.FILING_NOT_DUE.value,
    )

    result = evaluate_quality((untrusted, incomplete, future))

    assert {finding.rule_key for finding in result.findings} == {
        "trusted_evidence",
        "complete_provenance",
        "claim_relative_time",
    }


def test_public_conflicts_and_verification_are_permutation_invariant() -> None:
    records = (
        QualityRecord(
            evidence_item_id="ev-a",
            source_snapshot_id="snap-a",
            company_id="company",
            metric_definition_id="metric",
            source_type="companies_house",
            locator="source://a",
            checksum="aaa",
            is_untrusted=False,
            temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
            value=10,
        ),
        QualityRecord(
            evidence_item_id="ev-b",
            source_snapshot_id="snap-b",
            company_id="company",
            metric_definition_id="metric",
            source_type="ukri_gtr",
            locator="source://b",
            checksum="bbb",
            is_untrusted=False,
            temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
            value=11,
        ),
    )
    evidence = (
        VerificationEvidence(
            evidence_id="ev-a",
            source_type="companies_house",
            value=10,
            currency=None,
            period_label="2025-Q2",
            expected_period_label="2025-Q2",
            publisher="Companies House",
            locator="source://a",
            checksum="aaa",
            temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
        ),
        VerificationEvidence(
            evidence_id="ev-b",
            source_type="ukri_gtr",
            value=11,
            currency=None,
            period_label="2025-Q2",
            expected_period_label="2025-Q2",
            publisher="UKRI",
            locator="source://b",
            checksum="bbb",
            temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
        ),
    )

    quality_vectors = {
        tuple(
            (finding.rule_key, finding.disposition.value, finding.message)
            for finding in evaluate_quality(tuple(order)).findings
        )
        for order in permutations(records)
    }
    verification_vectors = {
        verify_claim(
            candidate_value=10,
            candidate_currency=None,
            sourceability=Sourceability.PUBLICLY_SOURCEABLE,
            evidence=tuple(order),
        )
        for order in permutations(evidence)
    }
    assert len(quality_vectors) == 1
    assert len(verification_vectors) == 1
    assert next(iter(verification_vectors)).status is VerificationStatus.CONTRADICTED


def test_public_conflicts_compare_only_same_period_and_require_semantic_compatibility() -> None:
    def record(
        evidence_id: str,
        *,
        value: int,
        period_label: str,
        currency: str,
    ) -> QualityRecord:
        return QualityRecord(
            evidence_item_id=evidence_id,
            source_snapshot_id=f"snapshot-{evidence_id}",
            company_id="company",
            metric_definition_id="metric",
            source_type="public_source_fact",
            locator=f"source://{evidence_id}",
            checksum=f"checksum-{evidence_id}",
            is_untrusted=False,
            temporal_status=TemporalEligibilityStatus.ELIGIBLE.value,
            value=value,
            period_label=period_label,
            unit="currency_units",
            currency=currency,
        )

    different_periods = evaluate_quality(
        (
            record("prior", value=100, period_label="2025-Q1", currency="GBP"),
            record("current", value=150, period_label="2025-Q2", currency="GBP"),
        )
    )
    incompatible_currency = evaluate_quality(
        (
            record("gbp", value=100, period_label="2025-Q2", currency="GBP"),
            record("usd", value=100, period_label="2025-Q2", currency="USD"),
        )
    )

    assert not any(finding.rule_key == "public_conflict" for finding in different_periods.findings)
    conflict = next(
        finding
        for finding in incompatible_currency.findings
        if finding.rule_key == "public_conflict"
    )
    assert conflict.disposition is QualityDisposition.HOLD
    assert conflict.details is not None
    assert conflict.details["semantic_dimensions"] == [
        "currency_units:GBP",
        "currency_units:USD",
    ]


def test_future_public_evidence_cannot_support_historical_claim() -> None:
    result = verify_claim(
        candidate_value=10,
        candidate_currency=None,
        sourceability=Sourceability.PUBLICLY_SOURCEABLE,
        evidence=(
            VerificationEvidence(
                evidence_id="future",
                source_type="companies_house",
                value=10,
                currency=None,
                period_label="2025-Q2",
                expected_period_label="2025-Q2",
                publisher="Companies House",
                locator="source://future",
                checksum="future-hash",
                temporal_status=TemporalEligibilityStatus.FUTURE_PUBLISHED.value,
            ),
        ),
    )
    assert result.status is VerificationStatus.STALE
