from __future__ import annotations

from pathlib import Path

from sqlalchemy import func, select

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification, ReportStatus, RunStatus, VerificationStatus
from portfolio_agent.models import (
    AgentRunModel,
    ClaimModel,
    EvidenceItemModel,
    ExtractionModel,
    ReportModel,
)


def test_workflow_reaches_review_with_independent_verification(
    runtime: Runtime, synthetic_portfolio_path: Path
) -> None:
    imported = runtime.importer.import_file(
        synthetic_portfolio_path, classification=DataClassification.SYNTHETIC
    )
    result = runtime.workflow.run(imported.dataset_id)

    assert result.report_status is ReportStatus.PENDING_REVIEW
    assert result.claim_counts[VerificationStatus.SUPPORTED.value] > 0
    assert result.claim_counts[VerificationStatus.CONTRADICTED.value] > 0

    with runtime.session_factory() as session:
        agents = list(
            session.scalars(
                select(AgentRunModel)
                .where(AgentRunModel.run_id == result.run_id)
                .order_by(AgentRunModel.started_at)
            ).all()
        )
        report = session.get(ReportModel, result.report_id)
        untrusted = session.scalar(
            select(func.count(EvidenceItemModel.id)).where(EvidenceItemModel.is_untrusted.is_(True))
        )
        untrusted_extractions = session.scalar(
            select(func.count(ExtractionModel.id))
            .join(EvidenceItemModel)
            .where(
                ExtractionModel.run_id == result.run_id,
                EvidenceItemModel.is_untrusted.is_(True),
            )
        )
        claims_without_verification = session.scalar(
            select(func.count(ClaimModel.id)).where(
                ClaimModel.run_id == result.run_id,
                ~ClaimModel.verifications.any(),
            )
        )

    assert len(agents) == 8
    assert all(agent.status == RunStatus.SUCCEEDED.value for agent in agents)
    assert agents[-2].role == "report_composer"
    assert agents[-3].role == "independent_verifier"
    assert report is not None and report.status == ReportStatus.PENDING_REVIEW.value
    assert untrusted and untrusted > 0
    assert untrusted_extractions == 0
    assert claims_without_verification == 0
