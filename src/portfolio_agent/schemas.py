from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .cbit_contract import PeriodSemantics
from .enums import (
    DataClassification,
    EvaluationCondition,
    IdentifierScheme,
    IdentityCandidateStatus,
    IdentityDecisionType,
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
    period_semantics: PeriodSemantics = PeriodSemantics.NONE


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
    reporting_cutoff: date | None = None
    profile_key: str | None = None
    profile_version: str | None = None
    catalogue_version: str | None = None
    catalogue_sha256: str | None = None


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
    occurrences: int = 1


class ImportResult(Contract):
    dataset_id: str
    raw_submission_id: str
    reporting_period_id: str
    company_count: int
    observation_count: int
    issues: tuple[ImportIssue, ...] = ()
    reused_existing: bool = False
    profile_key: str | None = None
    profile_version: str | None = None
    reporting_cutoff: date | None = None
    narrative_count: int = 0
    held_field_count: int = 0
    formula_cell_count: int = 0
    identity_hold_count: int = 0
    programme_start_count: int = 0


class CompanyIdentifier(Contract):
    id: str
    company_id: str
    scheme: IdentifierScheme
    value: str
    normalized_value: str
    source_key: str | None = None
    reviewed: bool


class IdentityCandidate(Contract):
    id: str
    raw_submission_id: str
    imported_company_id: str
    candidate_company_id: str | None = None
    submitted_name: str
    normalized_name: str
    identifier_scheme: IdentifierScheme | None = None
    submitted_identifier: str | None = None
    status: IdentityCandidateStatus
    reason_code: str


class IdentityDecision(Contract):
    id: str
    candidate_id: str
    company_id: str | None = None
    decision: IdentityDecisionType
    actor: str
    reason: str
    created_at: datetime


class PipelineResult(Contract):
    run_id: str
    dataset_id: str
    report_id: str
    report_status: ReportStatus
    final_stage: WorkflowStage
    claim_counts: dict[str, int]


class ContextStatistic(Contract):
    metric_key: str
    metric_label: str
    status: str
    sample_size: int
    minimum_sample_size: int
    unit: str | None = None
    currency: str | None = None
    minimum: str | None = None
    first_quartile: str | None = None
    median: str | None = None
    third_quartile: str | None = None
    maximum: str | None = None


class ChangeComparison(Contract):
    company_id: str
    metric_key: str
    current_period: str
    prior_period: str | None = None
    status: str
    current_value: str
    prior_value: str | None = None
    absolute_change: str | None = None
    percentage_change: str | None = None


class StrictExtraction(Contract):
    company_name: str
    metric_key: str
    value: str | int | bool | None
    unit: str | None = None
    currency: str | None = None
    period_label: str | None = None
    evidence_locator: str
    evidence_span: str | None = Field(default=None, max_length=500)
    abstain_reason: str | None = Field(default=None, max_length=255)
    confidence: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def require_grounded_value_or_abstention(self) -> StrictExtraction:
        if self.value is None:
            if not self.abstain_reason or self.evidence_span is not None:
                raise ValueError(
                    "Null extraction requires an abstention reason and no evidence span."
                )
        elif not self.evidence_span or self.abstain_reason is not None:
            raise ValueError(
                "Non-null extraction requires an exact evidence span and no abstention reason."
            )
        return self


class DocumentExtraction(Contract):
    field_key: str
    value: str | int | bool | None
    raw_value: str | int | bool | None = None
    unit: str | None = None
    currency: str | None = None
    period_label: str | None = None
    evidence_locator: str | None = None
    extraction_method: str
    abstain_reason: str | None = None
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
    identity_correct: bool | None = None
    extraction_correct: bool | None = None
    temporal_correct: bool | None = None
    quality_correct: bool | None = None
    contradiction_correct: bool | None = None
    abstention_correct: bool
    event_correct: bool | None = None
    report_correct: bool | None = None
    reviewer_utility: float | None = None
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
    identity_accuracy: float | None
    extraction_accuracy: float | None
    temporal_accuracy: float | None
    quality_accuracy: float | None
    contradiction_accuracy: float | None
    abstention_accuracy: float | None
    event_accuracy: float | None
    report_accuracy: float | None
    reviewer_utility: float | None
    repeat_consistency: float | None
    mean_duration_ms: float | None
    llm_cost_usd: str | None = None
    notes: tuple[str, ...] = ()
