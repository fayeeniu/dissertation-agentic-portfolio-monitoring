# Final source, language and presentation review

> Historical review note, updated 31 August 2026: the decisions below pre-date the revisions to
> Sections 1.3, 1.4 and 2.1. Current Section 1.3 has since passed a fresh independent review. Sections
> 1.4 and 2.1 pass source, claim, language, build and rendered-page checks, but have not inherited the
> decisions below and their current independent gates remain pending.

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "Abstract"
  section_type: "abstract"
  round: 1
  scope: "frontmatter/abstract.tex"
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

## 1. Decision

**APPROVED.** The abstract matches the reported D0 results, says that RQ3 remains unanswered and avoids claims about live or real-world performance.

## 2. Scope and evidence consulted

- `frontmatter/abstract.tex` and the rendered abstract page.
- Chapters 1, 5, 6 and 8 for question, result and conclusion consistency.
- The final local PDF and the language checks.

Expected but unavailable: C0 and C3 observations, D1 and D2 results, and live company results. The abstract states these limits.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- Purpose and alignment: meets. The problem, method, current evidence and limits are clear.
- Evidence and accuracy: meets. Every reported value agrees with the results chapter.
- Academic style: meets. The wording is direct British English and remains within the requested B2/C1 range.
- Citations and scholarship: not applicable. The abstract does not rely on in-text references.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 1: Introduction"
  section_type: "introduction"
  round: 1
  scope: "chapters/01_introduction.tex"
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

## 1. Decision

**APPROVED.** The chapter gives a clear problem, stable research questions, practical objectives and honest limits for the available evidence.

## 2. Scope and evidence consulted

- `chapters/01_introduction.tex` and its Mermaid figure.
- Research questions and objectives as repeated in Chapters 3, 6 and 8.
- Local citation files, paragraph claim rows and the rendered pages.

Expected but unavailable: approved real-company and participant results. The chapter does not present them as completed work.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- Purpose and alignment: meets. The primary question and RQ1 to RQ3 remain consistent across the report.
- Evidence and accuracy: meets. Scope and contribution statements match the built prototype and current evaluation.
- Structure and coherence: meets. The problem leads clearly to the questions, objectives and chapter plan.
- Citations and scholarship: meets. Claims use admitted local sources and round Harvard citations.
- Academic style: meets. The language is clear British English without em dashes.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 2: Literature Review"
  section_type: "literature review"
  round: 1
  scope: "chapters/02_literature_review.tex"
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

## 1. Decision

**APPROVED.** The chapter explains the main ideas needed by the project, compares their limits and links them to the design without pretending to be an exhaustive review.

## 2. Scope and evidence consulted

- `chapters/02_literature_review.tex`, its tables and two Mermaid figures.
- All cited local PDFs, source manifest, checksums and page-level claim records.
- The bibliography and the Chapter 6 literature comparison.

Expected but unavailable: a systematic search record or formal risk-of-bias study. The chapter makes no claim that either was completed.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- Purpose and alignment: meets. The review supports the design choices and the later result discussion.
- Evidence and accuracy: meets. Every substantive paragraph has a checked source row and local source copy.
- Critical analysis: meets. The chapter separates traceability, correctness, human control and practical value.
- Citations and scholarship: meets. The citations and reference entries follow the selected Harvard WMS rules.
- Tables, figures and reproducibility: meets. The diagrams have versioned Mermaid source, rendered PNG files and checked hashes.
- Academic style: meets. Dense phrases were replaced with simpler British English.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 3: Research Design and Methodology"
  section_type: "methodology"
  round: 1
  scope: "chapters/03_methodology.tex"
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

## 1. Decision

**APPROVED.** The chapter clearly separates fictional engineering cases from the planned pilot, final set and human comparison.

## 2. Scope and evidence consulted

- `chapters/03_methodology.tex`, method tables and three Mermaid figures.
- Dataset, condition, measure and evidence-control records.
- Statistical-method sources and the implemented D0 evaluator.

Expected but unavailable: D1 calibration, sealed D2 observations, fixed C0/C3 participant data and final statistical choices. The chapter leaves these as planned work.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- Purpose and alignment: meets. The method directly addresses the primary question and RQ1 to RQ3.
- Methodological validity: meets for the current design. It controls leakage, grouping, denominators and unavailable values.
- Evidence and accuracy: meets. Completed, planned and held activities are kept separate.
- Citations and scholarship: meets. Method claims use the admitted local sources.
- Tables, figures and reproducibility: meets. Study choices, measures and evidence limits are recorded in reusable artefacts.
- Academic style: meets. The wording is plain enough for the requested level while keeping the method precise.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 4: System Design"
  section_type: "system design"
  round: 1
  scope: "chapters/04_system_design.tex"
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

## 1. Decision

