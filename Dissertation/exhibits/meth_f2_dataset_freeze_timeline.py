#!/usr/bin/env python3
"""Render METH-F2's accessible SVG as a deterministic vector PDF."""

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
    raise SystemExit("ReportLab is required to render METH-F2") from exc


SVG_NS = "{http://www.w3.org/2000/svg}"
CLASS_RE = re.compile(r"\.([A-Za-z0-9_-]+)\s*\{([^}]*)\}")
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
PATH_TOKEN_RE = re.compile(r"[MLZ]|-?\d+(?:\.\d+)?", re.IGNORECASE)


def declarations(value: str) -> dict[str, str]:
    """Parse the restricted CSS declaration syntax used by the source SVG."""
    parsed: dict[str, str] = {}
    for item in value.split(";"):
        if ":" in item:
            key, raw = item.split(":", 1)
            parsed[key.strip()] = raw.strip()
    return parsed


def number(value: str | None, default: float = 0.0) -> float:
    """Read the first numeric token from an SVG attribute."""
    if value is None:
        return default
    match = NUMBER_RE.search(value)
    return float(match.group()) if match else default


def colour(value: str | None, default: str = "#000000"):
    """Convert the deliberately restricted hexadecimal colour syntax."""
    return HexColor(value if value and value.startswith("#") else default)


def font_details(style: dict[str, str]) -> tuple[str, float]:
    """Map SVG font declarations to deterministic PDF core fonts."""
    shorthand = style.get("font", "")
    match = re.search(r"(?:(700|bold)\s+)?(\d+(?:\.\d+)?)px", shorthand)
    weight = style.get("font-weight", match.group(1) if match else "400")
    size = float(match.group(2)) if match else number(style.get("font-size"), 12.0)
    name = "Helvetica-Bold" if weight in {"700", "bold"} else "Helvetica"
    return name, size


def element_style(element: ET.Element, classes: dict[str, dict[str, str]]) -> dict[str, str]:
    """Resolve class, inline and direct presentation attributes."""
    style: dict[str, str] = {}
    for class_name in element.get("class", "").split():
        style.update(classes.get(class_name, {}))
    style.update(declarations(element.get("style", "")))
    for key in ("fill", "stroke", "stroke-width", "font-weight", "text-anchor"):
        if element.get(key) is not None:
            style[key] = element.get(key, "")
    return style


def draw_text(pdf, element: ET.Element, height: float, classes: dict[str, dict[str, str]]) -> None:
    """Render one plain SVG text element without rasterisation."""
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
    y = height - number(element.get("y"))
    pdf.setFont(font_name, font_size)
    pdf.setFillColor(colour(style.get("fill"), "#000000"))
    pdf.drawString(x, y, value)


def parse_path(value: str) -> list[tuple[str, list[float]]]:
    """Parse the absolute M/L/Z paths deliberately used by METH-F2."""
    tokens = PATH_TOKEN_RE.findall(value)
    commands: list[tuple[str, list[float]]] = []
    index = 0
    while index < len(tokens):
        command = tokens[index].upper()
        index += 1
        count = {"M": 2, "L": 2, "Z": 0}[command]
        values = [float(item) for item in tokens[index : index + count]]
        index += count
        commands.append((command, values))
    return commands


def draw_path(pdf, element: ET.Element, height: float, classes: dict[str, dict[str, str]]) -> None:
    """Render one simple vector path."""
    style = element_style(element, classes)
    path = pdf.beginPath()
    for command, values in parse_path(element.get("d", "")):
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
        pdf.setStrokeColor(colour(stroke_value))
        pdf.setLineWidth(number(style.get("stroke-width"), 1.0))
    pdf.drawPath(path, fill=fill_value != "none", stroke=stroke_value != "none")


def render(svg_path: Path, output_path: Path) -> None:
    """Render the accessible source SVG using deterministic vector operations."""
    root = ET.parse(svg_path).getroot()
    width = number(root.get("width"))
    height = number(root.get("height"))
    if root.find(f"{SVG_NS}title") is None or root.find(f"{SVG_NS}desc") is None:
        raise SystemExit("SVG must retain an accessible title and description")
    style_node = root.find(f"{SVG_NS}defs/{SVG_NS}style")
    if style_node is None:
        raise SystemExit("SVG must retain embedded style definitions")
    style_text = "".join(style_node.itertext())
    classes = {name: declarations(body) for name, body in CLASS_RE.findall(style_text)}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(
        str(output_path),
        pagesize=(width, height),
        invariant=1,
        pageCompression=1,
    )
    pdf.setTitle("Dataset tiers and freeze timeline")
    pdf.setAuthor("Faye Niu")
    pdf.setSubject("METH-F2 conceptual dataset-tier and evaluation-freeze timeline")
    pdf.setCreator("Deterministic ReportLab SVG renderer")

    for element in root:
        tag = element.tag.removeprefix(SVG_NS)
        if tag in {"title", "desc", "defs"}:
            continue
        style = element_style(element, classes)
        if tag == "rect":
            x = number(element.get("x"))
            y = number(element.get("y"))
            box_width = number(element.get("width"))
            box_height = number(element.get("height"))
            radius = number(element.get("rx"))
            fill_value = style.get("fill", "none")
            stroke_value = style.get("stroke", "none")
            if fill_value != "none":
                pdf.setFillColor(colour(fill_value))
            if stroke_value != "none":
                pdf.setStrokeColor(colour(stroke_value))
                pdf.setLineWidth(number(style.get("stroke-width"), 1.0))
            pdf.roundRect(
                x,
                height - y - box_height,
                box_width,
                box_height,
                radius,
                fill=fill_value != "none",
                stroke=stroke_value != "none",
            )
        elif tag == "line":
            pdf.setStrokeColor(colour(style.get("stroke")))
            pdf.setLineWidth(number(style.get("stroke-width"), 1.0))
            pdf.line(
                number(element.get("x1")),
                height - number(element.get("y1")),
                number(element.get("x2")),
                height - number(element.get("y2")),
            )
        elif tag == "path":
            draw_path(pdf, element, height, classes)
        elif tag == "text":
            draw_text(pdf, element, height, classes)
        else:
            raise SystemExit(f"Unsupported SVG element: {tag}")

    pdf.showPage()
    pdf.save()


def main() -> None:
    """Parse CLI arguments and render the adjacent SVG by default."""
    default_svg = Path(__file__).with_suffix(".svg")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg", type=Path, default=default_svg)
    parser.add_argument("--output", type=Path, default=default_svg.with_suffix(".pdf"))
    args = parser.parse_args()
    render(args.svg, args.output)


if __name__ == "__main__":
    main()
