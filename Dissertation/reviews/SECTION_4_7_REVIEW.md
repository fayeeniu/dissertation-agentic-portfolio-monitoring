```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: RE_REVIEW
  section: "4.7 Bounded public-web company-research case study"
  section_type: "system design and implementation"
  round: 2
  scope: "Dissertation/chapters/04_system_design.tex Section 4.7 and Figure 4.5 SYS-F5"
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

# Section 4.7 round-two reviewer gate

## 1. Decision

**APPROVED.** Section 4.7 accurately describes the current bounded public-web implementation,
keeps controlled-test evidence separate from live or empirical evidence, and now has a closed
implementation, citation, exhibit, build and rendering record.

## 2. Scope and evidence consulted

- Section 4.7 and Figure 4.5 in the fresh 78-page dissertation build.
- The current company-research service, its integration and migration tests, fixture tests, source
  admission register, Figure 4.5 TeX/text alternative and refreshed provenance record.
- Claim-ledger rows `4.7-P1`--`4.7-P5`, report structure, Section 4.7 round-one review and the
  dissertation system-design rubric.
- All six cited local PDFs at the pages recorded in the claim ledger, together with the source
  manifest, bibliography and SHA-256 inventory.
- Python compilation, 37 focused controlled tests, the strict local-source checker, Tectonic build
  and rendered physical pages 60--62.

No live OpenAI, publisher, company, participant, browser, export or production research action was
run or inferred. Section 4.8 was not drafted or reviewed.

## 3. Blocking findings

None.

## 4. Prior-finding reconciliation

| Finding | Previous severity | Status | Verification |
|---|---:|---|---|
| `SYS47-002` | MAJOR | RESOLVED | `company_research.py` compiles at current SHA `738d77f9...`; the focused suite collects and passes all 37 cases. |
| `SYS47-001` | MINOR | RESOLVED | The integration assertion and implementation now agree on `company-intelligence-deck-v3`; no schema mismatch remains in the focused suite. |

## 5. Non-blocking notes

None for the stated scope.

## 6. Section-level assessment

- **Purpose and alignment: meets.** The section presents the public-web route as implementation
  evidence within the approved system-design chapter and explicitly rejects an additional empirical
  research question.
- **Evidence and accuracy: meets.** Reviewed identity, bounded URL discovery, guarded capture,
  redaction, exact-span admission, serial persisted tasks, budgets, telemetry, recovery,
  contradiction handling and pending review match the current implementation and controlled tests.
- **Methodological and technical validity: meets.** The design separates discovery from evidence
  admission and preserves blocked, unsupported, failed and uncovered states instead of turning them
  into company facts.
- **Critical analysis: meets.** The prose states that local fakes and controlled responses do not
  establish live coverage, accuracy, usefulness, superiority, production safety or investment
  validity.
- **Structure and coherence: meets.** Five paragraphs follow the discover--capture--extract--compose
  sequence and close with the evidence boundary.
- **Citations and scholarship: meets.** The five paragraphs contain 2/2/3/2/3 distinct citations;
  each cited key resolves to a readable local, hash-recorded PDF and supports the associated
  external claim rather than certifying repository mechanics.
- **Academic style: meets.** The section uses clear MSc-level British English, calibrated claims and
  no promotional or production-readiness language.
- **Tables, figures and reproducibility: meets.** SYS-F5 is numbered, referenced, legible and paired
  with a text alternative. TeX SHA is `90d8fd5b...`, text SHA is `85c4028f...`, and refreshed
  provenance SHA is `a1d92202...`; all 12 inputs and both outputs match. Physical page 60 contains
  the complete prose, page 61 the complete figure and page 62 only the untouched 4.8--4.9 headings,
  without clipping, overlap or unreadable content.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the
stated scope and evidence available.

There are no remaining non-blocking notes for Section 4.7.
