from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    project_root: Path
    database_url: str
    raw_data_dir: Path
    openai_model: str = "gpt-5.4-mini"
    openai_escalation_model: str = "gpt-5.4"
    allow_external_llm: bool = False

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> Settings:
        root = (project_root or Path.cwd()).resolve()
        database_url = os.getenv(
            "PORTFOLIO_DATABASE_URL", f"sqlite:///{root / 'var' / 'portfolio.db'}"
        )
        raw_setting = Path(os.getenv("PORTFOLIO_RAW_DATA_DIR", "var/raw"))
        raw_data_dir = raw_setting if raw_setting.is_absolute() else root / raw_setting
        return cls(
            project_root=root,
            database_url=database_url,
            raw_data_dir=raw_data_dir.resolve(),
            openai_model=os.getenv("PORTFOLIO_OPENAI_MODEL", "gpt-5.4-mini"),
            openai_escalation_model=os.getenv("PORTFOLIO_OPENAI_ESCALATION_MODEL", "gpt-5.4"),
            allow_external_llm=_as_bool(os.getenv("PORTFOLIO_ALLOW_EXTERNAL_LLM")),
        )
