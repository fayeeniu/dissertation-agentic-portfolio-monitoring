#!/usr/bin/env python3
"""Generate the shared Mermaid theme for every dissertation figure.

`exhibits/figure_palette.json` is the single source of truth for figure colour, typography and
semantic node roles. This script expands it into the two files the renderer consumes:

* `exhibits/mermaid-config.json` - Mermaid theme variables and layout geometry;
* `exhibits/mermaid.css`         - the semantic `fx-*` node classes.

Both outputs are byte-deterministic for a given palette, so `MERMAID_MANIFEST.csv` can bind them by
SHA-256. Figure sources therefore carry no colour literals: an `.mmd` file only assigns roles with
`class <nodes> fx-<role>`, and the meaning of each role lives in the palette.

Run `scripts/render_mermaid_figures.sh` to regenerate the theme and every figure together.
"""

from __future__ import annotations

import json
from pathlib import Path

DISSERTATION_ROOT = Path(__file__).resolve().parents[1]
PALETTE_PATH = DISSERTATION_ROOT / "exhibits" / "figure_palette.json"
CONFIG_PATH = DISSERTATION_ROOT / "exhibits" / "mermaid-config.json"
CSS_PATH = DISSERTATION_ROOT / "exhibits" / "mermaid.css"

GENERATED_BANNER = (
    "/* GENERATED FILE - do not edit.\n"
    " * Source: exhibits/figure_palette.json\n"
    " * Regenerate with: python3 scripts/build_figure_theme.py\n"
    " */\n"
)

SHAPE_SELECTOR_SUFFIXES = ("> rect", "> polygon", "> path", "> circle", "> ellipse")


def load_palette() -> dict:
    with PALETTE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def colour_map(palette: dict) -> dict[str, str]:
    return {name: entry["hex"] for name, entry in palette["colours"].items()}


def build_config(palette: dict) -> dict:
    c = colour_map(palette)
    type_ = palette["typography"]
    layout = palette["layout"]
    font = type_["font_family"]
    base_size = f"{type_['base_font_size_px']}px"

    return {
        "theme": "base",
        "securityLevel": "strict",
        "deterministicIds": True,
        "deterministicIDSeed": "wmg-agentic-portfolio-dissertation",
        "fontFamily": font,
        "themeVariables": {
            "fontFamily": font,
            "fontSize": base_size,
            "primaryColor": c["mist"],
            "primaryTextColor": c["ink"],
            "primaryBorderColor": c["ink"],
            "secondaryColor": c["paper"],
            "secondaryTextColor": c["ink"],
            "secondaryBorderColor": c["quiet_line"],
            "tertiaryColor": c["neutral_fill"],
            "tertiaryTextColor": c["ink"],
            "tertiaryBorderColor": c["neutral_line"],
            "background": c["canvas"],
            "lineColor": c["edge"],
            "textColor": c["ink"],
            "mainBkg": c["mist"],
            "nodeBorder": c["ink"],
            "nodeTextColor": c["ink"],
            "clusterBkg": c["paper"],
            "clusterBorder": c["quiet_line"],
            "edgeLabelBackground": c["canvas"],
            "titleColor": c["ink"],
            "noteBkgColor": c["neutral_fill"],
            "noteBorderColor": c["neutral_line"],
            "noteTextColor": c["ink"],
            "labelBoxBkgColor": c["mist"],
            "labelBoxBorderColor": c["ink"],
            "labelTextColor": c["ink"],
        },
        "flowchart": {
            "defaultRenderer": layout["flowchart_renderer"],
            "curve": "basis",
            "htmlLabels": True,
            "nodeSpacing": layout["node_spacing_px"],
            "rankSpacing": layout["rank_spacing_px"],
            "padding": layout["node_padding_px"],
            "diagramPadding": layout["diagram_padding_px"],
            "wrappingWidth": layout["wrapping_width_px"],
            "useMaxWidth": False,
        },
        "block": {
            "padding": layout["block_padding_px"],
            "useMaxWidth": False,
        },
        "state": {
            "useMaxWidth": False,
        },
    }


def dash_declaration(dash: str | None) -> str:
    if dash is None:
        return "  stroke-dasharray: none !important;\n"
    return f"  stroke-dasharray: {dash} !important;\n"


