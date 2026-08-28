#!/usr/bin/env python3
"""Validate the dissertation's local-source and paragraph-citation contract.

The check is deliberately self-contained so it can run without adding a project
dependency.  It verifies the manifest/checksum/PDF/bibliography chain and then
requires at least two distinct, admitted citations in each substantive body
paragraph.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "sources"
CHAPTER_ROOT = ROOT / "chapters"

CITATION_RE = re.compile(
    r"\\cite(?:p|t|alp|alt|author|year|yearpar)?"
    r"(?:\s*\[[^\]]*\]){0,2}\s*\{([^}]+)\}"
)
BIBITEM_RE = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}")
BEGIN_END_RE = re.compile(r"\\(?:begin|end)\{[^}]+\}")
COMMAND_ONLY_RE = re.compile(
    r"^\s*\\(?:chapter|section|subsection|subsubsection|paragraph|label|"
    r"input|include|includegraphics|caption|centering|clearpage|newpage|"
    r"toprule|midrule|bottomrule|addcontentsline|phantomsection)\b"
)
IGNORED_ENVIRONMENTS = {
    "figure",
    "figure*",
    "table",
    "table*",
    "tabular",
    "tabularx",
    "longtable",
    "equation",
    "equation*",
    "align",
    "align*",
    "gather",
    "gather*",
    "verbatim",
    "lstlisting",
}


@dataclass(frozen=True)
class Paragraph:
    path: Path
    line: int
    text: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def strip_comment(line: str) -> str:
    """Strip an unescaped LaTeX comment while preserving escaped percent signs."""

    for index, character in enumerate(line):
        if character != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return line[:index]
    return line


def load_manifest(errors: list[str]) -> dict[str, dict[str, str]]:
    manifest_path = SOURCE_ROOT / "MANIFEST.csv"
    required = {
        "citation_key",
        "title",
        "year",
        "identifier",
        "pdf_file",
        "origin_url",
        "pages",
        "sha256",
        "admission_role",
        "verification_note",
    }
    if not manifest_path.is_file():
        errors.append(f"missing source manifest: {manifest_path}")
        return {}

    rows: dict[str, dict[str, str]] = {}
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_fields = required.difference(reader.fieldnames or [])
        if missing_fields:
            errors.append(
                "manifest is missing fields: " + ", ".join(sorted(missing_fields))
            )
        for row_number, row in enumerate(reader, start=2):
            key = (row.get("citation_key") or "").strip()
            if not key:
                errors.append(f"manifest row {row_number} has no citation key")
                continue
            if key in rows:
                errors.append(f"duplicate manifest citation key: {key}")
                continue
            rows[key] = row
    return rows


def load_checksum_file(filename: str, errors: list[str]) -> dict[str, str]:
    checksum_path = SOURCE_ROOT / filename
    if not checksum_path.is_file():
        errors.append(f"missing checksum file: {checksum_path}")
        return {}

    checksums: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        checksum_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(.+)", line)
        if not match:
            errors.append(f"invalid checksum line {line_number}: {raw_line}")
            continue
        digest, relative_path = match.groups()
        relative_path = relative_path.strip()
        if relative_path in checksums:
            errors.append(f"duplicate checksum path: {relative_path}")
            continue
        checksums[relative_path] = digest.lower()
    return checksums


def load_checksums(errors: list[str]) -> dict[str, str]:
    return load_checksum_file("SHA256SUMS", errors)


def validate_sources(
    manifest: dict[str, dict[str, str]],
    checksums: dict[str, str],
    errors: list[str],
) -> None:
    manifest_paths: set[str] = set()
    for key, row in manifest.items():
        relative = row.get("pdf_file", "").strip()
        if not relative:
            errors.append(f"{key}: manifest has no PDF path")
            continue
        if relative in manifest_paths:
            errors.append(f"PDF is assigned to multiple manifest rows: {relative}")
        manifest_paths.add(relative)

        path = SOURCE_ROOT / relative
        if not path.is_file():
            errors.append(f"{key}: local PDF is missing: {relative}")
            continue
        with path.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                errors.append(f"{key}: local file is not a PDF: {relative}")
        actual = sha256(path)
        manifest_digest = row.get("sha256", "").strip().lower()
        checksum_digest = checksums.get(relative)
        if actual != manifest_digest:
            errors.append(
                f"{key}: manifest hash mismatch for {relative}: "
                f"expected {manifest_digest}, got {actual}"
            )
        if checksum_digest is None:
            errors.append(f"{key}: no SHA256SUMS entry for {relative}")
        elif actual != checksum_digest:
            errors.append(
                f"{key}: SHA256SUMS mismatch for {relative}: "
                f"expected {checksum_digest}, got {actual}"
            )
        try:
            page_count = int(row.get("pages", ""))
            if page_count <= 0:
                raise ValueError
        except ValueError:
            errors.append(f"{key}: manifest page count is not a positive integer")
        if not row.get("origin_url", "").startswith(("https://", "http://")):
            errors.append(f"{key}: manifest origin URL is not HTTP(S)")

    extra_checksums = set(checksums).difference(manifest_paths)
    for relative in sorted(extra_checksums):
        errors.append(f"checksum has no manifest row: {relative}")


def validate_web_captures(
    manifest: dict[str, dict[str, str]], errors: list[str]
) -> int:
    capture_path = SOURCE_ROOT / "WEB_CAPTURES.csv"
    if not capture_path.is_file():
        return 0

    capture_checksums = load_checksum_file("WEB_CAPTURE_SHA256SUMS", errors)
    required = {
        "citation_key",
        "source_url",
        "captured_at",
        "html_file",
        "html_sha256",
        "pdf_file",
        "pdf_sha256",
        "pdf_pages",
        "capture_method",
        "verification_note",
    }
    seen_keys: set[str] = set()
    seen_paths: set[str] = set()
    with capture_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_fields = required.difference(reader.fieldnames or [])
        if missing_fields:
            errors.append(
                "web-capture manifest is missing fields: "
                + ", ".join(sorted(missing_fields))
            )
        for row_number, row in enumerate(reader, start=2):
            key = (row.get("citation_key") or "").strip()
            if not key:
                errors.append(f"web-capture row {row_number} has no citation key")
                continue
            if key in seen_keys:
                errors.append(f"duplicate web-capture citation key: {key}")
                continue
            seen_keys.add(key)
            admitted = manifest.get(key)
            if admitted is None:
                errors.append(f"{key}: web capture has no main-manifest row")
                continue
            if admitted.get("origin_url", "").strip() != row.get("source_url", "").strip():
                errors.append(f"{key}: web-capture URL differs from main manifest")
            if admitted.get("pdf_file", "").strip() != row.get("pdf_file", "").strip():
                errors.append(f"{key}: web-capture PDF path differs from main manifest")
            if admitted.get("sha256", "").strip() != row.get("pdf_sha256", "").strip():
                errors.append(f"{key}: web-capture PDF hash differs from main manifest")
            if admitted.get("pages", "").strip() != row.get("pdf_pages", "").strip():
                errors.append(f"{key}: web-capture page count differs from main manifest")

            for kind in ("html", "pdf"):
                relative = row.get(f"{kind}_file", "").strip()
                expected = row.get(f"{kind}_sha256", "").strip().lower()
                if not relative:
                    errors.append(f"{key}: web capture has no {kind.upper()} path")
                    continue
                if relative in seen_paths:
                    errors.append(f"web-capture file is reused: {relative}")
                seen_paths.add(relative)
                path = SOURCE_ROOT / relative
                if not path.is_file():
                    errors.append(f"{key}: web-capture file is missing: {relative}")
                    continue
                actual = sha256(path)
                if actual != expected:
                    errors.append(
                        f"{key}: web-capture {kind.upper()} hash mismatch for {relative}: "
                        f"expected {expected}, got {actual}"
                    )
                checksum_digest = capture_checksums.get(relative)
                if checksum_digest is None:
                    errors.append(f"{key}: no web checksum entry for {relative}")
                elif checksum_digest != actual:
                    errors.append(f"{key}: web checksum mismatch for {relative}")
                if kind == "pdf":
                    with path.open("rb") as pdf_handle:
                        if pdf_handle.read(5) != b"%PDF-":
                            errors.append(f"{key}: rendered capture is not a PDF")
                elif b"<html" not in path.read_bytes()[:4096].lower():
                    errors.append(f"{key}: captured source is not recognisable HTML")

    for relative in sorted(set(capture_checksums).difference(seen_paths)):
        errors.append(f"web checksum has no capture row: {relative}")
    return len(seen_keys)


def bibliography_keys(errors: list[str]) -> set[str]:
    bibliography = ROOT / "references.tex"
    if not bibliography.is_file():
        errors.append(f"missing bibliography: {bibliography}")
        return set()
    keys = BIBITEM_RE.findall(bibliography.read_text(encoding="utf-8"))
    if len(keys) != len(set(keys)):
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        errors.append("duplicate bibliography keys: " + ", ".join(duplicates))
    return set(keys)


def iter_prose_paragraphs(path: Path) -> list[Paragraph]:
    """Return blank-line-delimited prose outside non-prose LaTeX environments."""

    paragraphs: list[Paragraph] = []
    buffer: list[str] = []
    start_line = 0
    ignored_stack: list[str] = []

    def flush() -> None:
        nonlocal buffer, start_line
        if not buffer:
            return
        text = "\n".join(buffer).strip()
        buffer = []
        if not text:
            return
        paragraphs.append(Paragraph(path=path, line=start_line, text=text))

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
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
    return paragraphs


def prose_word_count(text: str) -> int:
    without_citations = CITATION_RE.sub("", text)
    without_commands = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", without_citations)
    without_braces = re.sub(r"[{}&$]", " ", without_commands)
    without_env = BEGIN_END_RE.sub(" ", without_braces)
    return len(re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", without_env))


def validate_citations(
    manifest_keys: set[str],
    bib_keys: set[str],
    strict_bibliography: bool,
    errors: list[str],
    warnings: list[str],
) -> tuple[int, int, set[str]]:
    paragraph_count = 0
    cited_keys: set[str] = set()

    for path in sorted(CHAPTER_ROOT.glob("*.tex")):
        for paragraph in iter_prose_paragraphs(path):
            word_count = prose_word_count(paragraph.text)
            if word_count < 20:
                continue
            paragraph_count += 1
            keys = {
                key.strip()
                for group in CITATION_RE.findall(paragraph.text)
                for key in group.split(",")
                if key.strip()
            }
            cited_keys.update(keys)
            location = f"{path.relative_to(ROOT)}:{paragraph.line}"
            if len(keys) < 2:
                errors.append(
                    f"{location}: substantive paragraph has {len(keys)} distinct "
                    f"citation(s); at least 2 are required"
                )
            unknown_manifest = keys.difference(manifest_keys)
            if unknown_manifest:
                errors.append(
                    f"{location}: citations without admitted local PDFs: "
                    + ", ".join(sorted(unknown_manifest))
                )
            unknown_bib = keys.difference(bib_keys)
            if unknown_bib:
                errors.append(
                    f"{location}: citations missing from bibliography: "
                    + ", ".join(sorted(unknown_bib))
                )

    manifest_missing_bib = manifest_keys.intersection(cited_keys).difference(bib_keys)
    if manifest_missing_bib:
        errors.append(
            "cited manifest keys absent from bibliography: "
            + ", ".join(sorted(manifest_missing_bib))
        )

    unused_bib = bib_keys.difference(cited_keys)
    if unused_bib:
        message = "bibliography entries not yet cited: " + ", ".join(sorted(unused_bib))
        if strict_bibliography:
            errors.append(message)
        else:
            warnings.append(message)

    return paragraph_count, len(cited_keys), cited_keys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict-bibliography",
        action="store_true",
        help="fail when an admitted bibliography entry is not cited in body prose",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    manifest = load_manifest(errors)
    checksums = load_checksums(errors)
    validate_sources(manifest, checksums, errors)
    web_capture_count = validate_web_captures(manifest, errors)
    bib_keys = bibliography_keys(errors)

    orphan_bib = bib_keys.difference(manifest)
    if orphan_bib:
        errors.append(
            "bibliography entries without admitted local PDFs: "
            + ", ".join(sorted(orphan_bib))
        )

    paragraph_count, citation_count, _ = validate_citations(
        set(manifest), bib_keys, args.strict_bibliography, errors, warnings
    )

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"FAIL: {len(errors)} error(s); {len(manifest)} local sources; "
            f"{paragraph_count} substantive body paragraph(s)",
            file=sys.stderr,
        )
        return 1

    print(
        f"PASS: {len(manifest)} local PDFs and hashes verified; "
        f"{web_capture_count} immutable web capture(s); "
        f"{paragraph_count} substantive body paragraph(s); "
        f"{citation_count} distinct cited source(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
