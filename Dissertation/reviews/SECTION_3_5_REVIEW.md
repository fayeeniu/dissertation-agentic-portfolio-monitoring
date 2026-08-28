```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: SECTION_REVIEW
  section: "3.5 Measures and denominator rules"
  section_type: "methodology, measurement, and denominator design"
  round: 1
  scope: "Dissertation/chapters/03_methodology.tex lines 58-70, including Table 3.3 METH-T3"
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

# Section 3.5 independent review

## 1. Decision

**APPROVED.** The section defines a prospective measurement contract with explicit units,
denominators, dependence, null rules and evidence holds. It does not overstate the narrower current
D0 evaluator as implementing the complete planned protocol. Table 3.3 accurately expands the
contract across two continuous pages, is accessible and provenance-verified, and completes before
Section 3.6 begins.

## 2. Scope and evidence consulted

- `Dissertation/chapters/03_methodology.tex` lines 58--70: Section 3.5 prose and METH-T3 inclusion.
- `Dissertation/REPORT_STRUCTURE.md` and `Dissertation/sources/CLAIM_LEDGER.md` rows
  `3.5-P1`--`3.5-P5` for the section allocation, claim contract and exact page locators.
- `Dissertation/references.tex`, `Dissertation/sources/MANIFEST.csv` and
  `Dissertation/sources/SHA256SUMS` for admission and checksum bindings.
- Exact admitted pages: Artstein and Poesio pp. 2--8 and 35--37; Pineau et al. pp. 1--4 and 9--13;
  NIST AI RMF pp. 33--35; Gao et al. ALCE pp. 3--5, 8--10 and 15--17; Nikiforova et al.
  pp. 2--8 and 12--17; Gebru et al. pp. 4--7; Mitchell et al. pp. 1--5; and Amershi et al.
  pp. 2--8.
- `docs/EVALUATION_PROTOCOL.md`, `docs/DATA_DICTIONARY.md`, the current D0 manifest/output,
  `src/portfolio_agent/evaluation.py` and `tests/unit/test_evaluation.py` for the planned-versus-
  implemented boundary, formulas, null states and current synthetic evidence.
- `Dissertation/exhibits/meth_t3_metric_denominator_matrix.tex`, `.txt` and `_provenance.json`.
- Citation-stripped word/citation extraction; all provenance input/output hash checks; a focused D0
  evaluator test run; strict source checker; fresh multi-pass Tectonic build; reference/list-of-tables
  inspection; and fresh raster inspection of physical pages 39--42.

No material expected evidence was unavailable.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose and alignment — meets.** The section performs the planned measures-and-denominators job
  in exactly 399 citation-stripped words across five substantive paragraphs. It distinguishes field,
  claim, report, workflow and reviewer units, defines a field as a company--metric--period
  observation, preserves within-company/report dependence and pre-populates no acceptance
  threshold.
- **Evidence and accuracy — meets.** Claim precision, claim recall, F1, unsupported-claim rate,
  claim-support rate and contradiction-detection recall reproduce the project protocol. F1 is used
  only when precision and recall are defined and their sum is positive. A zero denominator or no
  eligible labelled cases yields null/N/A with a reason, never an invented measured zero.
- **Methodological or technical validity — meets.** The prose and matrix keep extraction,
  normalisation and missing-state, identity/acquisition/temporal/source-quality, provenance,
  reporting, efficiency, reliability and usability as distinct measurement families. Unfrozen
  eligible sets, aggregation rules, severity handling, repeat sets and human instruments remain
  explicitly `TO FREEZE`. Claims and fields are clustered at report/company level rather than
  treated as independent observations.
- **Efficiency, cost and human measures — meets.** Active human minutes are separated from elapsed
  wall-clock time; machine stages, attempts, retries, failures, tokens and edit events remain
  separately observable. Monetary cost requires the official price effective on the execution
  date plus the exact formula, units, currency and token quantities; otherwise it is null. Usability
  belongs only to separately authorised C3 work under a frozen instrument, and current D0
  reviewer/event observations remain null.
- **Implementation boundary — meets.** The current synthetic D0 evaluator implements a narrower
  subset for C1/C2 and keeps C0, C3, reviewer, event and several field/report layers null. Its present
  `contradiction_accuracy` output and simplified synthetic provenance calculation are not relabelled
  as the planned contradiction-recall and final provenance-completeness specifications. The section
  and matrix consistently say conceptual/non-empirical and claim neither complete implementation
  nor an authorised empirical result. Eight focused evaluator tests pass.
- **Critical analysis — meets.** Citation presence is not equated with claim support, provenance
  completeness is not equated with truth, missingness is not converted to zero, and no composite
  context-free quality score is invented. The prose also separates an implemented review interface
  from measured reviewer benefit.
- **Citations and scholarship — meets.** The five substantive paragraphs contain 3, 2, 3, 3 and 3
  distinct locally admitted citations respectively. Every scholarly proposition fits the inspected
  pages: the literature motivates documented, task-specific, reproducible and human-aware
  measurement, while the project protocol supplies the project-specific formulas and denominator
  choices. No external benchmark value or literature threshold is transferred into the study.
- **Academic style — meets.** The prose is precise British academic English at MSc level. It makes
  no invented sample size, threshold, condition ranking, time saving, cost saving, usability,
  causal-benefit, live-system or production claim.
- **Tables, equations and reproducibility — meets.** Table 3.3's 19 rows, formulae, caption, label,
  continuation header, source note and current-status hold agree with the prose and complete TXT
  alternative. All 11 declared inputs and both outputs match; TeX SHA-256 is
  `ed4f865de4e4e3702e0f22e148386bd35609c352773684697ea14a08ac5fbe49`, TXT SHA-256 is
  `3cd3b182b27fbc670719c7221a4105850807db9441dda64674de926db79ecdca`, and provenance SHA-256 is
  `24c869c601d2f03d20d7396439c54d93a1074724ec829996cc6b986c4a6acd66`. Provenance is non-circular
  and does not declare the mutable claim ledger as an input. Meaning does not depend on colour.
- **Build, counter and placement — meets.** The strict source gate passes with 37 local PDFs and
  hashes, two immutable captures, 64 substantive paragraphs and 30 cited sources. The fresh build
  resolves the prose reference and lists Table 3.3 exactly once. Four first-pass longtable underfull
  alignment diagnostics disappeared on the required later passes and correspond to no final layout
  defect. Section 3.5 renders cleanly on physical page 39, the two continuous halves of Table 3.3 on
  pages 40--41, and Section 3.6 begins on page 42. The repeated header, continuation marker and
  explicit table-counter correction preserve the Table 3.3 identity without clipping, overlap,
  blank pages or float-order error.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated
scope and evidence available.

No non-blocking note remains. This approval does not pre-approve Section 3.6.
