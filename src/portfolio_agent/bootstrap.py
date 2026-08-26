from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from .catalogue import seed_catalogue
from .config import Settings
from .connectors.fixtures import FixtureConnector
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


def create_runtime(settings: Settings | None = None) -> Runtime:
    selected = settings or Settings.from_env(project_root())
    engine = create_db_engine(selected.database_url)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory.begin() as session:
        seed_catalogue(session)
    connector = FixtureConnector.from_path(
        selected.project_root / "fixtures" / "evidence" / "synthetic_evidence.json"
    )
    return Runtime(
        settings=selected,
        engine=engine,
        session_factory=session_factory,
        importer=PortfolioImporter(session_factory, selected.raw_data_dir),
        workflow=PortfolioWorkflow(
            session_factory,
            connector=connector,
            extraction_provider=DeterministicExtractionProvider(),
        ),
        reports=ReportService(session_factory, selected.project_root / "var" / "exports"),
    )
