from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base
from .enums import (
    DataClassification,
    ReportStatus,
    ResolutionStatus,
    RunStatus,
    WorkflowStage,
)
from .ids import new_id


def utc_now() -> datetime:
    return datetime.now(UTC)


claim_evidence = Table(
    "claim_evidence",
    Base.metadata,
    Column("claim_id", ForeignKey("claims.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "evidence_item_id",
        ForeignKey("evidence_items.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

run_evidence = Table(
    "run_evidence",
    Base.metadata,
    Column("run_id", ForeignKey("workflow_runs.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "evidence_item_id",
        ForeignKey("evidence_items.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class CompanyModel(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("co"))
    canonical_name: Mapped[str] = mapped_column(String(255))
    normalized_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    resolution_status: Mapped[str] = mapped_column(
        String(32), default=ResolutionStatus.RESOLVED.value
    )
    classification: Mapped[str] = mapped_column(
        String(32), default=DataClassification.RESTRICTED.value
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ReportingPeriodModel(Base):
    __tablename__ = "reporting_periods"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("rp"))
    label: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class MetricDefinitionModel(Base):
    __tablename__ = "metric_definitions"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("md"))
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(255))
    label: Mapped[str] = mapped_column(String(255))
    data_type: Mapped[str] = mapped_column(String(32))
    sourceability: Mapped[str] = mapped_column(String(32))
    unit: Mapped[str | None] = mapped_column(String(64))
    aliases_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    description: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class RawSubmissionModel(Base):
    __tablename__ = "raw_submissions"
    __table_args__ = (
        UniqueConstraint("sha256", "reporting_period_id", name="uq_submission_hash_period"),
    )

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("raw"))
    dataset_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    reporting_period_id: Mapped[str] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="RESTRICT"), index=True
    )
    source_format: Mapped[str] = mapped_column(String(16))
    original_filename: Mapped[str] = mapped_column(String(255))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    snapshot_path: Mapped[str] = mapped_column(Text)
    classification: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    reporting_period: Mapped[ReportingPeriodModel] = relationship()


class ObservationModel(Base):
    __tablename__ = "observations"
    __table_args__ = (
        UniqueConstraint(
            "raw_submission_id",
            "company_id",
            "metric_definition_id",
            name="uq_observation_submission_company_metric",
        ),
    )

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("obs"))
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), index=True
    )
    metric_definition_id: Mapped[str] = mapped_column(
        ForeignKey("metric_definitions.id", ondelete="RESTRICT"), index=True
    )
    reporting_period_id: Mapped[str] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="RESTRICT"), index=True
    )
    raw_submission_id: Mapped[str] = mapped_column(
        ForeignKey("raw_submissions.id", ondelete="RESTRICT"), index=True
    )
    original_value_json: Mapped[Any] = mapped_column(JSON)
    normalized_value_json: Mapped[Any] = mapped_column(JSON)
    missing_state: Mapped[str] = mapped_column(String(32), index=True)
    unit: Mapped[str | None] = mapped_column(String(64))
    currency: Mapped[str | None] = mapped_column(String(3))
    source_cell: Mapped[str | None] = mapped_column(String(32))
    normalization_issue_code: Mapped[str | None] = mapped_column(String(100))
    normalization_issue_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    company: Mapped[CompanyModel] = relationship()
    metric_definition: Mapped[MetricDefinitionModel] = relationship()
    raw_submission: Mapped[RawSubmissionModel] = relationship()


class EvidenceItemModel(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("ev"))
    company_id: Mapped[str | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), index=True
    )
    metric_definition_id: Mapped[str | None] = mapped_column(
        ForeignKey("metric_definitions.id", ondelete="SET NULL"), index=True
    )
    raw_submission_id: Mapped[str | None] = mapped_column(
        ForeignKey("raw_submissions.id", ondelete="RESTRICT"), index=True
    )
    source_type: Mapped[str] = mapped_column(String(64))
    connector: Mapped[str] = mapped_column(String(100))
    locator: Mapped[str] = mapped_column(Text)
    publisher: Mapped[str | None] = mapped_column(String(255))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    content_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    checksum: Mapped[str] = mapped_column(String(64), index=True)
    connector_version: Mapped[str] = mapped_column(String(50))
    classification: Mapped[str] = mapped_column(String(32))
    is_untrusted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    company: Mapped[CompanyModel | None] = relationship()
    metric_definition: Mapped[MetricDefinitionModel | None] = relationship()


class WorkflowRunModel(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("run"))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("raw_submissions.dataset_id", ondelete="RESTRICT"), index=True
    )
    reporting_period_id: Mapped[str] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="RESTRICT"), index=True
    )
    stage: Mapped[str] = mapped_column(String(32), default=WorkflowStage.PLAN.value)
    status: Mapped[str] = mapped_column(String(32), default=RunStatus.PENDING.value)
    configuration_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)


