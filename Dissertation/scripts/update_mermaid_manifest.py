#!/usr/bin/env python3
"""Rebind exhibits/MERMAID_MANIFEST.csv to the figures currently on disk.

The manifest is the provenance record for the figure pipeline: it ties every Mermaid source to its
SVG and PNG renders and to the shared inputs that decide how those renders look (the palette, the
generated Mermaid config, the generated stylesheet and the render script).

Only hashes are recomputed. The `status` column is editorial and is carried over unchanged, so a
retired figure stays retired. `scripts/render_mermaid_figures.sh` calls this after rendering, and
`scripts/check_mermaid_figures.py` verifies the result.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

DISSERTATION_ROOT = Path(__file__).resolve().parents[1]
EXHIBIT_DIR = DISSERTATION_ROOT / "exhibits"
MANIFEST_PATH = EXHIBIT_DIR / "MERMAID_MANIFEST.csv"
RENDERER = "mermaid-cli@11.16.0"

SHARED_INPUTS = {
    "palette_sha256": EXHIBIT_DIR / "figure_palette.json",
    "config_sha256": EXHIBIT_DIR / "mermaid-config.json",
    "css_sha256": EXHIBIT_DIR / "mermaid.css",
    "render_script_sha256": DISSERTATION_ROOT / "scripts" / "render_mermaid_figures.sh",
}

FIELDNAMES = [
    "figure_id",
    "source_mmd",
    "source_sha256",
    "render_svg",
    "svg_sha256",
    "render_png",
    "render_sha256",
    "renderer",
    "palette_sha256",
    "config_sha256",
    "css_sha256",
    "render_script_sha256",
    "status",
]

# Figures kept as review history: rendered and hashed, but not referenced by the manuscript.
RETIRED_BY_DEFAULT = {
    "intro_f1_problem_to_research_contract",
    "meth_f2_dataset_freeze_timeline",
    "meth_f3_analysis_decision_flow",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def existing_statuses() -> dict[str, str]:
    if not MANIFEST_PATH.is_file():
        return {}
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
        return {
            row["figure_id"]: row["status"]
            for row in csv.DictReader(handle)
            if row.get("figure_id") and row.get("status")
        }


def figure_order() -> list[str]:
    """Manuscript order, taken from the render script so the two never drift."""
    script = (DISSERTATION_ROOT / "scripts" / "render_mermaid_figures.sh").read_text(
        encoding="utf-8"
    )
    _, _, tail = script.partition("readonly FIGURES=(")
    block, _, _ = tail.partition(")")
    return [line.strip().strip('"') for line in block.splitlines() if line.strip().startswith('"')]


def main() -> int:
    statuses = existing_statuses()
    shared = {field: sha256(path) for field, path in SHARED_INPUTS.items()}

    rows = []
    missing: list[str] = []
    for figure_id in figure_order():
        source = EXHIBIT_DIR / f"{figure_id}.mmd"
        svg = EXHIBIT_DIR / f"{figure_id}.svg"
        png = EXHIBIT_DIR / f"{figure_id}.png"
        absent = [path.name for path in (source, svg, png) if not path.is_file()]
        if absent:
            missing.append(f"{figure_id}: {', '.join(absent)}")
            continue

        default_status = "retired" if figure_id in RETIRED_BY_DEFAULT else "current"
        rows.append(
            {
                "figure_id": figure_id,
                "source_mmd": f"exhibits/{source.name}",
                "source_sha256": sha256(source),
                "render_svg": f"exhibits/{svg.name}",
                "svg_sha256": sha256(svg),
                "render_png": f"exhibits/{png.name}",
                "render_sha256": sha256(png),
                "renderer": RENDERER,
                "status": statuses.get(figure_id, default_status),
                **shared,
            }
        )

    if missing:
        for entry in missing:
            print(f"ERROR: missing artefact for {entry}")
        print(f"FAIL: {len(missing)} figure(s) have no complete render set")
        return 1

    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    current = sum(1 for row in rows if row["status"] == "current")
    print(
        f"Manifest rebound: {len(rows)} figures ({current} current, {len(rows) - current} retired)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
