from __future__ import annotations

import csv
import html
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from .ids import sha256_bytes

WIDTH = 1200
HEIGHT = 720
INK = "#17211f"
MUTED = "#56615e"
PAPER = "#fffdf7"
LINE = "#c7cec9"
TEAL = "#006c62"
BLUE = "#2f6690"
AMBER = "#d18b16"
RED = "#a23b3b"
PURPLE = "#665191"
GREEN = "#2c7a55"
PALETTE = (TEAL, BLUE, AMBER, RED, PURPLE, GREEN, "#7b6d45", "#3f7f8f")


class _WorkflowVisualData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observations: int
    verification: dict[str, int]
    evidence: dict[str, int]
    missingness: dict[str, int]
    quality: dict[str, int]
    extraction_attempts: dict[str, int]


class _IdentityVisualData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_columns: int
    exact_registry_identifiers: int
    review_holds: int


class _ContextVisualData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    values: tuple[Decimal, ...]
    unit: str
    minimum_sample_size: int


class _EvaluationConditionData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    precision: float
    recall: float
    verification_accuracy: float


class _EvaluationVisualData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_count: int
    deterministic_single_agent: _EvaluationConditionData
    multi_agent_verification: _EvaluationConditionData


class _VisualPackData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["dissertation-visual-pack-v1"]
    classification: str
    cutoff: str
    workflow_fixture: str
    workflow: _WorkflowVisualData
    identity_structural_profile: _IdentityVisualData
    illustrative_context: _ContextVisualData
    evaluation: _EvaluationVisualData


@dataclass(frozen=True, slots=True)
class Figure:
    key: str
    title: str
    kind: str
    source: str
    sample: str
    cutoff: str
    textual_alternative: str
    svg: str


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _text(
    x: float,
    y: float,
    value: object,
    *,
    size: int = 18,
    weight: int = 400,
    fill: str = INK,
    anchor: str = "start",
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}">{_esc(value)}</text>'
    )


def _rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str = PAPER,
    stroke: str = LINE,
    radius: int = 8,
    opacity: float = 1,
) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
        f'rx="{radius}" fill="{fill}" stroke="{stroke}" opacity="{opacity}"/>'
    )


def _line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str = LINE,
    width: int = 2,
    dashed: bool = False,
    marker: bool = False,
) -> str:
    dash = ' stroke-dasharray="7 6"' if dashed else ""
    end = ' marker-end="url(#arrow)"' if marker else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{stroke}" stroke-width="{width}"{dash}{end}/>'
    )


def _document(
    *,
    title: str,
    subtitle: str,
    description: str,
    body: str,
    source: str,
    sample: str,
    cutoff: str,
) -> str:
    title_id = "figure-title"
    desc_id = "figure-description"
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-labelledby="{title_id} {desc_id}">'
        f'<title id="{title_id}">{_esc(title)}</title>'
        f'<desc id="{desc_id}">{_esc(description)}</desc>'
        '<defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" '
        'orient="auto"><path d="M0,0 L10,4 L0,8 Z" fill="#56615e"/></marker>'
        '<pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" '
        'patternTransform="rotate(45)"><rect width="8" height="8" fill="#fff7e5"/>'
        '<line x1="0" y1="0" x2="0" y2="8" stroke="#d18b16" stroke-width="3"/>'
        "</pattern></defs>"
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>'
        f"{_text(60, 58, title, size=30, weight=750)}"
        f"{_text(60, 88, subtitle, size=16, fill=MUTED)}"
        f"{body}"
        f"{_line(60, 665, 1140, 665, stroke=LINE, width=1)}"
        f"{_text(60, 692, f'Source: {source}', size=13, fill=MUTED)}"
        f"{_text(600, 692, f'Sample: {sample}', size=13, fill=MUTED, anchor='middle')}"
        f"{_text(1140, 692, f'Cutoff: {cutoff}', size=13, fill=MUTED, anchor='end')}"
        "</svg>\n"
    )


