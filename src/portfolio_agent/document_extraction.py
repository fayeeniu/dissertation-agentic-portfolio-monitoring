from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from .catalogue import canonicalize_label
from .schemas import DocumentExtraction

_DASHES = {"-", "\u2013", "\u2014", "\u2212", ""}
_CURRENCY_SYMBOLS = {"£": "GBP", "$": "USD", "€": "EUR"}
_SCALE_WORDS = {
    "thousand": Decimal("1000"),
    "thousands": Decimal("1000"),
    "million": Decimal("1000000"),
    "millions": Decimal("1000000"),
    "billion": Decimal("1000000000"),
    "billions": Decimal("1000000000"),
}


@dataclass(frozen=True, slots=True)
class DocumentFieldRequest:
    field_key: str
    aliases: tuple[str, ...]
    period_label: str | None = None
    json_pointers: tuple[str, ...] = ()
    ixbrl_names: tuple[str, ...] = ()
    expected_unit: str | None = None
    selection: str = "single"

    def __post_init__(self) -> None:
        if not self.field_key or not self.aliases:
            raise ValueError("Document field requests require a key and aliases.")
        if self.selection not in {"single", "total", "maximum"}:
            raise ValueError("Document selection must be single, total, or maximum.")


@dataclass(frozen=True, slots=True)
class _ParsedNumber:
    value: str | None
    currency: str | None
    unit: str | None
    abstain_reason: str | None = None


def _decimal_text(value: Decimal) -> str:
    rendered = format(value.normalize(), "f")
    return "0" if rendered in {"-0", ""} else rendered


def parse_reported_number(
    raw: str | int | float | Decimal,
    *,
    scale_power: int = 0,
    sign: str | None = None,
) -> _ParsedNumber:
    text = str(raw).strip()
    if text in _DASHES:
        return _ParsedNumber(None, None, None, "explicit_dash_or_blank")
    currency = next((code for symbol, code in _CURRENCY_SYMBOLS.items() if symbol in text), None)
    upper = text.upper()
    if currency is None:
        currency = next((code for code in ("GBP", "USD", "EUR") if code in upper), None)
    unit = "percentage_points" if "%" in text else None
    negative = ("(" in text and ")" in text) or sign == "-"
    compact = text.strip("() ")
    for symbol in _CURRENCY_SYMBOLS:
        compact = compact.replace(symbol, "")
    compact = re.sub(r"\b(?:GBP|USD|EUR)\b", "", compact, flags=re.IGNORECASE)
    compact = compact.replace(",", "").replace("%", "").strip().strip("() ")
    multiplier = Decimal(10) ** scale_power
    for word, scale in _SCALE_WORDS.items():
        if re.search(rf"\b{word}\b", compact, flags=re.IGNORECASE):
            multiplier *= scale
            compact = re.sub(rf"\b{word}\b", "", compact, flags=re.IGNORECASE).strip()
            break
    suffix = re.search(r"(?i)([kmb])$", compact)
    if suffix:
        multiplier *= {"k": 1000, "m": 1_000_000, "b": 1_000_000_000}[suffix.group(1).lower()]
        compact = compact[:-1].strip()
    try:
        value = Decimal(compact) * multiplier
    except InvalidOperation:
        return _ParsedNumber(None, currency, unit, "invalid_numeric_literal")
    if not value.is_finite():
        return _ParsedNumber(None, currency, unit, "non_finite_numeric_literal")
    if negative:
        value = -abs(value)
    return _ParsedNumber(_decimal_text(value), currency, unit)


def _abstain(request: DocumentFieldRequest, method: str, reason: str) -> DocumentExtraction:
    return DocumentExtraction(
        field_key=request.field_key,
        value=None,
        extraction_method=method,
        abstain_reason=reason,
        confidence=0.0,
    )


