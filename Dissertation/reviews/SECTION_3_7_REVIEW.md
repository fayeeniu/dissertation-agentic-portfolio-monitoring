```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: RE_REVIEW
  section: "3.7 Ethics, leakage prevention, and reproducibility"
  section_type: "methodology, ethics, governance, leakage control, and reproducibility"
  round: 2
  scope: "Dissertation/chapters/03_methodology.tex lines 91-101, including Table 3.4 METH-T4"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 0
    minor: 0
    optional: 0
  previous_findings:
    resolved: 1
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: none
```

# Section 3.7 independent re-review

## 1. Decision

**APPROVED.** `METH37-001` is resolved: METH-T4 now binds the current source-admission and
requirements artefacts, every declared input and output matches, and no semantic or rendered-layout
regression was found.

## 2. Scope and evidence consulted

- The round-one review and its acceptance condition for `METH37-001`.
- `Dissertation/chapters/03_methodology.tex` lines 91--101, claim-ledger rows
  `3.7-P1`--`3.7-P4`, and the Section 3.7 audit-ledger row.
- `docs/SOURCE_ADMISSION_REGISTER.md`, `docs/REQUIREMENTS.md`, and
  `Dissertation/exhibits/meth_t4_evidence_control_matrix.{tex,txt}` plus its provenance JSON.
- Independent SHA-256 verification of all 18 declared inputs, both declared outputs and the
  provenance file itself; exact citation-stripped word and citation checks.
- The strict source checker, a fresh Tectonic build, PDF text-order checks and fresh raster
  inspection of physical pages 44--47.

The re-review was restricted to the provenance correction, the dependent ledgers and regression
checks. Chapter 4 content was not reviewed.

## 3. Blocking findings

None.

## 4. Previous-finding reconciliation

| Finding | Prior severity | Status | Resolution evidence |
|---|---:|---|---|
| `METH37-001` | MAJOR | **RESOLVED** | Provenance SHA-256 is `9493f388b48ece214d8476c314c8b3809aa14e497c55e676963b7bfb9d7419bb`; it declares the current SOURCE_ADMISSION_REGISTER SHA-256 `8cc3e9c79b366a59efa1f29331449f33f7f863c0119927c6a05bcc07fb9e2267` and REQUIREMENTS SHA-256 `9ed985e0506bbcbe4c8f74b329ec4baf4bea79b36231c09b613d6f1dd8403744`. All 18 inputs and both outputs match. Claim-ledger row `3.7-P4` records the same hashes. The visible TEX and TXT remain byte-identical to the accepted round-one artefacts. |

No partially resolved, unresolved, waived or regression findings remain.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose and alignment — meets.** The section remains exactly 300 citation-stripped words in
  four substantive paragraphs, with 3, 2, 3 and 3 distinct admitted citations respectively.
- **Evidence and accuracy — meets.** The refreshed register and requirements bindings agree with
  the table's implemented, planned, sealed and unavailable status distinctions. No ethics approval,
  participant execution, D1/D2 opening, live evaluation, empirical result, compliance,
  security-effectiveness or human-benefit claim has been introduced.
- **Methodological and technical validity — meets.** Data authority, restricted-data and external-
  model boundaries, prospective freeze controls, D2 leakage prevention, reproducibility records,
  stop conditions and builder/evaluator bias controls retain the accepted round-one meaning.
- **Citations and scholarship — meets.** The prose and unchanged table preserve the accepted exact-
  page source mappings; repository-specific classifications remain attributed to project contracts
  rather than presented as literature-derived universal rules.
- **Academic style and coherence — meets.** The unchanged prose remains concise British MSc-level
  writing with appropriately conditional and prospective status language.
- **Table integrity and accessibility — meets.** METH-T4 TEX SHA-256 remains
  `1568610c1ac0e2d70e31cf011aa0264cbfa35b4f7fa7e99ad6fac98e922d72d3` and TXT SHA-256 remains
  `80cf12b8249653b747117a74f26081ce4553426b9c4bd8061f3efc82cfa2932c`. The linear TXT alternative,
  repeated header, status key and source note remain complete. The five repeated longtable
  measurement-pass underfull-alignment messages have no visible defect.
- **Validation and placement — meets.** The strict source gate passes with 38 local PDFs and
  hashes, two immutable captures, 73 substantive paragraphs and 33 cited sources. Tectonic builds
  the 63-page report successfully. Physical page 44 contains the Section 3.7 prose, pages 45--46
  contain the complete two-page Table 3.4, and Chapter 4 begins on page 47. Fresh raster inspection
  found no blank page, clipping, overlap, counter error, unreadable row or float-order regression.

## 7. Handoff

Section 3.7 and METH-T4 are approved at round two. No further Section 3.7 revision or reviewer
handoff is required. This approval does not review or pre-approve Chapter 4.
