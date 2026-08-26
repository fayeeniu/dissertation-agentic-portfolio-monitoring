from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from .cbit_contract import (
    CBIT_CONTRACT_VERSION,
    CBIT_ROWS,
    CbitRowRole,
    CbitValueShape,
    PeriodSemantics,
)
from .enums import MetricDataType, Sourceability
from .models import CatalogueVersionModel, MetricDefinitionModel
from .schemas import MetricDefinition


def canonicalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


CATALOGUE_VERSION = f"portfolio-metrics-{CBIT_CONTRACT_VERSION}"


BASE_METRICS: tuple[MetricDefinition, ...] = (
    MetricDefinition(
        key="employees_total",
        category="Employment and economic impact",
        label="Total employees",
        data_type=MetricDataType.INTEGER,
        unit="people",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("number of employees", "total number of employees"),
        period_semantics=PeriodSemantics.AS_AT_CUTOFF,
        description="Headcount reported by the portfolio company for the period.",
    ),
    MetricDefinition(
        key="jobs_created",
        category="Employment and economic impact",
        label="Jobs created",
        data_type=MetricDataType.INTEGER,
        unit="people",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("new jobs created",),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="New jobs created during the reporting period.",
    ),
    MetricDefinition(
        key="women_employees_percentage",
        category="Diversity and sustainability",
        label="Women employees",
        data_type=MetricDataType.PERCENTAGE,
        unit="percentage_points",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("percentage of women employees", "female employees percentage"),
        period_semantics=PeriodSemantics.AS_AT_CUTOFF,
        description="Women as a percentage of employees, represented in percentage points.",
    ),
    MetricDefinition(
        key="research_development_spend",
        category="Research and development",
        label="Research and development spend",
        data_type=MetricDataType.CURRENCY,
        unit="currency_units",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("r&d spend", "r and d spend"),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Company-reported research and development expenditure.",
    ),
    MetricDefinition(
        key="technology_readiness_level",
        category="Technology readiness",
        label="Technology readiness level",
        data_type=MetricDataType.INTEGER,
        unit="trl_level",
        sourceability=Sourceability.MIXED,
        aliases=("trl",),
        period_semantics=PeriodSemantics.AS_AT_CUTOFF,
        description="Technology readiness level on the 1 to 9 ordinal scale.",
    ),
    MetricDefinition(
        key="products_launched",
        category="Products and processes",
        label="Products launched",
        data_type=MetricDataType.INTEGER,
        unit="products",
        sourceability=Sourceability.MIXED,
        aliases=("number of products launched", "new products launched"),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Products launched during the reporting period.",
    ),
    MetricDefinition(
        key="process_efficiency_improvement",
        category="Products and processes",
        label="Process efficiency improvement",
        data_type=MetricDataType.PERCENTAGE,
        unit="percentage_points",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("efficiency improvement", "process improvement percentage"),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Company-reported process efficiency change in percentage points.",
    ),
    MetricDefinition(
        key="external_investment",
        category="Funding and investments",
        label="External investment raised",
        data_type=MetricDataType.CURRENCY,
        unit="currency_units",
        sourceability=Sourceability.MIXED,
        aliases=("investment raised", "funding raised", "external investment"),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="External equity or debt investment raised in the period.",
    ),
    MetricDefinition(
        key="grant_funding",
        category="Funding and investments",
        label="Grant funding awarded",
        data_type=MetricDataType.CURRENCY,
        unit="currency_units",
        sourceability=Sourceability.PUBLICLY_SOURCEABLE,
        aliases=("grant funding", "grants awarded", "public funding awarded"),
        period_semantics=PeriodSemantics.SINCE_PROGRAMME_START,
        description="Grant funding supported by a named public or internal source.",
    ),
    MetricDefinition(
        key="awards_received",
        category="Market and partnerships",
        label="Awards received",
        data_type=MetricDataType.INTEGER,
        unit="awards",
        sourceability=Sourceability.PUBLICLY_SOURCEABLE,
        aliases=("number of awards",),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Count of independently sourceable awards in the period.",
    ),
    MetricDefinition(
        key="new_markets_entered",
        category="Market and partnerships",
        label="New markets entered",
        data_type=MetricDataType.INTEGER,
        unit="markets",
        sourceability=Sourceability.MIXED,
        aliases=("markets entered",),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Count of newly entered markets in the reporting period.",
    ),
    MetricDefinition(
        key="new_partnerships",
        category="Market and partnerships",
        label="New partnerships",
        data_type=MetricDataType.INTEGER,
        unit="partnerships",
        sourceability=Sourceability.MIXED,
        aliases=("partnerships formed",),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="New material partnerships formed during the reporting period.",
    ),
    MetricDefinition(
        key="revenue",
        category="Financial impact",
        label="Revenue",
        data_type=MetricDataType.CURRENCY,
        unit="currency_units",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("turnover", "total revenue"),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Company-reported revenue for the period.",
    ),
    MetricDefinition(
        key="gross_margin",
        category="Financial impact",
        label="Gross margin",
        data_type=MetricDataType.PERCENTAGE,
        unit="percentage_points",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("gross profit margin",),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Company-reported gross margin in percentage points.",
    ),
    MetricDefinition(
        key="valuation",
        category="Financial impact",
        label="Valuation",
        data_type=MetricDataType.CURRENCY,
        unit="currency_units",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("company valuation",),
        period_semantics=PeriodSemantics.AS_AT_CUTOFF,
        description="Most recent company-reported valuation and explicit currency.",
    ),
    MetricDefinition(
        key="policies_influenced",
        category="Policy and influence",
        label="Policies influenced",
        data_type=MetricDataType.INTEGER,
        unit="policies",
        sourceability=Sourceability.MIXED,
        aliases=(),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Count of evidenced policy influence outcomes.",
    ),
    MetricDefinition(
        key="ai_hours_saved",
        category="AI operational efficiency",
        label="AI-enabled hours saved",
        data_type=MetricDataType.DURATION_HOURS,
        unit="hours",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("hours saved through ai", "ai time saved"),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description=(
            "Estimated hours saved through AI, with the estimate method retained separately."
        ),
    ),
    MetricDefinition(
        key="ai_error_reduction",
        category="AI operational efficiency",
        label="AI-enabled error reduction",
        data_type=MetricDataType.PERCENTAGE,
        unit="percentage_points",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("mistakes reduced by ai", "ai mistakes reduction"),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Company-reported error reduction attributed to AI in percentage points.",
    ),
    MetricDefinition(
        key="ai_core_process_coverage",
        category="AI adoption and readiness",
        label="Core processes using AI",
        data_type=MetricDataType.PERCENTAGE,
        unit="percentage_points",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("core processes that use ai", "ai process coverage"),
        period_semantics=PeriodSemantics.AS_AT_CUTOFF,
        description="Core business processes using AI, expressed in percentage points.",
    ),
    MetricDefinition(
        key="ai_tools_adopted",
        category="AI adoption and readiness",
        label="AI tools adopted",
        data_type=MetricDataType.INTEGER,
        unit="tools",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("number of ai tools adopted",),
        period_semantics=PeriodSemantics.AS_AT_CUTOFF,
        description="Count of AI tools adopted by the company.",
    ),
    MetricDefinition(
        key="material_news_items",
        category="Market and partnerships",
        label="Material news items",
        data_type=MetricDataType.INTEGER,
        unit="items",
        sourceability=Sourceability.PUBLICLY_SOURCEABLE,
        aliases=("news items", "company news"),
        period_semantics=PeriodSemantics.REPORTING_PERIOD,
        description="Count of material, period-bounded public news items with provenance.",
    ),
)