def _pointer(document: Any, pointer: str) -> Any:
    if not pointer.startswith("/"):
        raise ValueError("JSON pointers must begin with '/'.")
    current = document
    for token in pointer[1:].split("/"):
        key = token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit() and int(key) < len(current):
            current = current[int(key)]
        else:
            raise KeyError(pointer)
    return current


def extract_structured_json(
    content: bytes,
    request: DocumentFieldRequest,
) -> DocumentExtraction:
    try:
        document = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _abstain(request, "structured_json", "invalid_json")
    matches: list[tuple[str, Any]] = []
    for pointer in request.json_pointers:
        try:
            matches.append((pointer, _pointer(document, pointer)))
        except KeyError:
            continue
    if not matches:
        return _abstain(request, "structured_json", "field_absent")
    if len(matches) != 1:
        return _abstain(request, "structured_json", "ambiguous_multiple_fields")
    pointer, raw = matches[0]
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        parsed = parse_reported_number(raw)
        value: str | int | bool | None = parsed.value
        currency = parsed.currency
        unit = parsed.unit or request.expected_unit
    elif isinstance(raw, str) and request.expected_unit is not None:
        parsed = parse_reported_number(raw)
        if parsed.value is None:
            return _abstain(
                request,
                "structured_json",
                parsed.abstain_reason or "invalid_value",
            )
        value = parsed.value
        currency = parsed.currency
        unit = parsed.unit or request.expected_unit
    elif isinstance(raw, (str, bool)) or raw is None:
        value = raw
        currency = None
        unit = request.expected_unit
    else:
        return _abstain(request, "structured_json", "non_scalar_field")
    return DocumentExtraction(
        field_key=request.field_key,
        value=value,
        raw_value=raw,
        unit=unit,
        currency=currency,
        period_label=request.period_label,
        evidence_locator=f"json-pointer:{pointer}",
        extraction_method="structured_json",
        abstain_reason=None,
        confidence=1.0,
    )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def extract_ixbrl(content: bytes, request: DocumentFieldRequest) -> DocumentExtraction:
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return _abstain(request, "ixbrl", "invalid_xml")
    contexts: dict[str, str] = {}
    for element in root.iter():
        if _local_name(element.tag) != "context" or not element.attrib.get("id"):
            continue
        period_value = next(
            (
                child.text.strip()
                for child in element.iter()
                if _local_name(child.tag) in {"instant", "endDate"}
                and child.text
                and child.text.strip()
            ),
            None,
        )
        if period_value:
            contexts[element.attrib["id"]] = period_value

    allowed_names = {canonicalize_label(name) for name in request.ixbrl_names}
    candidates: list[tuple[ET.Element[str], str]] = []
    for element in root.iter():
        if _local_name(element.tag) != "nonFraction":
            continue
        name = element.attrib.get("name", "").split(":")[-1]
        context_ref = element.attrib.get("contextRef", "")
        if canonicalize_label(name) not in allowed_names:
            continue
        period = contexts.get(context_ref)
        if request.period_label and period != request.period_label:
            continue
        candidates.append((element, period or request.period_label or ""))
    if not candidates:
        return _abstain(request, "ixbrl", "field_or_period_absent")
    if len(candidates) != 1:
        return _abstain(request, "ixbrl", "ambiguous_multiple_facts")
    element, period = candidates[0]
    raw = "".join(element.itertext()).strip()
    try:
        scale = int(element.attrib.get("scale", "0"))
    except ValueError:
        return _abstain(request, "ixbrl", "invalid_scale")
    parsed = parse_reported_number(raw, scale_power=scale, sign=element.attrib.get("sign"))
    if parsed.value is None:
        return _abstain(request, "ixbrl", parsed.abstain_reason or "invalid_value")
    name = element.attrib.get("name", "")
    context_ref = element.attrib.get("contextRef", "")
    return DocumentExtraction(
        field_key=request.field_key,
        value=parsed.value,
        raw_value=raw,
        unit=parsed.unit or request.expected_unit,
        currency=parsed.currency,
        period_label=period or None,
        evidence_locator=f"ixbrl://fact/{name}?contextRef={context_ref}",
        extraction_method="ixbrl",
        confidence=1.0,
    )


