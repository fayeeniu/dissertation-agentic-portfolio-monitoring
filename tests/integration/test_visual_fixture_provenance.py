from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest
from sqlalchemy import select

from portfolio_agent.bootstrap import Runtime, project_root
from portfolio_agent.enums import DataClassification
from portfolio_agent.evaluation import run_evaluation
from portfolio_agent.models import (
    ClaimModel,
    EvidenceItemModel,
    ExtractionAttemptModel,
    ObservationModel,
    QualityViolationModel,
    run_evidence,
)


def test_visual_numeric_inputs_match_executable_synthetic_evidence(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    visual = json.loads(
        (project_root() / "fixtures" / "visualisation_pack.json").read_text(encoding="utf-8")
    )
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    result = runtime.workflow.run(imported.dataset_id)
    with runtime.session_factory() as session:
        verification = Counter(
            session.scalars(
                select(ClaimModel.verification_status).where(ClaimModel.run_id == result.run_id)
            ).all()
        )
        evidence = Counter(
            session.scalars(
                select(EvidenceItemModel.source_type)
                .join(run_evidence, run_evidence.c.evidence_item_id == EvidenceItemModel.id)
                .where(run_evidence.c.run_id == result.run_id)
            ).all()
        )
        missingness = Counter(session.scalars(select(ObservationModel.missing_state)).all())
        quality = Counter(
            session.scalars(
                select(QualityViolationModel.disposition).where(
                    QualityViolationModel.run_id == result.run_id
                )
            ).all()
        )
        attempts = Counter(
            session.scalars(
                select(ExtractionAttemptModel.status).where(
                    ExtractionAttemptModel.run_id == result.run_id
                )
            ).all()
        )

    assert visual["workflow"]["observations"] == imported.observation_count
    assert visual["workflow"]["verification"] == dict(verification)
    assert visual["workflow"]["evidence"] == dict(evidence)
    assert visual["workflow"]["missingness"] == dict(missingness)
    for disposition, count in visual["workflow"]["quality"].items():
        assert quality[disposition] == count
    for status, count in visual["workflow"]["extraction_attempts"].items():
        assert attempts[status] == count

    evaluation = run_evaluation(project_root() / "fixtures" / "evaluation_manifest.json", repeats=3)
    summaries = {item["condition"]: item for item in evaluation["summaries"]}
    for condition in ("deterministic_single_agent", "multi_agent_verification"):
        for metric, expected in visual["evaluation"][condition].items():
            assert summaries[condition][metric] == pytest.approx(expected, abs=1e-9)
