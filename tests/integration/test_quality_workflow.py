from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from sqlalchemy import select

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.connectors.base import (
    SourceCapabilityManifest,
    SourceCollection,
    SourceFactContract,
    SourceRequest,
)
from portfolio_agent.connectors.registry import SourceRegistry
from portfolio_agent.enums import (
    CollectionStatus,
    DataClassification,
    IdentifierScheme,
)
from portfolio_agent.models import (
    CompanyIdentifierModel,
    ObservationModel,
    QualityContractModel,
    QualityViolationModel,
    ReportSectionModel,
    SourceSnapshotModel,
)


def test_workflow_persists_versioned_source_linked_quality(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    result = runtime.workflow.run(imported.dataset_id)
    with runtime.session_factory() as session:
        contract = session.scalar(select(QualityContractModel))
        findings = list(
            session.scalars(
                select(QualityViolationModel).where(QualityViolationModel.run_id == result.run_id)
            ).all()
        )
    assert contract is not None
    assert contract.version == "uk-public-evidence-quality-v2"
    assert contract.sha256
    assert {(finding.rule_key, finding.disposition) for finding in findings} == {
        ("trusted_evidence", "exclude"),
        ("public_conflict", "hold"),
    }
    assert all(finding.evidence_item_id for finding in findings)


class _TerminalCompaniesHouseConnector:
    manifest = SourceCapabilityManifest(
        key="companies_house",
        version="terminal-state-test-v1",
        publisher="Synthetic terminal-state source",
        identifier_schemes=(IdentifierScheme.COMPANIES_HOUSE_NUMBER,),
        fact_contracts=(
            SourceFactContract(
                fact_key="company_status",
                metric_keys=(None,),
                extraction_method="deterministic_json_pointer",
                extraction_schema_version="terminal-state-test-v1",
            ),
        ),
        event_types=(),
        media_types=("application/json",),
        retrieval_modes=("offline_snapshot",),
        licence_reference="repository-owned synthetic fixture",
        terms_reference="local deterministic tests only",
        admission_reviewed_at=date(2026, 8, 26),
    )

    def __init__(self, status: CollectionStatus) -> None:
        self.status = status

    def collect_source(self, request: SourceRequest) -> SourceCollection:
        return SourceCollection(
            status=self.status,
            locator=f"fixture://terminal-state/{request.identifier_value}",
            retrieved_at=datetime(2025, 6, 30, 12, tzinfo=UTC),
            classification=DataClassification.SYNTHETIC,
            error_code=f"synthetic_{self.status.value}",
            error_message="Synthetic terminal state for quality-contract validation.",
        )


@pytest.mark.parametrize(
    ("status", "expected_rule", "expected_disposition", "expected_text"),
    (
        (CollectionStatus.NO_RECORD, "bounded_no_record", "warn", "no public record"),
        (
            CollectionStatus.SOURCE_UNAVAILABLE,
            "expected_missingness",
            "warn",
            "unavailable",
        ),
        (
            CollectionStatus.FAILED,
            "source_collection_failure",
            "hold",
            "terminal contract failure",
        ),
    ),
)
def test_source_terminal_states_have_distinct_visible_quality_outcomes(
    runtime: Runtime,
    status: CollectionStatus,
    expected_rule: str,
    expected_disposition: str,
    expected_text: str,
) -> None:
    payload = {
        "reporting_period": {"label": "SOURCE-UNAVAILABLE-Q2", "end_date": "2025-06-30"},
        "companies": [
            {
                "name": "Unavailable Synthetic Ltd",
                "external_id": "SYN-UNAVAILABLE",
                "metrics": {"jobs_created": 1},
            }
        ],
    }
    imported = runtime.importer.import_bytes(
        json.dumps(payload).encode(),
        filename="source-unavailable.json",
        classification=DataClassification.SYNTHETIC,
    )
    with runtime.session_factory.begin() as session:
        company_id = session.scalar(
            select(ObservationModel.company_id).where(
                ObservationModel.raw_submission_id == imported.raw_submission_id
            )
        )
        assert company_id is not None
        session.add(
            CompanyIdentifierModel(
                company_id=company_id,
                scheme=IdentifierScheme.COMPANIES_HOUSE_NUMBER.value,
                value="00000077",
                normalized_value="00000077",
                source_key="companies_house",
                reviewed=True,
            )
        )
    registry = SourceRegistry(
        runtime.session_factory,
        runtime.settings.raw_data_dir.parent / f"terminal-source-{status.value}",
        (_TerminalCompaniesHouseConnector(status),),
    )
    runtime.workflow._source_registry = registry
    pipeline = runtime.workflow.run(imported.dataset_id)

    with runtime.session_factory() as session:
        snapshot = session.scalar(select(SourceSnapshotModel))
        assert snapshot is not None
        finding = session.scalar(
            select(QualityViolationModel).where(
                QualityViolationModel.run_id == pipeline.run_id,
                QualityViolationModel.source_snapshot_id == snapshot.id,
            )
        )
        quality_section = session.scalar(
            select(ReportSectionModel).where(
                ReportSectionModel.report_id == pipeline.report_id,
                ReportSectionModel.section_key == "quality-contract",
            )
        )
    assert snapshot.status == status.value
    assert finding is not None
    assert finding.disposition == expected_disposition
    assert finding.rule_key == expected_rule
    assert quality_section is not None
    assert expected_text in quality_section.body_markdown.lower()
    assert "| pass | 0 explicit violations |" not in quality_section.body_markdown
