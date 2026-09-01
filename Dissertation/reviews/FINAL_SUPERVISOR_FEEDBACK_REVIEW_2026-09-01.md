# Final supervisor-feedback re-review

```yaml
review:
  skill: dissertation-reviewer
  gate: HOLD
  verdict: EVIDENCE_REQUIRED
  mode: FINAL_CROSS_SECTION_AUDIT
  section: "Complete revised dissertation candidate"
  section_type: "whole-report supervisor-feedback and submission-integrity gate"
  round: 3
  scope: "Dissertation front matter, Abstract, Chapters 1-8, appendices, exhibits, evidence records and compiled build/main.pdf"
  evidence_confidence: HIGH
  findings:
    blocker: 1
    major: 0
    minor: 0
    optional: 0
  previous_findings:
    resolved: 10
    partially_resolved: 1
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: user
```

## 1. Decision

**EVIDENCE REQUIRED.** The revised academic content, evaluation provenance, word count, exhibits,
captions and PDF pass the requested supervisor-feedback checks, but `AI-DISC-001` remains partly open
because candidate-controlled ethics evidence, submission metadata and confirmation of a complete AI-use
inventory are not yet available.

## 2. Scope and evidence consulted

- the current Abstract, Chapters 1--8, front matter, metadata and appendix structure;
- the eleven live findings selected for this implementation round in
  `SUPERVISOR_FEEDBACK_FULL_REPORT_REVIEW.md`;
- the candidate-supplied WMG section 3.2 wording preserved in
  `sources/WMG_AI_USE_GUIDANCE_CANDIDATE_SUPPLIED.md`;
- `audit/d0_evaluation_2026-09-01.json`, its SHA-256 checksum and the matching Chapter 5 and exhibit
  records;
- the active research questions, source manifest, claim ledger, references, report structure and
  section ledger;
- the source, claim-ledger, Harvard, British-English, Mermaid, word-count and focused evaluation-test
  outputs run on 1 September 2026;
- the 106-page `build/main.pdf`, including a full contact-sheet inspection and detailed renders of the
  pro-forma, Abstract, Table 1.2, accepted/held examples, long tables and Appendix I.

Expected but unavailable evidence is the candidate's ethics-training record, approval or waiver
confirmation and reference, remaining candidate-controlled metadata, and confirmation that Appendix I
contains the complete material prompt inventory for the whole assessed work rather than only the final
revision.

## 3. Blocking findings

### `AI-DISC-001` - `BLOCKER` - Submission disclosure is materially improved but candidate evidence remains incomplete

- **Status:** `PARTIALLY_RESOLVED`
- **Location:** `frontmatter/submission_proforma.tex`; `frontmatter/declaration.tex`;
  `appendices/appendix_structure.tex`, Appendices A, B and I; `metadata.tex`
- **Criterion:** truthful generative-AI disclosure and the pro-forma requirement for ethics approval or
  waiver evidence before submission
- **Problem:** Appendix I now names the tool, purposes, material final-revision prompts and checking
  process; the declaration contains the acknowledgement; and the first seven pro-forma boxes are
  correctly ticked. Appendix A still contains a pending training-evidence notice, Appendix B and the
  eighth box are deliberately pending, the ethics reference and other candidate metadata are blank, and
  the candidate has not confirmed that the three listed prompt summaries form the complete material
  prompt inventory for the whole project.
- **Why it matters:** the current wording is honest, but the dissertation is not yet a complete submission
  package and the reviewer cannot infer missing ethics or AI-use records.
- **Evidence:** the three files above, the preserved candidate-supplied WMG instruction and the user's
  explicit statement that the ethics approval screenshot will be supplied later
- **Required revision:** insert the candidate-supplied ethics-training and approval or waiver evidence;
  fill the ethics reference and remaining candidate metadata; tick the eighth box only after the evidence
  is present; and confirm Appendix I as complete or add any omitted material prompts with their purpose,
  affected output, candidate modification and verification.
- **Acceptance condition:** Appendices A and B contain the required evidence, all candidate-controlled
  fields are complete, the eighth box and ethics reference agree with that evidence, and the candidate
  confirms that Appendix I is a factually complete disclosure under the preserved WMG instruction.

