from __future__ import annotations

from portfolio_agent.enums import Sourceability, VerificationStatus
from portfolio_agent.verification import VerificationEvidence, verify_claim


def _evidence(
    *,
    value: object,
    period: str = "P1",
    source_type: str = "synthetic_public_fixture",
    currency: str | None = None,
    untrusted: bool = False,
) -> VerificationEvidence:
    return VerificationEvidence(
        evidence_id=f"evidence-{value}-{currency}",
        source_type=source_type,
        value=value,
        currency=currency,
        period_label=period,
        expected_period_label="P1",
        publisher=None if source_type == "portfolio_submission" else "Synthetic register",
        locator="fixture://evidence",
        checksum="synthetic-checksum",
        is_untrusted=untrusted,
    )


def test_internal_exact_match_is_supported() -> None:
    result = verify_claim(
        candidate_value=0,
        candidate_currency=None,
        sourceability=Sourceability.INTERNAL_ONLY,
        evidence=(_evidence(value=0, source_type="portfolio_submission"),),
    )
    assert result.status is VerificationStatus.SUPPORTED


def test_publicly_sourceable_metric_requires_current_public_provenance() -> None:
    internal_only = verify_claim(
        candidate_value=1,
        candidate_currency=None,
        sourceability=Sourceability.PUBLICLY_SOURCEABLE,
        evidence=(_evidence(value=1, source_type="portfolio_submission"),),
    )
    stale_public = verify_claim(
        candidate_value=1,
        candidate_currency=None,
        sourceability=Sourceability.PUBLICLY_SOURCEABLE,
        evidence=(
            _evidence(value=1, source_type="portfolio_submission"),
            _evidence(value=1, period="P0"),
        ),
    )
    assert internal_only.status is VerificationStatus.INSUFFICIENT_EVIDENCE
    assert stale_public.status is VerificationStatus.STALE


def test_current_conflict_overrides_internal_match() -> None:
    result = verify_claim(
        candidate_value="100",
        candidate_currency="GBP",
        sourceability=Sourceability.MIXED,
        evidence=(
            _evidence(value="100", source_type="portfolio_submission", currency="GBP"),
            _evidence(value="90", currency="GBP"),
        ),
    )
    assert result.status is VerificationStatus.CONTRADICTED


def test_stale_and_untrusted_evidence_are_never_support() -> None:
    stale = verify_claim(
        candidate_value=1,
        candidate_currency=None,
        sourceability=Sourceability.PUBLICLY_SOURCEABLE,
        evidence=(_evidence(value=1, period="P0"),),
    )
    untrusted = verify_claim(
        candidate_value=1,
        candidate_currency=None,
        sourceability=Sourceability.PUBLICLY_SOURCEABLE,
        evidence=(_evidence(value=1, untrusted=True),),
    )
    assert stale.status is VerificationStatus.STALE
    assert untrusted.status is VerificationStatus.REJECTED_UNTRUSTED


def test_currency_conflict_is_not_converted() -> None:
    result = verify_claim(
        candidate_value="400",
        candidate_currency="GBP",
        sourceability=Sourceability.MIXED,
        evidence=(_evidence(value="400", currency="USD"),),
    )
    assert result.status is VerificationStatus.CONTRADICTED
