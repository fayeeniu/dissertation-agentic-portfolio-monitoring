from __future__ import annotations

import io
import json
import stat
from pathlib import Path

import pytest
from openpyxl import Workbook
from sqlalchemy import select

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification, MissingState
from portfolio_agent.importers import ImportValidationError
from portfolio_agent.models import ObservationModel


def test_json_import_is_immutable_idempotent_and_preserves_missing_states(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    first = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    second = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )

    assert first.company_count == 3
    assert first.observation_count == 21
    assert any(issue.code == "unknown_metric" for issue in first.issues)
    assert second.reused_existing
    assert second.dataset_id == first.dataset_id

    snapshot = next((runtime.settings.raw_data_dir / first.dataset_id).iterdir())
    assert stat.S_IMODE(snapshot.stat().st_mode) == 0o600
    with runtime.session_factory() as session:
        states = set(
            session.scalars(
                select(ObservationModel.missing_state).where(
                    ObservationModel.raw_submission_id == first.raw_submission_id
                )
            ).all()
        )
    assert {MissingState.ZERO.value, MissingState.BLANK.value}.issubset(states)
    assert MissingState.NOT_REPORTED.value in states
    assert MissingState.NOT_FOUND_PUBLICLY.value in states


def test_matrix_import_supports_csv_and_xlsx(runtime: Runtime) -> None:
    csv_payload = b"Metric,Aster Synthetic\nemployees_total,4\njobs_created,0\n"
    csv_result = runtime.importer.import_bytes(
        csv_payload,
        filename="synthetic.csv",
        period_label="CSV-PERIOD",
        classification=DataClassification.SYNTHETIC,
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Metric", "Redwood Synthetic"])
    sheet.append(["employees_total", "5"])
    sheet.append(["grant_funding", "GBP 10"])
    buffer = io.BytesIO()
    workbook.save(buffer)
    xlsx_result = runtime.importer.import_bytes(
        buffer.getvalue(),
        filename="synthetic.xlsx",
        period_label="XLSX-PERIOD",
        classification=DataClassification.SYNTHETIC,
    )

    assert csv_result.observation_count == 2
    assert xlsx_result.observation_count == 2


def test_conflicting_company_identity_is_held(runtime: Runtime) -> None:
    first = {
        "reporting_period": {"label": "IDENTITY-1"},
        "companies": [
            {"name": "Same Synthetic Ltd", "external_id": "ONE", "metrics": {"employees_total": 1}}
        ],
    }
    second = {
        "reporting_period": {"label": "IDENTITY-2"},
        "companies": [
            {"name": "Same Synthetic Ltd", "external_id": "TWO", "metrics": {"employees_total": 2}}
        ],
    }
    runtime.importer.import_bytes(
        json.dumps(first).encode(),
        filename="first.json",
        classification=DataClassification.SYNTHETIC,
    )
    result = runtime.importer.import_bytes(
        json.dumps(second).encode(),
        filename="second.json",
        classification=DataClassification.SYNTHETIC,
    )
    assert result.company_count == 0
    assert any(issue.code == "ambiguous_company_identity" for issue in result.issues)


def test_xlsx_and_csv_require_period_labels(runtime: Runtime) -> None:
    with pytest.raises(ImportValidationError, match="period"):
        runtime.importer.import_bytes(b"Metric,Company\nrevenue,1\n", filename="x.csv")
