from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .enums import (
    DataClassification,
    EvaluationCondition,
    MetricDataType,
    MissingState,
    ReportStatus,
    ResolutionStatus,
    ReviewDecisionType,
    Sourceability,
    VerificationStatus,
    WorkflowStage,
)

JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Company(Contract):
    id: str
    canonical_name: str
    external_id: str | None = None
    resolution_status: ResolutionStatus = ResolutionStatus.RESOLVED


class ReportingPeriod(Contract):
    id: str
    label: str
    start_date: date | None = None
    end_date: date | None = None


class MetricDefinition(Contract):
    key: str
    category: str
    label: str
    data_type: MetricDataType
    sourceability: Sourceability
    unit: str | None = None
    aliases: tuple[str, ...] = ()
    description: str


class NormalizedValue(Contract):
    value: str | int | bool | None
    missing_state: MissingState
    unit: str | None = None
    currency: str | None = None
    issue_code: str | None = None
    issue_message: str | None = None


class RawSubmission(Contract):
    id: str
    dataset_id: str
    reporting_period_id: str
    sha256: str
    source_format: str
    original_filename: str
    snapshot_path: str
    classification: DataClassification


class Observation(Contract):
    id: str
    company_id: str
    metric_key: str
    reporting_period_id: str
    raw_submission_id: str
    original_value: JsonValue
    normalized: NormalizedValue
    source_cell: str | None = None


class EvidenceItem(Contract):
    id: str
    company_id: str | None = None
    metric_key: str | None = None
    source_type: str
    connector: str
    locator: str
    publisher: str | None = None
    retrieved_at: datetime
    published_at: datetime | None = None
    content: dict[str, Any]
    checksum: str
    connector_version: str
    classification: DataClassification
    is_untrusted: bool = False


class Claim(Contract):
    id: str
    company_id: str
    metric_key: str
    reporting_period_id: str
    text: str
    normalized_value: str | int | bool | None
    verification_status: VerificationStatus
    evidence_ids: tuple[str, ...] = ()


class Verification(Contract):
    id: str
    claim_id: str
    status: VerificationStatus
    rationale: str
    verifier_role: str = "independent_verifier"
    verified_at: datetime


class AgentRun(Contract):
    id: str
    run_id: str
    stage: WorkflowStage
    role: str
    status: str
    input_hash: str
    output_hash: str | None = None
    model: str | None = None
    attempts: int = 1
    prompt_version: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: str | None = None
    duration_ms: int | None = None
    error: str | None = None


class ReportSection(Contract):
    key: str
    heading: str
    order: int
    body_markdown: str
    claim_ids: tuple[str, ...] = ()
    version: int = 1


class Report(Contract):
    id: str
    run_id: str
    dataset_id: str
    reporting_period_id: str
    title: str
    status: ReportStatus
    version: int
    sections: tuple[ReportSection, ...]


class ReviewDecision(Contract):
    id: str
    report_id: str
    decision: ReviewDecisionType
    actor: str
    reason: str
    section_key: str | None = None
    created_at: datetime


class ImportIssue(Contract):
    severity: str
    code: str
    message: str
    location: str | None = None


class ImportResult(Contract):
    dataset_id: str
    raw_submission_id: str
    reporting_period_id: str
    company_count: int
    observation_count: int
    issues: tuple[ImportIssue, ...] = ()
    reused_existing: bool = False


class PipelineResult(Contract):
    run_id: str
    dataset_id: str
    report_id: str
    report_status: ReportStatus
    final_stage: WorkflowStage
    claim_counts: dict[str, int]


class StrictExtraction(Contract):
    company_name: str
    metric_key: str
    value: str | int | bool | None
    unit: str | None = None
    currency: str | None = None
    period_label: str | None = None
    evidence_locator: str
    confidence: float = Field(ge=0, le=1)


class EvaluationCaseResult(Contract):
    case_id: str
    condition: EvaluationCondition
    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int
    supported_claims: int
    unsupported_claims: int
    provenance_complete_claims: int
    total_claims: int
    schema_valid: bool
    normalization_correct: bool
    verification_correct: bool
    duration_ms: int


class EvaluationSummary(Contract):
    condition: EvaluationCondition
    case_count: int
    precision: float | None
    recall: float | None
    f1: float | None
    claim_support_rate: float | None
    hallucination_rate: float | None
    provenance_completeness: float | None
    schema_validity_rate: float | None
    normalization_accuracy: float | None
    verification_accuracy: float | None
    repeat_consistency: float | None
    mean_duration_ms: float | None
    llm_cost_usd: str | None = None
    notes: tuple[str, ...] = ()
