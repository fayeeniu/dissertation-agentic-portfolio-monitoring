#!/usr/bin/env python3
"""Validate the code-authored dissertation figure chain.

Checks the pinned Mermaid source/render manifest, PNG integrity and dimensions, that every figure
also has a vector SVG master, that all figures share one generated palette, config and stylesheet,
and that the manuscript references the current PNG renders rather than superseded PDF renders.
"""

from __future__ import annotations

import csv
import hashlib
import re
import struct
from pathlib import Path

DISSERTATION_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = DISSERTATION_ROOT / "exhibits" / "MERMAID_MANIFEST.csv"
PALETTE_PATH = DISSERTATION_ROOT / "exhibits" / "figure_palette.json"
CONFIG_PATH = DISSERTATION_ROOT / "exhibits" / "mermaid-config.json"
CSS_PATH = DISSERTATION_ROOT / "exhibits" / "mermaid.css"
RENDER_SCRIPT_PATH = DISSERTATION_ROOT / "scripts" / "render_mermaid_figures.sh"
EXPECTED_IDS = {
    "intro_f1_problem_to_research_contract",
    "lit_f1_evidence_claim_admission_audit_chain",
    "lit_f2_discovery_is_not_evidence",
    "meth_f1_design_science_evidence_chain",
    "meth_f2_dataset_freeze_timeline",
    "meth_f3_analysis_decision_flow",
    "sys_f1_architecture_deployment_boundary",
    "sys_f2_canonical_data_provenance_model",
    "sys_f3_legal_identity_decision_flow",
    "sys_f4_fixed_workflow_verification_state_machine",
    "sys_f5_company_research_evidence_funnel",
    "eval_f1_d0_metric_profile",
}
REQUIRED_FIELDS = {
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
}
# Colour must live in the shared palette only, never in an individual figure source.
HEX_COLOUR = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
INLINE_STYLE = re.compile(r"^\s*(classDef|style|linkStyle)\s", re.MULTILINE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise ValueError("invalid PNG signature")
        length = struct.unpack(">I", handle.read(4))[0]
        chunk_type = handle.read(4)
        if chunk_type != b"IHDR" or length < 8:
            raise ValueError("missing PNG IHDR")
        return struct.unpack(">II", handle.read(8))


def manuscript_text() -> str:
    paths = sorted((DISSERTATION_ROOT / "chapters").glob("*.tex"))
    paths.extend(sorted((DISSERTATION_ROOT / "exhibits").glob("*.tex")))
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def main() -> int:
    errors: list[str] = []
    if not MANIFEST_PATH.is_file():
        print(f"FAIL: missing {MANIFEST_PATH}")
        return 1

    with MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_FIELDS.difference(reader.fieldnames or ())
        if missing:
            errors.append("manifest fields missing: " + ", ".join(sorted(missing)))
        rows = list(reader)

    ids = [row.get("figure_id", "") for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("manifest contains duplicate figure IDs")
    if set(ids) != EXPECTED_IDS:
        errors.append(
            "manifest figure IDs differ: missing="
            + ",".join(sorted(EXPECTED_IDS.difference(ids)))
            + " extra="
            + ",".join(sorted(set(ids).difference(EXPECTED_IDS)))
        )

    shared_hashes = {
        "palette_sha256": (PALETTE_PATH, sha256(PALETTE_PATH)),
        "config_sha256": (CONFIG_PATH, sha256(CONFIG_PATH)),
        "css_sha256": (CSS_PATH, sha256(CSS_PATH)),
        "render_script_sha256": (RENDER_SCRIPT_PATH, sha256(RENDER_SCRIPT_PATH)),
    }
    tex = manuscript_text()
    dimensions: list[str] = []

    for row in rows:
        figure_id = row["figure_id"]
        source = DISSERTATION_ROOT / row["source_mmd"]
        render = DISSERTATION_ROOT / row["render_png"]
        vector = DISSERTATION_ROOT / row["render_svg"]

        if row["renderer"] != "mermaid-cli@11.16.0":
            errors.append(f"{figure_id}: renderer is not pinned to mermaid-cli@11.16.0")
        if row["status"] not in {"current", "retired"}:
            errors.append(f"{figure_id}: manifest status must be current or retired")

        if source.is_file():
            text = source.read_text(encoding="utf-8")
            if HEX_COLOUR.search(text) or INLINE_STYLE.search(text):
                errors.append(
                    f"{figure_id}: source declares its own colour or style; every figure must use "
                    "the shared fx-* roles from exhibits/figure_palette.json"
                )

        for path, expected_hash, label in (
            (source, row["source_sha256"], "source"),
            (vector, row["svg_sha256"], "vector"),
            (render, row["render_sha256"], "render"),
        ):
            if not path.is_file():
                errors.append(f"{figure_id}: missing {label} {path}")
                continue
            actual = sha256(path)
            if actual != expected_hash:
                errors.append(
                    f"{figure_id}: {label} hash mismatch: expected {expected_hash}, got {actual}"
                )

        if render.is_file():
            try:
                width, height = png_dimensions(render)
                dimensions.append(f"{figure_id}={width}x{height}")
                if width < 1000 or height < 450:
                    errors.append(
                        f"{figure_id}: render is below the minimum 1000x450 ({width}x{height})"
                    )
            except ValueError as exc:
                errors.append(f"{figure_id}: {exc}")

        for field, (_, actual_hash) in shared_hashes.items():
            if row[field] != actual_hash:
                errors.append(
                    f"{figure_id}: {field} mismatch: expected {row[field]}, got {actual_hash}"
                )

        if row["status"] == "current":
            if f"{figure_id}.png" not in tex:
                errors.append(f"{figure_id}: current PNG is not referenced by the manuscript")
            if f"{figure_id}.pdf" in tex:
                errors.append(f"{figure_id}: superseded PDF is still referenced by the manuscript")
        elif f"{figure_id}.png" in tex or f"{figure_id}.pdf" in tex:
            errors.append(f"{figure_id}: retired figure is still referenced by the manuscript")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAIL: {len(errors)} figure provenance error(s)")
        return 1

    current = sum(1 for row in rows if row["status"] == "current")
    print(
        f"PASS: {len(rows)} Mermaid records, including {current} current manuscript figures and "
        f"{len(rows) - current} retired figures, with sources, SVG masters, PNG renders, the shared "
        "palette-driven render inputs and all hashes verified"
    )
    print("Dimensions: " + "; ".join(dimensions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
