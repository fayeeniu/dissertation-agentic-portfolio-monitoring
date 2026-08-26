from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

APPROVED_OPENAI_MODEL = "gpt-5.4-mini"
APPROVED_OPENAI_ESCALATION_MODEL = "gpt-5.4"


def _as_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    project_root: Path
    database_url: str
    raw_data_dir: Path
    source_snapshot_dir: Path | None = None
    openai_model: str = APPROVED_OPENAI_MODEL
    openai_escalation_model: str = APPROVED_OPENAI_ESCALATION_MODEL
    allow_external_llm: bool = False
    allow_live_public_retrieval: bool = False
    enable_synthetic_fixture_connector: bool = False
    http_timeout_seconds: float = 10.0
    http_max_response_bytes: int = 5 * 1024 * 1024
    http_max_attempts: int = 3
    openai_timeout_seconds: float = 30.0
    reviewer_name: str | None = None

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> Settings:
        root = (project_root or Path.cwd()).resolve()
        database_url = os.getenv(
            "PORTFOLIO_DATABASE_URL", f"sqlite:///{root / 'var' / 'portfolio.db'}"
        )
        raw_setting = Path(os.getenv("PORTFOLIO_RAW_DATA_DIR", "var/raw"))
        raw_data_dir = raw_setting if raw_setting.is_absolute() else root / raw_setting
        snapshot_setting = Path(os.getenv("PORTFOLIO_SOURCE_SNAPSHOT_DIR", "var/sources"))
        source_snapshot_dir = (
            snapshot_setting if snapshot_setting.is_absolute() else root / snapshot_setting
        )
        return cls(
            project_root=root,
            database_url=database_url,
            raw_data_dir=raw_data_dir.resolve(),
            source_snapshot_dir=source_snapshot_dir.resolve(),
            openai_model=os.getenv("PORTFOLIO_OPENAI_MODEL", APPROVED_OPENAI_MODEL),
            openai_escalation_model=os.getenv(
                "PORTFOLIO_OPENAI_ESCALATION_MODEL", APPROVED_OPENAI_ESCALATION_MODEL
            ),
            allow_external_llm=_as_bool(os.getenv("PORTFOLIO_ALLOW_EXTERNAL_LLM")),
            allow_live_public_retrieval=_as_bool(
                os.getenv("PORTFOLIO_ALLOW_LIVE_PUBLIC_RETRIEVAL")
            ),
            enable_synthetic_fixture_connector=_as_bool(
                os.getenv("PORTFOLIO_ENABLE_SYNTHETIC_FIXTURE_CONNECTOR")
            ),
            http_timeout_seconds=float(os.getenv("PORTFOLIO_HTTP_TIMEOUT_SECONDS", "10")),
            http_max_response_bytes=int(
                os.getenv("PORTFOLIO_HTTP_MAX_RESPONSE_BYTES", str(5 * 1024 * 1024))
            ),
            http_max_attempts=int(os.getenv("PORTFOLIO_HTTP_MAX_ATTEMPTS", "3")),
            openai_timeout_seconds=float(os.getenv("PORTFOLIO_OPENAI_TIMEOUT_SECONDS", "30")),
            reviewer_name=os.getenv("PORTFOLIO_REVIEWER_NAME") or None,
        )
