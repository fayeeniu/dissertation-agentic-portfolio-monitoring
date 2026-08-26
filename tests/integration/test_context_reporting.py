from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select

from portfolio_agent.bootstrap import Runtime
from portfolio_agent.enums import DataClassification
from portfolio_agent.models import ContextStatisticModel, MetricDefinitionModel, ReportSectionModel


def _portfolio_payload(period: str, start: str, end: str, companies: list[dict[str, Any]]) -> bytes:
    return json.dumps(
        {
            "schema_version": "1.0",
            "classification": "synthetic",
            "reporting_period": {"label": period, "start_date": start, "end_date": end},
            "companies": companies,
        }
    ).encode()


def test_context_retains_outlier_and_five_number_definition(runtime: Runtime) -> None:
    companies = [
        {
            "external_id": f"SYN-CONTEXT-{index}",
            "name": f"Synthetic Context {index}",
            "metrics": {"employees_total": value},
        }
        for index, value in enumerate((1, 2, 3, 100), start=1)
    ]
    imported = runtime.importer.import_bytes(
        _portfolio_payload("SYN-CONTEXT-Q2", "2025-04-01", "2025-06-30", companies),
        filename="context.json",
        classification=DataClassification.SYNTHETIC,
    )
    result = runtime.workflow.run(imported.dataset_id)

    with runtime.session_factory() as session:
        statistic = session.scalar(
            select(ContextStatisticModel).where(
                ContextStatisticModel.run_id == result.run_id,
                ContextStatisticModel.status == "available",
            )
        )
        section = session.scalar(
            select(ReportSectionModel).where(
                ReportSectionModel.report_id == result.report_id,
                ReportSectionModel.section_key == "portfolio-context",
                ReportSectionModel.is_current.is_(True),
            )
        )

    assert statistic is not None
    assert statistic.sample_size == 4
    assert statistic.value_json == {
        "minimum": "1",
        "first_quartile": "1.75",
        "median": "2.5",
        "third_quartile": "27.25",
        "maximum": "100",
    }
    assert statistic.cohort_definition_json["minimum_sample_size"] == 3
    assert statistic.source_versions_json
    assert section is not None
    assert "No ranking or recommendation" in section.body_markdown
    assert "100" in section.body_markdown


def test_period_change_requires_compatible_unit_and_currency(runtime: Runtime) -> None:
    prior = runtime.importer.import_bytes(
        _portfolio_payload(
            "SYN-PRIOR",
            "2025-01-01",
            "2025-03-31",
            [
                {
                    "external_id": "SYN-CHANGE",
                    "name": "Synthetic Change Ltd",
                    "metrics": {
                        "employees_total": 10,
                        "research_development_spend": "GBP 100",
                    },
                }
            ],
        ),
        filename="prior.json",
        classification=DataClassification.SYNTHETIC,
    )
    runtime.workflow.run(prior.dataset_id)
    current = runtime.importer.import_bytes(
        _portfolio_payload(
            "SYN-CURRENT",
            "2025-04-01",
            "2025-06-30",
            [
                {
                    "external_id": "SYN-CHANGE",
                    "name": "Synthetic Change Ltd",
                    "metrics": {
                        "employees_total": 12,
                        "research_development_spend": "USD 100",
                    },
                }
            ],
        ),
        filename="current.json",
        classification=DataClassification.SYNTHETIC,
    )
    result = runtime.workflow.run(current.dataset_id)
    with runtime.session_factory() as session:
        section = session.scalar(
            select(ReportSectionModel).where(
                ReportSectionModel.report_id == result.report_id,
                ReportSectionModel.section_key == "period-change",
                ReportSectionModel.is_current.is_(True),
            )
        )
    assert section is not None
    assert "| comparable | 12 | 10 | 2 | 20% |" in section.body_markdown
    assert "| not_comparable |" in section.body_markdown


def test_cumulative_change_requires_identical_programme_origin(runtime: Runtime) -> None:
    prior = runtime.importer.import_bytes(
        _portfolio_payload(
            "SYN-CUMULATIVE-PRIOR",
            "2025-01-01",
            "2025-03-31",
            [
                {
                    "external_id": "SYN-CUMULATIVE-CHANGE",
                    "name": "Synthetic Cumulative Change Ltd",
                    "programme_start_date": "2024-01-01",
                    "metrics": {"grant_funding": "GBP 100"},
                }
            ],
        ),
        filename="cumulative-prior.json",
        classification=DataClassification.SYNTHETIC,
    )
    runtime.workflow.run(prior.dataset_id)
    current = runtime.importer.import_bytes(
        _portfolio_payload(
            "SYN-CUMULATIVE-CURRENT",
            "2025-04-01",
            "2025-06-30",
            [
                {
                    "external_id": "SYN-CUMULATIVE-CHANGE",
                    "name": "Synthetic Cumulative Change Ltd",
                    "programme_start_date": "2025-01-01",
                    "metrics": {"grant_funding": "GBP 150"},
                }
            ],
        ),
        filename="cumulative-current.json",
        classification=DataClassification.SYNTHETIC,
    )
    result = runtime.workflow.run(current.dataset_id)
    with runtime.session_factory() as session:
        section = session.scalar(
            select(ReportSectionModel).where(
                ReportSectionModel.report_id == result.report_id,
                ReportSectionModel.section_key == "period-change",
                ReportSectionModel.is_current.is_(True),
            )
        )
    assert section is not None
    assert "| not_comparable | 150 | — | — | — |" in section.body_markdown
    assert "| comparable | 150 | 100 | 50 | 50% |" not in section.body_markdown


