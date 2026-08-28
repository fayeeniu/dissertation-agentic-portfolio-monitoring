```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: RE_REVIEW
  section: "3.6 Statistical and qualitative analysis"
  section_type: "methodology, statistical analysis, and qualitative analysis"
  round: 2
  scope: "Dissertation/chapters/03_methodology.tex lines 71-90, including Figure 3.3 METH-F3"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 0
    minor: 0
    optional: 0
  previous_findings:
    resolved: 2
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: none
```

# Section 3.6 independent re-review

## 1. Decision

**APPROVED.** `METH36-001` and `METH36-002` are resolved: every scoped artefact now describes the
analysis plan as current and draft, retains an explicit future `TO FREEZE` gate, and restricts the
candidate procedures to locally supported, conditional exact-paired and Wilcoxon-style methods. No
regression was identified.

## 2. Scope and evidence consulted

- The round-one Section 3.6 review and the acceptance conditions for `METH36-001` and
  `METH36-002`.
- `Dissertation/chapters/03_methodology.tex` lines 71--90: revised Section 3.6 prose, Figure 3.3
  reference and caption.
- `Dissertation/sources/CLAIM_LEDGER.md` rows `3.6-P1`--`3.6-P5`, `references.tex`,
  `sources/MANIFEST.csv` and `sources/SHA256SUMS`.
- Exact admitted pages relevant to the revisions: Demšar PDF pp. 1--9 and 20--28; DiCiccio and
  Efron PDF pp. 1--8 and 34--39; and NIST AI RMF PDF pp. 33--35. The unchanged locally admitted
  pages for Gale, Artstein and Poesio, Kapoor and Narayanan, and Pineau were retained from round one.
- `docs/EVALUATION_PROTOCOL.md`, `Dissertation/REPORT_STRUCTURE.md` and
  `docs/PROJECT_CHARTER.md` for the draft-protocol status, authorised evidence boundary and future
  analysis-freeze conditions.
- `Dissertation/exhibits/meth_f3_analysis_decision_flow.{py,svg,pdf,txt}` and
  `meth_f3_analysis_decision_flow_provenance.json`.
- Independent stale-phrase search; citation-stripped word/citation extraction; all declared
  input/output hash checks; deterministic repeat rendering; strict source checker; fresh Tectonic
  build; PDF text extraction; and fresh raster inspection of physical pages 42--44.

No material expected evidence was unavailable.

## 3. Blocking findings

None.

## 4. Prior-finding reconciliation

| Finding | Previous severity | Status | Verification |
|---|---:|---|---|
| `METH36-001` | MAJOR | RESOLVED | Section paragraph 2 now says “the current draft analysis plan”; the Figure 3.3 caption says “the current draft project evaluation plan”; the SVG description, TXT purpose statement and provenance consistently use draft/current-draft status. The chapter, visible figure, TXT and provenance retain the future `TO FREEZE` gate for the exact method and sample size, while paragraph 4 separately keeps severity definitions `TO FREEZE before scoring`. A case-insensitive search found no stale “frozen current protocol”, “frozen analysis” or “frozen project evaluation” wording in the chapter, SVG, TXT, provenance or claim ledger. |
| `METH36-002` | MAJOR | RESOLVED | Paired-permutation wording is absent from the chapter, SVG, PDF-visible figure, TXT, provenance and claim ledger. The replacement distinguishes a conditional exact paired method for binary outcomes from a conditional paired Wilcoxon-style method for non-normal time/edit outcomes and says the exact method is not selected. Demšar pp. 1--2 discuss paired binary/McNemar comparison, while pp. 5--9 define paired signed-rank and sign/binomial comparisons, exact critical values and assumption-dependent use; the wider admitted locator covers the method-selection and multiplicity context. DiCiccio and Efron support the separate finite-sample interval-coverage caution, and NIST supports documented uncertainty rather than defining either test. The prose and figure therefore no longer attribute the removed method to those sources. |

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose and alignment — meets.** The section remains exactly 350 citation-stripped words across
  five substantive paragraphs, covering flow accounting, dependence, conditional inference,
  uncertainty, multiplicity, sensitivity, qualitative analysis and unavailable authorised feedback.
- **Evidence and accuracy — meets.** The current plan is labelled draft, the exact test, interval
  method, sample size and severity definitions remain subject to stated future gates, and no D1/D2,
  C0/C3, participant-feedback or inferential result is claimed.
- **Methodological or technical validity — meets.** The candidate exact-paired and paired
  Wilcoxon-style families remain conditional on the unit, pairing, sample, distributional and
  measurement assumptions; effect sizes, uncertainty, dependence-aware aggregation, prospective
  multiplicity handling and failure-inclusive sensitivity remain explicit.
- **Critical analysis — meets.** Non-parametric is not treated as assumption-free; agreement is not
  treated as validity; purposive feedback is not converted into prevalence; and negative, null and
  regressive outcomes remain reportable.
- **Structure and coherence — meets.** The five-paragraph sequence moves cleanly from quantitative
  accounting and conditional method choice to qualitative auditability and the authorised-data hold,
  with one resolved prose reference to Figure 3.3.
- **Citations and scholarship — meets.** Every paragraph contains exactly three distinct locally
  admitted sources. The revised method-family wording fits Demšar's exact pages; the separate
  interval, qualitative, agreement, reproducibility, leakage and governance propositions retain the
  round-one verified source-page fit.
- **Academic style — meets.** The prose is concise British MSc-level writing, uses appropriately
  conditional future tense and makes no live, production, participant-benefit or causal claim.
- **Tables, figures, equations, and reproducibility — meets.** METH-F3 remains a one-page,
  vector-only conceptual figure with an SVG title/description, complete reading-order TXT
  alternative and explicit `CONCEPTUAL / NO RESULTS` and `STOP / TO FREEZE` controls. All 12 inputs
  and four outputs match their provenance declarations. The output hashes are renderer
  `4cf964d4e6fa935e4456d54f934ef73347977e140c202b8085104b4e1c74ab23`, SVG
  `7b2e009ff5dda7a75a817ed9ac289659f306fd766eb30fc60010554a56dbb9de`, PDF
  `257433a5887e62adc9f0bbe0db2fe321c57bb8201a938c096b01a67ec862f8b3` and TXT
  `7a1cdc94d7a45c93f12fe29fd349bfb7ba22407f1eac1c0245b86d9609737abf`; provenance SHA-256 is
  `68a6d0c6277c37f695e746899b9783985b3952ef610076a6ccbeab70107a6d75`. A fresh render is
  byte-identical to the declared PDF. The strict checker passes with 38 local PDFs/hashes, two
  immutable captures, 69 substantive paragraphs and 33 cited sources. Tectonic builds successfully
  with no METH-F3 warning or unresolved reference. Section 3.6 is clean on physical page 42, Figure
  3.3 is legible on page 43, and the Section 3.7 heading starts on page 44, with no clipping, overlap,
  empty inserted page or float-order defect.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated
scope and evidence available.

No non-blocking note remains. This approval is scoped to Section 3.6 and METH-F3 and does not review
or pre-approve Section 3.7.