def _flow_figure(
    *,
    key: str,
    title: str,
    subtitle: str,
    nodes: tuple[tuple[str, str], ...],
    source: str,
    sample: str,
    cutoff: str,
    description: str,
) -> Figure:
    columns = 4
    box_width = 235
    box_height = 92
    gap_x = 45
    start_x = 60
    start_y = 150
    gap_y = 95
    pieces: list[str] = []
    positions: list[tuple[float, float]] = []
    for index, (heading, detail) in enumerate(nodes):
        row, column = divmod(index, columns)
        x = start_x + column * (box_width + gap_x)
        y = start_y + row * (box_height + gap_y)
        positions.append((x, y))
        pieces.extend(
            [
                _rect(x, y, box_width, box_height, fill="#f5fbf9", stroke=TEAL),
                _text(x + 16, y + 32, heading, size=17, weight=700),
                _text(x + 16, y + 61, detail, size=13, fill=MUTED),
            ]
        )
    for index in range(len(positions) - 1):
        x1, y1 = positions[index]
        x2, y2 = positions[index + 1]
        if y1 == y2:
            pieces.append(
                _line(
                    x1 + box_width,
                    y1 + box_height / 2,
                    x2 - 8,
                    y2 + box_height / 2,
                    marker=True,
                    stroke=MUTED,
                )
            )
        else:
            pieces.append(
                _line(
                    x1 + box_width / 2,
                    y1 + box_height,
                    x1 + box_width / 2,
                    y2 - 28,
                    marker=True,
                    stroke=MUTED,
                )
            )
    svg = _document(
        title=title,
        subtitle=subtitle,
        description=description,
        body="".join(pieces),
        source=source,
        sample=sample,
        cutoff=cutoff,
    )
    return Figure(key, title, "flow diagram", source, sample, cutoff, description, svg)


def _bar_figure(
    *,
    key: str,
    title: str,
    subtitle: str,
    values: tuple[tuple[str, float], ...],
    source: str,
    sample: str,
    cutoff: str,
    description: str,
    maximum: float | None = None,
) -> Figure:
    chart_x, chart_y, chart_width = 330.0, 145.0, 780.0
    row_height = 64.0
    max_value = maximum or max((value for _, value in values), default=1)
    pieces: list[str] = []
    for index, (label, value) in enumerate(values):
        y = chart_y + index * row_height
        bar_width = 0 if max_value == 0 else chart_width * value / max_value
        pieces.extend(
            [
                _text(chart_x - 20, y + 28, label, size=16, anchor="end"),
                _rect(chart_x, y, chart_width, 36, fill="#edf1ef", stroke="none", radius=3),
                _rect(
                    chart_x,
                    y,
                    bar_width,
                    36,
                    fill=PALETTE[index % len(PALETTE)],
                    stroke="none",
                    radius=3,
                ),
                _text(chart_x + bar_width + 10, y + 25, f"{value:g}", size=15, weight=700),
            ]
        )
    svg = _document(
        title=title,
        subtitle=subtitle,
        description=description,
        body="".join(pieces),
        source=source,
        sample=sample,
        cutoff=cutoff,
    )
    return Figure(key, title, "horizontal bar chart", source, sample, cutoff, description, svg)


