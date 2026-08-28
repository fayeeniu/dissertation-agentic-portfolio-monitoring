```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: SECTION_REVIEW
  section: "3.2 Evaluand and experimental conditions"
  section_type: "methodology and experimental design"
  round: 1
  scope: "Dissertation/chapters/03_methodology.tex lines 18-28, including Table 3.1 METH-T1"
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

# Section 3.2 independent review

## 1. Decision

**APPROVED.** The section defines the workflow configuration as the evaluand, operationalises C0--C3
without transferring authority from the cited literature, and preserves the exact parity, scoring,
execution-state and public-web exclusion boundaries required by the current protocol. Table 3.1 is
accurate, accessible, provenance-verified and correctly placed.

## 2. Scope and evidence consulted

- `Dissertation/chapters/03_methodology.tex` lines 18--28: Section 3.2 prose and METH-T1 inclusion.
- `Dissertation/REPORT_STRUCTURE.md`: RQ1--RQ3, the 350-word Section 3.2 allocation, current C0/C3
  NO-GO state and exclusion of the live-unrun public-web path.
- `Dissertation/sources/CLAIM_LEDGER.md` rows `3.2-P1`--`3.2-P4`, `references.tex`,
  `sources/MANIFEST.csv` and `sources/SHA256SUMS`.
- Exact admitted source pages: Hevner et al. pp. 4, 9 and 11; Peffers et al. pp. 16--18; Mitchell et
  al. pp. 1 and 4--5; Pineau et al. pp. 1--4; NIST AI RMF pp. 33--35; and Kapoor and Narayanan
  pp. 1--7.
- `docs/EVALUATION_PROTOCOL.md`, `docs/PROJECT_CHARTER.md` and `docs/REQUIREMENTS.md` for the
  evaluand, C0--C3 operational definitions, parity, current evidence states, ethics stops and
  implementation/protocol/finding boundary.
- `src/portfolio_agent/enums.py`, `src/portfolio_agent/evaluation.py`,
  `src/portfolio_agent/workflow.py`, `fixtures/evaluation_manifest.json`,
  `tests/unit/test_evaluation.py` and `tests/integration/test_workflow.py` for the implemented
  condition identifiers, D0 execution, null human summaries, bounded roles and separate verifier.
- `Dissertation/exhibits/meth_t1_condition_matrix.tex`, `.txt` and `_provenance.json`.
- Citation-stripped word/citation extraction; all provenance hash checks; strict source checker;
  fresh Tectonic build; cross-reference extraction; and fresh raster inspection of physical pages
  33--35.

No material expected evidence was unavailable.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose and alignment — meets.** The section supplies the planned evaluand and C0--C3 condition
  contract in exactly 350 citation-stripped words across four substantive paragraphs.
- **Evidence and accuracy — meets.** The evaluand binds input, catalogue, source access, roles,
  verification, human involvement, prompt/schema versions, environment and stops exactly as the
  repository protocol specifies. Literature citations justify design-science evaluation,
  reproducibility, documentation and information-boundary controls; they are not presented as the
  source of the project-specific condition definitions.
- **Methodological or technical validity — meets.** C0 is an authorised manual workflow with all tool
  or model assistance logged; C1 is the deterministic no-verifier baseline; C2 adds a separately
  recorded verifier and has no human edits before scoring; and C3 scores the approved post-review
  version separately from pre-review C2. Table 3.1 also makes the no-human-edit boundary explicit for
  both C1 and C2.
- **Critical analysis — meets.** The same canonical definitions, period, eligible inputs,
  source-access window and frozen gold reference are required for comparable conditions, without
  claiming that an unexecuted study has achieved parity. C0 remains protocol-only/NO-GO; C1 and C2
  are implemented only on synthetic labelled D0 cases; and the C3 workflow exists while human
  results remain protocol-only/NO-GO and null.
- **Structure and coherence — meets.** The four paragraphs progress from evaluand definition through
  C0/C1 and C2/C3 operationalisation to authority status and the explicit engineering-case exclusion.
- **Citations and scholarship — meets.** Paragraphs contain 3, 2, 2 and 2 distinct locally admitted
  citations respectively, and each literature proposition fits its inspected pages.
- **Academic style — meets.** The prose is plain, precise British academic English at MSc level and
  avoids model-leaderboard, agent-anthropomorphism, human-benefit, live-performance or production
  overclaim.
- **Tables, figures, equations, and reproducibility — meets.** The prose resolves to Table 3.1, whose
  caption, condition rows, parity rule, scoring points, current evidence states and public-web
  exclusion agree with the chapter, TXT alternative and provenance. All six recorded inputs/outputs
  and the external provenance SHA-256 match. The complete TXT companion supplies reading-order
  access and the portrait table does not rely on colour. Section 3.2 renders cleanly on physical page
  33, Table 3.1 on page 34 and Section 3.3 begins on page 35, with no scoped warning, unresolved
  reference, clipping, overlap or float-order defect.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated
scope and evidence available.

No non-blocking note remains. This approval does not pre-approve Section 3.3.
