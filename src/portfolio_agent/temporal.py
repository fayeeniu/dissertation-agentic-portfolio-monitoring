from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .enums import TemporalEligibilityStatus

UK_REPORTING_ZONE = ZoneInfo("Europe/London")


@dataclass(frozen=True, slots=True)
class TemporalWindow:
    reporting_cutoff: date
    period_start: date | None = None
    period_end: date | None = None


@dataclass(frozen=True, slots=True)
class TemporalEvidence:
    published_at: datetime | None
    effective_from: datetime | date | None = None
    effective_to: datetime | date | None = None
    is_internal_submission: bool = False


@dataclass(frozen=True, slots=True)
class TemporalDecision:
    status: TemporalEligibilityStatus
    eligible: bool
    rationale: str


def restore_persisted_utc(value: datetime | None) -> datetime | None:
    """Restore UTC lost by SQLite after an already-validated timestamp round trip."""

    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=UTC)


def reporting_cutoff_instant(cutoff: date) -> datetime:
    """Inclusive end of a UK civil reporting-cutoff day, represented in UTC."""

    next_midnight = datetime.combine(cutoff + timedelta(days=1), time.min, tzinfo=UK_REPORTING_ZONE)
    return next_midnight.astimezone(UTC) - timedelta(microseconds=1)


def _instant(value: datetime | date, *, end_of_day: bool = False) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError("Temporal evidence timestamps must include a timezone.")
        return value.astimezone(UTC)
    if end_of_day:
        return reporting_cutoff_instant(value)
    return datetime.combine(value, time.min, tzinfo=UK_REPORTING_ZONE).astimezone(UTC)


def temporal_eligibility(
    evidence: TemporalEvidence,
    window: TemporalWindow,
) -> TemporalDecision:
    cutoff = reporting_cutoff_instant(window.reporting_cutoff)
    if evidence.published_at is None:
        if evidence.is_internal_submission:
            return TemporalDecision(
                TemporalEligibilityStatus.ELIGIBLE,
                True,
                "Immutable internal submission is available at ingestion cutoff.",
            )
        return TemporalDecision(
            TemporalEligibilityStatus.MISSING_PUBLISHED_AT,
            False,
            "Public evidence has no availability timestamp.",
        )
    if _instant(evidence.published_at) > cutoff:
        return TemporalDecision(
            TemporalEligibilityStatus.FUTURE_PUBLISHED,
            False,
            "Evidence became publicly available after the reporting cutoff.",
        )
    if evidence.effective_from is not None and _instant(evidence.effective_from) > cutoff:
        return TemporalDecision(
            TemporalEligibilityStatus.FUTURE_EFFECTIVE,
            False,
            "Evidence was not effective by the reporting cutoff.",
        )
    if (
        evidence.effective_to is not None
        and window.period_start is not None
        and _instant(evidence.effective_to, end_of_day=True) < _instant(window.period_start)
    ):
        return TemporalDecision(
            TemporalEligibilityStatus.EXPIRED,
            False,
            "Evidence ceased to apply before the claim period began.",
        )
    return TemporalDecision(
        TemporalEligibilityStatus.ELIGIBLE,
        True,
        "Evidence was available and applicable by the reporting cutoff.",
    )
