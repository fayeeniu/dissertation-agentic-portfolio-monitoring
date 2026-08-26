from enum import StrEnum


class DataClassification(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    SYNTHETIC = "synthetic"


class Sourceability(StrEnum):
    PUBLICLY_SOURCEABLE = "publicly_sourceable"
    INTERNAL_ONLY = "internal_only"
    MIXED = "mixed"
    DERIVED = "derived"


class MetricDataType(StrEnum):
    INTEGER = "integer"
    DECIMAL = "decimal"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    BOOLEAN = "boolean"
    TEXT = "text"
    DATE = "date"
    DURATION_HOURS = "duration_hours"


class MissingState(StrEnum):
    OBSERVED = "observed"
    BLANK = "blank"
    ZERO = "zero"
    NONE_STATED = "none_stated"
    NOT_APPLICABLE = "not_applicable"
    NOT_REPORTED = "not_reported"
    NOT_FOUND_PUBLICLY = "not_found_publicly"
    INVALID = "invalid"


class ResolutionStatus(StrEnum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


class WorkflowStage(StrEnum):
    PLAN = "plan"
    RESOLVE = "resolve"
    COLLECT = "collect"
    EXTRACT = "extract"
    NORMALIZE = "normalize"
    VERIFY = "verify"
    COMPOSE = "compose"
    HUMAN_REVIEW = "human_review"
    APPROVE_EXPORT = "approve_export"
    COMPLETE = "complete"
    FAILED = "failed"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class VerificationStatus(StrEnum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    STALE = "stale"
    REJECTED_UNTRUSTED = "rejected_untrusted"


class ReportStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPORTED = "exported"


class ReviewDecisionType(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_EDIT = "request_edit"


class EvaluationCondition(StrEnum):
    MANUAL = "manual"
    DETERMINISTIC_SINGLE_AGENT = "deterministic_single_agent"
    MULTI_AGENT_VERIFICATION = "multi_agent_verification"
    MULTI_AGENT_HITL = "multi_agent_hitl"
