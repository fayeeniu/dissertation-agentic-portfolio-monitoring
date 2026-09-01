# Dissertation

This directory contains the section-gated LaTeX draft for Faye Niu's WMG MSc Applied Artificial
Intelligence dissertation. The opening sequence follows the supplied WMG template:

1. Project Submission Pro-Forma;
2. title page;
3. Declaration;
4. Abstract; and
5. Table of Contents;
6. List of tables;
7. List of figures; and
8. Glossary and Acronyms.

Acknowledgements remain omitted because they are optional. The lists are generated from LaTeX
caption records and the glossary is deliberately maintained as a plain front-matter table, avoiding
an additional indexing program. `references.tex` provides a natbib-compatible author-year
`thebibliography` mechanism; only verified sources should be added as `\bibitem` entries.

The current supervisor-feedback revision is pending a fresh independent review gate. Body
subsections are populated and are only approved after local-source validation, compilation and that
review. Planned work remains clearly separated from completed implementation and evaluation.
Candidate-controlled fields, signatures, course-regulation wording, ethics evidence, and submission
date remain visibly incomplete.

## Build

From this directory:

```bash
./scripts/render_mermaid_figures.sh
python3 scripts/check_mermaid_figures.py
tectonic main.tex --outdir build
```

`render_mermaid_figures.sh` rebuilds every figure from source in one step: it expands
`exhibits/figure_palette.json` into the shared Mermaid config and stylesheet, renders each of the
twelve `.mmd` sources to an SVG vector master and the PNG the LaTeX build consumes, and rebinds
`exhibits/MERMAID_MANIFEST.csv`. Nine renders are referenced by the manuscript and three are
retained as review history. Every figure shares one print-safe, colour-blind-safe palette; colour
never appears in a figure source, only semantic `fx-*` roles. The renderer is pinned to
`@mermaid-js/mermaid-cli@11.16.0`, and the manifest binds every source, render and shared render
input by SHA-256. See `exhibits/VISUALISATION_MIGRATION.md` for the palette and pipeline.
Superseded Python and hand-authored PDF figure artefacts are retained only as historical review
evidence and are not referenced by the manuscript.

The reviewed export is copied to
`WMG_MSc_Applied_AI_Dissertation_Abstract_Draft.pdf` after compilation and visual inspection.

The expert/reviewer feedback loop and finding reconciliation are recorded in
`reviews/REVIEW_LOG.md` and `audit/SECTION_LEDGER.md`.

## Evidence checks

Every cited source must resolve through `sources/MANIFEST.csv` and `sources/SHA256SUMS` to a
readable local PDF. Every substantive body paragraph must contain at least two distinct,
claim-relevant citations. Run the incremental gate with:

```bash
python3 scripts/check_sources.py
```

The final manuscript gate also rejects bibliography entries that are not used:

```bash
python3 scripts/check_sources.py --strict-bibliography
python3 scripts/check_claim_ledger.py
python3 scripts/check_harvard.py
python3 scripts/check_language.py
python3 scripts/word_count.py --check
```

The word-count command applies the candidate-confirmed 15,000-word target with a ten-per-cent
tolerance. It counts Chapters 1--8 prose and excludes the Abstract and other front matter, tables,
figures, references and appendices. Its per-chapter output is the source for `REPORT_STRUCTURE.md`
and the section ledger; authenticated WMG instructions take precedence if they define an exclusion
differently.

Official web documentation used as a source also retains the rendered HTML, the full print PDF,
the capture date, and both hashes in `sources/WEB_CAPTURES.csv` and
`sources/WEB_CAPTURE_SHA256SUMS`.

## Evidence boundary

The abstract distinguishes repository implementation, synthetic engineering evaluation, protocol-
only work, and evidence still required. In particular, it does not represent the implemented
public-web company-research path as empirically validated: no live company/model research run,
frozen public-company comparison, manual baseline, or authorised human study has been completed.
The bounded path remains an engineering case study rather than a fourth research question.
