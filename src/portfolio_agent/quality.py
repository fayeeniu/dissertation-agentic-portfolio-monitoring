from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .enums import (
    MissingState,
    QualityDisposition,
    TemporalEligibilityStatus,
)
from .ids import stable_hash
from .models import QualityContractModel, QualityViolationModel

QUALITY_CONTRACT_VERSION = "uk-public-evidence-quality-v2"

DEFAULT_QUALITY_RULES: tuple[dict[str, Any], ...] = (
    {
        "key": "trusted_evidence",
        "description": "Untrusted evidence is excluded before extraction and verification.",
        "disposition": QualityDisposition.EXCLUDE.value,
    },
    {
        "key": "complete_provenance",
        "description": "Every evidence item requires a stable locator and checksum.",
        "disposition": QualityDisposition.HOLD.value,
    },
    {
        "key": "claim_relative_time",
        "description": "Public evidence must be available and applicable by the run cutoff.",
        "disposition": QualityDisposition.EXCLUDE.value,
    },
    {
        "key": "public_conflict",
        "description": "Conflicting eligible public facts force a review hold.",
        "disposition": QualityDisposition.HOLD.value,
    },
    {
        "key": "expected_missingness",
        "description": (
            "Filing not due, dormant, not required, and source unavailable are distinct states."
        ),
        "disposition": QualityDisposition.WARN.value,
    },
    {
        "key": "bounded_no_record",
        "description": "A completed exact-identifier lookup may return no public record.",
        "disposition": QualityDisposition.WARN.value,
    },
    {
        "key": "source_collection_failure",
        "description": (
            "Policy, authentication, media, size, or other terminal failures require review."
        ),
        "disposition": QualityDisposition.HOLD.value,
    },
)

EXPECTED_MISSING_STATES = {
    MissingState.FILING_NOT_DUE.value,
    MissingState.DORMANT.value,
    MissingState.NOT_REQUIRED.value,
}


@dataclass(frozen=True, slots=True)
class QualityRecord:
    evidence_item_id: str | None
    source_snapshot_id: str | None
    company_id: str | None
    metric_definition_id: str | None
    source_type: str
    locator: str
    checksum: str
    is_untrusted: bool
    temporal_status: str | None
    value: Any
    missing_state: str | None = None
    source_terminal_status: str | None = None
    period_label: str | None = None
    unit: str | None = None
    currency: str | None = None

    @property
    def is_public(self) -> bool:
        return self.source_type != "portfolio_submission"


@dataclass(frozen=True, slots=True)
class QualityFinding:
    fingerprint: str
    rule_key: str
    severity: str
    disposition: QualityDisposition
    message: str
    company_id: str | None
    metric_definition_id: str | None
    evidence_item_id: str | None = None
    source_snapshot_id: str | None = None
    details: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class QualityEvaluation:
    findings: tuple[QualityFinding, ...]
    disposition_counts: dict[str, int]
    eligible_record_count: int


def compile_quality_contract(
    rules: tuple[dict[str, Any], ...] = DEFAULT_QUALITY_RULES,
) -> tuple[str, str]:
    keys: set[str] = set()
    for rule in rules:
        if set(rule) != {"key", "description", "disposition"}:
            raise ValueError("Quality rule has fields outside the versioned schema.")
        key = rule["key"]
        if not isinstance(key, str) or not key or key in keys:
            raise ValueError("Quality rule keys must be unique non-empty strings.")
        QualityDisposition(rule["disposition"])
        keys.add(key)
    return QUALITY_CONTRACT_VERSION, stable_hash(rules)


def _finding(
    *,
    rule_key: str,
    severity: str,
    disposition: QualityDisposition,
    message: str,
    record: QualityRecord,
    details: dict[str, Any] | None = None,
) -> QualityFinding:
    fingerprint = stable_hash(
        {
            "rule_key": rule_key,
            "company_id": record.company_id,
            "metric_definition_id": record.metric_definition_id,
            "evidence_item_id": record.evidence_item_id,
            "source_snapshot_id": record.source_snapshot_id,
            "details": details or {},
        }
    )
    return QualityFinding(
        fingerprint=fingerprint,
        rule_key=rule_key,
        severity=severity,
        disposition=disposition,
        message=message,
        company_id=record.company_id,
        metric_definition_id=record.metric_definition_id,
        evidence_item_id=record.evidence_item_id,
        source_snapshot_id=record.source_snapshot_id,
        details=details,
    )


