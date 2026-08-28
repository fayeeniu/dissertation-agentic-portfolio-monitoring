#!/usr/bin/env python3
"""Render INTRO-F1's accessible SVG to a deterministic vector PDF."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("ReportLab is required to render INTRO-F1") from exc


SVG_NS = "{http://www.w3.org/2000/svg}"
CLASS_RE = re.compile(r"\.([A-Za-z0-9_-]+)\s*\{([^}]*)\}")
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
PATH_TOKEN_RE = re.compile(r"[MLCZ]|-?\d+(?:\.\d+)?", re.IGNORECASE)


def declarations(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in value.split(";"):
        if ":" in item:
            key, raw = item.split(":", 1)
            result[key.strip()] = raw.strip()
    return result


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
    name = "Helvetica-Bold" if weight in {"700", "bold"} else "Helvetica"
    return name, size


def element_style(element: ET.Element, classes: dict[str, dict[str, str]]) -> dict[str, str]:
    style: dict[str, str] = {}
    for class_name in element.get("class", "").split():
        style.update(classes.get(class_name, {}))
    style.update(declarations(element.get("style", "")))
    for key in ("fill", "stroke", "stroke-width", "font-weight", "text-anchor", "marker-end"):
        if element.get(key) is not None:
            style[key] = element.get(key, "")
    return style


def text_segments(element: ET.Element, base: dict[str, str]) -> list[tuple[str, dict[str, str]]]:
    segments: list[tuple[str, dict[str, str]]] = []
    if element.text and element.text.strip():
        segments.append((element.text.strip(), base))
    for child in element:
        child_style = dict(base)
        child_style.update(declarations(child.get("style", "")))
        if child.get("font-weight"):
            child_style["font-weight"] = child.get("font-weight", "")
        if child.text:
            segments.append((child.text, child_style))
        if child.tail:
            segments.append((child.tail, base))
    return segments


def draw_text(pdf, element: ET.Element, height: float, classes: dict[str, dict[str, str]]) -> None:
    base = element_style(element, classes)
    segments = text_segments(element, base)
    if not segments:
        return
    widths = []
    for value, style in segments:
        font_name, font_size = font_details(style)
        widths.append(stringWidth(value, font_name, font_size))
    x = number(element.get("x"))
    anchor = base.get("text-anchor", element.get("text-anchor", "start"))
    total_width = sum(widths)
    if anchor == "middle":
        x -= total_width / 2
    elif anchor == "end":
        x -= total_width
    y = height - number(element.get("y"))
    for (value, style), width in zip(segments, widths):
        font_name, font_size = font_details(style)
        pdf.setFont(font_name, font_size)
        pdf.setFillColor(colour(style.get("fill"), "#000000"))
        pdf.drawString(x, y, value)
        x += width


def parse_path(value: str) -> tuple[list[tuple[str, list[float]]], tuple[float, float] | None]:
    tokens = PATH_TOKEN_RE.findall(value)
    commands: list[tuple[str, list[float]]] = []
    end: tuple[float, float] | None = None
    index = 0
    while index < len(tokens):
        command = tokens[index].upper()
        index += 1
        count = {"M": 2, "L": 2, "C": 6, "Z": 0}[command]
        values = [float(item) for item in tokens[index : index + count]]
        index += count
        commands.append((command, values))
        if command in {"M", "L"}:
            end = (values[0], values[1])
        elif command == "C":
            end = (values[4], values[5])
    return commands, end


def draw_path(pdf, element: ET.Element, height: float, classes: dict[str, dict[str, str]]) -> None:
    style = element_style(element, classes)
    commands, end = parse_path(element.get("d", ""))
    path = pdf.beginPath()
    for command, values in commands:
        if command == "M":
            path.moveTo(values[0], height - values[1])
        elif command == "L":
            path.lineTo(values[0], height - values[1])
        elif command == "C":
            path.curveTo(values[0], height - values[1], values[2], height - values[3], values[4], height - values[5])
        elif command == "Z":
            path.close()
    fill_value = style.get("fill", "none")
    stroke_value = style.get("stroke", "none")
    if fill_value != "none":
        pdf.setFillColor(colour(fill_value))
    if stroke_value != "none":
        pdf.setStrokeColor(colour(stroke_value))
        pdf.setLineWidth(number(style.get("stroke-width"), 1.0))
    pdf.drawPath(path, fill=fill_value != "none", stroke=stroke_value != "none")
    if end and style.get("marker-end"):
        x, y = end
        pdf.setFillColor(colour(stroke_value, "#8A929D"))
        arrow = pdf.beginPath()
        arrow.moveTo(x, height - y)
        arrow.lineTo(x - 7, height - (y - 4))
        arrow.lineTo(x - 7, height - (y + 4))
        arrow.close()
        pdf.drawPath(arrow, fill=1, stroke=0)


def render(svg_path: Path, output_path: Path) -> None:
    root = ET.parse(svg_path).getroot()
    width = number(root.get("width"))
    height = number(root.get("height"))
    if root.find(f"{SVG_NS}title") is None or root.find(f"{SVG_NS}desc") is None:
        raise SystemExit("SVG must retain an accessible title and description")
    style_text = "".join(root.find(f"{SVG_NS}defs/{SVG_NS}style").itertext())
    classes = {name: declarations(body) for name, body in CLASS_RE.findall(style_text)}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=(width, height), invariant=1, pageCompression=1)
    pdf.setTitle("From heterogeneous evidence to the research contract")
    pdf.setAuthor("Faye Niu")
    pdf.setSubject("INTRO-F1 conceptual problem-control traceability map")
    pdf.setCreator("Deterministic ReportLab SVG renderer")

    for element in root:
        tag = element.tag.removeprefix(SVG_NS)
        if tag in {"title", "desc", "defs"}:
            continue
        style = element_style(element, classes)
        if tag == "rect":
            x = number(element.get("x"))
            y = number(element.get("y"))
            w = number(element.get("width"))
            h = number(element.get("height"))
            radius = number(element.get("rx"))
            fill_value = style.get("fill", "none")
            stroke_value = style.get("stroke", "none")
            if fill_value != "none":
                pdf.setFillColor(colour(fill_value))
            if stroke_value != "none":
                pdf.setStrokeColor(colour(stroke_value))
                pdf.setLineWidth(number(style.get("stroke-width"), 1.0))
            pdf.roundRect(x, height - y - h, w, h, radius, fill=fill_value != "none", stroke=stroke_value != "none")
        elif tag == "line":
            pdf.setStrokeColor(colour(style.get("stroke")))
            pdf.setLineWidth(number(style.get("stroke-width"), 1.0))
            pdf.line(number(element.get("x1")), height - number(element.get("y1")), number(element.get("x2")), height - number(element.get("y2")))
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
