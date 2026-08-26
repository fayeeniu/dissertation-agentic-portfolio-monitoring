from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from .catalogue import seed_catalogue
from .config import Settings
from .connectors.companies_house import CompaniesHouseConnector
from .connectors.fixtures import FixtureConnector, NoopConnector
from .connectors.registry import SourceRegistry
from .connectors.ukri import UkriConnector
from .db import create_db_engine, create_session_factory, initialize_database
from .importers import PortfolioImporter
from .llm.deterministic import DeterministicExtractionProvider
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


def create_runtime(settings: Settings | None = None) -> Runtime:
    selected = settings or Settings.from_env(project_root())
    if selected.allow_live_public_retrieval:
        raise RuntimeError(
            "Default runtime refuses live public retrieval while source-admission Gate G2 is open."
        )
    if selected.allow_external_llm:
        raise RuntimeError(
            "Default runtime refuses external-model routing while experiment Gate G4 is open; "
            "an approved experiment must inject the guarded provider explicitly."
        )
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
            extraction_provider=DeterministicExtractionProvider(),
            source_registry=source_registry,
        ),
        reports=ReportService(session_factory, selected.project_root / "var" / "exports"),
        sources=source_registry,
    )