def build_css(palette: dict) -> str:
    c = colour_map(palette)
    type_ = palette["typography"]
    font = type_["font_family"]
    line_height = type_["line_height"]

    parts: list[str] = [GENERATED_BANNER, "\n"]

    parts.append(
        "/* Typography and shared geometry */\n"
        ".root,\n.flowchart,\n.block,\n.stateDiagram,\n.erDiagram {\n"
        f"  font-family: {font} !important;\n"
        "}\n\n"
        ".node rect,\n.node polygon,\n.node path,\n.node circle,\n.node ellipse,\n"
        ".block rect,\n.cluster rect {\n"
        "  shape-rendering: geometricPrecision;\n"
        "}\n\n"
        ".node rect,\n.block rect {\n"
        "  rx: 5px;\n  ry: 5px;\n"
        "}\n\n"
        ".nodeLabel,\n.edgeLabel,\n.cluster-label,\n.label {\n"
        f"  color: {c['ink']};\n"
        f"  font-family: {font} !important;\n"
        "}\n\n"
        ".node .label,\n.block .label {\n"
        f"  line-height: {line_height};\n"
        "}\n\n"
        ".label foreignObject {\n  overflow: visible;\n}\n\n"
    )

    parts.append(
        "/* Connectors */\n"
        ".flowchart-link,\n.transition {\n"
        f"  stroke: {c['edge']} !important;\n"
        "  stroke-width: 1.7px !important;\n"
        "}\n\n"
        ".marker,\n.marker path {\n"
        f"  fill: {c['edge']} !important;\n"
        f"  stroke: {c['edge']} !important;\n"
        "}\n\n"
        ".edgeLabel {\n"
        f"  background-color: {c['canvas']} !important;\n"
        f"  color: {c['edge']} !important;\n"
        "  padding: 2px 6px !important;\n"
        "  font-size: 0.86em !important;\n"
        "}\n"
        ".edgeLabel rect,\n.edgeLabel foreignObject div {\n"
        f"  fill: {c['canvas']} !important;\n"
        "}\n\n"
    )

    parts.append(
        "/* Clusters */\n"
        ".cluster rect {\n"
        f"  fill: {c['paper']} !important;\n"
        f"  stroke: {c['quiet_line']} !important;\n"
        "  stroke-width: 1.3px !important;\n"
        "  rx: 8px;\n  ry: 8px;\n"
        "}\n"
        # Cluster titles keep the inherited weight on purpose: Mermaid measures the label box
        # before any external stylesheet loads, so widening the glyphs here clips the last letter.
        ".cluster-label,\n.cluster-label span {\n"
        f"  color: {c['navy']} !important;\n"
        "}\n\n"
    )

    parts.append("/* Semantic node roles - one block per role in exhibits/figure_palette.json */\n")
    for role, spec in palette["roles"].items():
        selectors = ",\n".join(f".{role} {suffix}" for suffix in SHAPE_SELECTOR_SUFFIXES)
        parts.append(
            f"/* {spec['meaning']} */\n"
            f"{selectors} {{\n"
            f"  fill: {c[spec['fill']]} !important;\n"
            f"  stroke: {c[spec['stroke']]} !important;\n"
            f"  stroke-width: {spec['stroke_width_px']}px !important;\n"
            f"{dash_declaration(spec['dash'])}"
            "}\n"
            f".{role} .nodeLabel,\n.{role} .nodeLabel *,\n.{role} .label,\n.{role} .label * {{\n"
            f"  color: {c[spec['text']]} !important;\n"
            "}\n\n"
        )

    return "".join(parts)


def write_if_changed(path: Path, content: str) -> bool:
    previous = path.read_text(encoding="utf-8") if path.is_file() else None
    if previous == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    palette = load_palette()
    config_text = json.dumps(build_config(palette), indent=2, ensure_ascii=False) + "\n"
    css_text = build_css(palette)

    changed = [
        label
        for label, path, text in (
            ("mermaid-config.json", CONFIG_PATH, config_text),
            ("mermaid.css", CSS_PATH, css_text),
        )
        if write_if_changed(path, text)
    ]

    palette_name = f"{palette['name']} v{palette['version']}"
    if changed:
        print(f"Theme rebuilt from {palette_name}: updated " + ", ".join(changed))
    else:
        print(f"Theme already current for {palette_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
