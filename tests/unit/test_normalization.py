from __future__ import annotations

import pytest

from portfolio_agent.catalogue import MetricCatalogue
from portfolio_agent.enums import MissingState
from portfolio_agent.normalization import normalize_value


@pytest.mark.parametrize(
    ("raw", "expected_state", "expected_value"),
    [
        (None, MissingState.BLANK, None),
        ("", MissingState.BLANK, None),
        (0, MissingState.ZERO, 0),
        ("0", MissingState.ZERO, 0),
        ("none", MissingState.NONE_STATED, None),
        ("n/a", MissingState.NOT_APPLICABLE, None),
        ("not reported", MissingState.NOT_REPORTED, None),
        ("not found publicly", MissingState.NOT_FOUND_PUBLICLY, None),
    ],
)
def test_missing_states_are_not_collapsed(
    raw: object, expected_state: MissingState, expected_value: object
) -> None:
    metric = MetricCatalogue().get("jobs_created")
    result = normalize_value(raw, metric)
    assert result.missing_state is expected_state
    assert result.value == expected_value


def test_currency_requires_explicit_code_or_symbol() -> None:
    metric = MetricCatalogue().get("grant_funding")

    explicit = normalize_value("GBP 1,250.50", metric)
    missing = normalize_value("1250.50", metric)

    assert explicit.value == "1250.5"
    assert explicit.currency == "GBP"
    assert missing.value == "1250.5"
    assert missing.currency is None
    assert missing.issue_code == "currency_missing"


def test_percentage_does_not_infer_ratio_scale() -> None:
    metric = MetricCatalogue().get("gross_margin")
    result = normalize_value("0.4", metric)
    assert result.value == "0.4"
    assert result.unit == "percentage_points"


def test_non_integral_count_is_invalid() -> None:
    metric = MetricCatalogue().get("employees_total")
    result = normalize_value("2.5", metric)
    assert result.missing_state is MissingState.INVALID
    assert result.issue_code == "non_integral_count"


@pytest.mark.parametrize(
    ("metric_key", "raw"),
    (
        ("employees_total", float("nan")),
        ("grant_funding", "GBP Infinity"),
        ("gross_margin", "-Infinity%"),
        ("ai_hours_saved", "NaN"),
    ),
)
def test_non_finite_numbers_are_invalid(metric_key: str, raw: object) -> None:
    result = normalize_value(raw, MetricCatalogue().get(metric_key))
    assert result.missing_state is MissingState.INVALID
    assert result.value is None
    assert result.issue_code == "non_finite_number"
