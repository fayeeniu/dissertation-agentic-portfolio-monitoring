from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from .catalogue import seed_catalogue
from .company_intelligence import CompanyIntakeService
from .company_research import (
    CompanyResearchService,
    OpenAICompanyResearchClient,
    PublicFetcher,
    ResearchModelClient,
    SafePublicFetcher,
)
from .company_research_fixtures import (
    FixturePublicFetcher,
    FixtureResearchCorpus,
    FixtureResearchModel,
    load_fixture_pages,
)
from .config import Settings
from .connectors.companies_house import CompaniesHouseConnector
from .connectors.fixtures import FixtureConnector, NoopConnector
from .connectors.registry import SourceRegistry
from .connectors.ukri import UkriConnector
from .db import create_db_engine, create_session_factory, initialize_database
from .importers import PortfolioImporter
from .llm.base import ExtractionProvider
from .llm.deterministic import DeterministicExtractionProvider
from .llm.experiment import SyntheticOpenAIExperimentProvider
from .llm.openai_provider import OpenAIStructuredExtractionProvider
from .reporting import ReportService
from .workflow import PortfolioWorkflow


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Runtime:
    settings: Settings
    engine: Engine
    session_factory: sessionmaker[Session]
    importer: PortfolioImporter
    workflow: PortfolioWorkflow
    reports: ReportService
    sources: SourceRegistry
    intakes: CompanyIntakeService
    company_research: CompanyResearchService | None = None
    #: ``closed`` when both research gates are shut, ``live`` when the external
    #: model and public retrieval are open, ``fixture`` when the run replays an
    #: offline synthetic corpus with no model call and no outbound request.
    research_mode: str = "closed"


def _assemble_runtime(settings: Settings, *, extraction_provider: ExtractionProvider) -> Runtime:
    selected = settings
    engine = create_db_engine(selected.database_url)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory.begin() as session:
        seed_catalogue(session)
    connector = (
        FixtureConnector.from_path(
            selected.project_root / "fixtures" / "evidence" / "synthetic_evidence.json"
        )
        if selected.enable_synthetic_fixture_connector
        else NoopConnector()
    )
    source_connectors = (
        (
            CompaniesHouseConnector(
                local_snapshot_path=(
                    selected.project_root
                    / "fixtures"
                    / "evidence"
                    / "companies_house_synthetic.json"
                )
            ),
            UkriConnector(selected.project_root / "fixtures" / "evidence" / "ukri_synthetic.json"),
        )
        if selected.enable_synthetic_fixture_connector
        else ()
    )
    source_registry = SourceRegistry(
        session_factory,
        selected.source_snapshot_dir or (selected.project_root / "var" / "sources").resolve(),
        connectors=source_connectors,
    )
    source_registry.seed_manifests()
    return Runtime(
        settings=selected,
        engine=engine,
        session_factory=session_factory,
        importer=PortfolioImporter(session_factory, selected.raw_data_dir),
        workflow=PortfolioWorkflow(
            session_factory,
            connector=connector,
            extraction_provider=extraction_provider,
            source_registry=source_registry,
        ),
        reports=ReportService(session_factory, selected.project_root / "var" / "exports"),
        sources=source_registry,
        intakes=CompanyIntakeService(session_factory, selected.raw_data_dir),
    )


def create_runtime(
    settings: Settings | None = None,
    *,
    company_research_client: ResearchModelClient | None = None,
    public_fetcher: PublicFetcher | None = None,
) -> Runtime:
    selected = settings or Settings.from_env(project_root())
    if selected.allow_external_llm and not selected.allow_live_public_retrieval:
        raise RuntimeError(
            "Gate G4 external-model opt-in cannot open the default runtime alone; company "
            "research also requires PORTFOLIO_ALLOW_LIVE_PUBLIC_RETRIEVAL."
        )
    if selected.allow_live_public_retrieval and not selected.allow_external_llm:
        raise RuntimeError(
            "Gate G2 live-retrieval opt-in cannot open the default runtime alone; company "
            "research also requires PORTFOLIO_ALLOW_EXTERNAL_LLM."
        )
    if selected.allow_external_llm and not selected.reviewer_name:
        raise RuntimeError("Live company research requires PORTFOLIO_REVIEWER_NAME.")
    if (
        selected.allow_external_llm
        and company_research_client is None
        and not os.getenv("OPENAI_API_KEY")
    ):
        raise RuntimeError("OPENAI_API_KEY must be set for live company research.")
    runtime = _assemble_runtime(
        selected,
        extraction_provider=DeterministicExtractionProvider(),
    )
    if selected.allow_external_llm:
        model_client = company_research_client or OpenAICompanyResearchClient(selected)
        fetcher = public_fetcher or SafePublicFetcher(selected)
        object.__setattr__(
            runtime,
            "company_research",
            CompanyResearchService(
                runtime.session_factory,
                selected,
                model_client=model_client,
                fetcher=fetcher,
            ),
        )
        object.__setattr__(runtime, "research_mode", "live")
    return runtime


def create_fixture_research_runtime(settings: Settings | None = None) -> Runtime:
    """Create a runtime whose research stages replay an offline synthetic corpus.

    No model call and no outbound request is made. The orchestrator, snapshot
    checksums, exact-span validation, contradiction detection and the human
    approval gate all execute normally, so this is a faithful rehearsal of the
    workflow rather than a mock of its result. Runs produced here are synthetic
    and every surface must label them as such.
    """

    base = settings or Settings.from_env(project_root())
    selected = replace(
        base,
        allow_external_llm=True,
        allow_live_public_retrieval=True,
        reviewer_name=base.reviewer_name or "Local fixture reviewer",
    )
    corpus = FixtureResearchCorpus(
        load_fixture_pages(selected.project_root / "fixtures" / "company_research_demo.json")
    )
    runtime = create_runtime(
        selected,
        company_research_client=FixtureResearchModel(corpus),
        public_fetcher=FixturePublicFetcher(corpus),
    )
    object.__setattr__(runtime, "research_mode", "fixture")
    return runtime


def create_openai_experiment_runtime(
    settings: Settings | None = None,
    *,
    client: Any | None = None,
) -> Runtime:
    """Create the separately authorised, synthetic-only live experiment runtime."""

    selected = settings or Settings.from_env(project_root())
    if not selected.allow_external_llm:
        raise RuntimeError("Set PORTFOLIO_ALLOW_EXTERNAL_LLM=true for the live smoke command.")
    if not selected.enable_synthetic_fixture_connector:
        raise RuntimeError(
            "Set PORTFOLIO_ENABLE_SYNTHETIC_FIXTURE_CONNECTOR=true for the live smoke command."
        )
    if selected.allow_live_public_retrieval:
        raise RuntimeError("The live smoke command cannot enable public retrieval.")
    if client is None and not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY must be set in the process environment.")
    live_provider = OpenAIStructuredExtractionProvider(selected, client=client)
    return _assemble_runtime(
        selected,
        extraction_provider=SyntheticOpenAIExperimentProvider(live_provider),
    )