def _metric_data_type(shape: CbitValueShape) -> MetricDataType:
    return {
        CbitValueShape.INTEGER: MetricDataType.INTEGER,
        CbitValueShape.CURRENCY: MetricDataType.CURRENCY,
        CbitValueShape.PERCENTAGE: MetricDataType.PERCENTAGE,
        CbitValueShape.ORDINAL: MetricDataType.INTEGER,
        CbitValueShape.REPORTED_DURATION: MetricDataType.TEXT,
        CbitValueShape.TEXT: MetricDataType.TEXT,
        CbitValueShape.LIST: MetricDataType.TEXT,
    }[shape]


def _build_default_metrics() -> tuple[MetricDefinition, ...]:
    by_key = {metric.key: metric for metric in BASE_METRICS}
    for row in CBIT_ROWS:
        if row.role is not CbitRowRole.INPUT:
            continue
        assert row.metric_key is not None
        assert row.sourceability is not None
        existing = by_key.get(row.metric_key)
        if existing is not None:
            aliases = tuple(dict.fromkeys((*existing.aliases, row.label)))
            by_key[row.metric_key] = existing.model_copy(
                update={
                    "category": row.category,
                    "sourceability": row.sourceability,
                    "unit": row.unit,
                    "aliases": aliases,
                    "period_semantics": row.period_semantics,
                }
            )
            continue
        by_key[row.metric_key] = MetricDefinition(
            key=row.metric_key,
            category=row.category,
            label=row.label,
            data_type=_metric_data_type(row.value_shape),
            sourceability=row.sourceability,
            unit=row.unit,
            aliases=(),
            period_semantics=row.period_semantics,
            description=(
                "CBIT workbook field retained under the versioned supplied-workbook contract; "
                f"period semantics: {row.period_semantics.value}."
            ),
        )
    return tuple(by_key.values())