def test_cumulative_context_segments_different_programme_windows(runtime: Runtime) -> None:
    companies = [
        {
            "external_id": f"SYN-WINDOW-{index}",
            "name": f"Synthetic Window {index}",
            "programme_start_date": start,
            "metrics": {"grant_funding": f"GBP {100 * index}"},
        }
        for index, start in enumerate(("2024-01-01", "2024-01-01", "2025-01-01"), start=1)
    ]
    imported = runtime.importer.import_bytes(
        _portfolio_payload("SYN-WINDOWS", "2025-04-01", "2025-06-30", companies),
        filename="cumulative-context.json",
        classification=DataClassification.SYNTHETIC,
    )
    result = runtime.workflow.run(imported.dataset_id)
    with runtime.session_factory() as session:
        statistics = list(
            session.scalars(
                select(ContextStatisticModel).where(ContextStatisticModel.run_id == result.run_id)
            ).all()
        )
    grant_statistics = [
        statistic
        for statistic in statistics
        if statistic.cohort_definition_json["period_semantics"] == "since_programme_start"
    ]
    assert sorted(statistic.sample_size for statistic in grant_statistics) == [1, 2]
    assert {statistic.status for statistic in grant_statistics} == {"insufficient_sample"}
    assert (
        len({statistic.cohort_definition_json["exposure_window"] for statistic in grant_statistics})
        == 2
    )


def test_currency_context_excludes_values_without_explicit_currency(runtime: Runtime) -> None:
    companies = [
        {
            "external_id": f"SYN-CURRENCY-CONTEXT-{index}",
            "name": f"Synthetic Currency Context {index}",
            "programme_start_date": "2024-01-01",
            "metrics": {"grant_funding": value},
        }
        for index, value in enumerate((100, 200, 300), start=1)
    ]
    imported = runtime.importer.import_bytes(
        _portfolio_payload("SYN-CURRENCY-CONTEXT", "2025-04-01", "2025-06-30", companies),
        filename="currency-context.json",
        classification=DataClassification.SYNTHETIC,
    )
    result = runtime.workflow.run(imported.dataset_id)

    with runtime.session_factory() as session:
        grant_statistics = list(
            session.scalars(
                select(ContextStatisticModel)
                .join(
                    MetricDefinitionModel,
                    MetricDefinitionModel.id == ContextStatisticModel.metric_definition_id,
                )
                .where(
                    ContextStatisticModel.run_id == result.run_id,
                    MetricDefinitionModel.key == "grant_funding",
                )
            ).all()
        )

    assert grant_statistics == []


def test_duplicate_latest_prior_period_fails_closed(runtime: Runtime) -> None:
    for filename, value in (("prior-original.json", 10), ("prior-correction.json", 11)):
        imported = runtime.importer.import_bytes(
            _portfolio_payload(
                "SYN-DUPLICATE-PRIOR",
                "2025-01-01",
                "2025-03-31",
                [
                    {
                        "external_id": "SYN-DUPLICATE-PRIOR-CO",
                        "name": "Synthetic Duplicate Prior Ltd",
                        "metrics": {"employees_total": value},
                    }
                ],
            ),
            filename=filename,
            classification=DataClassification.SYNTHETIC,
        )
        runtime.workflow.run(imported.dataset_id)

    current = runtime.importer.import_bytes(
        _portfolio_payload(
            "SYN-DUPLICATE-CURRENT",
            "2025-04-01",
            "2025-06-30",
            [
                {
                    "external_id": "SYN-DUPLICATE-PRIOR-CO",
                    "name": "Synthetic Duplicate Prior Ltd",
                    "metrics": {"employees_total": 12},
                }
            ],
        ),
        filename="duplicate-current.json",
        classification=DataClassification.SYNTHETIC,
    )
    result = runtime.workflow.run(current.dataset_id)

    with runtime.session_factory() as session:
        section = session.scalar(
            select(ReportSectionModel).where(
                ReportSectionModel.report_id == result.report_id,
                ReportSectionModel.section_key == "period-change",
                ReportSectionModel.is_current.is_(True),
            )
        )

    assert section is not None
    assert "| conflicted_prior_period | 12 | — | — | — |" in section.body_markdown
    assert "| comparable | 12 | 10 | 2 | 20% |" not in section.body_markdown
    assert "| comparable | 12 | 11 | 1 |" not in section.body_markdown
