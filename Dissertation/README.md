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

The Abstract has passed its independent review gate. Body subsections are populated sequentially
and only marked complete after local-source validation, compilation, and an independent review.
Unwritten chapters retain headings so planned work is not presented as completed.
Candidate-controlled fields, signatures, course-regulation wording, ethics evidence, and submission
date remain visibly incomplete.

## Build

From this directory:

```bash
tectonic main.tex --outdir build
```

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
```

Official web documentation used as a source also retains the rendered HTML, the full print PDF,
the capture date, and both hashes in `sources/WEB_CAPTURES.csv` and
`sources/WEB_CAPTURE_SHA256SUMS`.

## Evidence boundary

The abstract distinguishes repository implementation, synthetic engineering evaluation, protocol-
only work, and evidence still required. In particular, it does not represent the implemented
public-web company-research path as empirically validated: no live company/model research run,
frozen public-company comparison, manual baseline, or authorised human study has been completed.
The bounded path remains an engineering case study rather than a fourth research question.
