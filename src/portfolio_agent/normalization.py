from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from .enums import MetricDataType, MissingState
from .schemas import MetricDefinition, NormalizedValue

_MISSING_TOKENS: dict[str, MissingState] = {
    "none": MissingState.NONE_STATED,
    "nil": MissingState.NONE_STATED,
    "n/a": MissingState.NOT_APPLICABLE,
    "na": MissingState.NOT_APPLICABLE,
    "not applicable": MissingState.NOT_APPLICABLE,
    "not reported": MissingState.NOT_REPORTED,
    "not provided": MissingState.NOT_REPORTED,
    "unknown": MissingState.NOT_REPORTED,
    "not found": MissingState.NOT_FOUND_PUBLICLY,
    "not found publicly": MissingState.NOT_FOUND_PUBLICLY,
    "filing not due": MissingState.FILING_NOT_DUE,
    "not yet due": MissingState.FILING_NOT_DUE,
    "dormant": MissingState.DORMANT,
    "not required": MissingState.NOT_REQUIRED,
    "source unavailable": MissingState.SOURCE_UNAVAILABLE,
}

_CURRENCY_SYMBOLS = {"£": "GBP", "$": "USD", "€": "EUR"}


def _decimal_text(value: Decimal) -> str:
    normalized = value.normalize()
    result = format(normalized, "f")
    return "0" if result in {"-0", ""} else result


def _parse_decimal(value: Any) -> tuple[Decimal | None, str | None]:
    if isinstance(value, bool):
        return None, "boolean_is_not_numeric"
    if isinstance(value, (int, float, Decimal)):
        try:
            parsed = Decimal(str(value))
        except InvalidOperation:
            return None, "invalid_number"
        if not parsed.is_finite():
            return None, "non_finite_number"
        return parsed, None
    if not isinstance(value, str):
        return None, "unsupported_numeric_type"
    compact = value.strip().replace(",", "").replace("_", "")
    negative = compact.startswith("(") and compact.endswith(")")
    if negative:
        compact = compact[1:-1]
    compact = compact.removesuffix("%").strip()
    for symbol in _CURRENCY_SYMBOLS:
        compact = compact.replace(symbol, "")
    compact = re.sub(r"\b(GBP|USD|EUR)\b", "", compact, flags=re.IGNORECASE).strip()
    try:
        parsed = Decimal(compact)
    except InvalidOperation:
        return None, "invalid_number"
    if not parsed.is_finite():
        return None, "non_finite_number"
    return (-parsed if negative else parsed), None


def _currency(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    for symbol, code in _CURRENCY_SYMBOLS.items():
        if symbol in value:
            return code
    upper = value.upper()
    for code in ("GBP", "USD", "EUR"):
        if re.search(rf"\b{code}\b", upper):
            return code
    return None


def _invalid(metric: MetricDefinition, code: str, message: str) -> NormalizedValue:
    return NormalizedValue(
        value=None,
        missing_state=MissingState.INVALID,
        unit=metric.unit,
        issue_code=code,
        issue_message=message,
    )


def normalize_value(value: Any, metric: MetricDefinition) -> NormalizedValue:
    if value is None:
        return NormalizedValue(value=None, missing_state=MissingState.BLANK, unit=metric.unit)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return NormalizedValue(value=None, missing_state=MissingState.BLANK, unit=metric.unit)
        missing_state = _MISSING_TOKENS.get(stripped.lower())
        if missing_state is not None:
            return NormalizedValue(value=None, missing_state=missing_state, unit=metric.unit)

    if metric.data_type is MetricDataType.TEXT:
        if not isinstance(value, str):
            return _invalid(metric, "invalid_text_type", "Expected text without type coercion.")
        return NormalizedValue(
            value=value.strip(), missing_state=MissingState.OBSERVED, unit=metric.unit
        )

    if metric.data_type is MetricDataType.BOOLEAN:
        if isinstance(value, bool):
            parsed_bool = value
        elif isinstance(value, str) and value.strip().lower() in {"true", "yes", "y"}:
            parsed_bool = True
        elif isinstance(value, str) and value.strip().lower() in {"false", "no", "n"}:
            parsed_bool = False
        else:
            return _invalid(metric, "invalid_boolean", "Expected an explicit true/false value.")
        return NormalizedValue(
            value=parsed_bool,
            missing_state=MissingState.OBSERVED,
            unit=metric.unit,
        )

    if metric.data_type is MetricDataType.DATE:
        if isinstance(value, date):
            parsed_date = value
        elif isinstance(value, str):
            try:
                parsed_date = date.fromisoformat(value.strip())
            except ValueError:
                return _invalid(metric, "invalid_date", "Expected an ISO 8601 calendar date.")
        else:
            return _invalid(metric, "invalid_date_type", "Expected a date or ISO date string.")
        return NormalizedValue(
            value=parsed_date.isoformat(),
            missing_state=MissingState.OBSERVED,
            unit=metric.unit,
        )

    parsed, error = _parse_decimal(value)
    if error is not None or parsed is None:
        return _invalid(metric, error or "invalid_number", "Value is not a valid numeric literal.")

    missing_state = MissingState.ZERO if parsed == 0 else MissingState.OBSERVED
    if metric.data_type is MetricDataType.INTEGER:
        if parsed != parsed.to_integral_value():
            return _invalid(metric, "non_integral_count", "Count metrics require a whole number.")
        return NormalizedValue(value=int(parsed), missing_state=missing_state, unit=metric.unit)

    if metric.data_type is MetricDataType.PERCENTAGE and not Decimal("0") <= parsed <= Decimal(
        "100"
    ):
        return _invalid(
            metric,
            "percentage_out_of_range",
            "Percentage-point values must be between 0 and 100; ratios are not inferred.",
        )

    return NormalizedValue(
        value=_decimal_text(parsed),
        missing_state=missing_state,
        unit=metric.unit,
        currency=_currency(value) if metric.data_type is MetricDataType.CURRENCY else None,
        issue_code=(
            "currency_missing"
            if metric.data_type is MetricDataType.CURRENCY and _currency(value) is None
            else None
        ),
        issue_message=(
            "Currency was not explicit; the value is retained but cannot be aggregated."
            if metric.data_type is MetricDataType.CURRENCY and _currency(value) is None
            else None
        ),
    )
