from __future__ import annotations

import json
from pathlib import Path

import pytest

from portfolio_agent.cli import main
from portfolio_agent.evaluation import run_evaluation
from portfolio_agent.evaluation_datasets import (
    EvaluationDatasetError,
    SealedDatasetError,
    ensure_operational_id,
    load_evaluation_dataset,
)
from portfolio_agent.ids import sha256_bytes


def test_synthetic_evaluation_keeps_human_conditions_unexecuted(
    evaluation_cases_path: Path,
) -> None:
    result = run_evaluation(evaluation_cases_path, repeats=3)
    summaries = {item["condition"]: item for item in result["summaries"]}

    assert result["source"]["classification"] == "synthetic"
    assert result["source"]["tier"] == "D0"
    assert result["source"]["namespace"] == "benchmark:d0"
    assert all(item["case_id"].startswith("benchmark:d0:case:") for item in result["case_results"])
    assert summaries["manual"]["case_count"] == 0
    assert summaries["manual"]["precision"] is None
    assert summaries["multi_agent_hitl"]["case_count"] == 0
    assert summaries["multi_agent_verification"]["repeat_consistency"] == 1.0
    assert summaries["multi_agent_verification"]["hallucination_rate"] == 0.0
    assert summaries["multi_agent_verification"]["event_accuracy"] is None
    assert summaries["multi_agent_verification"]["identity_accuracy"] is None
    assert summaries["multi_agent_verification"]["extraction_accuracy"] is None
    assert summaries["multi_agent_verification"]["temporal_accuracy"] is None
    assert summaries["multi_agent_verification"]["quality_accuracy"] is None
    assert summaries["multi_agent_verification"]["report_accuracy"] is None
    assert summaries["multi_agent_verification"]["contradiction_accuracy"] == 1.0
    assert result["condition_parity"]["shared_core"] == [
        "catalogue",
        "normalization",
        "input_cases",
    ]


def test_evaluation_holdout_is_sealed_and_namespace_cannot_join_operations(
    evaluation_cases_path: Path,
) -> None:
    with pytest.raises(SealedDatasetError, match="sealed"):
        load_evaluation_dataset(evaluation_cases_path, tier="D2")
    with pytest.raises(EvaluationDatasetError, match="operational"):
        ensure_operational_id("benchmark:d0:entity:fictional")


def test_evaluation_manifest_checksum_is_enforced(
    evaluation_cases_path: Path, tmp_path: Path
) -> None:
    manifest = evaluation_cases_path.read_text(encoding="utf-8").replace(
        "f403d59ed8db8b3a7c8e2f19cae9e8d098317f6c09da94be361ffcf8a122c94b",
        "0" * 64,
    )
    copied_cases = tmp_path / "evaluation_cases.json"
    copied_cases.write_bytes((evaluation_cases_path.parent / "evaluation_cases.json").read_bytes())
    copied_manifest = tmp_path / "evaluation_manifest.json"
    copied_manifest.write_text(manifest, encoding="utf-8")
    with pytest.raises(EvaluationDatasetError, match="checksum"):
        load_evaluation_dataset(copied_manifest)


def test_evaluation_period_groups_cannot_cross_partitions(
    evaluation_cases_path: Path, tmp_path: Path
) -> None:
    cases_path = evaluation_cases_path.parent / "evaluation_cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    cases["cases"][0]["split"] = "development"
    copied_cases = tmp_path / "evaluation_cases.json"
    payload = json.dumps(cases, indent=2, sort_keys=True).encode()
    copied_cases.write_bytes(payload)

    manifest = json.loads(evaluation_cases_path.read_text(encoding="utf-8"))
    manifest["datasets"][0]["sha256"] = sha256_bytes(payload)
    copied_manifest = tmp_path / "evaluation_manifest.json"
    copied_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(EvaluationDatasetError, match="Period groups cross"):
        load_evaluation_dataset(copied_manifest)


def test_evaluation_rejects_unsupported_dataset_schema_version(
    evaluation_cases_path: Path, tmp_path: Path
) -> None:
    cases = json.loads(
        (evaluation_cases_path.parent / "evaluation_cases.json").read_text(encoding="utf-8")
    )
    cases["schema_version"] = "evaluation-cases-v999"
    payload = json.dumps(cases, sort_keys=True).encode()
    (tmp_path / "evaluation_cases.json").write_bytes(payload)
    manifest = json.loads(evaluation_cases_path.read_text(encoding="utf-8"))
    manifest["datasets"][0]["sha256"] = sha256_bytes(payload)
    manifest["datasets"][0]["source_version"] = "evaluation-cases-v999"
    copied_manifest = tmp_path / "evaluation_manifest.json"
    copied_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="evaluation-cases-v1"):
        load_evaluation_dataset(copied_manifest)


def test_evaluation_manifest_source_version_must_match_document(
    evaluation_cases_path: Path, tmp_path: Path
) -> None:
    (tmp_path / "evaluation_cases.json").write_bytes(
        (evaluation_cases_path.parent / "evaluation_cases.json").read_bytes()
    )
    manifest = json.loads(evaluation_cases_path.read_text(encoding="utf-8"))
    manifest["datasets"][0]["source_version"] = "evaluation-cases-v999"
    copied_manifest = tmp_path / "evaluation_manifest.json"
    copied_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(EvaluationDatasetError, match="source version"):
        load_evaluation_dataset(copied_manifest)


def test_deprecated_cases_cli_resolves_only_through_sibling_manifest(
    evaluation_cases_path: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "evaluation.json"
    exit_code = main(
        [
            "evaluate",
            "--cases",
            str(evaluation_cases_path.parent / "evaluation_cases.json"),
            "--output",
            str(output),
            "--repeats",
            "2",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "--cases is deprecated" in captured.err
    assert output.is_file()
    assert json.loads(output.read_text(encoding="utf-8"))["source"]["tier"] == "D0"


def test_deprecated_cases_cli_rejects_unadmitted_file(tmp_path: Path) -> None:
    unadmitted = tmp_path / "evaluation_cases.json"
    unadmitted.write_text('{"schema_version":"evaluation-cases-v1"}', encoding="utf-8")

    with pytest.raises(EvaluationDatasetError, match="sibling"):
        main(["evaluate", "--cases", str(unadmitted)])