def evaluate_quality(records: tuple[QualityRecord, ...]) -> QualityEvaluation:
    findings: list[QualityFinding] = []
    eligible: list[QualityRecord] = []
    for record in records:
        if record.is_untrusted:
            findings.append(
                _finding(
                    rule_key="trusted_evidence",
                    severity="error",
                    disposition=QualityDisposition.EXCLUDE,
                    message="Untrusted evidence was excluded.",
                    record=record,
                )
            )
            continue
        if not record.locator or not record.checksum:
            findings.append(
                _finding(
                    rule_key="complete_provenance",
                    severity="error",
                    disposition=QualityDisposition.HOLD,
                    message="Evidence lacks a locator or immutable checksum.",
                    record=record,
                )
            )
            continue
        temporal_status = record.temporal_status
        if temporal_status is None:
            if record.is_public:
                findings.append(
                    _finding(
                        rule_key="claim_relative_time",
                        severity="error",
                        disposition=QualityDisposition.EXCLUDE,
                        message="Public evidence has no recorded temporal-eligibility decision.",
                        record=record,
                        details={"temporal_status": "not_evaluated"},
                    )
                )
                continue
            temporal_status = TemporalEligibilityStatus.ELIGIBLE.value
        if temporal_status != TemporalEligibilityStatus.ELIGIBLE.value:
            findings.append(
                _finding(
                    rule_key="claim_relative_time",
                    severity="error",
                    disposition=QualityDisposition.EXCLUDE,
                    message=f"Evidence is temporally ineligible: {temporal_status}.",
                    record=record,
                    details={"temporal_status": temporal_status},
                )
            )
            continue
        if record.source_terminal_status == "failed":
            findings.append(
                _finding(
                    rule_key="source_collection_failure",
                    severity="error",
                    disposition=QualityDisposition.HOLD,
                    message="The public-source collection ended in a terminal contract failure.",
                    record=record,
                    details={"source_terminal_status": record.source_terminal_status},
                )
            )
            continue
        if record.source_terminal_status == "no_record":
            findings.append(
                _finding(
                    rule_key="bounded_no_record",
                    severity="warning",
                    disposition=QualityDisposition.WARN,
                    message="The bounded exact-identifier lookup returned no public record.",
                    record=record,
                    details={
                        "source_terminal_status": record.source_terminal_status,
                        "missing_state": MissingState.NOT_FOUND_PUBLICLY.value,
                    },
                )
            )
            continue
        if record.missing_state == MissingState.SOURCE_UNAVAILABLE.value:
            findings.append(
                _finding(
                    rule_key="expected_missingness",
                    severity="warning",
                    disposition=QualityDisposition.WARN,
                    message="The admitted public source was unavailable at collection time.",
                    record=record,
                )
            )
            continue
        if record.is_public and record.missing_state in {
            MissingState.NOT_REPORTED.value,
            MissingState.NOT_APPLICABLE.value,
        }:
            findings.append(
                _finding(
                    rule_key="expected_missingness",
                    severity="warning",
                    disposition=QualityDisposition.WARN,
                    message=(
                        f"Public-source aggregate state '{record.missing_state}' prevents a "
                        "complete metric claim; no zero or currency conversion was inferred."
                    ),
                    record=record,
                    details={"missing_state": record.missing_state, "expected": True},
                )
            )
            continue
        if record.missing_state in EXPECTED_MISSING_STATES:
            findings.append(
                _finding(
                    rule_key="expected_missingness",
                    severity="warning",
                    disposition=QualityDisposition.WARN,
                    message=(
                        f"Expected source state '{record.missing_state}' was recorded; "
                        "this is not a data-quality defect."
                    ),
                    record=record,
                    details={"missing_state": record.missing_state, "expected": True},
                )
            )
            continue
        eligible.append(record)

    grouped: dict[tuple[str, str, str], list[QualityRecord]] = defaultdict(list)
    for record in eligible:
        if record.is_public and record.company_id and record.metric_definition_id:
            grouped[
                (
                    record.company_id,
                    record.metric_definition_id,
                    record.period_label or "",
                )
            ].append(record)
    for pair in sorted(grouped):
        group = grouped[pair]
        semantic_dimensions = {(record.unit, record.currency) for record in group}
        distinct_values = {stable_hash(record.value) for record in group}
        if len(distinct_values) <= 1 and len(semantic_dimensions) <= 1:
            continue
        anchor = sorted(
            group,
            key=lambda item: (
                item.source_type,
                item.locator,
                item.evidence_item_id or "",
            ),
        )[0]
        findings.append(
            _finding(
                rule_key="public_conflict",
                severity="error",
                disposition=QualityDisposition.HOLD,
                message=(
                    "Eligible current public sources contain conflicting values or incompatible "
                    "unit/currency semantics."
                ),
                record=anchor,
                details={
                    "evidence_item_ids": sorted(
                        record.evidence_item_id
                        for record in group
                        if record.evidence_item_id is not None
                    ),
                    "distinct_value_count": len(distinct_values),
                    "period_label": pair[2] or None,
                    "semantic_dimensions": sorted(
                        {
                            f"{unit or '-'}:{currency or '-'}"
                            for unit, currency in semantic_dimensions
                        }
                    ),
                },
            )
        )

    ordered = tuple(sorted(findings, key=lambda finding: finding.fingerprint))
    counts = Counter(finding.disposition.value for finding in ordered)
    return QualityEvaluation(
        findings=ordered,
        disposition_counts=dict(sorted(counts.items())),
        eligible_record_count=len(eligible),
    )


def persist_quality_evaluation(
    session: Session,
    *,
    run_id: str,
    evaluation: QualityEvaluation,
) -> None:
    version, checksum = compile_quality_contract()
    contract = session.scalar(
        select(QualityContractModel).where(QualityContractModel.version == version)
    )
    if contract is None:
        session.add(
            QualityContractModel(
                version=version,
                sha256=checksum,
                rules_json=list(DEFAULT_QUALITY_RULES),
                active=True,
            )
        )
    elif contract.sha256 != checksum:
        raise ValueError("Quality contract version was reused with changed rules.")
    existing_fingerprints = set(
        session.scalars(
            select(QualityViolationModel.fingerprint).where(QualityViolationModel.run_id == run_id)
        ).all()
    )
    for finding in evaluation.findings:
        run_fingerprint = stable_hash({"run_id": run_id, "finding": finding.fingerprint})
        if run_fingerprint in existing_fingerprints:
            continue
        session.add(
            QualityViolationModel(
                fingerprint=run_fingerprint,
                run_id=run_id,
                company_id=finding.company_id,
                metric_definition_id=finding.metric_definition_id,
                evidence_item_id=finding.evidence_item_id,
                source_snapshot_id=finding.source_snapshot_id,
                rule_key=finding.rule_key,
                severity=finding.severity,
                disposition=finding.disposition.value,
                message=finding.message,
                details_json=finding.details or {},
            )
        )