## 4. Prior-finding reconciliation

| Finding | Previous severity | Status | Verification |
|---|---:|---|---|
| `AI-DISC-001` | BLOCKER | PARTIALLY_RESOLVED | Declaration, Appendix I and seven content boxes are complete; candidate ethics evidence, metadata and whole-project prompt-inventory confirmation remain pending. |
| `AI-PERM-001` | MAJOR | RESOLVED | The supplied WMG section 3.2 wording is preserved in the repository and the declaration follows its statement-plus-appendix structure. |
| `SFR-RES-002` | BLOCKER | RESOLVED | Frozen D0 output exists at the stated path and its full SHA-256 `dcc2fbffab100dfcf034784002d63b610cd9f97a8d6e6f9218b6e7f900de9dcd` matches the file. |
| `SFR-XS-001` | BLOCKER | RESOLVED | The title is narrowed to the implemented workflow and no longer claims impact or auditability. |
| `SFR-RES-004` | MAJOR | RESOLVED | Chapter 5 consistently reports two labelled contradictions. |
| `SFR-CAPTION-001` | MAJOR | RESOLVED | Static inspection covers 9 figures, 24 tables and 4 captioned long tables; detailed PDF renders place captions below content and table numbering is sequential. |
| `SFR-ABS-001` | MAJOR | RESOLVED | The 400-word Abstract states the business problem, RQ1/RQ2, method, principal result and scope in plain language. |
| `SFR-XS-003` | MAJOR | RESOLVED | `scripts/word_count.py --check` reproducibly reports 15,660 main-body words under the confirmed 13,500--16,500 convention. |
| `SFR-XS-005` | MAJOR | RESOLVED | Every included table and figure is referenced; the only unreferenced label is the internal research-question section anchor. |
| `SFR-XS-007` | MAJOR | RESOLVED | `REVIEW_LOG.md` marks earlier approvals as historical and this report is the current gate. |
| `SFR-PDF-001` | MAJOR | RESOLVED | The final 106-page A4 PDF compiles without unresolved references or overfull boxes and passes visual inspection. |

## 5. Non-blocking notes

None. The remaining work is candidate-controlled evidence, not a prose workaround or optional polish.

## 6. Section-level assessment

- **Purpose and alignment - meets.** The title, Abstract, body and conclusion address the implemented
  workflow and RQ1/RQ2 without claiming real-company or business benefit.
- **Evidence and accuracy - meets.** D0 values, contradictions, null comparisons and provenance agree
  with the frozen output and repository evidence.
- **Methodological and technical validity - meets.** The report distinguishes designed fixture evidence,
  engineering tests and prospective pilot work, with equal-input C1/C2 conditions.
- **Critical analysis - meets.** The literature, alternatives, limitations and discussion explain why
  functional separation was selected while conceding that a simpler system could apply the same rule.
- **Structure and coherence - meets.** The argument flows from business process and evidence risks through
  literature, design, evaluation, RQ answers, limitations and pilot.
- **Citations and scholarship - meets.** All 188 substantive body paragraphs reconcile to page-level
  claim-ledger records and 47 cited references pass the Harvard gate.
- **Academic style - meets.** The current manuscript passes the British-English and no-em-dash checks and
  uses a non-technical register outside the implementation sections.
- **Tables, figures and reproducibility - meets.** Captions follow content, large supporting tables are in
  appendices, accepted and held examples are explicit, and the build and word-count routes are repeatable.
- **Submission evidence - partly meets.** The AI acknowledgement is present, but the candidate-controlled
  records in `AI-DISC-001` are still required.

## 7. Handoff

Minimum evidence required from the user:

1. the ethics-training evidence required for Appendix A;
2. the ethics approval or waiver screenshot/email and reference for Appendix B;
3. Student ID, qualifications if required, submission month/year, signature and date; and
4. confirmation that Appendix I is the complete material AI-use and prompt inventory, or the omitted
   prompt records needed to make it complete.

No claim of ethics approval, participant evidence or business benefit can be approved without its
corresponding evidence. The eighth pro-forma box must remain unticked until Appendix B is complete.
