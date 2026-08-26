from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from .cbit_contract import PeriodSemantics
from .enums import MetricDataType, MissingState
from .ids import stable_hash
from .models import (
    CompanyProgrammeMembershipModel,
    ContextStatisticModel,
    ObservationModel,
    ReportingPeriodModel,
    WorkflowRunModel,
)

CONTEXT_CONTRACT_VERSION = "within-portfolio-distribution-v3"
DEFAULT_MINIMUM_SAMPLE_SIZE = 3


@dataclass(frozen=True, slots=True)
class ChangeComparison:
    company_id: str
    company_name: str
    metric_definition_id: str
    metric_key: str
    metric_label: str
    current_period: str
    prior_period: str | None
    status: str
    current_value: str | None
    prior_value: str | None
    absolute_change: str | None
    percentage_change: str | None
    unit: str | None
    currency: str | None


@dataclass(frozen=True, slots=True)
class ContextSummary:
    metric_definition_id: str
    metric_key: str
    metric_label: str
    status: str
    sample_size: int
    minimum_sample_size: int
    unit: str | None
    currency: str | None
    exposure_window: str
    minimum: str | None
    first_quartile: str | None
    median: str | None
    third_quartile: str | None
    maximum: str | None


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def _render_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    rendered = format(value.normalize(), "f")
    return "0" if rendered in {"-0", ""} else rendered


