#!/usr/bin/env python3
"""Render SYS-F4's accessible SVG as a deterministic vector PDF."""

from __future__ import annotations

import argparse
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("ReportLab is required to render SYS-F4") from exc


SVG_NS = "{http://www.w3.org/2000/svg}"
CLASS_RE = re.compile(r"\.([A-Za-z0-9_-]+)\s*\{([^}]*)\}")
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
PATH_TOKEN_RE = re.compile(r"[MLZ]|-?\d+(?:\.\d+)?", re.IGNORECASE)


def declarations(value: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in value.split(";"):
        if ":" in item:
            key, raw = item.split(":", 1)
            parsed[key.strip()] = raw.strip()
    return parsed


def number(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    match = NUMBER_RE.search(value)
    return float(match.group()) if match else default


def colour(value: str | None, default: str = "#000000"):
    return HexColor(value if value and value.startswith("#") else default)


def font_details(style: dict[str, str]) -> tuple[str, float]:
    shorthand = style.get("font", "")
    match = re.search(r"(?:(700|bold)\s+)?(\d+(?:\.\d+)?)px", shorthand)
    weight = style.get("font-weight", match.group(1) if match else "400")
    size = float(match.group(2)) if match else number(style.get("font-size"), 12.0)
    return ("Helvetica-Bold" if weight in {"700", "bold"} else "Helvetica", size)


def element_style(element: ET.Element, classes: dict[str, dict[str, str]]) -> dict[str, str]:
    style: dict[str, str] = {}
    for class_name in element.get("class", "").split():
        style.update(classes.get(class_name, {}))
    style.update(declarations(element.get("style", "")))
    for key in (
        "fill",
        "stroke",
        "stroke-width",
        "stroke-dasharray",
        "font-weight",
        "text-anchor",
        "marker-end",
    ):
        if element.get(key) is not None:
            style[key] = element.get(key, "")
    return style


def set_stroke(pdf, style: dict[str, str], default: str = "#617684") -> None:
    pdf.setStrokeColor(colour(style.get("stroke"), default))
    pdf.setLineWidth(number(style.get("stroke-width"), 1.0))
    dash = style.get("stroke-dasharray", "").strip()
    pdf.setDash([float(item) for item in NUMBER_RE.findall(dash)] if dash and dash != "none" else [])


def draw_text(pdf, element: ET.Element, height: float, classes: dict[str, dict[str, str]]) -> None:
    style = element_style(element, classes)
    value = "".join(element.itertext()).strip()
    if not value:
        return
    font_name, font_size = font_details(style)
    width = stringWidth(value, font_name, font_size)
    x = number(element.get("x"))
    anchor = style.get("text-anchor", element.get("text-anchor", "start"))
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    pdf.setFont(font_name, font_size)
    pdf.setFillColor(colour(style.get("fill"), "#000000"))
    pdf.drawString(x, height - number(element.get("y")), value)


def parse_path(
    value: str,
) -> tuple[list[tuple[str, list[float]]], tuple[float, float] | None, tuple[float, float] | None]:
    tokens = PATH_TOKEN_RE.findall(value)
    commands: list[tuple[str, list[float]]] = []
    previous: tuple[float, float] | None = None
    end: tuple[float, float] | None = None
    index = 0
    while index < len(tokens):
        command = tokens[index].upper()
        index += 1
        count = {"M": 2, "L": 2, "Z": 0}[command]
        values = [float(item) for item in tokens[index : index + count]]
        index += count
        commands.append((command, values))
        if command in {"M", "L"}:
            if command == "L":
                previous = end
            end = (values[0], values[1])
    return commands, previous, end


def draw_arrowhead(
    pdf,
    previous: tuple[float, float],
    end: tuple[float, float],
    height: float,
    stroke_value: str,
) -> None:
    dx, dy = end[0] - previous[0], end[1] - previous[1]
    magnitude = math.hypot(dx, dy)
    if magnitude == 0:
        return
    unit_x, unit_y = dx / magnitude, dy / magnitude
    base_x, base_y = end[0] - (8 * unit_x), end[1] - (8 * unit_y)
    perp_x, perp_y = -unit_y, unit_x
    left = (base_x + (4 * perp_x), base_y + (4 * perp_y))
    right = (base_x - (4 * perp_x), base_y - (4 * perp_y))
    pdf.setFillColor(colour(stroke_value, "#617684"))
    arrow = pdf.beginPath()
    arrow.moveTo(end[0], height - end[1])
    arrow.lineTo(left[0], height - left[1])
    arrow.lineTo(right[0], height - right[1])
    arrow.close()
    pdf.drawPath(arrow, fill=1, stroke=0)


def draw_path(pdf, element: ET.Element, height: float, classes: dict[str, dict[str, str]]) -> None:
    style = element_style(element, classes)
    commands, previous, end = parse_path(element.get("d", ""))
    path = pdf.beginPath()
    for command, values in commands:
        if command == "M":
            path.moveTo(values[0], height - values[1])
        elif command == "L":
            path.lineTo(values[0], height - values[1])
        elif command == "Z":
            path.close()
    fill_value = style.get("fill", "none")
    stroke_value = style.get("stroke", "none")
    if fill_value != "none":
        pdf.setFillColor(colour(fill_value))
    if stroke_value != "none":
        set_stroke(pdf, style)
    pdf.drawPath(path, fill=fill_value != "none", stroke=stroke_value != "none")
    pdf.setDash()
    if previous and end and style.get("marker-end"):
        draw_arrowhead(pdf, previous, end, height, stroke_value)


def render(svg_path: Path, output_path: Path) -> None:
    root = ET.parse(svg_path).getroot()
    width, height = number(root.get("width")), number(root.get("height"))
    if root.find(f"{SVG_NS}title") is None or root.find(f"{SVG_NS}desc") is None:
        raise SystemExit("SVG must retain an accessible title and description")
    style_node = root.find(f"{SVG_NS}defs/{SVG_NS}style")
    if style_node is None:
        raise SystemExit("SVG must retain embedded style definitions")
    classes = {
        name: declarations(body)
        for name, body in CLASS_RE.findall("".join(style_node.itertext()))
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=(width, height), invariant=1, pageCompression=1)
    pdf.setTitle("Fixed workflow and verification state machine")
    pdf.setAuthor("Faye Niu")
    pdf.setSubject("SYS-F4 bounded workflow, verification, review and controlled-export states")
    pdf.setCreator("Deterministic ReportLab SVG renderer")

    for element in root:
        tag = element.tag.removeprefix(SVG_NS)
        if tag in {"title", "desc", "defs"}:
            continue
        style = element_style(element, classes)
        if tag == "rect":
            x, y = number(element.get("x")), number(element.get("y"))
            box_width, box_height = number(element.get("width")), number(element.get("height"))
            radius = number(element.get("rx"))
            fill_value, stroke_value = style.get("fill", "none"), style.get("stroke", "none")
            if fill_value != "none":
                pdf.setFillColor(colour(fill_value))
            if stroke_value != "none":
                set_stroke(pdf, style)
            pdf.roundRect(
                x,
                height - y - box_height,
                box_width,
                box_height,
                radius,
                fill=fill_value != "none",
                stroke=stroke_value != "none",
            )
            pdf.setDash()
        elif tag == "line":
            set_stroke(pdf, style)
            pdf.line(
                number(element.get("x1")),
                height - number(element.get("y1")),
                number(element.get("x2")),
                height - number(element.get("y2")),
            )
            pdf.setDash()
        elif tag == "path":
            draw_path(pdf, element, height, classes)
        elif tag == "text":
            draw_text(pdf, element, height, classes)
        else:
            raise SystemExit(f"Unsupported SVG element: {tag}")

    pdf.showPage()
    pdf.save()


def main() -> None:
    default_svg = Path(__file__).with_suffix(".svg")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg", type=Path, default=default_svg)
    parser.add_argument("--output", type=Path, default=default_svg.with_suffix(".pdf"))
    args = parser.parse_args()
    render(args.svg, args.output)


if __name__ == "__main__":
    main()