DEFAULT_METRICS = _build_default_metrics()


class CatalogueDriftError(ValueError):
    """Raised when persisted metric semantics disagree with the selected catalogue."""


class MetricCatalogue:
    def __init__(
        self,
        metrics: Iterable[MetricDefinition] = DEFAULT_METRICS,
        *,
        version: str = CATALOGUE_VERSION,
    ) -> None:
        self._metrics = tuple(metrics)
        self.version = version
        self._by_key = {metric.key: metric for metric in self._metrics}
        if len(self._by_key) != len(self._metrics):
            raise ValueError("Duplicate metric key in catalogue.")
        self._by_label: dict[str, MetricDefinition] = {}
        for metric in self._metrics:
            for label in (metric.key, metric.label, *metric.aliases):
                canonical = canonicalize_label(label)
                existing = self._by_label.get(canonical)
                if existing is not None and existing.key != metric.key:
                    raise ValueError(f"Ambiguous metric alias: {label}")
                self._by_label[canonical] = metric
        payload = [
            metric.model_dump(mode="json")
            for metric in sorted(self._metrics, key=lambda item: item.key)
        ]
        self.sha256 = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    @property
    def metrics(self) -> tuple[MetricDefinition, ...]:
        return self._metrics

    def get(self, key: str) -> MetricDefinition:
        return self._by_key[key]

    def resolve(self, label: str) -> MetricDefinition | None:
        return self._by_label.get(canonicalize_label(label))


def seed_catalogue(session: Session, catalogue: MetricCatalogue | None = None) -> None:
    selected = catalogue or MetricCatalogue()
    stored_version = session.scalar(
        select(CatalogueVersionModel).where(CatalogueVersionModel.version == selected.version)
    )
    if stored_version is None:
        session.add(
            CatalogueVersionModel(
                version=selected.version,
                sha256=selected.sha256,
                definition_count=len(selected.metrics),
                active=True,
            )
        )
    elif stored_version.sha256 != selected.sha256 or stored_version.definition_count != len(
        selected.metrics
    ):
        raise CatalogueDriftError(
            f"Catalogue version {selected.version} was reused with different semantics."
        )
    existing = {row.key: row for row in session.scalars(select(MetricDefinitionModel)).all()}
    for metric in selected.metrics:
        stored = existing.get(metric.key)
        if stored is not None:
            stored_contract = {
                "category": stored.category,
                "label": stored.label,
                "data_type": stored.data_type,
                "sourceability": stored.sourceability,
                "unit": stored.unit,
                "aliases": tuple(stored.aliases_json),
                "description": stored.description,
                "period_semantics": stored.period_semantics,
            }
            selected_contract = {
                "category": metric.category,
                "label": metric.label,
                "data_type": metric.data_type.value,
                "sourceability": metric.sourceability.value,
                "unit": metric.unit,
                "aliases": metric.aliases,
                "description": metric.description,
                "period_semantics": metric.period_semantics.value,
            }
            if stored.period_semantics is None:
                stored.period_semantics = metric.period_semantics.value
                stored_contract["period_semantics"] = metric.period_semantics.value
            if stored_contract != selected_contract:
                raise CatalogueDriftError(
                    f"Persisted metric definition differs from {selected.version}: {metric.key}"
                )
            continue
        session.add(
            MetricDefinitionModel(
                key=metric.key,
                category=metric.category,
                label=metric.label,
                data_type=metric.data_type.value,
                sourceability=metric.sourceability.value,
                unit=metric.unit,
                aliases_json=list(metric.aliases),
                description=metric.description,
                period_semantics=metric.period_semantics.value,
                active=True,
            )
        )
