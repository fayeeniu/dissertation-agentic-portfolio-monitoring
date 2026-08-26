from __future__ import annotations

import re
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from .enums import MetricDataType, Sourceability
from .models import MetricDefinitionModel
from .schemas import MetricDefinition


def canonicalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


DEFAULT_METRICS: tuple[MetricDefinition, ...] = (
    MetricDefinition(
        key="employees_total",
        category="Employment and economic impact",
        label="Total employees",
        data_type=MetricDataType.INTEGER,
        unit="people",
        sourceability=Sourceability.INTERNAL_ONLY,
        aliases=("number of employees", "total number of employees"),
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
        description="Company-reported research and development expenditure.",
    ),
    MetricDefinition(
        key="technology_readiness_level",
        category="Technology readiness",
        label="Technology readiness level",
        data_type=MetricDataType.INTEGER,
        unit="trl_level",
        sourceability=Sourceability.MIXED,
        aliases=("trl", "trl progression"),
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
        description="Most recent company-reported valuation and explicit currency.",
    ),
    MetricDefinition(
        key="policies_influenced",
        category="Policy and influence",
        label="Policies influenced",
        data_type=MetricDataType.INTEGER,
        unit="policies",
        sourceability=Sourceability.MIXED,
        aliases=("policy influence",),
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
        description="Count of material, period-bounded public news items with provenance.",
    ),
)


class MetricCatalogue:
    def __init__(self, metrics: Iterable[MetricDefinition] = DEFAULT_METRICS) -> None:
        self._metrics = tuple(metrics)
        self._by_key = {metric.key: metric for metric in self._metrics}
        self._by_label: dict[str, MetricDefinition] = {}
        for metric in self._metrics:
            for label in (metric.key, metric.label, *metric.aliases):
                canonical = canonicalize_label(label)
                existing = self._by_label.get(canonical)
                if existing is not None and existing.key != metric.key:
                    raise ValueError(f"Ambiguous metric alias: {label}")
                self._by_label[canonical] = metric

    @property
    def metrics(self) -> tuple[MetricDefinition, ...]:
        return self._metrics

    def get(self, key: str) -> MetricDefinition:
        return self._by_key[key]

    def resolve(self, label: str) -> MetricDefinition | None:
        return self._by_label.get(canonicalize_label(label))


def seed_catalogue(session: Session, catalogue: MetricCatalogue | None = None) -> None:
    selected = catalogue or MetricCatalogue()
    existing_keys = set(session.scalars(select(MetricDefinitionModel.key)).all())
    for metric in selected.metrics:
        if metric.key in existing_keys:
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
                active=True,
            )
        )
