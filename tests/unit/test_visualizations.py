from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree

import pytest

from portfolio_agent.bootstrap import project_root
from portfolio_agent.visualizations import generate_visual_pack


def test_visual_pack_is_deterministic_accessible_and_manifested(tmp_path: Path) -> None:
    source = project_root() / "fixtures" / "visualisation_pack.json"
    relocated = tmp_path / "relocated" / source.name
    relocated.parent.mkdir()
    relocated.write_bytes(source.read_bytes())
    first = tmp_path / "first"
    second = tmp_path / "second"
    manifest_a = generate_visual_pack(source, first)
    manifest_b = generate_visual_pack(relocated, second)

    assert manifest_a == manifest_b
    assert (first / "manifest.json").read_bytes() == (second / "manifest.json").read_bytes()
    assert manifest_a["input"]["name"] == "visualisation_pack.json"
    assert "path" not in manifest_a["input"]
    assert manifest_a["figure_count"] >= 12
    assert (first / "figure-data.csv").read_bytes() == (second / "figure-data.csv").read_bytes()
    for row in manifest_a["figures"]:
        first_bytes = (first / row["filename"]).read_bytes()
        assert first_bytes == (second / row["filename"]).read_bytes()
        root = ElementTree.fromstring(first_bytes)
        namespace = "{http://www.w3.org/2000/svg}"
        assert root.attrib["role"] == "img"
        assert root.find(f"{namespace}title") is not None
        assert root.find(f"{namespace}desc") is not None
        assert row["source"] and row["sample"] and row["cutoff"]
        assert row["textual_alternative"]

    loaded = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    assert loaded["input"]["classification"] == "synthetic-and-structural-counts-only"


def test_visual_pack_rejects_unsupported_schema_version(tmp_path: Path) -> None:
    source = project_root() / "fixtures" / "visualisation_pack.json"
    document = json.loads(source.read_text(encoding="utf-8"))
    document["schema_version"] = "dissertation-visual-pack-v999"
    unsupported = tmp_path / "unsupported.json"
    unsupported.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match="dissertation-visual-pack-v1"):
        generate_visual_pack(unsupported, tmp_path / "generated")


def test_visual_text_alternatives_are_derived_from_current_input(tmp_path: Path) -> None:
    source = project_root() / "fixtures" / "visualisation_pack.json"
    document = json.loads(source.read_text(encoding="utf-8"))
    document["workflow"]["evidence"] = {"portfolio_submission": 5, "public": 7}
    document["workflow"]["quality"] = {"exclude": 2, "hold": 3, "warn": 4}
    document["workflow"]["extraction_attempts"] = {
        "succeeded": 6,
        "abstained": 7,
        "rejected": 8,
        "failed": 9,
    }
    document["evaluation"]["case_count"] = 23
    document["evaluation"]["deterministic_single_agent"] = {
        "precision": 0.12,
        "recall": 0.34,
        "verification_accuracy": 0.56,
    }
    document["evaluation"]["multi_agent_verification"] = {
        "precision": 0.65,
        "recall": 0.43,
        "verification_accuracy": 0.21,
    }
    modified = tmp_path / "visualisation_pack.json"
    modified.write_text(json.dumps(document), encoding="utf-8")

    manifest = generate_visual_pack(modified, tmp_path / "generated")
    alternatives = {row["key"]: row["textual_alternative"] for row in manifest["figures"]}

    assert "5 portfolio submission items, 7 public items" in alternatives["source-coverage"]
    assert "exclude 2, hold 3, warn 4" in alternatives["quality-dispositions"]
    assert (
        "succeeded 6, abstained 7, rejected 8, failed 9"
        in alternatives["extraction-attempt-outcomes"]
    )
    assert "23 cases" in alternatives["evaluation-condition-comparison"]
    assert (
        "precision 0.12, recall 0.34, verification accuracy 0.56"
        in alternatives["evaluation-condition-comparison"]
    )
    assert (
        "precision 0.65, recall 0.43, verification accuracy 0.21"
        in alternatives["evaluation-condition-comparison"]
    )
