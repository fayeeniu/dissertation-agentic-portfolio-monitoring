#!/usr/bin/env python3
"""Check that every dissertation paragraph matches its source-verification row.

The source checker proves that cited PDFs exist. This companion check proves that
the current paragraph-level citation sets still match the page-level verification
ledger after editing.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from check_sources import (
    CHAPTER_ROOT,
    CITATION_RE,
    COMMAND_ONLY_RE,
    IGNORED_ENVIRONMENTS,
    ROOT,
    prose_word_count,
    strip_comment,
)

LEDGER_PATH = ROOT / "sources" / "CLAIM_LEDGER.md"
SECTION_RE = re.compile(r"^\s*\\section\{")
LEDGER_ID_RE = re.compile(r"^`([1-8]\.\d+-P\d+)`$")


@dataclass(frozen=True)
class ParagraphRecord:
    paragraph_id: str
    path: Path
    line: int
    citations: frozenset[str]


@dataclass(frozen=True)
class LedgerRecord:
    paragraph_id: str
    citations: frozenset[str]
    page_evidence: str
    status: str


def chapter_number(path: Path) -> int:
    match = re.match(r"(\d+)_", path.name)
    if not match:
        raise ValueError(f"cannot derive chapter number from {path.name}")
    return int(match.group(1))


def chapter_paragraphs(path: Path) -> list[ParagraphRecord]:
    """Return substantive prose paragraphs with stable section paragraph IDs."""

    chapter = chapter_number(path)
    section = 0
    paragraph_counts: dict[int, int] = {}
    records: list[ParagraphRecord] = []
    buffer: list[str] = []
    start_line = 0
    ignored_stack: list[str] = []

    def flush() -> None:
        nonlocal buffer, start_line
        if not buffer:
            return
        text = "\n".join(buffer).strip()
        buffer = []
        if not text or prose_word_count(text) < 20:
            return
        if section == 0:
            raise ValueError(f"substantive prose before first section in {path}:{start_line}")
        paragraph_counts[section] = paragraph_counts.get(section, 0) + 1
        paragraph_id = f"{chapter}.{section}-P{paragraph_counts[section]}"
        keys = {
            key.strip()
            for group in CITATION_RE.findall(text)
            for key in group.split(",")
            if key.strip()
        }
        records.append(
            ParagraphRecord(
                paragraph_id=paragraph_id,
                path=path,
                line=start_line,
                citations=frozenset(keys),
            )
        )

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = strip_comment(raw_line).rstrip()
        begins = re.findall(r"\\begin\{([^}]+)\}", line)
        ends = re.findall(r"\\end\{([^}]+)\}", line)

        if ignored_stack:
            for environment in begins:
                if environment in IGNORED_ENVIRONMENTS:
                    ignored_stack.append(environment)
            for environment in ends:
                if environment in ignored_stack:
                    reverse_index = ignored_stack[::-1].index(environment)
                    del ignored_stack[len(ignored_stack) - reverse_index - 1 :]
            continue

        ignored_begin = next(
            (environment for environment in begins if environment in IGNORED_ENVIRONMENTS),
            None,
        )
        if ignored_begin:
            flush()
            if ignored_begin not in ends:
                ignored_stack.append(ignored_begin)
            continue

        if SECTION_RE.match(line):
            flush()
            section += 1
            continue
        if not line.strip():
            flush()
            continue
        if COMMAND_ONLY_RE.match(line):
            flush()
            continue
        if not buffer:
            start_line = line_number
        buffer.append(line)

    flush()
    return records


def load_ledger() -> dict[str, LedgerRecord]:
    records: dict[str, LedgerRecord] = {}
    for line_number, line in enumerate(
        LEDGER_PATH.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.startswith("| `"):
            continue
        columns = [column.strip() for column in line.split("|")]
        if len(columns) < 7:
            continue
        match = LEDGER_ID_RE.fullmatch(columns[1])
        if not match:
            continue
        paragraph_id = match.group(1)
        citations = frozenset(re.findall(r"`([^`]+)`", columns[3]))
        record = LedgerRecord(
            paragraph_id=paragraph_id,
            citations=citations,
            page_evidence=columns[4],
            status=columns[5],
        )
        if paragraph_id in records:
            raise ValueError(f"duplicate ledger row {paragraph_id} at line {line_number}")
        records[paragraph_id] = record
    return records


def main() -> int:
    errors: list[str] = []
    actual: dict[str, ParagraphRecord] = {}
    for path in sorted(CHAPTER_ROOT.glob("*.tex")):
        for record in chapter_paragraphs(path):
            if record.paragraph_id in actual:
                errors.append(f"duplicate manuscript paragraph ID: {record.paragraph_id}")
            actual[record.paragraph_id] = record

    ledger = load_ledger()
    for paragraph_id in sorted(set(actual).difference(ledger)):
        record = actual[paragraph_id]
        errors.append(
            f"{paragraph_id}: manuscript paragraph has no ledger row "
            f"({record.path.relative_to(ROOT)}:{record.line})"
        )
    for paragraph_id in sorted(set(ledger).difference(actual)):
        errors.append(f"{paragraph_id}: ledger row has no current manuscript paragraph")

    for paragraph_id in sorted(set(actual).intersection(ledger)):
        paragraph = actual[paragraph_id]
        evidence = ledger[paragraph_id]
        if paragraph.citations != evidence.citations:
            errors.append(
                f"{paragraph_id}: citation drift at "
                f"{paragraph.path.relative_to(ROOT)}:{paragraph.line}; "
                f"manuscript={sorted(paragraph.citations)}, "
                f"ledger={sorted(evidence.citations)}"
            )
        if not evidence.citations:
            errors.append(f"{paragraph_id}: ledger row has no citation keys")
        for key in evidence.citations:
            if f"`{key}`" not in evidence.page_evidence:
                errors.append(f"{paragraph_id}: page evidence does not name {key}")
        if "Verified" not in evidence.status and "verified" not in evidence.status:
            errors.append(f"{paragraph_id}: ledger status is not verified")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAIL: {len(errors)} claim-ledger error(s)", file=sys.stderr)
        return 1

    print(
        f"PASS: {len(actual)} substantive manuscript paragraphs match "
        "page-level citation evidence rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
