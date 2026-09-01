#!/usr/bin/env python3
"""Check the dissertation's Harvard WMS citation and reference-list rules."""

from __future__ import annotations

import re
import sys

from check_sources import BIBITEM_WITH_LABEL_RE, ROOT, bibliography_sort_key

REFERENCES_PATH = ROOT / "references.tex"
STYLE_PATH = ROOT / "style.tex"
AUTHOR_YEAR_RE = re.compile(r"^.+\((?:(?:19|20)\d{2}[a-z]?|n\.d\.(?:-[a-z])?)\)$")
CORPORATE_AUTHORS_WITH_AND = {
    "Central Digital and Data Office",
    "National Institute of Standards and Technology",
}


def main() -> int:
    errors: list[str] = []
    references = REFERENCES_PATH.read_text(encoding="utf-8")
    style = STYLE_PATH.read_text(encoding="utf-8")
    labelled_entries = BIBITEM_WITH_LABEL_RE.findall(references)

    if not re.search(r"\\usepackage\[[^\]]*authoryear[^\]]*round[^\]]*\]\{natbib\}", style):
        errors.append("natbib must use author-year citations in round brackets")
    if not re.search(r"\\setcitestyle\{[^}]*round", style):
        errors.append("the active citation style must explicitly use round brackets")

    labels = [label for label, _ in labelled_entries]
    if any(not AUTHOR_YEAR_RE.fullmatch(label) for label in labels):
        for label in labels:
            if not AUTHOR_YEAR_RE.fullmatch(label):
                errors.append(f"bibliography display label is not author-year: {label!r}")
    if labels != sorted(labels, key=bibliography_sort_key):
        errors.append("reference list is not in A-Z order")

    for label in labels:
        author_part = label.rsplit("(", maxsplit=1)[0]
        if " and " in author_part and author_part not in CORPORATE_AUTHORS_WITH_AND:
            errors.append(f"use '&' rather than 'and' in the citation label: {label!r}")

    entries = re.split(r"(?=\\bibitem)", references)
    for entry in entries:
        match = re.match(r"\\bibitem\[([^\]]+)\]\{([^}]+)\}", entry)
        if match is None:
            continue
        label, key = match.groups()
        year_match = re.search(r"\((?:19|20)\d{2}[a-z]?|n\.d\.(?:-[a-z])?\)\.", entry)
        if year_match is None:
            errors.append(f"{key}: reference body has no matching author-year date")
        author_text = entry[match.end() : year_match.start()] if year_match else ""
        if "," in author_text and r"\&" not in author_text:
            errors.append(f"{key}: multi-author reference must use '&' before the final author")
        if "Available at:" in entry or "(accessed" in entry:
            errors.append(f"{key}: web reference does not use Harvard WMS wording")
        if "Available from:" in entry and not re.search(
            r"\(Accessed\s+\d{1,2}\s+[A-Z][a-z]+\s+\d{4}\)\.", entry
        ):
            errors.append(f"{key}: online source has no correctly formed access date")
        if label.startswith("OpenAI(") and "n.d.-" not in label:
            errors.append(f"{key}: undated OpenAI page must use n.d. with a suffix")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAIL: {len(errors)} Harvard error(s)", file=sys.stderr)
        return 1

    print(
        f"PASS: {len(labelled_entries)} references use round author-date Harvard WMS "
        "labels, '&', A-Z order and dated online-source wording"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