def _quantile(ordered: tuple[Decimal, ...], probability: Decimal) -> Decimal:
    if not ordered:
        raise ValueError("A quantile requires at least one value.")
    if len(ordered) == 1:
        return ordered[0]
    position = Decimal(len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - Decimal(lower)
    return ordered[lower] + ((ordered[upper] - ordered[lower]) * weight)


def _programme_start(session: Session, observation: ObservationModel) -> date | None:
    return session.scalar(
        select(CompanyProgrammeMembershipModel.programme_start_date).where(
            CompanyProgrammeMembershipModel.raw_submission_id == observation.raw_submission_id,
            CompanyProgrammeMembershipModel.company_id == observation.company_id,
        )
    )


def _exposure_window(
    session: Session, observation: ObservationModel
) -> tuple[tuple[str, ...], str]:
    semantics = PeriodSemantics(
        observation.metric_definition.period_semantics or PeriodSemantics.NONE.value
    )
    period = observation.raw_submission.reporting_period
    cutoff = observation.raw_submission.reporting_cutoff or period.end_date

    def incomplete(reason: str) -> tuple[tuple[str, ...], str]:
        # Company-specific isolation makes an under-specified interval visible but prevents a
        # misleading cross-company cohort.
        return (
            (
                semantics.value,
                "incomplete",
                reason,
                observation.raw_submission_id,
                observation.company_id,
            ),
            f"{semantics.value}: incomplete {reason}",
        )

    if semantics in {PeriodSemantics.REPORTING_PERIOD, PeriodSemantics.LAST_QUARTER}:
        if period.start_date is None or period.end_date is None:
            return incomplete("period bounds")
        return (
            (semantics.value, period.start_date.isoformat(), period.end_date.isoformat()),
            (
                f"{semantics.value}: {period.start_date.isoformat()} through "
                f"{period.end_date.isoformat()}"
            ),
        )
    if semantics is PeriodSemantics.AS_AT_CUTOFF:
        if cutoff is None:
            return incomplete("reporting cutoff")
        return ((semantics.value, cutoff.isoformat()), f"as at {cutoff.isoformat()}")
    if semantics is PeriodSemantics.SINCE_PROGRAMME_START:
        start = _programme_start(session, observation)
        if start is None or cutoff is None:
            return incomplete("programme window")
        return (
            (semantics.value, start.isoformat(), cutoff.isoformat()),
            f"since programme start: {start.isoformat()} through {cutoff.isoformat()}",
        )
    if semantics is PeriodSemantics.BEFORE_PROGRAMME:
        start = _programme_start(session, observation)
        if start is None:
            return incomplete("programme start")
        return ((semantics.value, start.isoformat()), f"before {start.isoformat()}")
    return incomplete("origin or interval")


def _periods_are_comparable(
    session: Session,
    *,
    current: ObservationModel,
    prior: ObservationModel,
) -> bool:
    current_semantics = PeriodSemantics(
        current.metric_definition.period_semantics or PeriodSemantics.NONE.value
    )
    prior_semantics = PeriodSemantics(
        prior.metric_definition.period_semantics or PeriodSemantics.NONE.value
    )
    if current_semantics is not prior_semantics:
        return False
    current_period = current.raw_submission.reporting_period
    prior_period = prior.raw_submission.reporting_period
    if current_semantics in {
        PeriodSemantics.REPORTING_PERIOD,
        PeriodSemantics.LAST_QUARTER,
    }:
        bounds = (
            current_period.start_date,
            current_period.end_date,
            prior_period.start_date,
            prior_period.end_date,
        )
        if any(bound is None for bound in bounds):
            return False
        assert current_period.start_date is not None and current_period.end_date is not None
        assert prior_period.start_date is not None and prior_period.end_date is not None
        return prior_period.end_date < current_period.start_date and (
            current_period.end_date - current_period.start_date
        ) == (prior_period.end_date - prior_period.start_date)
    current_cutoff = current.raw_submission.reporting_cutoff or current_period.end_date
    prior_cutoff = prior.raw_submission.reporting_cutoff or prior_period.end_date
    if current_cutoff is None or prior_cutoff is None or prior_cutoff >= current_cutoff:
        return False
    if current_semantics is PeriodSemantics.AS_AT_CUTOFF:
        return True
    if current_semantics is PeriodSemantics.SINCE_PROGRAMME_START:
        current_start = _programme_start(session, current)
        prior_start = _programme_start(session, prior)
        return current_start is not None and current_start == prior_start
    # Before-programme and lifetime/unspecified values lack two complete changing intervals.
    return False


def derive_context_statistics(
    session: Session,
    *,
    run: WorkflowRunModel,
    observations: tuple[ObservationModel, ...],
    source_versions: dict[str, str],
    minimum_sample_size: int = DEFAULT_MINIMUM_SAMPLE_SIZE,
) -> tuple[ContextSummary, ...]:
    if run.reporting_cutoff is None:
        raise ValueError("Context statistics require an explicit reporting cutoff.")
    if minimum_sample_size < 2:
        raise ValueError("Context statistics require a minimum sample size of at least two.")

    session.execute(delete(ContextStatisticModel).where(ContextStatisticModel.run_id == run.id))
    grouped: dict[
        tuple[str, str | None, str | None, tuple[str, ...]],
        list[tuple[ObservationModel, Decimal, str]],
    ] = defaultdict(list)
    for observation in observations:
        if observation.missing_state not in {
            MissingState.OBSERVED.value,
            MissingState.ZERO.value,
        }:
            continue
        if (
            observation.metric_definition.data_type == MetricDataType.CURRENCY.value
            and observation.currency is None
        ):
            continue
        value = _decimal(observation.normalized_value_json)
        if value is None:
            continue
        exposure_key, exposure_label = _exposure_window(session, observation)
        grouped[
            (
                observation.metric_definition_id,
                observation.unit,
                observation.currency,
                exposure_key,
            )
        ].append((observation, value, exposure_label))

    summaries: list[ContextSummary] = []
    for (metric_id, unit, currency, exposure_key), rows in sorted(grouped.items()):
        anchor = rows[0][0]
        exposure_label = rows[0][2]
        values = tuple(sorted(value for _, value, _ in rows))
        enough = len(values) >= minimum_sample_size
        five_number = (
            {
                "minimum": _render_decimal(values[0]),
                "first_quartile": _render_decimal(_quantile(values, Decimal("0.25"))),
                "median": _render_decimal(_quantile(values, Decimal("0.5"))),
                "third_quartile": _render_decimal(_quantile(values, Decimal("0.75"))),
                "maximum": _render_decimal(values[-1]),
            }
            if enough
            else None
        )
        status = "available" if enough else "insufficient_sample"
        cohort = {
            "contract_version": CONTEXT_CONTRACT_VERSION,
            "definition": (
                "Within-import portfolio distribution of observed or explicit-zero values; "
                "not an external UK cohort"
            ),
            "reporting_period": anchor.raw_submission.reporting_period.label,
            "period_semantics": anchor.metric_definition.period_semantics,
            "exposure_window": exposure_label,
            "unit": unit,
            "currency": currency,
            "minimum_sample_size": minimum_sample_size,
            "excluded_missing_states": True,
        }
        session.add(
            ContextStatisticModel(
                run_id=run.id,
                metric_definition_id=metric_id,
                statistic_key=(
                    f"five_number:{unit or '-'}:{currency or '-'}:{stable_hash(exposure_key)[:12]}"
                ),
                cohort_definition_json=cohort,
                sample_size=len(values),
                reporting_cutoff=run.reporting_cutoff,
                source_versions_json=source_versions,
                value_json=five_number,
                status=status,
            )
        )
        summaries.append(
            ContextSummary(
                metric_definition_id=metric_id,
                metric_key=anchor.metric_definition.key,
                metric_label=anchor.metric_definition.label,
                status=status,
                sample_size=len(values),
                minimum_sample_size=minimum_sample_size,
                unit=unit,
                currency=currency,
                exposure_window=exposure_label,
                minimum=five_number["minimum"] if five_number else None,
                first_quartile=five_number["first_quartile"] if five_number else None,
                median=five_number["median"] if five_number else None,
                third_quartile=five_number["third_quartile"] if five_number else None,
                maximum=five_number["maximum"] if five_number else None,
            )
        )
    return tuple(summaries)


def compare_with_prior_periods(
    session: Session,
    *,
    observations: tuple[ObservationModel, ...],
) -> tuple[ChangeComparison, ...]:
    comparisons: list[ChangeComparison] = []
    for current in observations:
        current_value = _decimal(current.normalized_value_json)
        if current_value is None or current.missing_state not in {
            MissingState.OBSERVED.value,
            MissingState.ZERO.value,
        }:
            continue
        current_period = current.raw_submission.reporting_period
        candidates = list(
            session.scalars(
                select(ObservationModel)
                .join(ReportingPeriodModel)
                .where(
                    ObservationModel.company_id == current.company_id,
                    ObservationModel.metric_definition_id == current.metric_definition_id,
                    ObservationModel.id != current.id,
                )
                .options(
                    joinedload(ObservationModel.company),
                    joinedload(ObservationModel.metric_definition),
                    joinedload(ObservationModel.raw_submission).joinedload(
                        type(current.raw_submission).reporting_period
                    ),
                )
                .order_by(ReportingPeriodModel.end_date.desc())
            ).all()
        )
        dated_prior = [
            row
            for row in candidates
            if current_period.end_date is not None
            and row.raw_submission.reporting_period.end_date is not None
            and row.raw_submission.reporting_period.end_date < current_period.end_date
        ]
        compatible = [
            row
            for row in dated_prior
            if row.unit == current.unit
            and row.currency == current.currency
            and not (
                current.metric_definition.data_type == MetricDataType.CURRENCY.value
                and current.currency is None
            )
            and row.missing_state in {MissingState.OBSERVED.value, MissingState.ZERO.value}
            and _decimal(row.normalized_value_json) is not None
            and _periods_are_comparable(session, current=current, prior=row)
        ]
        latest_period_rows: list[ObservationModel] = []
        if compatible:
            latest_end = compatible[0].raw_submission.reporting_period.end_date
            latest_period_rows = [
                row
                for row in compatible
                if row.raw_submission.reporting_period.end_date == latest_end
            ]
        prior = latest_period_rows[0] if len(latest_period_rows) == 1 else None
        status = (
            "comparable"
            if prior is not None
            else "conflicted_prior_period"
            if len(latest_period_rows) > 1
            else "not_comparable"
            if dated_prior
            else "no_comparable_prior_period"
        )
        prior_value = _decimal(prior.normalized_value_json) if prior is not None else None
        absolute = current_value - prior_value if prior_value is not None else None
        percentage = None
        if absolute is not None and prior_value is not None and prior_value != Decimal(0):
            percentage = (absolute / abs(prior_value)) * Decimal(100)
        comparisons.append(
            ChangeComparison(
                company_id=current.company_id,
                company_name=current.company.canonical_name,
                metric_definition_id=current.metric_definition_id,
                metric_key=current.metric_definition.key,
                metric_label=current.metric_definition.label,
                current_period=current_period.label,
                prior_period=(prior.raw_submission.reporting_period.label if prior else None),
                status=status,
                current_value=_render_decimal(current_value),
                prior_value=_render_decimal(prior_value),
                absolute_change=_render_decimal(absolute),
                percentage_change=_render_decimal(percentage),
                unit=current.unit,
                currency=current.currency,
            )
        )
    return tuple(
        sorted(comparisons, key=lambda item: (item.company_name.casefold(), item.metric_key))
    )
