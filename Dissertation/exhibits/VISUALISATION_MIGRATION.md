# Visualisation render authority

The current dissertation figures are the twelve Mermaid `.mmd` sources in this directory and their
generated `.svg` vector masters and `.png` renders, all listed in `MERMAID_MANIFEST.csv`. Nine are
referenced by the manuscript; three (`intro_f1`, `meth_f2`, `meth_f3`) are retained as rendered
review history and are not referenced.

## Pipeline

One command rebuilds the theme, every figure and the manifest:

```bash
./scripts/render_mermaid_figures.sh
python3 scripts/check_mermaid_figures.py
```

The chain is:

1. `exhibits/figure_palette.json` is the single source of truth for colour, typography, layout
   geometry and the meaning of every semantic node role.
2. `scripts/build_figure_theme.py` expands it into `exhibits/mermaid-config.json` and
   `exhibits/mermaid.css`. Both are generated files and must not be edited by hand.
3. `@mermaid-js/mermaid-cli@11.16.0`, pinned, renders each `.mmd` source to `.svg` and `.png`.
4. `scripts/update_mermaid_manifest.py` rebinds `MERMAID_MANIFEST.csv` to the new hashes.

The LaTeX build consumes the PNG renders; the SVG files are the genuinely vector masters. No figure
uses a raster effect. `scripts/check_mermaid_figures.py` verifies every hash, rejects a figure
source that declares its own colour or `classDef`/`style`/`linkStyle`, and rejects a manuscript
reference to a retired figure or a superseded PDF.

## Shared palette

Colour never appears in a figure source. An `.mmd` file assigns meaning only, with
`class <nodes> fx-<role>`, and the role table in `figure_palette.json` decides how that renders.
The palette is one blue hue family (four tints plus one deep shade), one warm amber accent for
held, blocked, rejected or failed states, and one neutral grey.

| Role | Meaning |
| --- | --- |
| `fx-banner` | Framing statement, evidence boundary or table header row (deep navy, white text) |
| `fx-key` | Emphasised gate, decision or verification point (medium tint) |
| `fx-stage` | Standard implemented process step (light tint) |
| `fx-input` | Input or candidate material that is not yet evidence (lightest tint, muted border) |
| `fx-live` | Control built and tested, but never run against a live external source (navy dashed) |
| `fx-hold` | Held, blocked, rejected, failed or explicitly unmeasured (amber dashed) |
| `fx-note` | Side annotation or out-of-scope material (neutral grey dashed) |
| `fx-rowhead`, `fx-cell` | Table row labels and value cells |

Accessibility: no meaning depends on red against green, and blue against amber stays separable
under deuteranopia, protanopia and tritanopia. Every non-standard role also carries a second,
non-colour cue - a dash pattern and stroke weight - so the figures remain readable in greyscale
print.

## Layout notes

Line breaks inside node labels are authored deliberately with `<br/>` rather than left to automatic
wrapping. Block diagrams give every cell the width of the widest cell, and a figure is scaled to the
text width of a portrait A4 page, so a narrow figure is a larger, more legible figure. Flowcharts
use the ELK renderer, which keeps annotation nodes on both sides of a chain instead of letting the
chain drift diagonally. Nodes that carry no relationship in the diagram are positioned with
Mermaid's invisible `~~~` links, so their placement never implies an edge that the figure does not
assert.

Two constraints are worth recording:

- `intro_f1` carries a per-figure `init` directive pinning it to the Dagre renderer. It is the only
  figure whose meaning depends on `direction` inside a subgraph, and ELK reorders those members, which
  breaks its numbered columns. This is a layout override, not a colour override; colour still comes
  only from the shared palette.
- A block diagram gives every cell the height of the tallest cell, so a short full-width banner above
  tall stage cells leaves visible whitespace (`sys_f5`). The compact grid is what keeps the label text
  legible at page scale, so the whitespace is accepted deliberately.

## Superseded artefacts

Earlier Python generators, hand-authored SVG/PDF renders, table-based exhibits and per-figure
provenance JSON files are retained as historical review evidence only. They are not referenced by
the manuscript and are not the current visual authority. This preserves review history without
presenting superseded renders as current.
