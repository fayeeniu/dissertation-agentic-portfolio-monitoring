from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select

from .bootstrap import Runtime
from .enums import DataClassification
from .ids import sha256_bytes, stable_hash
from .llm.experiment import SYNTHETIC_EXPERIMENT_EVIDENCE_ID
from .models import EvidenceItemModel, ExtractionAttemptModel, ExtractionModel


class OpenAISmokeTestError(RuntimeError):
    pass


def _safe_attempt(attempt: ExtractionAttemptModel) -> dict[str, Any]:
    return {
        "attempt_number": attempt.attempt_number,
        "provider": attempt.provider,
        "model": attempt.model,
        "status": attempt.status,
        "input_hash": attempt.input_hash,
        "output_hash": attempt.output_hash,
        "input_tokens": attempt.input_tokens,
        "output_tokens": attempt.output_tokens,
        "duration_ms": attempt.duration_ms,
        "escalation_cause": attempt.escalation_cause,
        "error_type": attempt.error.split(":", 1)[0] if attempt.error else None,
    }


def run_openai_synthetic_smoke(
    runtime: Runtime,
    *,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Run one real model extraction inside the fixed synthetic workflow."""

    fixture_path = runtime.settings.project_root / "fixtures" / "synthetic_portfolio.json"
    evidence_fixture_path = (
        runtime.settings.project_root / "fixtures" / "evidence" / "synthetic_evidence.json"
    )
    imported = runtime.importer.import_file(
        fixture_path,
        classification=DataClassification.SYNTHETIC,
    )
    pipeline = runtime.workflow.run(imported.dataset_id)

    with runtime.session_factory() as session:
        evidence = session.get(EvidenceItemModel, SYNTHETIC_EXPERIMENT_EVIDENCE_ID)
        attempts = list(
            session.scalars(
                select(ExtractionAttemptModel)
                .where(
                    ExtractionAttemptModel.run_id == pipeline.run_id,
                    ExtractionAttemptModel.evidence_item_id == SYNTHETIC_EXPERIMENT_EVIDENCE_ID,
                    ExtractionAttemptModel.provider == "openai_responses_structured_extractor",
                )
                .order_by(ExtractionAttemptModel.attempt_number)
            ).all()
        )
        extraction = session.scalar(
            select(ExtractionModel).where(
                ExtractionModel.run_id == pipeline.run_id,
                ExtractionModel.evidence_item_id == SYNTHETIC_EXPERIMENT_EVIDENCE_ID,
                ExtractionModel.provider == "openai_responses_structured_extractor",
            )
        )
        safe_attempts = [_safe_attempt(attempt) for attempt in attempts]
        evidence_checksum = evidence.checksum if evidence is not None else None

    manifest = {
        "schema_version": "1.0",
        "experiment": "bounded_synthetic_openai_smoke",
        "created_at": datetime.now(UTC).isoformat(),
        "dataset_id": imported.dataset_id,
        "run_id": pipeline.run_id,
        "report_id": pipeline.report_id,
        "report_status": pipeline.report_status,
        "selected_evidence_id": SYNTHETIC_EXPERIMENT_EVIDENCE_ID,
        "selected_evidence_checksum": evidence_checksum,
        "portfolio_fixture_sha256": sha256_bytes(fixture_path.read_bytes()),
        "evidence_fixture_sha256": sha256_bytes(evidence_fixture_path.read_bytes()),
        "external_model_attempts": safe_attempts,
        "strict_extraction_persisted": extraction is not None,
        "claim_counts": pipeline.claim_counts,
        "evidence_boundary": "One checksum-pinned synthetic item; no restricted/internal input.",
        "claim_boundary": "Development smoke evidence only; no performance or cost claim.",
    }
    envelope = {"manifest": manifest, "manifest_sha256": stable_hash(manifest)}
    target_dir = output_dir or runtime.settings.project_root / "var" / "experiments"
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"openai-smoke-{pipeline.run_id}.json"
    temporary_path = output_path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(envelope, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)

    result = {
        "status": "passed" if extraction is not None else "failed",
        "manifest": str(output_path),
        "manifest_sha256": envelope["manifest_sha256"],
        "run_id": pipeline.run_id,
        "report_id": pipeline.report_id,
        "report_status": pipeline.report_status,
        "external_model_attempt_count": len(attempts),
        "models": [attempt.model for attempt in attempts],
        "input_tokens": sum(attempt.input_tokens or 0 for attempt in attempts),
        "output_tokens": sum(attempt.output_tokens or 0 for attempt in attempts),
    }
    if extraction is None:
        raise OpenAISmokeTestError(
            f"The live model did not produce a persisted strict extraction; inspect {output_path}."
        )
    return result
