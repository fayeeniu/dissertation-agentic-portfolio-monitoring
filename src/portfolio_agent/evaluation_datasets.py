from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from .enums import Sourceability
from .ids import sha256_bytes

EVALUATION_NAMESPACE_PREFIX = "benchmark:"


class EvaluationDatasetError(ValueError):
    pass


class SealedDatasetError(EvaluationDatasetError):
    pass


class EvidenceCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    source_type: str
    value: str | int | bool | None
    currency: str | None
    period_label: str | None
    publisher: str | None
    locator: str
    checksum: str
    is_untrusted: bool


class EvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    category: str
    metric_key: str
    candidate_value: str | int | bool | None
    candidate_currency: str | None
    sourceability: Sourceability
    precondition: Literal["valid", "ambiguous_identity", "source_inaccessible"]
    evidence: tuple[EvidenceCase, ...]
    expected_emit: bool
    expected_status: str
    entity_group: str | None = None
    period_group: str = "SYN-PERIOD"
    split: Literal["development", "validation", "test"] = "test"

    @model_validator(mode="after")
    def default_group(self) -> EvaluationCase:
        if self.entity_group is None:
            self.entity_group = self.case_id
        return self


class EvaluationDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["evaluation-cases-v1"]
    classification: Literal["synthetic"]
    cases: tuple[EvaluationCase, ...]


class DatasetEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tier: Literal["D0", "D1", "D2"]
    namespace: str
    status: Literal["executable", "protocol_only", "sealed"]
    classification: str
    path: str | None
    sha256: str | None
    source_version: str
    partition_policy: str
    permitted_use: str


class DatasetManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["evaluation-dataset-manifest-v1"]
    datasets: tuple[DatasetEntry, ...]


@dataclass(frozen=True, slots=True)
class LoadedEvaluationDataset:
    entry: DatasetEntry
    document: EvaluationDocument
    manifest_path: Path
    manifest_sha256: str
    dataset_sha256: str


def ensure_operational_id(value: str) -> None:
    if value.startswith(EVALUATION_NAMESPACE_PREFIX):
        raise EvaluationDatasetError(
            "Benchmark identifiers cannot be attached to an operational portfolio object."
        )


def validate_evaluation_document(document: EvaluationDocument) -> None:
    entity_splits: dict[str, set[str]] = {}
    period_splits: dict[str, set[str]] = {}
    case_ids: set[str] = set()
    for case in document.cases:
        if case.case_id in case_ids:
            raise EvaluationDatasetError(f"Duplicate evaluation case ID: {case.case_id}")
        case_ids.add(case.case_id)
        assert case.entity_group is not None
        entity_splits.setdefault(case.entity_group, set()).add(case.split)
        period_splits.setdefault(case.period_group, set()).add(case.split)
    leaked = sorted(group for group, splits in entity_splits.items() if len(splits) > 1)
    if leaked:
        raise EvaluationDatasetError(
            "Entity groups cross evaluation partitions: " + ", ".join(leaked)
        )
    leaked_periods = sorted(group for group, splits in period_splits.items() if len(splits) > 1)
    if leaked_periods:
        raise EvaluationDatasetError(
            "Period groups cross evaluation partitions: " + ", ".join(leaked_periods)
        )


def load_evaluation_dataset(manifest_path: Path, *, tier: str = "D0") -> LoadedEvaluationDataset:
    resolved_manifest = manifest_path.resolve()
    manifest_bytes = resolved_manifest.read_bytes()
    manifest = DatasetManifest.model_validate_json(manifest_bytes)
    entries = [entry for entry in manifest.datasets if entry.tier == tier]
    if len(entries) != 1:
        raise EvaluationDatasetError(f"Manifest must define exactly one {tier} dataset.")
    entry = entries[0]
    if entry.status == "sealed":
        raise SealedDatasetError(
            f"{tier} is sealed. No application code path can unseal it; a separately approved "
            "manifest transition is required."
        )
    if entry.status != "executable" or not entry.path or not entry.sha256:
        raise EvaluationDatasetError(f"{tier} is protocol-only and has no executable artifact.")
    if not entry.namespace.startswith(EVALUATION_NAMESPACE_PREFIX):
        raise EvaluationDatasetError("Evaluation namespaces must use the benchmark prefix.")
    dataset_path = (resolved_manifest.parent / entry.path).resolve()
    if not dataset_path.is_relative_to(resolved_manifest.parent.resolve()):
        raise EvaluationDatasetError("Evaluation dataset path escapes the manifest directory.")
    payload = dataset_path.read_bytes()
    dataset_sha256 = sha256_bytes(payload)
    if dataset_sha256 != entry.sha256:
        raise EvaluationDatasetError("Evaluation dataset checksum does not match its manifest.")
    document = EvaluationDocument.model_validate_json(payload)
    if entry.source_version != document.schema_version:
        raise EvaluationDatasetError(
            "Evaluation manifest source version does not match its dataset schema version."
        )
    if entry.classification != document.classification:
        raise EvaluationDatasetError(
            "Evaluation manifest classification does not match its dataset classification."
        )
    validate_evaluation_document(document)
    namespace = entry.namespace.rstrip(":")
    namespaced_cases: list[EvaluationCase] = []
    for case in document.cases:
        namespaced_evidence = tuple(
            item.model_copy(update={"id": f"{namespace}:evidence:{item.id}"})
            for item in case.evidence
        )
        namespaced_cases.append(
            case.model_copy(
                update={
                    "case_id": f"{namespace}:case:{case.case_id}",
                    "entity_group": f"{namespace}:entity:{case.entity_group}",
                    "evidence": namespaced_evidence,
                }
            )
        )
    namespaced_document = document.model_copy(update={"cases": tuple(namespaced_cases)})
    return LoadedEvaluationDataset(
        entry=entry,
        document=namespaced_document,
        manifest_path=resolved_manifest,
        manifest_sha256=sha256_bytes(manifest_bytes),
        dataset_sha256=dataset_sha256,
    )


def manifest_for_legacy_cases(cases_path: Path) -> Path:
    """Resolve a deprecated cases path through its required sibling admission manifest."""
    resolved_cases = cases_path.resolve()
    manifest_path = resolved_cases.parent / "evaluation_manifest.json"
    if not manifest_path.is_file():
        raise EvaluationDatasetError(
            "Deprecated --cases input requires a sibling evaluation_manifest.json."
        )
    loaded = load_evaluation_dataset(manifest_path, tier="D0")
    assert loaded.entry.path is not None
    admitted_cases = (manifest_path.parent / loaded.entry.path).resolve()
    if admitted_cases != resolved_cases:
        raise EvaluationDatasetError(
            "Deprecated --cases input is not the D0 dataset admitted by its sibling manifest."
        )
    return manifest_path