**APPROVED.** The chapter explains the local architecture, evidence controls, identity checks, verification and export boundaries without turning design features into performance claims.

## 2. Scope and evidence consulted

- `chapters/04_system_design.tex`, system tables and five Mermaid figures.
- Implementation, migrations, tests, local runtime records and project control files cited by the chapter.
- Literature used to explain provenance, reliability, human control and AI risk.

Expected but unavailable: a hosted security assessment, live source run, multi-user access evidence and production operating record. These remain outside the chapter's claims.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- Purpose and alignment: meets. The design supports the stated evidence-first workflow.
- Technical validity: meets for the local prototype. The chapter describes the present contracts and their limits accurately.
- Evidence and accuracy: meets. Claims about implementation are kept separate from unrun live and human work.
- Citations and scholarship: meets. Explanatory claims are linked to checked local sources.
- Tables, figures and reproducibility: meets. Diagrams are monochrome, source-controlled and readable in the final PDF.
- Academic style: meets. The chapter uses simpler British English without losing key distinctions.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 5: Implementation and Results"
  section_type: "results"
  round: 1
  scope: "chapters/05_evaluation_results.tex"
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

## 1. Decision

**APPROVED.** The reported values match the saved D0 outputs and clearly remain fictional-case engineering results rather than real-world estimates.

## 2. Scope and evidence consulted

- `chapters/05_implementation_results.tex`, result tables and the Mermaid metric figure.
- Saved D0 outputs, denominators, checksums, implementation records and previous result reconciliation.
- Abstract, Chapter 6 and Chapter 8 statements that repeat the results.

Expected but unavailable: D1, D2, C0, C3 and live public-company observations. Their cells and conclusions remain blank or explicitly unavailable.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- Purpose and alignment: meets. The results provide the evidence currently available for RQ1 and RQ2.
- Evidence and accuracy: meets. Counts, rates and denominators reconcile with the saved outputs.
- Methodological validity: meets for D0. The text does not generalise beyond the designed cases.
- Critical analysis: meets. The chapter explains what zero, blank and unavailable values mean.
- Tables, figures and reproducibility: meets. Result tables and the metric figure are readable and traceable.
- Academic style: meets. Results are stated in direct British English.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 6: Discussion"
  section_type: "discussion"
  round: 1
  scope: "chapters/06_discussion.tex"
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

## 1. Decision

**APPROVED.** The discussion now gives a clear qualitative comparison with the literature and rejects a statistical claim that the D0 result is normal or non-anomalous.

## 2. Scope and evidence consulted

- `chapters/06_discussion.tex` and its literature-alignment and transfer tables.
- Chapter 5 results, D0 design records and the relevant local literature on citation support, reproducibility, human review and statistical comparison.
- Research questions and conclusion statements.

Expected but unavailable: an independent comparison distribution, unseen real cases and a completed human comparison. These prevent a statistical anomaly test and an answer to RQ3.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- Purpose and alignment: meets. RQ1 and RQ2 receive bounded answers and RQ3 remains unanswered.
- Evidence and accuracy: meets. The interpretation does not exceed the D0 evidence.
- Methodological validity: meets. The chapter explains why D0 cannot support a population or anomaly claim.
- Critical analysis: meets. Directional agreement is separated from independent confirmation.
- Citations and scholarship: meets. The comparison draws only on checked local sources.
- Academic style: meets. The explanation is direct and avoids unnecessary specialist language.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 7: Ethics, Governance and Limitations"
  section_type: "ethics and limitations"
  round: 1
  scope: "chapters/07_governance_limitations.tex"
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

## 1. Decision

**APPROVED.** The chapter states the data, provider, security, human and deployment limits plainly and does not claim legal compliance or production readiness.

## 2. Scope and evidence consulted

- `chapters/07_ethics_governance_limitations.tex` and the governance table.
- Local policy, implementation and test evidence cited by the chapter.
- Checked local copies of the governance, security and human-AI literature.

Expected but unavailable: formal ethics approval, authorised participant evidence, a production security review and provider account evidence at execution time. The chapter keeps these as required future evidence.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- Purpose and alignment: meets. The chapter limits the uses and conclusions of the prototype.
- Evidence and accuracy: meets. Implemented safeguards and unverified authority are clearly separated.
- Critical analysis: meets. Residual risks and limits remain visible.
- Citations and scholarship: meets. Governance claims use checked local evidence.
- Academic style: meets. The wording is clear British English and avoids inflated claims.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 8: Conclusion and Future Work"
  section_type: "conclusion"
  round: 1
  scope: "chapters/08_conclusion.tex"
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

## 1. Decision

**APPROVED.** The conclusion answers the primary question only partly, keeps RQ3 open and carries the literature comparison forward without adding a new claim.

## 2. Scope and evidence consulted

