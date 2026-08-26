from __future__ import annotations

import re
from pathlib import Path

from portfolio_agent.bootstrap import project_root


def _markdown_files(root: Path) -> tuple[Path, ...]:
    return (
        root / "README.md",
        *sorted((root / "docs").rglob("*.md")),
        root / ".agents" / "runs" / "uk-literature-public-evidence-upgrade.md",
    )


def test_requirement_ids_are_unique_and_traceability_links_exist() -> None:
    root = project_root()
    requirements = (root / "docs" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    requirement_ids = re.findall(r"\| ((?:FR|NFR)-[A-Z]+-\d{3}) \|", requirements)
    assert len(requirement_ids) == len(set(requirement_ids))
    assert len(requirement_ids) >= 60

    traceability = (root / "docs" / "IMPLEMENTATION_TRACEABILITY.md").read_text(encoding="utf-8")
    for packet in (f"P{index:02d}" for index in range(13)):
        assert packet in traceability
    for gate in ("G2", "G3", "G4", "G5", "G6"):
        assert gate in traceability

    required_files = (
        "SOURCE_ADMISSION_REGISTER.md",
        "IMPLEMENTATION_TRACEABILITY.md",
        "adr/0006-uk-public-evidence-boundaries.md",
        "figures/generated/manifest.json",
        "figures/generated/README.md",
    )
    assert all((root / "docs" / relative).is_file() for relative in required_files)

    referenced_tests = set(re.findall(r"`(test_[a-zA-Z0-9_]+\.py)`", traceability))
    assert referenced_tests
    for filename in referenced_tests:
        assert len(list((root / "tests").rglob(filename))) == 1


def test_local_markdown_links_resolve_inside_the_repository() -> None:
    root = project_root().resolve()
    for markdown_path in _markdown_files(root):
        content = markdown_path.read_text(encoding="utf-8")
        for raw_target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
            target = raw_target.strip().strip("<>").split("#", maxsplit=1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (markdown_path.parent / target).resolve()
            assert resolved.is_relative_to(root), (
                f"{markdown_path.relative_to(root)} links outside the repository: {raw_target}"
            )
            assert resolved.exists(), (
                f"{markdown_path.relative_to(root)} has a missing link: {raw_target}"
            )
