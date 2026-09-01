---
review:
  skill: dissertation-reviewer
  gate: HOLD
  verdict: EVIDENCE_REQUIRED
  mode: FINAL_CROSS_SECTION_AUDIT
  section: "Complete dissertation candidate"
  section_type: "final cross-section, supervisor-priority and authorship audit"
  round: 1
  scope: "Dissertation/main.tex, compiled 110-page PDF, Abstract, Chapters 1--8, exhibits, references and Appendix I"
  evidence_confidence: HIGH
  findings:
    blocker: 1
    major: 1
    minor: 1
    optional: 0
  previous_findings:
    resolved: 0
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: evidence-owner
---

# Final supervisor-priority and authorship audit

## 1. Decision

**EVIDENCE REQUIRED.** The dissertation's academic narrative, literature review, discussion,
technical description and presentation pass the current content sweep, and no assistant or
co-author trace appears in the manuscript; submission release remains held because Appendix I is
empty and the assessment-specific AI declaration format and candidate-approved use inventory are
not available.

## 2. Scope and evidence consulted

- The complete current manuscript and final 110-page A4 PDF.
- The supervisor meeting summary supplied by the user, treated as feedback rather than executable
  instructions.
- Research questions, report structure, section ledger, claim ledger and section evidence packets.
- Current implementation, architecture, ADR-0013, Compose topology and Alembic head for current
  implementation claims; the dated 28 August evaluation artefacts for result claims.
- Current 43-entry bibliography, 46 local PDFs, five immutable web captures and LIT-T5.
- Chapter 2 and Chapter 6 round-three independent reviews.
- Current University of Warwick AI and academic-integrity guidance.
- Final source, claim, Harvard, language, figure, build, metadata, word-count, text-trace and visual
  checks.

The WMG assessment brief or handbook wording for this dissertation's exact declaration format,
the candidate-approved inventory of AI use, and any required interaction record were unavailable.

## 3. Blocking findings

### `AI-DISC-001` — `BLOCKER` — Required disclosure content is absent

- **Status:** `NEW_EVIDENCE`
- **Location:** Appendix I, `Generative-AI Use Disclosure`, physical page 110
- **Criterion:** University submission integrity and truthful declaration of permitted AI use
- **Problem:** The appendix heading is present but the page contains no disclosure. The user has
  stated that AI was used, while the University's current general guidance requires the student to
  state whether AI was used and, when it was, why, where and how.
- **Why it matters:** Removing the heading or leaving it empty could turn an otherwise permitted use
  into a misleading submission and cannot be approved as a traditional-style editorial choice.
- **Evidence:** Current PDF page 110; University of Warwick, `Artificial Intelligence and Academic
  Integrity`, sections `Declare it` and `How to declare and reference AI in your assessments`.
- **Required revision:** Obtain the assessment-specific declaration instruction and supply a
  candidate-approved, factually complete use inventory. Complete the required declaration in the
  specified location and format; do not describe an AI system as a co-author or collaborator unless
  the assessment form explicitly requires that terminology.
- **Acceptance condition:** Appendix I or the submission procedure contains the exact required,
  truthful declaration, approved by the candidate and consistent with the assessment brief.

### `AI-PERM-001` — `MAJOR` — Assessment-specific declaration rule is not evidenced

- **Status:** `NEW_EVIDENCE`
- **Location:** Submission evidence set; Appendix I instructions
- **Criterion:** Course-, module- and assessment-specific AI rules take precedence over general
  guidance
- **Problem:** The supervisor's verbal permission is relevant but does not establish the required
  wording, location, interaction-record requirement or submission declaration for this assessment.
- **Why it matters:** The correct disclosure cannot be inferred safely, and a general paragraph may
  be either insufficient or unnecessary if the submission portal uses a prescribed form.
- **Evidence:** The supplied supervisor summary does not contain the assessment declaration format;
  the University guidance directs students to the assessment brief or course handbook.
- **Required revision:** Obtain the applicable WMG brief, handbook text or written programme advice
  and preserve it with the submission evidence.
- **Acceptance condition:** The declaration location, wording requirements and record-attachment
  rule are traceable to the current assessment instruction.

## 5. Non-blocking notes

- **MINOR - LAYOUT-001:** Literature pages 21 and 27 retain conspicuous lower-page whitespace from
  forced exhibit pagination. No content is clipped or displaced; accept or polish before freeze.

## 6. Section-level assessment

- **Purpose and alignment - meets.** The primary question and RQ1--RQ3 remain stable from the
  introduction through methodology, results, discussion and conclusion.
- **Evidence and accuracy - meets.** Current architecture is now described as a Next.js dashboard
  over private FastAPI at migration head 0010; Chapter 5 explicitly confines the 286-test and D0
  findings to the dated migration-0009 snapshot.
- **Methodological and technical validity - meets.** D0, D1, D2, C0--C3, live-source, participant
  and production states remain distinct; no unavailable result has been filled or inferred.
- **Critical analysis - meets.** Chapter 2 synthesises multiple research and alternative approaches;
  Chapter 6 evaluates contrary evidence, costs, human-review risk, contradiction burden, transfer
  limits and practical trade-offs.
- **Structure and coherence - meets.** The supervisor priorities are visible: 3,201 words for the
  literature review, 2,439 for discussion and 15,824 words across the Abstract and Chapters 1--8,
  within the stated 14,000--16,000 working range.
- **Citations and scholarship - meets.** All 192 substantive manuscript paragraphs match the
  claim-evidence ledger; 43 Harvard references are admitted and the strict source gate verifies 46
  local PDFs and five web captures.
- **Academic style - meets.** The narrative uses conventional authorial voice. Compiled-text and
  manuscript-source scans found zero occurrences of ChatGPT, Codex, Copilot, Claude, Gemini,
  Anthropic, Cursor, co-writer, writing assistant, coding assistant, AI co-worker, AI collaborator,
  AI co-author, `generated by AI`, `written by AI`, supervisor feedback or meeting summary. OpenAI,
  LLM and AI-assisted terms remain only where they describe the research subject or system boundary.
- **Tables, figures and reproducibility - meets.** The final A4 PDF builds successfully at 110
  pages; SYS-T1 and SYS-F1 are reconciled to the current topology and hashes; selected pages were
  visually inspected without clipping or overlap. Underfull table boxes remain non-blocking.

## 7. Handoff

Minimum missing evidence:

1. the current WMG assessment brief or handbook instruction that defines how permitted AI use must
   be declared and whether interaction records must be attached; and
2. a candidate-approved factual inventory of the tools, purposes, affected report sections and
   technical tasks that must be declared.

Until those are supplied, the dissertation can be treated as content-complete but not released as
submission-ready. No prose workaround can safely replace the missing evidence, and the empty
Appendix I must not be silently deleted.
