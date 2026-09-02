#!/usr/bin/env python3
"""Report the dissertation word count under the candidate-confirmed convention."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from check_sources import iter_prose_paragraphs, prose_word_count


ROOT = Path(__file__).resolve().parents[1]
CHAPTER_ROOT = ROOT / "chapters"
ABSTRACT = ROOT / "frontmatter" / "abstract.tex"
LOWER_BOUND = 13_500
UPPER_BOUND = 16_500
SECTION_RE = re.compile(r"^\\section\{(.+)\}\s*$")


def count_file(path: Path) -> int:
    return sum(prose_word_count(paragraph.text) for paragraph in iter_prose_paragraphs(path))


def count_sections(path: Path) -> list[dict[str, object]]:
    """Return reproducible section counts using the same prose convention as the total."""

    headings = [
        (line_number, match.group(1))
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if (match := SECTION_RE.match(line.strip()))
    ]
    paragraphs = iter_prose_paragraphs(path)
    chapter_number = int(path.name.split("_", maxsplit=1)[0])
    sections: list[dict[str, object]] = []
    for index, (start_line, title) in enumerate(headings, start=1):
        end_line = headings[index][0] if index < len(headings) else float("inf")
        selected = [
            paragraph
            for paragraph in paragraphs
            if start_line < paragraph.line < end_line
        ]
        sections.append(
            {
                "section": f"{chapter_number}.{index}",
                "title": title,
                "words": sum(prose_word_count(paragraph.text) for paragraph in selected),
                "paragraphs": len(selected),
            }
        )
    return sections


def counts() -> dict[str, object]:
    chapters = []
    for path in sorted(CHAPTER_ROOT.glob("*.tex")):
        chapters.append(
            {
                "file": path.name,
                "words": count_file(path),
                "sections": count_sections(path),
            }
        )
    main_body = sum(int(row["words"]) for row in chapters)
    return {
        "convention": (
            "Chapters 1-7 prose; excludes Abstract/front matter, table bodies and captions, "
            "figure content and captions, references, and appendices"
        ),
        "lower_bound": LOWER_BOUND,
        "target": 15_000,
        "upper_bound": UPPER_BOUND,
        "abstract_words_excluded": count_file(ABSTRACT),
        "chapters": chapters,
        "main_body_words": main_body,
        "within_range": LOWER_BOUND <= main_body <= UPPER_BOUND,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return a non-zero status when the main body is outside 13,500-16,500 words.",
    )
    args = parser.parse_args()
    result = counts()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["convention"])
        for row in result["chapters"]:
            print(f"{row['file']}: {row['words']:,}")
        print(f"Main body: {result['main_body_words']:,}")
        print(f"Target range: {LOWER_BOUND:,}-{UPPER_BOUND:,}")
        print(f"Abstract excluded: {result['abstract_words_excluded']:,}")
    return 1 if args.check and not result["within_range"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
