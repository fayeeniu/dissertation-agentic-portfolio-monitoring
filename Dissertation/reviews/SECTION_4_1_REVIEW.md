```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: RE_REVIEW
  section: "4.1 Requirements and trust boundaries"
  section_type: "system design and implementation"
  round: 2
  scope: "Dissertation/chapters/04_system_design.tex lines 2-10, including Table 4.1 SYS-T1"
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

# Section 4.1 independent re-review

## 1. Decision

**APPROVED.** `SYS41-001` and `SYS41-002` are resolved: SYS-T1 now binds every declared input
and output, the visible requirement identifier agrees with the requirements contract and accessible
alternative, and no semantic or rendered-layout regression was found.

## 2. Scope and evidence consulted

- The round-one review and acceptance conditions for `SYS41-001` and `SYS41-002`.
- `Dissertation/chapters/04_system_design.tex` lines 2--10, claim-ledger rows
  `4.1-P1`--`4.1-P3`, and the Section 4.1 audit-ledger row.
- `docs/SOURCE_ADMISSION_REGISTER.md`, `docs/REQUIREMENTS.md`,
  `src/portfolio_agent/config.py`, `tests/integration/test_company_research.py`, and
  `Dissertation/exhibits/sys_t1_requirements_trust_boundary_matrix.{tex,txt}` plus its provenance
  JSON.
- Independent SHA-256 verification of all 27 declared inputs, both declared outputs and the
  provenance file itself; a check for invalid standalone `RES-001` occurrences; exact word and
  citation-contract regression checks.
- Eleven selected boundary, intake, external-model, company-research and approval/export tests;
  the strict source checker; a fresh Tectonic build; PDF text-order checks; and fresh raster
  inspection of physical pages 47--50.

The re-review was restricted to the two corrections, dependent ledgers and regression checks.
Section 4.2 content was not reviewed.

## 3. Blocking findings

None.

## 4. Previous-finding reconciliation

| Finding | Prior severity | Status | Resolution evidence |
|---|---:|---|---|
| `SYS41-001` | MAJOR | **RESOLVED** | Provenance SHA-256 is `fded441c445df3d6742f0a0e507a97aacf10aba4477ab95455ec4b383818d4cd`. All 27 declared inputs and both outputs match. The three formerly stale bindings now match SOURCE_ADMISSION_REGISTER `34f8f3ba2e8cb33f58beaf24ad265e5031f34ba5a3afb703cc8ea6cbda01b49d`, `config.py` `5c9e1824b18f5d3f738c1c14d8bd163077abff3ae920b98f0018a8b4b3c3a856`, and `test_company_research.py` `4250792d2f7d433f9e832e6a8336b7532e2faa15c23ae53cfb363dafc4b08570`. Claim-ledger row `4.1-P3` records the same hashes and match counts. |
| `SYS41-002` | MINOR | **RESOLVED** | SYS-T1 TeX, TXT, `docs/REQUIREMENTS.md` and rendered physical page 48 consistently use `NFR-RES-001`; no invalid standalone `RES-001` remains. The refreshed TeX SHA-256 is `ba6c12e0d46653031625cf389ec652dd5f0a9bfed43d95f1b78af14df038033a`, while the unchanged TXT SHA-256 is `322746127c1c803a35581fd27b9fd3cbe1b40d278bb1c3b49d8dcfc0507a1934`. |

No partially resolved, unresolved, waived or regression findings remain.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose and alignment — meets.** The section remains exactly 250 citation-stripped words in
  three substantive paragraphs, with three distinct admitted local citations in each paragraph.
- **Evidence and accuracy — meets.** The unchanged prose and table preserve the accepted separation
  among implemented local controls, the synthetic provider seam, live-unrun public-company
  research, G2-held direct registry retrieval and future empirical work. No production, compliance,
  reviewer-benefit, live-performance or investment-quality claim has been introduced.
- **Technical validity — meets.** The corrected provenance binds the current source register,
  runtime configuration and company-research test evidence. The 11 selected tests pass; the sole
  diagnostic is the pre-existing Starlette TestClient deprecation warning.
- **Citations and scholarship — meets.** The prose preserves the accepted exact-page source fit and
  keeps repository-specific requirements grounded in project contracts rather than attributing
  them to the literature.
- **Academic style and coherence — meets.** The unchanged text remains calibrated British
  MSc-level writing with explicit non-goals and evidence-status boundaries.
- **Table integrity and accessibility — meets.** SYS-T1's TeX, TXT and provenance hashes match the
  accepted round-two values; all 27 inputs and both outputs verify. The visible table and linear TXT
  alternative agree, including `NFR-RES-001`, status labels and the non-empirical source note.
- **Validation and placement — meets.** The strict source gate passes with 38 local PDFs and hashes,
  two immutable captures, 76 substantive paragraphs and 34 distinct cited sources. Tectonic builds
  the 66-page A4 report successfully. Physical page 47 contains the Section 4.1 prose, pages 48--49
  contain the complete two-page Table 4.1, and Section 4.2 begins on page 50. Fresh raster inspection
  found no blank page, clipping, overlap, unreadable row or float-order regression. The two narrow-
  header and five longtable measurement-pass underfull-box diagnostics have no material rendered
  impact.

## 7. Handoff

Section 4.1 and SYS-T1 are approved at round two. No further Section 4.1 revision or reviewer
handoff is required. This approval does not review or pre-approve Section 4.2.