def _line_cells(line: str) -> list[str]:
    if "|" in line:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]
    if "\t" in line:
        return [cell.strip() for cell in line.split("\t")]
    return []


def _semantic_alias_match(
    line: str,
    request: DocumentFieldRequest,
) -> bool:
    canonical = canonicalize_label(line)
    aliases = {canonicalize_label(alias) for alias in request.aliases}
    if not any(alias in canonical for alias in aliases):
        return False
    if request.selection == "total" and "maximum" in canonical and "total" not in canonical:
        return False
    return not (
        request.selection == "maximum" and "total" in canonical and "maximum" not in canonical
    )


def extract_hierarchical_text(text: str, request: DocumentFieldRequest) -> DocumentExtraction:
    lines = text.splitlines()
    matches: list[tuple[int, str, str]] = []
    for line_index, line in enumerate(lines):
        if not _semantic_alias_match(line, request):
            continue
        cells = _line_cells(line)
        selected_text: str | None = None
        if cells:
            header_cells: list[str] = []
            for prior in reversed(lines[max(0, line_index - 3) : line_index]):
                candidate = _line_cells(prior)
                if len(candidate) == len(cells):
                    header_cells = candidate
                    break
            if request.period_label and request.period_label in header_cells:
                selected_text = cells[header_cells.index(request.period_label)]
            elif request.period_label and len(cells) > 2:
                continue
            elif len(cells) == 2:
                selected_text = cells[1]
        if selected_text is None:
            aliases = sorted(request.aliases, key=len, reverse=True)
            remainder = line
            for alias in aliases:
                match = re.search(re.escape(alias), line, flags=re.IGNORECASE)
                if match:
                    remainder = line[match.end() :]
                    break
            number = re.search(
                r"(?:\([£$€]?[\d,.]+(?:\s*(?:thousand|million|billion|[kmb]))?\)|"
                r"[£$€]?[+-]?[\d,.]+(?:\.\d+)?(?:\s*(?:%|thousand|million|billion|[kmb]))?)",
                remainder,
                flags=re.IGNORECASE,
            )
            if number:
                selected_text = number.group(0)
        if selected_text is not None:
            matches.append((line_index, line, selected_text))
    if not matches:
        return _abstain(request, "hierarchical_text", "field_or_period_absent")
    if len(matches) != 1:
        return _abstain(request, "hierarchical_text", "ambiguous_multiple_values")
    line_index, line, selected_text = matches[0]
    parsed = parse_reported_number(selected_text)
    if parsed.value is None:
        return _abstain(
            request,
            "hierarchical_text",
            parsed.abstain_reason or "invalid_value",
        )
    start = line.find(selected_text)
    return DocumentExtraction(
        field_key=request.field_key,
        value=parsed.value,
        raw_value=selected_text,
        unit=parsed.unit or request.expected_unit,
        currency=parsed.currency,
        period_label=request.period_label,
        evidence_locator=(f"line:{line_index + 1}:chars:{start + 1}-{start + len(selected_text)}"),
        extraction_method="hierarchical_text",
        confidence=0.95,
    )


def extract_document(
    content: bytes,
    *,
    media_type: str,
    request: DocumentFieldRequest,
) -> DocumentExtraction:
    normalized_type = media_type.split(";", 1)[0].strip().lower()
    if normalized_type == "application/json":
        return extract_structured_json(content, request)
    if normalized_type in {"application/xhtml+xml", "text/html", "application/xml"}:
        ixbrl_result = extract_ixbrl(content, request)
        if ixbrl_result.abstain_reason not in {"field_or_period_absent", "invalid_xml"}:
            return ixbrl_result
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return _abstain(request, "hierarchical_text", "non_utf8_document")
    return extract_hierarchical_text(text, request)
