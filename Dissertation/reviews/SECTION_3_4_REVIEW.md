```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: SECTION_REVIEW
  section: "3.4 Gold-reference construction and source-access parity"
  section_type: "methodology, reference construction, and source parity"
  round: 1
  scope: "Dissertation/chapters/03_methodology.tex lines 47-57, including Table 3.2 METH-T2"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 0
    minor: 0
    optional: 0
  previous_findings:
    resolved: 0
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: none
```

# Section 3.4 independent review

## 1. Decision

**APPROVED.** The section defines a prospective, independently labelled and adjudicated reference
process with source-access and temporal parity, while preserving the distinction between reliability
and validity and the current absence of a frozen gold reference. Table 3.2 accurately operationalises
the method, is accessible and provenance-verified, and precedes Section 3.5 without a layout defect.

## 2. Scope and evidence consulted

- `Dissertation/chapters/03_methodology.tex` lines 47--57: Section 3.4 prose and METH-T2 inclusion.
- `Dissertation/REPORT_STRUCTURE.md`: the 300-word Section 3.4 allocation, two-reviewer method,
  adjudication, source-access parity, inaccessible-source states and exact-span policy.
- `Dissertation/sources/CLAIM_LEDGER.md` rows `3.4-P1`--`3.4-P4`, `references.tex`,
  `sources/MANIFEST.csv` and `sources/SHA256SUMS`.
- Exact admitted source pages: Artstein and Poesio pp. 2--8, 16--23 and 35--37; Gao et al. ALCE
  pp. 3--5, 8--10 and 15--17; Pineau et al. pp. 1--5 and 9--13; Gebru et al. pp. 2 and 4--10; and
  NIST AI RMF pp. 32--35.
- `docs/EVALUATION_PROTOCOL.md`, `docs/DATA_DICTIONARY.md`, `docs/PROJECT_CHARTER.md`,
  `fixtures/evaluation_manifest.json` and `var/evaluation/smoke.json` for the gold-reference steps,
  label dimensions, source/time parity, current held execution state and the separate synthetic D0
  mechanism-evidence boundary.
- `Dissertation/exhibits/meth_t2_reference_parity_matrix.tex`, `.txt` and `_provenance.json`.
- Citation-stripped word/citation extraction; Artstein metadata and PDF-page-count inspection; all
  provenance input/output hash checks; strict source checker; fresh Tectonic build; cross-reference
  extraction; and fresh raster inspection of physical pages 37--39.

No material expected evidence was unavailable.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose and alignment — meets.** The section performs the planned reference-construction and
  source-parity job in exactly 300 citation-stripped words across four substantive paragraphs.
- **Evidence and accuracy — meets.** Two authorised domain reviewers independently receive the same
  frozen bundle and label canonical value or typed missing state, evidence eligibility,
  sourceability, period, claim support and report-section requirement. These project-specific fields
  reproduce the protocol and data dictionary rather than being attributed to the literature.
- **Methodological or technical validity — meets.** Raw agreement precedes adjudication; a
  chance-corrected statistic is conditional on the sample, label scale, category distribution and
  task-design assumptions; no universal threshold is imported; and adjudication reasons and
  codebook changes are versioned before the reference and manifest are frozen for scoring. Manual
  and system outputs remain evaluated conditions rather than truth, and scoring is blind to
  condition where practicable. Artstein and Poesio directly support the reliability/validity
  distinction, independent coding, prevalence and bias limitations, task-appropriate coefficient
  choice and rejection of a single cutoff for all purposes.
- **Critical analysis — meets.** The section does not equate reviewer agreement, adjudication or a
  cited source with truth. It records inaccessible, deleted, paywalled, login-only and
  later-published states; separates publication/availability, retrieval and cutoff times; excludes
  post-cutoff evidence from historical support; and requires an exact locator or span and source
  policy. Gao et al. support separate completeness and passage-support checks, while Gebru et al.
  and Pineau et al. support documented external-resource, time, version and reproducibility limits.
- **Evidence-status boundary — meets.** The gold reference has not been constructed or frozen, so
  the stated C0--C3 scores are unavailable in the planned common-reference comparison and no such
  empirical outcome is claimed. This does not relabel the explicitly separate C1/C2 D0 synthetic
  fixture measurements in Sections 3.1--3.3 as authorised empirical findings; C0 and human C3
  remain null/held in the current D0 artefact.
- **Structure and coherence — meets.** The argument moves from codebook and independent labels,
  through agreement/adjudication and source parity, to the frozen-record integration and current
  evidence hold. The prose reference resolves to Table 3.2.
- **Citations and scholarship — meets.** The four substantive paragraphs contain 2, 3, 3 and 4
  distinct locally admitted citations respectively, and every scholarly proposition fits the exact
  inspected pages. The new Artstein entry accurately records authors, year, title, journal,
  volume/issue, pp. 555--596 and DOI; its 42-page local PDF and manifest/checksum share SHA-256
  `1729af43712921de3857555972c6a3376d66bcba2474f81a32cddf4f98aef058`.
- **Academic style — meets.** The prose is precise British academic English at MSc level and makes
  no invented agreement value, threshold, sample size, condition ranking, human benefit or
  live/production claim.
- **Tables, figures, equations, and reproducibility — meets.** Table 3.2's eight stages, caption,
  label, source note and current-status hold agree with the prose, full TXT alternative and
  provenance. Meaning does not depend on colour. All ten declared inputs and both outputs match;
  the provenance SHA-256 is
  `f7ae8e388cc42da78e74bebab1fc498c5a558daec2f77758303301de6c0755d5`, and it does not declare
  the mutable claim ledger as an input. The strict source gate passes with 37 local PDFs/hashes, two
  immutable captures, 59 substantive paragraphs and 30 cited sources. The fresh build has no
  METH-T2 warning or unresolved reference. Section 3.4 renders cleanly on physical page 37, Table
  3.2 on page 38 and Section 3.5 begins on page 39, with no clipping, overlap, empty page or
  float-order defect.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated
scope and evidence available.

No non-blocking note remains. This approval does not pre-approve Section 3.5.