class AgentRunModel(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("ar"))
    run_id: Mapped[str] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"), index=True
    )
    stage: Mapped[str] = mapped_column(String(32), index=True)
    role: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(32))
    input_hash: Mapped[str] = mapped_column(String(64))
    output_hash: Mapped[str | None] = mapped_column(String(64))
    model: Mapped[str | None] = mapped_column(String(100))
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    prompt_version: Mapped[str | None] = mapped_column(String(50))
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ExtractionModel(Base):
    __tablename__ = "extractions"
    __table_args__ = (
        UniqueConstraint("run_id", "evidence_item_id", name="uq_extraction_run_evidence"),
    )

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("ext"))
    run_id: Mapped[str] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"), index=True
    )
    evidence_item_id: Mapped[str] = mapped_column(
        ForeignKey("evidence_items.id", ondelete="CASCADE"), index=True
    )
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), index=True
    )
    metric_definition_id: Mapped[str] = mapped_column(
        ForeignKey("metric_definitions.id", ondelete="RESTRICT"), index=True
    )
    extracted_value_json: Mapped[Any] = mapped_column(JSON)
    normalized_value_json: Mapped[Any] = mapped_column(JSON)
    missing_state: Mapped[str | None] = mapped_column(String(32), index=True)
    unit: Mapped[str | None] = mapped_column(String(64))
    currency: Mapped[str | None] = mapped_column(String(3))
    period_label: Mapped[str | None] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    schema_version: Mapped[str] = mapped_column(String(50), default="strict-extraction-v1")
    normalization_issue_code: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    evidence_item: Mapped[EvidenceItemModel] = relationship()
    metric_definition: Mapped[MetricDefinitionModel] = relationship()


class ReportModel(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("rep"))
    run_id: Mapped[str] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="RESTRICT"), unique=True, index=True
    )
    dataset_id: Mapped[str] = mapped_column(String(40), index=True)
    reporting_period_id: Mapped[str] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="RESTRICT"), index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default=ReportStatus.DRAFT.value)
    content_hash: Mapped[str | None] = mapped_column(String(64))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    sections: Mapped[list[ReportSectionModel]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


class ReportSectionModel(Base):
    __tablename__ = "report_sections"
    __table_args__ = (
        UniqueConstraint("report_id", "section_key", "version", name="uq_report_section_version"),
    )

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("sec"))
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[str | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), index=True
    )
    section_key: Mapped[str] = mapped_column(String(100))
    heading: Mapped[str] = mapped_column(String(255))
    order_index: Mapped[int] = mapped_column(Integer)
    body_markdown: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    report: Mapped[ReportModel] = relationship(back_populates="sections")
    claims: Mapped[list[ClaimModel]] = relationship(back_populates="report_section")


class ClaimModel(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("cl"))
    run_id: Mapped[str] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"), index=True
    )
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), index=True
    )
    metric_definition_id: Mapped[str] = mapped_column(
        ForeignKey("metric_definitions.id", ondelete="RESTRICT"), index=True
    )
    reporting_period_id: Mapped[str] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="RESTRICT"), index=True
    )
    report_section_id: Mapped[str | None] = mapped_column(
        ForeignKey("report_sections.id", ondelete="SET NULL"), index=True
    )
    text: Mapped[str] = mapped_column(Text)
    normalized_value_json: Mapped[Any] = mapped_column(JSON)
    verification_status: Mapped[str] = mapped_column(String(40), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    company: Mapped[CompanyModel] = relationship()
    metric_definition: Mapped[MetricDefinitionModel] = relationship()
    report_section: Mapped[ReportSectionModel | None] = relationship(back_populates="claims")
    evidence_items: Mapped[list[EvidenceItemModel]] = relationship(secondary=claim_evidence)
    verifications: Mapped[list[VerificationModel]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )


class VerificationModel(Base):
    __tablename__ = "verifications"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("ver"))
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    rationale: Mapped[str] = mapped_column(Text)
    verifier_role: Mapped[str] = mapped_column(String(100), default="independent_verifier")
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    claim: Mapped[ClaimModel] = relationship(back_populates="verifications")


class ReviewDecisionModel(Base):
    __tablename__ = "review_decisions"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=lambda: new_id("rev"))
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    section_id: Mapped[str | None] = mapped_column(
        ForeignKey("report_sections.id", ondelete="SET NULL"), index=True
    )
    actor: Mapped[str] = mapped_column(String(255))
    decision: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str] = mapped_column(Text)
    report_version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
