```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: RE_REVIEW
  section: "3.3 Dataset tiers and freeze protocol"
  section_type: "methodology, dataset governance, and leakage control"
  round: 2
  scope: "Dissertation/chapters/03_methodology.tex lines 29-46, including Figure 3.2 METH-F2"
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

# Section 3.3 independent re-review

## 1. Decision

**APPROVED.** `METH33-001` and `METH33-002` are resolved: the revised D0 paragraph now states the
actual distinction between manifest declarations and executable checks, and METH-F2's non-circular
provenance has exact input/output hashes while retaining its byte-identical visible PDF. No
regression was identified.

## 2. Scope and evidence consulted

- Round-one `Dissertation/reviews/SECTION_3_3_REVIEW.md`, including findings `METH33-001` and
  `METH33-002` and their acceptance conditions.
- `Dissertation/chapters/03_methodology.tex` lines 29--46: revised Section 3.3 prose and METH-F2
  inclusion.
- `Dissertation/REPORT_STRUCTURE.md`, `docs/EVALUATION_PROTOCOL.md`, `docs/PROJECT_CHARTER.md` and
  `docs/REQUIREMENTS.md` for the D0--D2, freeze, grouping, participant and current NO-GO states.
- `fixtures/evaluation_manifest.json`, `fixtures/evaluation_cases.json`,
  `src/portfolio_agent/evaluation_datasets.py` and `tests/unit/test_evaluation.py` for current
  manifest declarations, loader checks, accepted alternative namespaces/policies, grouping and the
  separately invoked operational-ID guard.
- `Dissertation/sources/CLAIM_LEDGER.md` rows `3.3-P1`--`3.3-P4`, `references.tex`,
  `sources/MANIFEST.csv`, `sources/SHA256SUMS` and the unchanged exact source pages approved in
  round one.
- `Dissertation/exhibits/meth_f2_dataset_freeze_timeline.{py,svg,pdf,txt}` and
  `meth_f2_dataset_freeze_timeline_provenance.json`.
- Round-two citation-stripped word/citation extraction; focused current and adversarial loader
  probes; focused loader tests; all provenance hashes; deterministic repeat rendering; strict
  source checker; fresh Tectonic build; PDF text extraction; and fresh raster inspection of physical
  pages 35--37.

No material expected evidence was unavailable. The earlier absence of a standalone Section 3.3
evidence packet did not impede this re-review: the mutable claim ledger is no longer declared as a
figure input, and the scoped claim rows, project contracts and hash-pinned sources remain directly
available.

## 3. Blocking findings

None.

## 4. Prior-finding reconciliation

| Finding | Previous severity | Status | Verification |
|---|---:|---|---|
| `METH33-001` | MAJOR | RESOLVED | Paragraph 1 now says the current manifest records/hash-pins the exact D0 namespace, source version, test-only policy and permitted use; separately states that the loader computes the manifest hash and enforces dataset checksum, source-version/classification and entity/period consistency; explicitly acknowledges that alternative `benchmark:` namespaces and policy strings remain accepted; and limits the benchmark-ID guard to locations where it is invoked. The focused probe reproduced every distinction, and all eight loader tests pass. |
| `METH33-002` | MAJOR | RESOLVED | METH-F2 provenance and traceability no longer declare `CLAIM_LEDGER.md` as an input, breaking the circular hash dependency. All 11 declared inputs and four outputs match; TXT SHA-256 is `40c90056...`, provenance SHA-256 is `06524fc2...`, the visible PDF remains `35f9c468...`, and a fresh render is byte-identical. |

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose and alignment — meets.** The section remains exactly 350 citation-stripped words across
  four paragraphs and covers D0, D1, one pre-D2 freeze, D2, dependence-aware grouping and the
  participant-state boundary.
- **Evidence and accuracy — meets.** D0 is correctly separated into current manifest declarations
  and loader-enforced checks; the loader's accepted namespace/policy scope and the operational-ID
  helper's invocation boundary are explicit. D1 remains protocol-only, D2 remains sealed with no
  path/checksum, and C0 and human-result C3 remain held.
- **Methodological or technical validity — meets.** The prose retains pilot-only D1 use,
  confirmatory exclusion, complete pre-D2 freeze, no D2 inspection/tuning, exploratory labelling
  after D2-informed changes, and company/report/entity-period dependence controls without claiming
  unimplemented enforcement.
- **Critical analysis — meets.** D0 remains mechanism evidence rather than portfolio-performance
  evidence; participant observations remain authorised C0/C3 executions rather than D3; and no
  D1/D2/C0/C3 result or human benefit is invented.
- **Structure and coherence — meets.** The revised first paragraph adds the necessary implementation
  boundary without disturbing the progression from visible synthetic fixtures through pilot,
  freeze, sealed holdout and clustered analysis.
- **Citations and scholarship — meets.** The four paragraphs retain 2, 2, 3 and 2 distinct locally
  admitted citations, with unchanged exact source-page fit. Literature justifies general synthetic
  data, dataset documentation, leakage and reproducibility principles rather than defining the
  project-specific D0--D2 tiers.
- **Academic style — meets.** The prose is concise British MSc-level writing and the implementation
  qualification is precise without becoming code narration or implying a security guarantee.
- **Tables, figures, equations, and reproducibility — meets.** Figure 3.2 remains accurately
  referenced, labelled, conceptual, vector-only and accessible through its SVG title/description and
  complete TXT alternative. The visible PDF/SVG/renderer hashes are unchanged; the revised TXT and
  provenance hashes match the claim ledger; all declared provenance hashes and the repeat render
  pass. Section 3.3 renders cleanly on physical page 35, Figure 3.2 on page 36 and Section 3.4 on page
  37, with no scoped warning, unresolved reference, clipping, overlap, empty page or float-order
  defect.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated
scope and evidence available.

No non-blocking note remains. This approval does not pre-approve Section 3.4.