- `chapters/08_conclusion_future_work.tex` and the future-work table.
- The research questions in Chapter 1, method in Chapter 3, results in Chapter 5 and interpretation in Chapter 6.
- Local literature and the paragraph claim ledger.

Expected but unavailable: the live, held-out and human evidence listed in the future-work sequence. The conclusion does not claim that this work has been completed.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- Purpose and alignment: meets. The conclusion directly returns to the primary question and each RQ.
- Evidence and accuracy: meets. Contributions and limits match the current evidence.
- Critical analysis: meets. The chapter distinguishes a useful research artefact from a proven production system.
- Citations and scholarship: meets. The final literature statement is supported by admitted local sources.
- Academic style: meets. The ending is concise, clear and in British English.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: MULTI_SECTION_REVIEW
  section: "References and visual presentation"
  section_type: "references and presentation"
  round: 1
  scope: "references.tex; style.tex; exhibits/*.mmd; exhibits/*.png; build/main.pdf"
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

## 1. Decision

**APPROVED.** The active references are locally backed and alphabetised, in-text citations use round brackets, all text colours are black and the twelve diagrams are reproducible Mermaid renders.

## 2. Scope and evidence consulted

- `references.tex`, `style.tex`, the final PDF and the Harvard checker.
- `sources/MANIFEST.csv`, `sources/SHA256SUMS`, `sources/REFERENCE_AUDIT.md` and all local PDFs.
- Twelve Mermaid source files, PNG renders, renderer inputs and `exhibits/MERMAID_MANIFEST.csv`.
- Visual checks of the title, abstract, representative chapter pages, all changed diagrams, results, discussion and reference pages.

Expected but unavailable: none for the active reference list. Three extra local PDFs are retained but are not cited.

## 3. Blocking findings

None.

## 5. Non-blocking notes

- Exact source titles retain their publishers' original spelling, including the words “Organization” and “Modeling”. Dissertation prose uses British spelling.

## 6. Section-level assessment

- Citations and scholarship: meets. Thirty-five active sources use round author-date labels, ampersands for two authors and A to Z order.
- Evidence and accuracy: meets. All active references map to readable local PDFs with checked page counts and hashes.
- Tables, figures and reproducibility: meets. Twelve diagrams have code, screenshots, fixed renderer inputs and matching hashes.
- Academic style: meets. The final PDF has no em dashes or square-bracket author-date citations.
- Visual presentation: meets. Headings, titles, citations, links, tables and diagrams are monochrome and readable.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

---

review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: FINAL_CROSS_SECTION_AUDIT
  section: "Whole dissertation"
  section_type: "cross-section coherence and evidence"
  round: 1
  scope: "Abstract, Chapters 1 to 8, references, figures and final PDF"
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

## 1. Decision

**APPROVED.** The report is internally consistent, locally sourced and clear about what the current evidence can and cannot answer.

## 2. Scope and evidence consulted

- All manuscript files, tables, figures and the final 109-page A4 PDF.
- Thirty-eight local PDFs, thirty-five active cited sources, two immutable web captures, source checksums and the reference audit.
- The 181-row paragraph claim check, saved D0 evidence and the research-question comparison.
- Harvard, British English, em dash, Mermaid, lint, formatting and PDF text checks.

Expected but unavailable: D1 and D2 outcomes, C0 and C3 participant observations, an independent anomaly distribution, authorised live company research and production evidence. The dissertation treats all of these as limits or future work.

## 3. Blocking findings

None.

## 5. Non-blocking notes

- The primary question is only partly answered. RQ1 and RQ2 have bounded D0 evidence, while RQ3 remains unanswered.
- The RQ1 and RQ2 results are compatible with the literature in direction. This is not independent validation because the literature informed the design and the fictional cases.
- No statistical claim that the results are anomalous or non-anomalous is supported.
- Candidate and institution-owned submission details remain blank until the correct information is supplied.

## 6. Section-level assessment

- Purpose and alignment: meets. Questions, objectives, method, results, discussion and conclusion agree.
- Evidence and accuracy: meets for the claims made. Completed, synthetic, planned, held and unavailable states remain distinct.
- Methodological and technical validity: meets for the local design and D0 evaluation, with real-world limits stated.
- Critical analysis: meets. The report explains why directional agreement is not a statistical normality test or external validation.
- Structure and coherence: meets. The argument moves from problem and literature through design and results to bounded conclusions.
- Citations and scholarship: meets. The active bibliography is local, checked, Harvard-formatted and alphabetised.
- Academic style: meets. The report uses clear British English and no em dashes.
- Tables, figures and reproducibility: meets. Tables are readable and diagrams have reproducible Mermaid source and checked renders.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated scope and evidence available.

This approval does not show that the prototype is ready for production or that it performs well on real companies. Those conclusions still require the held evaluation work.
