from __future__ import annotations

from pathlib import Path

from portfolio_agent.evaluation import run_evaluation


def test_synthetic_evaluation_keeps_human_conditions_unexecuted(
    evaluation_cases_path: Path,
) -> None:
    result = run_evaluation(evaluation_cases_path, repeats=3)
    summaries = {item["condition"]: item for item in result["summaries"]}

    assert result["source"]["classification"] == "synthetic"
    assert summaries["manual"]["case_count"] == 0
    assert summaries["manual"]["precision"] is None
    assert summaries["multi_agent_hitl"]["case_count"] == 0
    assert summaries["multi_agent_verification"]["repeat_consistency"] == 1.0
    assert summaries["multi_agent_verification"]["hallucination_rate"] == 0.0
