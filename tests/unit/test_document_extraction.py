from __future__ import annotations

import pytest

from portfolio_agent.document_extraction import (
    DocumentFieldRequest,
    extract_document,
    extract_hierarchical_text,
    extract_ixbrl,
    parse_reported_number,
)


def test_numeric_parser_handles_sign_currency_and_scale_without_guessing_dashes() -> None:
    assert parse_reported_number("(£1,200)").value == "-1200"
    assert parse_reported_number("£(1,200)").value == "-1200"
    assert parse_reported_number("USD 2.5 million").value == "2500000"
    assert parse_reported_number("3k").value == "3000"
    dash = parse_reported_number("\u2014")
    assert dash.value is None
    assert dash.abstain_reason == "explicit_dash_or_blank"


@pytest.mark.parametrize("raw", ("NaN", "Infinity", "-Infinity"))
def test_numeric_parser_abstains_on_non_finite_literals(raw: str) -> None:
    result = parse_reported_number(raw)
    assert result.value is None
    assert result.abstain_reason == "non_finite_numeric_literal"


def test_comparative_table_selects_only_the_requested_period() -> None:
    result = extract_hierarchical_text(
        "| Metric | 2025-06-30 | 2024-06-30 |\n| Revenue | £2.0 million | £1.5 million |",
        DocumentFieldRequest(
            field_key="revenue",
            aliases=("Revenue",),
            period_label="2024-06-30",
            expected_unit="currency_units",
        ),
    )
    assert result.value == "1500000"
    assert result.currency == "GBP"
    assert result.period_label == "2024-06-30"
    assert result.evidence_locator == "line:2:chars:28-39"


def test_total_funding_is_not_confused_with_maximum_funding() -> None:
    text = "Maximum grant funding | £1 million\nTotal grant funding | £2 million"
    total = extract_hierarchical_text(
        text,
        DocumentFieldRequest(
            field_key="grant_funding_total",
            aliases=("grant funding",),
            expected_unit="currency_units",
            selection="total",
        ),
    )
    maximum = extract_hierarchical_text(
        text,
        DocumentFieldRequest(
            field_key="grant_funding_maximum",
            aliases=("grant funding",),
            expected_unit="currency_units",
            selection="maximum",
        ),
    )
    assert total.value == "2000000"
    assert maximum.value == "1000000"


def test_ixbrl_preserves_context_scale_and_parentheses_sign() -> None:
    document = b"""<?xml version="1.0" encoding="UTF-8"?>
    <html xmlns="http://www.w3.org/1999/xhtml"
          xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"
          xmlns:xbrli="http://www.xbrl.org/2003/instance">
      <body>
        <xbrli:context id="FY24"><xbrli:period>
          <xbrli:endDate>2024-12-31</xbrli:endDate>
        </xbrli:period></xbrli:context>
        <ix:nonFraction name="uk-gaap:Turnover" contextRef="FY24" scale="3">(1,234)</ix:nonFraction>
      </body>
    </html>"""
    result = extract_ixbrl(
        document,
        DocumentFieldRequest(
            field_key="revenue",
            aliases=("Turnover",),
            ixbrl_names=("Turnover",),
            period_label="2024-12-31",
            expected_unit="currency_units",
        ),
    )
    assert result.value == "-1234000"
    assert result.evidence_locator == "ixbrl://fact/uk-gaap:Turnover?contextRef=FY24"


def test_structured_json_uses_exact_pointer_and_absent_fields_abstain() -> None:
    request = DocumentFieldRequest(
        field_key="award_amount",
        aliases=("award amount",),
        json_pointers=("/award/amount",),
        expected_unit="currency_units",
    )
    extracted = extract_document(
        b'{"award":{"amount":"GBP 42 thousand"}}',
        media_type="application/json",
        request=request,
    )
    absent = extract_document(b'{"award":{}}', media_type="application/json", request=request)
    assert extracted.value == "42000"
    assert extracted.currency == "GBP"
    assert extracted.evidence_locator == "json-pointer:/award/amount"
    assert absent.value is None
    assert absent.abstain_reason == "field_absent"