def _stacked_figure(data: _VisualPackData) -> Figure:
    values = tuple(data.workflow.verification.items())
    total = sum(value for _, value in values)
    x, y, width, height = 90.0, 230.0, 1020.0, 90.0
    cursor = x
    pieces = [_text(90, 190, f"{total} candidate claims", size=19, weight=700)]
    descriptions: list[str] = []
    for index, (label, value) in enumerate(values):
        segment = width * value / total if total else 0
        colour = {"supported": GREEN, "contradicted": RED, "stale": AMBER}.get(
            label, PALETTE[index]
        )
        pieces.append(_rect(cursor, y, segment, height, fill=colour, stroke=PAPER, radius=0))
        if segment > 90:
            pieces.append(
                _text(
                    cursor + segment / 2,
                    y + 53,
                    value,
                    size=22,
                    weight=750,
                    fill="#ffffff",
                    anchor="middle",
                )
            )
        descriptions.append(f"{label}: {value}")
        cursor += segment
    for index, (label, value) in enumerate(values):
        colour = {"supported": GREEN, "contradicted": RED, "stale": AMBER}.get(
            label, PALETTE[index]
        )
        legend_x = 110 + index * 330
        pieces.extend(
            [
                _rect(legend_x, 385, 22, 22, fill=colour, stroke="none", radius=2),
                _text(legend_x + 34, 402, f"{label.replace('_', ' ')} ({value})", size=16),
            ]
        )
    description = "Verification outcomes in the synthetic workflow: " + ", ".join(descriptions)
    return Figure(
        "verification-outcomes",
        "Verification outcomes",
        "stacked bar chart",
        data.workflow_fixture,
        f"N={total} claims",
        data.cutoff,
        description,
        _document(
            title="Verification outcomes",
            subtitle="Independent verification keeps conflicts and stale evidence visible",
            description=description,
            body="".join(pieces),
            source=data.workflow_fixture,
            sample=f"N={total} claims",
            cutoff=data.cutoff,
        ),
    )


def _heatmap_figure(data: _VisualPackData) -> Figure:
    items = tuple(data.workflow.missingness.items())
    maximum = max(value for _, value in items)
    pieces: list[str] = []
    for index, (label, value) in enumerate(items):
        row, column = divmod(index, 4)
        x = 80 + column * 275
        y = 165 + row * 170
        opacity = 0.18 + (0.72 * value / maximum if maximum else 0)
        pieces.extend(
            [
                _rect(x, y, 240, 120, fill=BLUE, stroke=BLUE, radius=6, opacity=opacity),
                _text(x + 120, y + 52, value, size=30, weight=800, anchor="middle"),
                _text(x + 120, y + 84, label.replace("_", " "), size=14, anchor="middle"),
            ]
        )
    description = "Missingness heatmap with explicit states: " + ", ".join(
        f"{label} {value}" for label, value in items
    )
    return Figure(
        "missingness-quality-heatmap",
        "Typed missingness profile",
        "heatmap",
        data.workflow_fixture,
        f"N={data.workflow.observations} observations",
        data.cutoff,
        description,
        _document(
            title="Typed missingness profile",
            subtitle="Zero, blank, not reported, and not applicable remain distinct",
            description=description,
            body="".join(pieces),
            source=data.workflow_fixture,
            sample=f"N={data.workflow.observations} observations",
            cutoff=data.cutoff,
        ),
    )


