from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .enums import Sourceability, VerificationStatus


@dataclass(frozen=True, slots=True)
class VerificationEvidence:
    evidence_id: str
    source_type: str
    value: Any
    currency: str | None
    period_label: str | None
    expected_period_label: str
    publisher: str | None
    locator: str
    checksum: str
    is_untrusted: bool = False

    @property
    def is_internal(self) -> bool:
        return self.source_type == "portfolio_submission"

    @property
    def is_current(self) -> bool:
        return self.period_label == self.expected_period_label

    @property
    def has_provenance(self) -> bool:
        return bool(self.locator and self.checksum and (self.publisher or self.is_internal))


@dataclass(frozen=True, slots=True)
class VerificationOutcome:
    status: VerificationStatus
    rationale: str
    supporting_evidence_ids: tuple[str, ...]


def _same_value(
    candidate_value: Any,
    candidate_currency: str | None,
    evidence: VerificationEvidence,
) -> bool:
    if candidate_value != evidence.value:
        return False
    return not (
        candidate_currency and evidence.currency and candidate_currency != evidence.currency
    )


def verify_claim(
    *,
    candidate_value: Any,
    candidate_currency: str | None,
    sourceability: Sourceability,
    evidence: tuple[VerificationEvidence, ...],
) -> VerificationOutcome:
    if not evidence:
        return VerificationOutcome(
            status=VerificationStatus.INSUFFICIENT_EVIDENCE,
            rationale="No evidence item is linked to the claim.",
            supporting_evidence_ids=(),
        )

    if sourceability is Sourceability.PUBLICLY_SOURCEABLE:
        public_evidence = tuple(item for item in evidence if not item.is_internal)
        if not public_evidence:
            return VerificationOutcome(
                status=VerificationStatus.INSUFFICIENT_EVIDENCE,
                rationale="A publicly sourceable metric requires eligible public provenance.",
                supporting_evidence_ids=(),
            )
        trusted_public = tuple(
            item for item in public_evidence if not item.is_untrusted and item.has_provenance
        )
        if not trusted_public:
            return VerificationOutcome(
                status=VerificationStatus.REJECTED_UNTRUSTED,
                rationale="Public evidence was untrusted or lacked required provenance.",
                supporting_evidence_ids=(),
            )
        current_public = tuple(item for item in trusted_public if item.is_current)
        if not current_public:
            return VerificationOutcome(
                status=VerificationStatus.STALE,
                rationale="Public evidence does not match the requested reporting period.",
                supporting_evidence_ids=tuple(item.evidence_id for item in trusted_public),
            )
        matching_public = tuple(
            item
            for item in current_public
            if _same_value(candidate_value, candidate_currency, item)
        )
        conflicting_public = tuple(
            item
            for item in current_public
            if not _same_value(candidate_value, candidate_currency, item)
        )
        if conflicting_public:
            return VerificationOutcome(
                status=VerificationStatus.CONTRADICTED,
                rationale="Current public evidence contains a conflicting value.",
                supporting_evidence_ids=tuple(item.evidence_id for item in current_public),
            )
        if matching_public:
            matching_internal = tuple(
                item
                for item in evidence
                if item.is_internal
                and item.is_current
                and _same_value(candidate_value, candidate_currency, item)
            )
            return VerificationOutcome(
                status=VerificationStatus.SUPPORTED,
                rationale="Current public evidence explicitly supports the normalized claim.",
                supporting_evidence_ids=tuple(
                    item.evidence_id for item in (*matching_public, *matching_internal)
                ),
            )
        return VerificationOutcome(
            status=VerificationStatus.INSUFFICIENT_EVIDENCE,
            rationale="No current public evidence exactly supports the normalized claim.",
            supporting_evidence_ids=tuple(item.evidence_id for item in current_public),
        )

    trusted = tuple(item for item in evidence if not item.is_untrusted and item.has_provenance)
    if not trusted:
        return VerificationOutcome(
            status=VerificationStatus.REJECTED_UNTRUSTED,
            rationale="Available evidence was untrusted or lacked required provenance.",
            supporting_evidence_ids=(),
        )

    current = tuple(item for item in trusted if item.is_current)
    if not current:
        return VerificationOutcome(
            status=VerificationStatus.STALE,
            rationale="Evidence does not match the requested reporting period.",
            supporting_evidence_ids=tuple(item.evidence_id for item in trusted),
        )

    matching = tuple(
        item for item in current if _same_value(candidate_value, candidate_currency, item)
    )
    conflicting = tuple(
        item for item in current if not _same_value(candidate_value, candidate_currency, item)
    )

    internal_match = any(item.is_internal for item in matching)
    public_match = any(not item.is_internal for item in matching)
    public_conflict = any(not item.is_internal for item in conflicting)

    if public_conflict:
        return VerificationOutcome(
            status=VerificationStatus.CONTRADICTED,
            rationale="A current, provenance-complete evidence item contains a conflicting value.",
            supporting_evidence_ids=tuple(item.evidence_id for item in current),
        )

    if internal_match:
        return VerificationOutcome(
            status=VerificationStatus.SUPPORTED,
            rationale=(
                "The normalized claim exactly matches the immutable portfolio submission"
                + (" and current public evidence." if public_match else ".")
            ),
            supporting_evidence_ids=tuple(item.evidence_id for item in matching),
        )

    if public_match and sourceability in {
        Sourceability.PUBLICLY_SOURCEABLE,
        Sourceability.MIXED,
    }:
        return VerificationOutcome(
            status=VerificationStatus.SUPPORTED,
            rationale="Current public evidence explicitly supports the normalized claim.",
            supporting_evidence_ids=tuple(item.evidence_id for item in matching),
        )

    return VerificationOutcome(
        status=VerificationStatus.INSUFFICIENT_EVIDENCE,
        rationale="No eligible evidence item exactly supports the normalized claim.",
        supporting_evidence_ids=tuple(item.evidence_id for item in current),
    )
