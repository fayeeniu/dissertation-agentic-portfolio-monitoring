#!/usr/bin/env python3
"""Check the dissertation's no-em-dash and British-English rules."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_DIRS = (ROOT / "frontmatter", ROOT / "chapters", ROOT / "exhibits")
SUFFIXES = {".tex", ".mmd", ".txt"}

AMERICAN_SPELLINGS = {
    "behavior": "behaviour",
    "behaviors": "behaviours",
    "behavioral": "behavioural",
    "analyze": "analyse",
    "analyzed": "analysed",
    "analyzes": "analyses",
    "analyzing": "analysing",
    "labeling": "labelling",
    "normalize": "normalise",
    "normalized": "normalised",
    "normalizes": "normalises",
    "normalizing": "normalising",
    "normalization": "normalisation",
    "organization": "organisation",
    "organizations": "organisations",
    "organize": "organise",
    "organized": "organised",
    "organizing": "organising",
    "modeling": "modelling",
    "artifact": "artefact",
    "artifacts": "artefacts",
    "finalize": "finalise",
    "finalized": "finalised",
    "finalizing": "finalising",
    "finalization": "finalisation",
}
AMERICAN_RE = re.compile(
    r"\b(" + "|".join(map(re.escape, AMERICAN_SPELLINGS)) + r")\b",
    re.IGNORECASE,
)
SQUARE_AUTHOR_DATE_RE = re.compile(
    r"\[(?:[A-Z][A-Za-z'`{}\\-]+(?:\s+(?:et al\.|&|and)\s+[^,\]]+)?)"
    r",?\s+(?:19|20)\d{2}[a-z]?\]"
)


def visible_line(path: Path, line: str) -> str:
    """Remove syntax-only fragments that can resemble prose spellings."""

    if path.suffix == ".mmd" and line.lstrip().startswith(("classDef ", "class ")):
        return ""
    if path.suffix == ".tex":
        line = re.sub(r"\\(?:begin|end)\{[^}]+\}", "", line)
        line = re.sub(r"\\(?:definecolor|color|colorbox)\b", "", line)
    return line


def main() -> int:
    errors: list[str] = []
    files = sorted(
        path
        for directory in MANUSCRIPT_DIRS
        for path in directory.rglob("*")
        if path.is_file() and path.suffix in SUFFIXES
    )

    for path in files:
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            location = f"{path.relative_to(ROOT)}:{line_number}"
            if "—" in raw_line or r"\textemdash" in raw_line or r"\emdash" in raw_line:
                errors.append(f"{location}: em dash is not allowed")
            if path.suffix == ".tex" and "---" in raw_line:
                errors.append(f"{location}: LaTeX triple hyphen renders as an em dash")

            line = visible_line(path, raw_line)
            for match in AMERICAN_RE.finditer(line):
                word = match.group(1)
                replacement = AMERICAN_SPELLINGS[word.casefold()]
                errors.append(f"{location}: use British spelling {replacement!r}, not {word!r}")
            if SQUARE_AUTHOR_DATE_RE.search(line):
                errors.append(
                    f"{location}: use round Harvard author-date citations, not square brackets"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAIL: {len(errors)} language error(s)", file=sys.stderr)
        return 1

    print(
        f"PASS: {len(files)} manuscript source file(s) use British spellings, "
        "contain no em dashes and contain no square author-date citations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