def _quantile(values: tuple[Decimal, ...], probability: Decimal) -> Decimal:
    ordered = tuple(sorted(values))
    position = Decimal(len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - Decimal(lower)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _box_figure(data: _VisualPackData) -> Figure:
    context = data.illustrative_context
    values = tuple(sorted(context.values))
    minimum, maximum = values[0], values[-1]
    q1 = _quantile(values, Decimal("0.25"))
    median = _quantile(values, Decimal("0.5"))
    q3 = _quantile(values, Decimal("0.75"))
    left, width = Decimal(130), Decimal(940)
    span = maximum - minimum or Decimal(1)

    def scale(value: Decimal) -> float:
        return float(left + ((value - minimum) / span * width))

    y = 300.0
    pieces = [
        _line(scale(minimum), y, scale(maximum), y, stroke=INK, width=3),
        _line(scale(minimum), y - 30, scale(minimum), y + 30, stroke=INK, width=3),
        _line(scale(maximum), y - 30, scale(maximum), y + 30, stroke=INK, width=3),
        _rect(scale(q1), y - 62, scale(q3) - scale(q1), 124, fill="#d9eeea", stroke=TEAL),
        _line(scale(median), y - 62, scale(median), y + 62, stroke=TEAL, width=5),
    ]
    for value, label in (
        (minimum, "min"),
        (q1, "Q1"),
        (median, "median"),
        (q3, "Q3"),
        (maximum, "max"),
    ):
        pieces.append(_text(scale(value), 405, f"{label}: {value:g}", size=15, anchor="middle"))
    pieces.append(
        _text(
            600,
            495,
            "Illustrative only — operational within-portfolio distributions suppress "
            f"N below {context.minimum_sample_size}",
            size=16,
            fill=RED,
            anchor="middle",
        )
    )
    description = (
        f"Five-number plot for {context.label}; N={len(values)}, minimum sample N="
        f"{context.minimum_sample_size}, minimum value {minimum}, Q1 {q1}, median {median}, "
        f"Q3 {q3}, maximum value {maximum} {context.unit}. Illustrative synthetic data."
    )
    return Figure(
        "cohort-context-five-number",
        "Within-portfolio distribution context",
        "five-number box plot",
        "fixtures/visualisation_pack.json (illustrative synthetic within-portfolio distribution)",
        f"N={len(values)} synthetic values",
        data.cutoff,
        description,
        _document(
            title="Within-portfolio distribution context",
            subtitle="Five-number summaries show distribution without a ranking or causal label",
            description=description,
            body="".join(pieces),
            source=(
                "fixtures/visualisation_pack.json "
                "(illustrative synthetic within-portfolio distribution)"
            ),
            sample=f"N={len(values)} synthetic values",
            cutoff=data.cutoff,
        ),
    )


def _evaluation_figure(data: _VisualPackData) -> Figure:
    conditions = (
        ("Single-agent ablation", data.evaluation.deterministic_single_agent),
        ("Multi-agent verification", data.evaluation.multi_agent_verification),
    )
    metrics: tuple[tuple[str, Literal["precision", "recall", "verification_accuracy"]], ...] = (
        ("Precision", "precision"),
        ("Recall", "recall"),
        ("Verification accuracy", "verification_accuracy"),
    )
    pieces: list[str] = []
    base_x, base_y = 140.0, 570.0
    bar_width = 70.0
    for condition_index, (condition_label, condition) in enumerate(conditions):
        group_x = base_x + condition_index * 520
        for metric_index, (metric_label, attribute) in enumerate(metrics):
            value = float(getattr(condition, attribute))
            x = group_x + metric_index * (bar_width + 25)
            height = value * 340
            pieces.extend(
                [
                    _rect(
                        x,
                        base_y - height,
                        bar_width,
                        height,
                        fill=PALETTE[metric_index],
                        stroke="none",
                        radius=3,
                    ),
                    _text(
                        x + bar_width / 2,
                        base_y - height - 12,
                        f"{value:.2f}",
                        size=14,
                        weight=700,
                        anchor="middle",
                    ),
                    _text(
                        x + bar_width / 2,
                        base_y + 25,
                        metric_label.split()[0],
                        size=13,
                        anchor="middle",
                    ),
                ]
            )
        pieces.append(
            _text(group_x + 120, 635, condition_label, size=16, weight=700, anchor="middle")
        )
    single = data.evaluation.deterministic_single_agent
    multi = data.evaluation.multi_agent_verification
    description = (
        f"D0 synthetic evaluation with {data.evaluation.case_count} cases. Single-agent ablation "
        f"precision {single.precision:.2f}, recall {single.recall:.2f}, verification accuracy "
        f"{single.verification_accuracy:.2f}. Multi-agent verification precision "
        f"{multi.precision:.2f}, recall {multi.recall:.2f}, verification accuracy "
        f"{multi.verification_accuracy:.2f}. These are synthetic functional results, not general "
        "performance claims."
    )
    return Figure(
        "evaluation-condition-comparison",
        "Controlled D0 condition comparison",
        "grouped bar chart",
        "fixtures/evaluation_manifest.json",
        f"N={data.evaluation.case_count} synthetic cases",
        data.cutoff,
        description,
        _document(
            title="Controlled D0 condition comparison",
            subtitle="Shared normalization core; independent verification is the declared addition",
            description=description,
            body="".join(pieces),
            source="fixtures/evaluation_manifest.json",
            sample=f"N={data.evaluation.case_count} synthetic cases",
            cutoff=data.cutoff,
        ),
    )


def _timeline_figure(
    *,
    key: str,
    title: str,
    subtitle: str,
    stages: tuple[str, ...],
    source: str,
    sample: str,
    cutoff: str,
    description: str,
) -> Figure:
    x1, x2, y = 110.0, 1090.0, 330.0
    pieces = [_line(x1, y, x2, y, stroke=TEAL, width=4)]
    for index, stage in enumerate(stages):
        x = x1 + index * (x2 - x1) / max(len(stages) - 1, 1)
        pieces.extend(
            [
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="18" fill="{PALETTE[index % len(PALETTE)]}" '
                f'stroke="{PAPER}" stroke-width="4"/>',
                _text(
                    x,
                    y - 45 if index % 2 == 0 else y + 70,
                    stage,
                    size=16,
                    weight=700,
                    anchor="middle",
                ),
                _text(x, y + 7, index + 1, size=13, weight=800, fill="#ffffff", anchor="middle"),
            ]
        )
    return Figure(
        key,
        title,
        "timeline",
        source,
        sample,
        cutoff,
        description,
        _document(
            title=title,
            subtitle=subtitle,
            description=description,
            body="".join(pieces),
            source=source,
            sample=sample,
            cutoff=cutoff,
        ),
    )


def _identity_figure(data: _VisualPackData) -> Figure:
    identity = data.identity_structural_profile
    values = (
        ("Portfolio company columns", float(identity.company_columns)),
        ("Exact registry identifiers", float(identity.exact_registry_identifiers)),
        ("Human-review holds", float(identity.review_holds)),
    )
    return _bar_figure(
        key="identity-resolution-funnel",
        title="Precision-first identity resolution",
        subtitle=("Only exact reviewed source identifiers proceed; new and name-only records stop"),
        values=values,
        source="Supplied workbook structural profile (counts only; no names or values)",
        sample=f"N={identity.company_columns} company columns",
        cutoff=data.cutoff,
        description=(
            f"Of {identity.company_columns} structural company columns, "
            f"{identity.exact_registry_identifiers} has an exact registry identifier and "
            f"{identity.review_holds} require human identity review."
        ),
    )


def build_figures(data: _VisualPackData) -> tuple[Figure, ...]:
    common_source = "Versioned repository contracts and deterministic synthetic fixtures"
    architecture = _flow_figure(
        key="architecture-trust-boundaries",
        title="Evidence-first architecture and trust boundaries",
        subtitle="Restricted submissions and public evidence remain separate until verification",
        nodes=(
            ("Submission", "restricted snapshot"),
            ("Identity", "exact IDs + holds"),
            ("Source snapshots", "public + immutable"),
            ("Typed facts", "time + locator"),
            ("Quality", "rules + dispositions"),
            ("Extraction", "deterministic first"),
            ("Verification", "independent role"),
            ("Human gate", "approve then export"),
        ),
        source="docs/ARCHITECTURE.md and source contracts",
        sample="8 bounded components",
        cutoff=data.cutoff,
        description=(
            "Flow from restricted submission through reviewed identity, immutable public "
            "snapshots, "
            "typed facts, quality, extraction, independent verification, and named human approval."
        ),
    )
    workflow = _flow_figure(
        key="agent-workflow-wayfinder",
        title="Bounded agent workflow",
        subtitle="A fixed acyclic state machine with persisted inputs, outputs, and stop states",
        nodes=tuple(
            (stage.title(), role)
            for stage, role in (
                ("plan", "scope + cutoff"),
                ("resolve", "identity gate"),
                ("collect", "immutable evidence"),
                ("extract", "typed values"),
                ("normalize", "units + missingness"),
                ("verify", "claims + conflicts"),
                ("compose", "tables + context"),
                ("review", "named decision"),
            )
        ),
        source="src/portfolio_agent/workflow.py",
        sample="8 persisted stages",
        cutoff=data.cutoff,
        description=(
            "Eight stages: plan, resolve, collect, extract, normalize, verify, compose, review."
        ),
    )
    provenance = _flow_figure(
        key="evidence-provenance-chain",
        title="Claim-to-source provenance chain",
        subtitle="Every supported statement remains traceable to immutable bytes",
        nodes=(
            ("Claim", "verification state"),
            ("Evidence fact", "typed value"),
            ("Exact locator", "cell / JSON / page"),
            ("Snapshot", "SHA-256 bytes"),
            ("Source manifest", "version + policy"),
        ),
        source=common_source,
        sample="5 provenance links",
        cutoff=data.cutoff,
        description=(
            "A claim links to a typed fact, exact locator, immutable snapshot, and source manifest."
        ),
    )
    source_coverage = _bar_figure(
        key="source-coverage",
        title="Synthetic source coverage",
        subtitle="Supplied and public evidence are counted separately",
        values=tuple(
            (key.replace("_", " "), float(value)) for key, value in data.workflow.evidence.items()
        ),
        source=data.workflow_fixture,
        sample=f"N={sum(data.workflow.evidence.values())} evidence items",
        cutoff=data.cutoff,
        description=(
            "Evidence coverage contains "
            + ", ".join(
                f"{value} {key.replace('_', ' ')} items"
                for key, value in data.workflow.evidence.items()
            )
            + "."
        ),
    )
    quality = _bar_figure(
        key="quality-dispositions",
        title="Executable quality dispositions",
        subtitle="Violations are decisions, not one opaque quality score",
        values=tuple((key, float(value)) for key, value in data.workflow.quality.items()),
        source=data.workflow_fixture,
        sample=f"N={sum(data.workflow.quality.values())} explicit findings",
        cutoff=data.cutoff,
        description=(
            "Synthetic workflow quality dispositions: "
            + ", ".join(
                f"{key.replace('_', ' ')} {value}" for key, value in data.workflow.quality.items()
            )
            + "."
        ),
        maximum=max(data.workflow.quality.values()) or 1,
    )
    extraction = _bar_figure(
        key="extraction-attempt-outcomes",
        title="Extraction attempt outcomes",
        subtitle="Every provider attempt has a persisted terminal state",
        values=tuple(
            (key, float(value)) for key, value in data.workflow.extraction_attempts.items()
        ),
        source=data.workflow_fixture,
        sample=f"N={sum(data.workflow.extraction_attempts.values())} attempts",
        cutoff=data.cutoff,
        description=(
            "Synthetic deterministic extraction attempts: "
            + ", ".join(
                f"{key.replace('_', ' ')} {value}"
                for key, value in data.workflow.extraction_attempts.items()
            )
            + "."
        ),
    )
    temporal = _timeline_figure(
        key="temporal-eligibility",
        title="Claim-relative temporal eligibility",
        subtitle="Availability time and effective time are checked against one frozen cutoff",
        stages=(
            "Event occurs",
            "Source publishes",
            "Snapshot retrieved",
            "Cutoff frozen",
            "Claim verified",
        ),
        source="src/portfolio_agent/temporal.py",
        sample="5 temporal checkpoints",
        cutoff=data.cutoff,
        description=(
            "Timeline separates event, publication, retrieval, reporting cutoff, and claim "
            "verification. "
            "Evidence published after the cutoff is excluded."
        ),
    )
    lifecycle = _timeline_figure(
        key="ukri-lifecycle",
        title="UKRI/GtR grant lifecycle",
        subtitle="Awards are append-only events; association never implies causal impact",
        stages=("Opportunity", "Decision", "Award", "Project", "Outcome"),
        source="fixtures/evidence/ukri_synthetic.json",
        sample="5 expected lifecycle stages",
        cutoff=data.cutoff,
        description="Lifecycle stages are opportunity, decision, award, project, and outcome.",
    )
    review = _timeline_figure(
        key="report-review-state-machine",
        title="Approval-gated export states",
        subtitle="Content changes revoke approval and stale browser actions fail",
        stages=("Draft", "Pending review", "Approved", "Exporting", "Exported"),
        source="src/portfolio_agent/reporting.py",
        sample="5 report states",
        cutoff=data.cutoff,
        description=(
            "Report states progress from draft to pending review, approved, exporting, and "
            "exported."
        ),
    )
    abstention = _flow_figure(
        key="extraction-abstention-decision",
        title="Hierarchical extraction and abstention",
        subtitle="Smallest sufficient context first; absent or ambiguous fields return null",
        nodes=(
            ("Structured field", "JSON / iXBRL"),
            ("Exact locator", "sign + scale"),
            ("Period match?", "comparative check"),
            ("Validate", "schema + span"),
            ("Abstain", "missing / ambiguous"),
        ),
        source="src/portfolio_agent/document_extraction.py",
        sample="5 decision points",
        cutoff=data.cutoff,
        description=(
            "The extractor searches structured fields, preserves exact locators and sign or scale, "
            "checks periods, validates, and abstains when evidence is absent or ambiguous."
        ),
    )
    return (
        architecture,
        workflow,
        provenance,
        _identity_figure(data),
        temporal,
        source_coverage,
        _stacked_figure(data),
        _heatmap_figure(data),
        quality,
        lifecycle,
        _box_figure(data),
        _evaluation_figure(data),
        extraction,
        abstention,
        review,
    )


def _atomic_text(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def generate_visual_pack(input_path: Path, output_dir: Path) -> dict[str, Any]:
    payload = input_path.read_bytes()
    data = _VisualPackData.model_validate_json(payload)
    figures = build_figures(data)
    resolved_output = output_dir.resolve()
    resolved_output.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, str]] = []
    for index, figure in enumerate(figures, start=1):
        filename = f"figure-{index:02d}-{figure.key}.svg"
        target = resolved_output / filename
        _atomic_text(target, figure.svg)
        manifest_rows.append(
            {
                "figure": str(index),
                "key": figure.key,
                "filename": filename,
                "title": figure.title,
                "kind": figure.kind,
                "source": figure.source,
                "sample": figure.sample,
                "cutoff": figure.cutoff,
                "sha256": sha256_bytes(figure.svg.encode()),
                "textual_alternative": figure.textual_alternative,
            }
        )
    manifest = {
        "schema_version": "dissertation-figure-manifest-v2",
        "input": {
            "name": input_path.name,
            "sha256": sha256_bytes(payload),
            "classification": data.classification,
        },
        "figure_count": len(manifest_rows),
        "figures": manifest_rows,
    }
    _atomic_text(
        resolved_output / "manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )
    csv_path = resolved_output / "figure-data.csv"
    csv_tmp = csv_path.with_suffix(".csv.tmp")
    with csv_tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    csv_tmp.replace(csv_path)
    readme = [
        "# Dissertation visual pack",
        "",
        "All figures are deterministic SVGs with embedded titles/descriptions, adjacent textual "
        "alternatives, source labels, sample sizes, and cutoffs. Synthetic results and "
        "illustrative "
        "data are not empirical claims about the supplied portfolio.",
        "",
        "| Figure | Visual | Type | Evidence boundary |",
        "|---:|---|---|---|",
    ]
    for row in manifest_rows:
        readme.append(
            f"| {row['figure']} | [{row['title']}]({row['filename']}) | {row['kind']} | "
            f"{row['sample']}; cutoff {row['cutoff']} |"
        )
    readme.extend(["", "## Visual gallery", ""])
    for row in manifest_rows:
        readme.extend(
            [
                f"### Figure {row['figure']}: {row['title']}",
                "",
                f"![{row['textual_alternative']}]({row['filename']})",
                "",
                f"Source: {row['source']}. {row['sample']}; cutoff {row['cutoff']}.",
                "",
            ]
        )
    readme.extend(
        [
            "",
            "## Textual alternatives",
            "",
            *[
                f"### Figure {row['figure']}: {row['title']}\n\n{row['textual_alternative']}"
                for row in manifest_rows
            ],
            "",
            "Regenerate with `portfolio-agent visualize`; compare `manifest.json` hashes before "
            "using a figure in the dissertation.",
        ]
    )
    _atomic_text(resolved_output / "README.md", "\n".join(readme).rstrip() + "\n")
    return manifest
