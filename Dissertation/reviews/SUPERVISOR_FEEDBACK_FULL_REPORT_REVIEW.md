# Supervisor-feedback full-report review

Reviewer: `dissertation-reviewer` (independent gate)
Date: 31 August 2026
Mode: `MULTI_SECTION_REVIEW` + `FINAL_CROSS_SECTION_AUDIT`, conducted as a `RE_REVIEW` against existing
review reports in `Dissertation/reviews/`.

This report does not modify any dissertation file. It is a review only.

---

## 0. How to read this report

The user explicitly requested a whole-report review, so the normal one-section default does not apply.
Sections 1--9 below each carry a complete machine-readable header and the seven contract sections for
one target section (Abstract, then Chapters 1--8). Section 10 is the cross-section audit. Section 11 is
the overall gate. Section 12 is the prioritised remediation plan with word budgets.

Finding identifiers use the prefix `SFR-` (supervisor-feedback review) plus a section code, which
avoids collision with the prior `LIT-COMP-*`, `CH2-*`, `DISC-SUP-*`, `STRUCT-*`, `ABSTRACT-*`,
`AI-*` and `LAYOUT-*` schemes. Two prior identifiers (`AI-DISC-001`, `AI-PERM-001`) are preserved
rather than renumbered because they remain live.

### Supervisor feedback axes tracked throughout

| Axis | Supervisor point | Primary findings |
|---|---|---|
| S1 | Focus on what was actually validated (scope creep is blocking) | `SFR-XS-001`, `SFR-DISC-002`, `SFR-SYS-002`, `SFR-RES-003` |
| S2 | Business problem, users, as-is process, why multi-agent rather than something simpler | `SFR-XS-002`, `SFR-INTRO-001` |
| S3 | Literature review and technical sections lack logical flow and are hard to read | `SFR-LIT-001`, `SFR-LIT-002`, `SFR-SYS-001` |
| S4 | Remove repeated limitations | `SFR-GOV-002`, `SFR-CONC-001` |
| S5 | Move large tables to appendices; add worked accepted/rejected claim examples | `SFR-XS-006`, `SFR-XS-005`, `SFR-RES-005` |
| S6 | Practical business pilot: integration, costs, staff, time savings, success metrics, remaining testing | `SFR-DISC-001` |
| U1 | Register and audience: plain British English for a non-technical reader | `SFR-ABS-001`, `SFR-SYS-001`, `SFR-LIT-002` |
| U2 | Scoping to the implementation, not generic AI-dissertation filler | `SFR-DISC-002`, `SFR-LIT-001` |
| U3 | Direct, traceable RQ addressing | `SFR-RES-001`, `SFR-ABS-001`, `SFR-CONC-001` |
| U4 | Expand the academic literature review | `SFR-LIT-001` |

---

## 1. Abstract

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Abstract"
  section_type: "abstract"
  round: 2
  scope: "Dissertation/frontmatter/abstract.tex (374 citation-stripped words)"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 1
    minor: 2
    optional: 0
  previous_findings:
    resolved: 2
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: dissertation-expert
```

### 1.1 Decision

**REVISE.** The Abstract is factually accurate and every reported number reproduces exactly from the
saved evaluation output, but it is written for a technical reader: the headline result is expressed in
undefined classification metrics and the research questions it is supposed to preview are never stated.

### 1.2 Scope and evidence consulted

- `Dissertation/frontmatter/abstract.tex`.
- `var/evaluation/smoke.json` (saved D0 output) for every numeric claim.
- `fixtures/evaluation_cases.json` (SHA-256 `f403d59e…c94b`, 14 cases) for the fixture description.
- `Dissertation/REPORT_STRUCTURE.md` for the active research contract.
- `Dissertation/reviews/REVIEW_LOG.md` for prior `ABSTRACT-001` and `ABSTRACT-002`.

Verified: the Abstract's C1 figures (precision 0.455, F1 0.625, source-record completeness 0.818,
unsupported-claim rate 0.545) and C2 figures (1.000 / 1.000 / 1.000 / 0.000) match the saved summaries
for conditions `deterministic_single_agent` and `multi_agent_verification` exactly. The fourteen-case
count, three repeats and zero model cost also match. Evidence status: `VERIFIED`.

### 1.3 Blocking findings

#### `SFR-ABS-001` — `MAJOR` — Abstract is unreadable for the intended non-technical audience and omits the research questions

- **Status:** `NEW`
- **Location:** `frontmatter/abstract.tex`, paragraph 2 ("The prototype is a local Next.js dashboard…")
  and paragraph 3 ("Precision, recall, F1 and source-record completeness were 1.000…").
- **Criterion:** Abstract rubric — "report the principal results with calibrated wording" and
  "stand alone"; user requirement U1 (plain British English for a non-technical reader); U3 (direct RQ
  addressing).
- **Problem:** Three separate barriers. First, the principal result is stated only as
  `precision`, `recall`, `F1` and `source-record completeness` with no plain-English gloss; a
  non-technical business reader cannot tell from paragraph 3 what actually improved. Second, paragraph 2
  opens on four unexplained product and technology names (`Next.js`, `FastAPI`, `SQLite`, and later
  `file checksum`) before the reader has been told what the system does. Third, the Abstract never
  states the research questions, although `REPORT_STRUCTURE.md` makes RQ1 and RQ2 the active research
  contract and the Abstract is the reader's only summary of it.
- **Why it matters:** The Abstract is the most-read part of the dissertation and, for an examiner, sets
  expectations for the whole report. As written, the strongest genuine finding — that adding a separate
  checking stage stopped six of eleven unsupported statements from reaching the report — is buried
  inside metric names. The supervisor's register complaint is most visible here.
- **Evidence:** `frontmatter/abstract.tex` lines 6 and 8. Glossary (`frontmatter/glossary.tex`) contains
  15 entries and defines none of `precision`, `recall`, `F1`, `Next.js`, `FastAPI`, `SQLite` or
  `checksum`. `REPORT_STRUCTURE.md` lines 18--28 state the primary question and RQ1/RQ2.
- **Required revision:** Add one plain-English sentence stating the result in counts before the metric
  sentence (the counts 11 emitted / 5 correct for C1 and 5 emitted / 5 correct for C2 are already
  verified and available). Gloss the metric names once, in parenthesis, on first use. Replace the
  bare technology list with a one-clause description of what the software is for, moving the stack names
  to a subordinate clause. Add one sentence naming the two research questions in plain terms.
- **Acceptance condition:** A reader who does not know what `precision` or `F1` mean can state, from the
  Abstract alone, (a) what the two research questions are, (b) what the system was asked to do, and
  (c) what changed between the two tested conditions, expressed in counts of claims. Metric names are
  each glossed at first use. Word count stays within 400.

### 1.4 Prior-finding reconciliation

| Finding | Previous severity | Status | Verification |
|---|---:|---|---|
| ABSTRACT-001 | (per `REVIEW_LOG.md`) | RESOLVED | The Abstract now confines results to D0 and explicitly denies real-portfolio, superiority, effort and production claims (line 10). |
| ABSTRACT-002 | (per `REVIEW_LOG.md`) | RESOLVED | The removed manual, participant, live-web and managed-platform comparisons are declared as prospective rather than reported (line 10). |

### 1.5 Non-blocking notes

- **MINOR — `SFR-ABS-M1`:** Paragraph 4 lists five things the dissertation does not establish. This is
  correct but it is the fourth consecutive negative statement in a 374-word abstract. One consolidated
  sentence would carry the same protection.
- **MINOR — `SFR-ABS-M2`:** "GBP 100 claim contradicted by GBP 200 evidence" (line 8) is a good concrete
  example but arrives without saying it is a fictional test case; the word "fictional" appears earlier in
  the paragraph and could be repeated here to prevent a skim-reader mistaking it for a real company.

### 1.6 Section-level assessment

- **Purpose and alignment — partly meets.** Problem, method, result and limitation are all present; the
  research questions are not.
- **Evidence and accuracy — meets.** Every number reproduces from `var/evaluation/smoke.json`.
- **Critical analysis — meets.** The scope boundary is explicit and calibrated.
- **Structure and coherence — meets.** Four paragraphs move problem → artefact → result → boundary.
- **Academic style — does not meet.** Undefined metrics and an unexplained technology stack breach the
  stated non-technical-reader requirement.

### 1.7 Handoff

Resolve `SFR-ABS-001`. Do not add any new number; the required counts already exist in
`var/evaluation/smoke.json` and in Chapter 5.

---

## 2. Chapter 1 — Introduction

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 1 - Introduction"
  section_type: "introduction"
  round: 2
  scope: "Dissertation/chapters/01_introduction.tex (1,387 citation-stripped words); exhibits/intro_t1_research_contract.tex"
  evidence_confidence: MEDIUM
  findings:
    blocker: 0
    major: 1
    minor: 2
    optional: 1
  previous_findings:
    resolved: 0
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: dissertation-expert
```

Chapter 1 is also the joint primary location for the cross-section blocker `SFR-XS-002`
(multi-agent justification). Its gate cannot pass while that blocker stands.

### 2.1 Decision

**REVISE.** Chapter 1 states a clear aim, a coherent research contract and an honest scope narrowing,
but the business problem that motivates the whole dissertation rests on a single internal project note,
has no quantified as-is baseline, no worked example and no figure, and the chapter never asks why a
role-separated system is needed rather than something simpler.

### 2.2 Scope and evidence consulted

- `chapters/01_introduction.tex` and `exhibits/intro_t1_research_contract.tex`.
- `docs/PROJECT_CHARTER.md` (the cited source for the business process).
- `data/README.md`, `docs/`, `fixtures/`, `research/` searched for a primary stakeholder artefact.
- `Dissertation/sources/CLAIM_LEDGER.md` rows `1.1-P1`--`1.6-P1`.
- `Dissertation/exhibits/MERMAID_MANIFEST.csv` and `exhibits/*.png`.

**Material evidence expected but unavailable:** no stakeholder transcript, meeting record, reporting
workbook, sample of an existing report, or any record of reporting volume, frequency, staff time or
error rate exists anywhere in the repository. `docs/PROJECT_CHARTER.md` refers to "the supplied
materials and stakeholder transcript" and "the workbook", but neither artefact is present.
`data/README.md` confirms such material is deliberately excluded from version control.

### 2.3 Blocking findings

#### `SFR-INTRO-001` — `MAJOR` — The business problem, users and as-is process rest on one internal note, with no baseline, no worked example and no figure

- **Status:** `NEW`
- **Location:** §1.1 "Early-stage portfolio reporting and company intelligence", paragraph 1 ("The
  verified project charter describes three broad reporting activities…") and
  Table 1.1 `tab:intro-business-process`, including its source note.
- **Criterion:** Introduction rubric — "establish the concrete research context and problem" and
  "explain why the problem matters"; evidence hierarchy (a project note is the lowest-ranked evidence
  class); supervisor point S2.
- **Problem:** Everything the reader learns about the business problem, the users and the current
  process comes from `docs/PROJECT_CHARTER.md`, which is a project note the student wrote. The
  chapter's own source note concedes that "the repository evidence does not establish reporting
  frequency, labour cost, error rate or job title". The result is a three-row process table with no
  volumes, no cycle time, no error baseline, no named user need and no example of a current report. The
  chapter then substitutes published literature about register quality and citation support for evidence
  about *this* organisation's problem. Chapter 1 also contains no figure at all, even though
  `exhibits/intro_f1_problem_to_research_contract.png` is a current, rendered, checksum-bound figure in
  `MERMAID_MANIFEST.csv` that is never used anywhere in the manuscript.
- **Why it matters:** The supervisor asked specifically for a clear explanation of the business problem,
  the users and the as-is process. Without a baseline or a worked example, the reader cannot judge
  whether the risks the dissertation addresses (wrong company, blank versus zero, wrong period,
  unresolved conflict, unsupported claim) actually occur, or how often. This weakens the motivation for
  the entire artefact and leaves the later pilot plan (§6.7) with nothing to be compared against.
- **Evidence:** `chapters/01_introduction.tex` lines 4--11 and 31--33; `docs/PROJECT_CHARTER.md`
  lines 29--47 (the "Problem definition" section, which is itself qualitative);
  `docs/PROJECT_CHARTER.md` line 103 ("No invented acceptance thresholds, baseline timings, participant
  results, or costs"); absence of any primary artefact confirmed by search across `docs/`, `data/`,
  `fixtures/`, `research/`; `exhibits/MERMAID_MANIFEST.csv` line 2.
- **Required revision:** Three connected changes, none of which invents data. (a) State explicitly and
  early that the as-is process description derives from a project charter based on supplied materials
  that cannot be reproduced in the dissertation, and that no volume, time or error baseline was
  available — this converts a hidden weakness into a declared scope boundary. (b) Add one short worked
  walk-through of a single reporting case through the three current stages, using the existing
  synthetic fixture (`fixtures/synthetic_portfolio.json`) and labelling it as illustrative, so a
  non-technical reader can see the problem rather than read a table about it. (c) Place
  `intro_f1_problem_to_research_contract.png` in §1.1 or §1.4 so the chapter has one visual anchor
  linking the business problem to the research contract.
- **Acceptance condition:** §1.1 contains an explicit statement of what business evidence was and was
  not available and its source class; one illustrative end-to-end reporting case appears in Chapter 1,
  labelled as synthetic; Chapter 1 references at least one figure; and no quantitative baseline claim
  (frequency, hours, cost, error rate) appears anywhere without a repository artefact behind it.

### 2.4 Prior-finding reconciliation

No prior finding was recorded specifically against Chapter 1 in the reviews folder;
`SECTION_1_1_REVIEW.md`--`SECTION_1_6_REVIEW.md` predate the 31 August revision and, per
`audit/SECTION_LEDGER.md`, "do not approve wording changed in this revision". All six Chapter 1
sections are recorded as `PENDING`.

### 2.5 Non-blocking notes

- **MINOR — `SFR-INTRO-M1`:** §1.4 "Scope narrowing" says "Chapter~7 records this limitation once", but
  the same limitation is restated in §1.5, §3.1, §3.2, §5.7, §6.6 and §8.1. See `SFR-GOV-002`.
- **MINOR — `SFR-INTRO-M2`:** `OCR` is expanded on first use (§1.1) but is absent from the glossary,
  while `HITL`, `OOS` and standalone `RQ` are in the glossary and never used in the body.
- **OPTIONAL — `SFR-INTRO-O1`:** The four objectives O1--O4 are given as a run-on paragraph in §1.4. A
  short list would help a reader map them to the chapters, at no word cost.

### 2.6 Section-level assessment

- **Purpose and alignment — partly meets.** Aim, questions, objectives, scope and roadmap are present and
  mutually consistent; the problem's grounding is weak.
- **Evidence and accuracy — partly meets.** Literature claims are traceable through `CLAIM_LEDGER.md`;
  the business-process claims rest on a self-authored note.
- **Critical analysis — partly meets.** The scope narrowing is handled well and honestly; the chapter
  never weighs design alternatives.
- **Structure and coherence — meets.** Six sections progress cleanly from context to roadmap.
- **Citations and scholarship — meets.** All cited keys resolve to verified local PDFs.
- **Academic style — meets.** Chapter 1 is the most readable chapter in the report; mean sentence length
  is 16.1 words and no sentence exceeds 30 words.
- **Tables and figures — partly meets.** Table 1.1 is well captioned and honestly annotated; the chapter
  has no figure despite one being available.

### 2.7 Handoff

Resolve `SFR-INTRO-001` and, jointly with Chapter 6, the cross-section blocker `SFR-XS-002`.

---

## 3. Chapter 2 — Literature Review

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 2 - Literature Review"
  section_type: "literature review"
  round: 4
  scope: "Dissertation/chapters/02_literature_review.tex (3,293 citation-stripped words); exhibits lit_t2, lit_t3, lit_t4, lit_t5; figures lit_f1, lit_f2"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 2
    minor: 2
    optional: 1
  previous_findings:
    resolved: 3
    partially_resolved: 1
    unresolved: 1
    regression: 0
    user_waived: 0
  next_owner: dissertation-expert
```

### 3.1 Decision

**REVISE.** Chapter 2 is well sourced and honest, but it is a statement of the project's design criteria
rather than a critical synthesis of prior research, and its paragraph construction actively obstructs
reading: 31 of its 36 substantive paragraphs end on a prohibition rather than a link to the next idea.
Both are the specific problems the supervisor raised.

### 3.2 Scope and evidence consulted

- `chapters/02_literature_review.tex` in full, and all four embedded exhibits.
- `Dissertation/references.tex` (45 entries) and `Dissertation/sources/REFERENCE_AUDIT.md`.
- `Dissertation/sources/MANIFEST.csv` (48 admitted sources) and the 42 local PDFs in `sources/papers/`.
- `Dissertation/sources/CLAIM_LEDGER.md` rows `2.1-P1`--`2.7-P5`.
- `Dissertation/sources/html/spacexai_grok_bot_bots.pdf` (read in full, 6 pages).
- Prior reports `CHAPTER_2_COMPREHENSIVENESS_REVIEW.md`, `SECTION_2_1_REVIEW.md`--`SECTION_2_7_REVIEW.md`.
- Citation-frequency analysis across the Abstract, all chapters and all exhibits.

Verified: the `spacexai2026grokbot` citation is **not** fabricated. The local capture is a genuine
six-page vendor documentation print ("Create and manage Bots | SpaceXAI Docs", last updated
22 August 2026) and pages 3--5 do support the attributed description of named Bots with distinct jobs,
tools and sources, working context, hand-offs and approval boundaries. Evidence status: `VERIFIED`.

### 3.3 Blocking findings

#### `SFR-LIT-001` — `MAJOR` — The chapter states design criteria rather than synthesising prior research, and three admitted, verified sources that would close the gaps are unused

- **Status:** `NEW`
- **Location:** Whole chapter; most visible in §2.3 (paragraph ending "These categories are a project
  design choice, not a general standard from the literature"), §2.4 (paragraph ending "These fields are
  project choices"), §2.5 (all five paragraphs) and §2.6 paragraphs 1--4.
- **Criterion:** Literature review rubric — "organise literature around themes, debates, methods, or
  evidence"; "compare approaches, assumptions, strengths, weaknesses"; "critical synthesis rather than a
  sequence of source summaries". Supervisor point S3/U4 (expand the academic literature review);
  user requirement U2 (grounded, not generic).
- **Problem:** The chapter's dominant paragraph shape is *[what the literature says] → [therefore this
  project does X] → [but this does not prove Y]*. Thirteen of 36 paragraphs contain an explicit
  project-design or prescriptive sentence, eleven of those also carry a disclaimer, and the chapter
  repeatedly concedes that its own categories are project choices rather than positions in a debate.
  There is no genuine disagreement between sources anywhere in the chapter: no two cited works are
  placed in tension, no methodological dispute is adjudicated, and no research finding is criticised on
  its merits. Concretely, five thematic gaps are present:
  1. **Multi-agent LLM systems.** The design decision at the heart of the dissertation is supported by
     one survey (`guo2024multiagent`), one framework paper (`wu2024autogen`), one trace analysis
     (`cemri2025masfailures`, used twice in the chapter) and one tool paper
     (`dibia2024autogenstudio`, used once). There is no primary empirical study of multi-agent
     performance, no literature on self-verification or model-as-checker designs, and no agentic
     evaluation benchmark. The only empirical multi-agent source, `cemri2025masfailures`, is used
     exclusively as an argument *against* the chosen architecture.
  2. **Verification and attribution.** `huang2023hallucination` is cited three times in the whole
     report; there is no automated claim-verification or fact-checking literature beyond
     `gao2023alce` and `gao2023rarr`.
  3. **Evidence provenance.** `buneman2001provenance` (a 2001 database-theory paper) is the sole
     provenance source, cited five times. There is no lineage-in-practice, audit-trail or
     provenance-standard literature.
  4. **Design science.** `hevner2004design` is cited 21 times across the report and **zero** times in
     Chapter 2. The methodological paradigm that governs the whole study is therefore never reviewed.
  5. **Governance and XAI.** `cddo2023genai` (13 uses) and `autio2024genai` (6 uses) are cited **zero**
     times in Chapter 2. Governance appears only as assertion in Chapters 4 and 7, never as reviewed
     literature.

  Separately, citation weight is concentrated on two procedural warrants:
  `pineau2021reproducibility` (57 uses) and `nist2023airmf` (51 uses) together account for roughly a
  quarter of all citation instances in the report, largely as generic reproducibility and risk
  boilerplate rather than as substantive literature.
- **Why it matters:** The supervisor asked for the academic literature review to be expanded, and an MSc
  literature review is assessed on critical synthesis. A chapter that only derives requirements cannot
  demonstrate that skill, and it leaves the central design choice without a literature warrant.
- **Evidence:** Citation-frequency analysis across `frontmatter/abstract.tex`, `chapters/*.tex` and
  `exhibits/*.tex`. Keys absent from Chapter 2: `artstein2008agreement`, `autio2024genai`,
  `cddo2023genai`, `demsar2006comparisons`, `diciccio1996bootstrap`, `gale2013framework`,
  `hevner2004design`, `openai2026datacontrols`. **Three sources are already admitted, checksum-verified
  and present locally but cited nowhere** (confirmed by comparing `sources/MANIFEST.csv` against
  `references.tex`):
  - `ribeiro2020checklist` — Ribeiro et al. (2020), *Beyond accuracy: Behavioral testing of NLP models
    with CheckList*, ACL 2020, `sources/papers/34_ribeiro_checklist.pdf`, 11 pages, admission role
    `direct-method`. The manifest note already reads "Behavioural test methodology; project adversarial
    cases remain constructed mechanism checks."
  - `sculley2015debt` — Sculley et al. (2015), *Hidden technical debt in machine learning systems*,
    NIPS 2015, `sources/papers/22_sculley_ml_technical_debt.pdf`, 9 pages, admission role
    `direct-method`.
  - `souppaya2022ssdf` — NIST SP 800-218, *Secure Software Development Framework v1.1*,
    `sources/papers/23_nist_ssdf_800_218.pdf`, 36 pages, admission role `authoritative-guidance`.
- **Required revision:** Do not add unverified sources. Close the gaps in this order, using material
  already admitted. (a) Introduce `ribeiro2020checklist` in §2.5 or §2.6 as the established paradigm for
  behavioural, capability-targeted test suites; this gives D0 a named methodological lineage and is the
  single highest-value addition available. (b) Introduce `sculley2015debt` in §2.6 to give the
  "more roles means more operational state and maintenance" trade-off an actual literature warrant
  instead of an assertion. (c) Introduce `souppaya2022ssdf` where secure-development practice is
  claimed. (d) Bring `hevner2004design`, `cddo2023genai` and `autio2024genai` into Chapter 2 so that
  design science and AI governance are reviewed, not merely invoked later. (e) Create at least three
  genuine points of tension between existing sources — for example `guo2024multiagent`'s case for role
  decomposition against `cemri2025masfailures`'s empirical failure taxonomy; `gao2023alce`'s citation
  metrics against `gao2023rarr`'s revision approach; and `krasikov2020ready` against
  `nikiforova2020quality` on whether register data fitness is a property of the data or of the task.
  (f) Reduce reliance on `pineau2021reproducibility` and `nist2023airmf` as end-of-paragraph warrants.
- **Acceptance condition:** Chapter 2 cites `ribeiro2020checklist`, `sculley2015debt` and
  `hevner2004design`; contains at least three passages where two cited sources are explicitly placed in
  tension and the chapter adjudicates between them; each of the five thematic gaps above is either
  addressed or its absence is explicitly declared as a review boundary; and no paragraph's only
  analytical move is deriving a project rule from a source.

#### `SFR-LIT-002` — `MAJOR` — Paragraph and exhibit construction obstruct reading: paragraphs end in dead ends, motivation is buried, and two unreferenced full-page tables interrupt the argument

- **Status:** `NEW`
- **Location:** Whole chapter. Specific locations: paragraph endings throughout (see evidence);
  §2.2.1 "Sector importance and existing reporting approaches" (line 66); the `\input` of
  `lit_t2_signal_inference_boundary.tex` at line 104 and `lit_t3_data_semantics_matrix.tex` at line 150;
  §2.1 (lines 4--28) and §2.7 (lines 310--353).
- **Criterion:** Structure and coherence rubric — "each paragraph has one controlling purpose and
  connects to the next"; "signposting is useful but not repetitive". Supervisor point S3; user
  requirement U1.
- **Problem:** Four compounding mechanical causes, all measurable:
  1. **Paragraphs terminate in prohibitions.** 31 of 36 substantive paragraphs end on a negation or a
     ban — "do not prove company quality", "cannot prove future success", "must not be merged
     automatically", "is not enough to pass either check", "It is never filled in from model memory",
     "More roles are not presumed better", "Agent, message or conversation counts are not task-success
     measures". Only paragraphs 3 and 36 hand off to what follows. A reader therefore finishes every
     paragraph at a stop sign and has to restart the thread 36 times. This single pattern is the most
     likely direct cause of the supervisor's "lacks logical flow and is hard to read".
  2. **Motivation is buried mid-chapter.** The sector's material importance, the monitoring-workload
     evidence and the entire commercial-product landscape sit in §2.2.1 — a subsection, the only one in
     the chapter, reached after the crowdfunding and register material. The reader meets the market
     context and the existing tools *after* being told what evidence cannot support.
  3. **Two full-page tables break the argument and are never referenced.** `lit_t2` (366 words) and
     `lit_t3` (397 words) are both `[p]` floats wrapped in `\clearpage`, so each forces a page break,
     and neither is referred to anywhere in the prose. `lit_t4` (458 words) is referenced once.
     Together the four Chapter 2 tables carry 1,456 words of tabular content.
  4. **Bookend overhead.** §2.1 (267 words) previews the chapter's structure and §2.7 (397 words)
     re-summarises the same material — 664 words, 20 per cent of the chapter, spent on framing rather
     than on literature.
- **Why it matters:** These are mechanical, fixable causes of an assessed weakness. The chapter's content
  is largely sound; its readability is not, and the supervisor named exactly this chapter.
- **Evidence:** Extraction of the final sentence of all 36 substantive paragraphs (31 end on a negation
  or prohibition). Exhibit reference audit: `tab:signal-inference-boundary` and
  `tab:data-semantics-matrix` have `\label` definitions but no `\ref` anywhere in
  `chapters/*.tex` or `frontmatter/*.tex`. `exhibits/lit_t2_signal_inference_boundary.tex` lines 1--2 and
  49--50 (`\clearpage` … `[p]` … `\clearpage`); same structure in `lit_t3`. Section word counts from
  `audit/SECTION_LEDGER.md`.
- **Required revision:** (a) Rewrite the final sentence of each paragraph so it advances or hands off;
  move the necessary prohibitions into the sentence where the risk is introduced, or into the single
  consolidated limitations location required by `SFR-GOV-002`. Retain at most six prohibition endings in
  the chapter. (b) Move §2.2.1's sector-importance and commercial-product material to the front of the
  chapter, or to Chapter 1 where it supports `SFR-INTRO-001`. (c) Either reference `lit_t2` and `lit_t3`
  in the prose and justify their full-page cost, or move them to an appendix — see `SFR-XS-006`.
  (d) Compress §2.1 and §2.7 to roughly 380 words combined, keeping the RQ-linked gap statement in §2.7.
- **Acceptance condition:** No more than six of Chapter 2's paragraphs end on a negation or prohibition;
  every table that remains in the chapter body is referenced in the prose at the point where it is
  needed; §2.1 plus §2.7 total no more than 420 words; and the sector-importance material appears before
  the first evidence-boundary discussion.

### 3.4 Prior-finding reconciliation

| Finding | Previous severity | Status | Verification |
|---|---:|---|---|
| LIT-COMP-003 | MAJOR | PARTIALLY_RESOLVED | `lit_t5` does compare five alternatives under common criteria and avoids superiority claims. However it was approved when it separated "RQ2 verification from RQ3 named human review"; RQ3 no longer exists, so the table's rationale has changed and its "Managed agent platform" row now supports scope creep (`SFR-DISC-002`). |
| CH2-REG-001 | MAJOR | UNRESOLVED (re-opened on new evidence) | The prior resolution rested on Chapter 2 being "3,201 words within … 14,000--16,000 words". Chapter 2 is now 3,293 words and the whole report measures 13,874 citation-stripped words, below the stated floor. See `SFR-XS-003`. Re-opened under re-review rule 7 (new evidence). |
| CH2-REG-002 | MAJOR | RESOLVED | `audit/SECTION_LEDGER.md` no longer inherits historical approvals; all 53 sections are recorded `PENDING`. |
| LIT-COMP-005 | MINOR | RESOLVED | `lit_t5`'s source note uses `\citet` author-date form and gives undated vendor entries no false year suffix. |
| LIT-COMP-006 | MINOR | UNRESOLVED | The forced-pagination whitespace persists by construction: `lit_t2` and `lit_t3` each retain `\clearpage` before and after a `[p]` float. Also recorded as `LAYOUT-001`. Resolution is now folded into `SFR-XS-006`. |
| CH2-R3-001 | MINOR | RESOLVED | Superseded by `SFR-XS-003`, which supplies a fresh count. |

**Independence note.** `CHAPTER_2_COMPREHENSIVENESS_REVIEW.md` (round 3) returned `gate: PASS` with
"Critical analysis — meets" and "Structure and coherence — meets". That gate was issued against a
draft with RQ1--RQ3 and a 3,201-word Chapter 2, and it is not sustainable for the current draft against
either the supervisor's feedback or the evidence in `SFR-LIT-001` and `SFR-LIT-002`. It is treated as
void for this round.

### 3.5 Non-blocking notes

- **MINOR — `SFR-LIT-M1`:** §2.6 final paragraph states "Current SpaceXAI documentation describes Grok
  Bot as persistent named Bots…" with no inline citation; three keys are bunched at the paragraph end.
  The claim is verified against `sources/html/spacexai_grok_bot_bots.pdf` pp. 3--5, so this is placement
  only, but the attribution should sit with the sentence.
- **MINOR — `SFR-LIT-M2`:** `audit/SECTION_LEDGER.md` records §2.6 as having 4 substantive paragraphs;
  `sources/CLAIM_LEDGER.md` contains row `2.6-P5`. The chapter has five. One of the two ledgers is stale.
- **OPTIONAL — `SFR-LIT-O1`:** `RAG` and `LLM` are both expanded on first use in §2.5, which is good
  practice; the same treatment would help `abstention` (§2.7) and `schema` (§2.2.1).

### 3.6 Section-level assessment

- **Purpose and alignment — partly meets.** The chapter reaches an explicit RQ-linked gap, but spends
  much of its length deriving project rules.
- **Evidence and accuracy — meets.** Every cited key resolves to a verified local PDF, and vendor
  material is correctly confined to capability description.
- **Critical analysis — does not meet.** No two sources are placed in tension; no research finding is
  criticised on its merits.
- **Structure and coherence — does not meet.** 31 of 36 paragraphs end in a dead end; motivation is
  buried in the only subsection; two unreferenced full-page tables interrupt the chapter.
- **Citations and scholarship — partly meets.** Sound at the row level, but weight is concentrated on two
  procedural warrants and three admitted relevant sources are unused.
- **Academic style — partly meets.** Sentences are short and plain (mean 16.0 words); the relentless
  negation rhythm undermines readability more than vocabulary does.
- **Tables and figures — does not meet.** Two of four tables are unreferenced full-page floats.

### 3.7 Handoff

Resolve `SFR-LIT-001` then `SFR-LIT-002`; re-check `LIT-COMP-003`, `CH2-REG-001` and `LIT-COMP-006`.

---

## 4. Chapter 3 — Research Design and Methodology

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 3 - Research Design and Methodology"
  section_type: "methodology and experimental design"
  round: 2
  scope: "Dissertation/chapters/03_methodology.tex (1,128 citation-stripped words); exhibits meth_t1-t4; figure meth_f1"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 1
    minor: 2
    optional: 1
  previous_findings:
    resolved: 0
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: dissertation-expert
```

### 4.1 Decision

**REVISE.** Chapter 3 is the most methodologically honest part of the dissertation — the confirmation
risk, the co-design of labels and rules, the truncated timings and the null measures are all declared —
but the D0 design itself has no methodological warrant in the literature, and an admitted source that
would supply one is unused.

### 4.2 Scope and evidence consulted

- `chapters/03_methodology.tex` and the four appendix exhibits it points to.
- `fixtures/evaluation_cases.json` (14 cases, SHA-256 `f403d59e…c94b`) and
  `fixtures/evaluation_manifest.json` (SHA-256 `1c16234a…4254`).
- `var/evaluation/smoke.json` for the executed conditions and repeats.
- `sources/MANIFEST.csv` row `ribeiro2020checklist`.

Verified: the fixture contains exactly fourteen cases whose identifiers match the Appendix F ledger
one-for-one; the manifest declares D0 `executable`, D1 `protocol_only` and D2 `sealed`; the saved output
records `repeats: 3` and includes `manual` and `multi_agent_hitl` summaries with all-null values and
explanatory notes. Every methodological claim checked in this chapter is `VERIFIED`.

### 4.3 Blocking findings

#### `SFR-METH-001` — `MAJOR` — The D0 design has no methodological warrant, and the single-case-per-category limitation is stated but never justified

- **Status:** `NEW`
- **Location:** §3.3 "D0 fixture, labels and freeze", all three paragraphs; and §3.6 "Analysis and
  interpretation", paragraph 1.
- **Criterion:** Methodology rubric — "justify design choices and viable alternatives"; "state enough
  detail for a competent reader to reproduce the design". Supervisor point S1 (defend what was actually
  validated).
- **Problem:** §3.3 describes what D0 is (fourteen labelled fictional cases covering known error
  categories) and correctly concedes that "the rules and cases were developed together, so the result
  establishes only whether the programmed gate behaves as designed on these cases". What it never does
  is defend that design as a legitimate research instrument. There is no reference to any established
  paradigm for constructing targeted behavioural test suites, so the reader is left with the impression
  that D0 is an ad hoc development fixture that happens to have been measured. The chapter also never
  addresses why one case per error category is the right number, what that implies for the reported
  rates, or why fourteen cases were chosen rather than, say, five per category. Chapter 5 later observes
  that "each category has only one case, so the result cannot describe a wider distribution", but that
  is a consequence stated in the results, not a design decision defended in the methodology.
- **Why it matters:** D0 is the only executed evaluation in the dissertation. If its design is not
  defended, the single empirical contribution rests on an undefended instrument, and an examiner can
  reasonably ask why a co-designed fourteen-case fixture counts as evaluation at all. A named paradigm
  converts the same fixture from a weakness into a deliberate method.
- **Evidence:** `chapters/03_methodology.tex` lines 54--74; `chapters/05_evaluation_results.tex`
  lines 110--112. `sources/MANIFEST.csv` admits `ribeiro2020checklist` (*Beyond accuracy: Behavioral
  testing of NLP models with CheckList*, ACL 2020, 11 pages, SHA-256 `98d15d25…b00e1`,
  `sources/papers/34_ribeiro_checklist.pdf`) with the admission role `direct-method` and the note
  "Behavioural test methodology; project adversarial cases remain constructed mechanism checks". The key
  appears in no `\cite` command anywhere in the manuscript.
- **Required revision:** Add a short passage in §3.3 that names capability-targeted behavioural testing
  as the paradigm D0 instantiates, citing `ribeiro2020checklist`, and state plainly what that paradigm
  does and does not license — that it tests whether specified behaviours hold on constructed cases, and
  that it is not a sample from a population. Then state the case-per-category decision as a decision:
  one case per category, chosen for coverage breadth over within-category depth, with the explicit
  consequence that no category-level rate is estimable. Do not add any new number or claim.
- **Acceptance condition:** §3.3 cites `ribeiro2020checklist` (or an equivalent already-admitted
  methodological source), names the paradigm, and states the single-case-per-category choice as a
  justified design decision with its consequence for interpretation. `sources/REFERENCE_AUDIT.md` and
  `references.tex` are updated for any newly cited key.

### 4.4 Prior-finding reconciliation

`SECTION_3_1_REVIEW.md`--`SECTION_3_7_REVIEW.md` predate the 31 August revision and carry no unresolved
finding identifiers. All seven Chapter 3 sections are `PENDING` in `audit/SECTION_LEDGER.md`.

### 4.5 Non-blocking notes

- **MINOR — `SFR-METH-M1`:** §3.1 lists "versioned code and fixtures" as a confirmation-risk control.
  `git log` shows `HEAD` at `6356aa4` "Diss report up to 4.8", and Chapter 5 confirms the working tree
  was dirty, so the reviewed Chapters 4.9--8 and the whole 31 August revision are uncommitted. The
  control is not currently satisfied for the reviewed manuscript. Related to `SFR-RES-002`.
- **MINOR — `SFR-METH-M2`:** §3.5 states "Contradiction accuracy has two applicable cases and is
  interpreted as a small case result, not a stable rate". This is exactly right, and it is contradicted
  once in §5.8 — see `SFR-RES-004`.
- **OPTIONAL — `SFR-METH-O1`:** `exhibits/meth_f2_dataset_freeze_timeline.png` and
  `exhibits/meth_f3_analysis_decision_flow.png` are current in `MERMAID_MANIFEST.csv` but unused. The
  freeze timeline in particular would carry §3.3 more efficiently than prose.

### 4.6 Section-level assessment

- **Purpose and alignment — meets.** Each method is tied to RQ1 or RQ2, and the removed conditions are
  explicitly excluded from the active questions.
- **Evidence and accuracy — meets.** Fixture, manifest, condition and repeat claims all verify against
  repository artefacts.
- **Methodological validity — partly meets.** Leakage, co-design, confirmation risk, truncated timings
  and null measures are handled properly; the instrument itself is undefended.
- **Critical analysis — meets.** The chapter argues against its own strength more than it needs to.
- **Structure and coherence — meets.** Seven sections move from strategy to ethics coherently.
- **Academic style — meets.** Plain and precise; mean sentence length 15.5 words.
- **Reproducibility — partly meets.** Fixture and manifest checksums verify; the code-versioning control
  does not hold in the current working tree.

### 4.7 Handoff

Resolve `SFR-METH-001`.

---

## 5. Chapter 4 — System Design and Implementation

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 4 - System Design and Implementation"
  section_type: "system design and implementation"
  round: 2
  scope: "Dissertation/chapters/04_system_design.tex (2,941 citation-stripped words); exhibits sys_t1-t3, sys_f5; figures sys_f1-f4"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 2
    minor: 4
    optional: 1
  previous_findings:
    resolved: 0
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: dissertation-expert
```

### 5.1 Decision

**REVISE.** Chapter 4's implementation claims verify against the repository, but the chapter is written
as a requirements-traceability document rather than as a dissertation chapter, and it describes a system
version that was never evaluated. It is the clearest instance of the register problem the user raised.

### 5.2 Scope and evidence consulted

- `chapters/04_system_design.tex` in full.
- `docs/REQUIREMENTS.md` for all seven cited requirement identifiers.
- `docs/ARCHITECTURE.md`, `docs/AGENT_CONTRACTS.md`, `docs/IMPLEMENTATION_TRACEABILITY.md`.
- `src/portfolio_agent/` (including `config.py`, `bootstrap.py`, `experiments.py`, `cli.py`,
  `llm/experiment.py`), `alembic/`, `compose.yaml`, `Dockerfile`, `dashboard/AGENTS.md`.
- `frontmatter/glossary.tex`; acronym extraction across all chapters.

Verified: all seven requirement identifiers cited in Chapter 4 exist in `docs/REQUIREMENTS.md` with the
meanings the chapter gives them — `NFR-SEC-001` (loopback binding, line 125), `FR-UI-003` (Next.js-only
publication, non-private client and Host rejection, CSRF, line 114), `FR-INT-001` (number-only intake
with identity hold, line 161), `FR-RES-001` (idempotent research run for a reviewed number, line 175),
`FR-EXT-005` (opt-in external model, public/synthetic only, `store=False`, line 67), `FR-REP-005`
(export blocked without approval, line 102), `FR-RES-007` (named approval with optimistic locking and
content-hash verification, line 181). Evidence status: `VERIFIED`.

### 5.3 Blocking findings

#### `SFR-SYS-001` — `MAJOR` — The chapter is written as a requirements-traceability document and is not readable by the stated non-technical audience

- **Status:** `NEW`
- **Location:** §4.1 "Requirements and trust boundaries" (all three paragraphs), §4.3 "Shared data
  definitions, storage and source records" (paragraphs 2--5), §4.4 paragraph 4, §4.6 paragraphs 3--4.
- **Criterion:** System design rubric — "explain the architecture only to the extent it supports the
  research method, reproducibility, or contribution"; "explain their significance". User requirement U1
  (plain British English for a non-technical reader outside designated technical sections);
  academic-style rubric — "unexplained acronyms or specialist terms".
- **Problem:** The problem is not sentence length; the chapter's mean sentence is 17.2 words. It is
  information density and unglossed vocabulary. Three measurable causes:
  1. **Requirement identifiers used as prose subjects.** §4.1 opens "Requirement NFR-SEC-001 limits the
     server binding, while FR-UI-003 rejects non-local clients and unexpected host headers… FR-INT-001
     allows a Companies House number without a name or website; however, FR-RES-001 requires that
     identifier to receive named review". Seven such identifiers appear in the chapter; none is
     explained, none is in the glossary, and the matrix that decodes them is in Appendix C. A reader
     must hold four opaque codes in mind to follow the first paragraph.
  2. **Twenty-plus specialist acronyms absent from the glossary.** The glossary has 15 entries. Used in
     the body but undefined: `CLI`, `CSRF`, `CSV`, `DNS`, `HTML`, `HTTPS`, `IP`, `JSON`, `MIME`, `ORM`,
     `PDF`, `TLS`, `UKRI`, `XLSX`, plus the seven `FR-`/`NFR-` codes. Undefined technology and
     technique names include `FastAPI`, `SQLite`, `Next.js`, `Alembic`, `optimistic lock`,
     `create-once`, `append-version`, `staged write`, `tenant isolation`, `egress isolation`,
     `foreign keys`, `robots` and `fingerprint`. Meanwhile `HITL`, `OOS` and standalone `RQ` occupy
     glossary rows and never appear in the body.
  3. **Noun-stacked clauses with no explanatory frame.** For example §4.3: "Connector snapshots record
     source and version, reviewed identifier, cutoff, locator, media type, checksum, retrieval and
     publication times, and classification." That is a nine-item field list presented as prose. §4.6
     paragraph 4 is a five-way enumeration of failure state names (`no_record`, `source_unavailable`,
     policy block, typed missing state, `failed`) with no statement of why the distinction matters to
     the research argument.
- **Why it matters:** Chapter 4 is 2,941 words, 21 per cent of the report, and the user's explicit
  requirement is that the report read like an MSc student's work aimed at a non-technical reader outside
  designated technical sections. As written, a business reader cannot extract what the system does or
  why any of it matters to RQ1. The implementation detail is also largely disconnected from the
  evaluation: D0 exercises the catalogue, normalisation, evidence eligibility and verifier only, so the
  connector registry, public-web route, export pipeline and network controls receive extensive
  description without contributing to either research question.
- **Evidence:** `chapters/04_system_design.tex` lines 4, 33, 35, 51, 57, 95;
  `frontmatter/glossary.tex` lines 9--18; acronym extraction across `chapters/*.tex` and
  `frontmatter/abstract.tex`; sentence-length analysis (Chapter 4 mean 17.2 words, only 3 of 172
  sentences at or above 35 words, confirming density rather than length is the cause).
- **Required revision:** (a) Replace requirement identifiers in prose with what they require, and keep
  the identifier in parentheses at most once per section — "the server accepts connections only from the
  same computer (`NFR-SEC-001`)". (b) Open each of §4.1--§4.9 with one plain sentence stating what the
  section's mechanism protects against in business terms, before any technical detail. (c) Extend the
  glossary to cover every acronym and specialist term actually used, and remove the three unused
  entries. (d) Convert the longest field lists into either a plain summary sentence naming the purpose
  plus a pointer to the appendix table, or into the appendix table alone. (e) State explicitly, once,
  which implemented components the D0 evaluation exercises and which it does not, so the reader knows
  which parts of the chapter carry evaluated weight.
- **Acceptance condition:** No requirement identifier appears as the grammatical subject of a sentence;
  every acronym and specialist term used in the body is either glossed at first use or present in the
  glossary; each section of Chapter 4 opens with a non-technical purpose sentence; and Chapter 4
  contains one explicit statement of which components D0 exercised.

#### `SFR-SYS-002` — `MAJOR` — Chapter 4 describes a system version that was never evaluated, contradicting Chapter 3's single-evaluand claim

- **Status:** `NEW`
- **Location:** §4.3 paragraph 2 ("Alembic revisions 0001--0010 reproduce the ORM schema…") against
  §5.1 paragraph 2 ("the local system at migration 0009") and §5.2 ("A new SQLite database applied
  migrations 0001-0009").
- **Criterion:** System design rubric — "distinguish prototype, research code, and production
  capability"; "planned components described as completed"; Methodology §3.2 states "This binds each
  observation to one defined artefact version". Supervisor point S1.
- **Problem:** Chapter 4 describes the artefact at migration head 0010, including "company-research and
  reviewed group-scope records" added by later revisions. Chapter 5 evaluates migration 0009 and
  discloses the gap in a single subordinate sentence: "Later interface and schema revisions described in
  Chapter~4 were not part of this dated snapshot and add no empirical result." So the implementation
  chapter and the results chapter describe different artefacts, while Chapter 3 asserts that each
  observation is bound to one defined version. The reader is given no indication, while reading
  Chapter 4, which of the described mechanisms were in the evaluated build.
- **Why it matters:** Design science requires the evaluand to be identified. A 2,941-word description of
  version 0010 followed by results from version 0009 means the largest chapter in the dissertation is
  partly outside the evaluated scope, which is precisely the scope-creep concern the supervisor raised.
  One sentence of disclosure in a later chapter is not proportionate to the size of the gap.
- **Evidence:** `chapters/04_system_design.tex` line 33; `chapters/05_evaluation_results.tex`
  lines 11--13 and 25--26; `chapters/03_methodology.tex` lines 34--38.
- **Required revision:** State the version boundary once, prominently, at the start of Chapter 4: which
  migration head the chapter describes, which head was evaluated, and which described mechanisms are
  therefore outside the evaluated build. Mark the affected passages so a reader can see the boundary in
  place rather than discovering it in Chapter 5. Reconcile the wording in §3.2 so its single-evaluand
  claim is scoped to the evaluated build rather than the described one.
- **Acceptance condition:** Chapter 4 states its described migration head and the evaluated migration
  head in its opening section; every mechanism introduced only after 0009 is identifiable as outside the
  evaluated build; and §3.2's evaluand statement is consistent with that boundary.

### 5.4 Prior-finding reconciliation

`SECTION_4_1_REVIEW.md`--`SECTION_4_9_REVIEW.md` predate the 31 August revision. `RES-001` and
`NFR-RES-001` appearing in `SECTION_4_1_REVIEW.md` and `REVIEW_LOG.md` are requirement identifiers, not
review findings. All nine Chapter 4 sections are `PENDING`.

### 5.5 Non-blocking notes

- **MINOR — `SFR-SYS-M1`:** `audit/SECTION_LEDGER.md` titles §4.5 "Fixed portfolio workflow and
  independent verification"; the chapter heading reads "…and separate verification". The chapter's
  wording is the better one (the verifier is not independent in the human sense) and the ledger should
  follow it.
- **MINOR — `SFR-SYS-M2`:** §4.7 describes the public-web route in 401 words plus a figure, and closes
  by conceding "no live company, model or public-web run establishes coverage, accuracy, usefulness or
  superiority". The section is honest but is the largest single block of unevaluated material in the
  chapter. Related to `SFR-DISC-002`.
- **MINOR — `SFR-SYS-M3`:** §4.9 line 91 states "Only two deterministic adapters are usable, both through
  synthetic offline replay". Two *registry replay* adapters exist as described (Companies House 1.4.0 at
  `connectors/companies_house.py:84`, UKRI 1.3.0 at `connectors/ukri.py:84`), but
  `connectors/fixtures.py` also provides `FixtureConnector` and `NoopConnector`, both registered in
  `bootstrap.py:69-90` and listed in `SOURCE_ADMISSION_REGISTER.md:13`. The sentence is true of admitted
  external-source adapters and false of connectors in general. Qualify it as "two admitted external-source
  adapters" so the count cannot be read as the total.
- **MINOR — `SFR-SYS-M4`:** The migration head is stated three different ways across the repository:
  Chapter 4 line 33 says `0001--0010`, Chapter 5 says `0009`, and `docs/REQUIREMENTS.md:118` (FR-OBS-003)
  says `0001`–`0009`. The working tree head is `0010_hybrid_evidence_scope.py`. Chapter 4 is the one that
  matches disk. This is the requirements-register leg of `SFR-SYS-002` and should be fixed in the same
  pass. Note that a check for the stale `Jinja`/FastAPI presentation path flagged in
  `.agents/runs/supervisor-feedback-parts-b-c-improvements.md:41` found it **already remediated** in the
  chapters; the only surviving references are in superseded review reports and one exhibit JSON where the
  asset is explicitly labelled a retired historical artefact. No finding is raised for it.
- **OPTIONAL — `SFR-SYS-O1`:** Four of the chapter's figures are `[p]` floats each wrapped in two
  `\clearpage` commands (lines 21--28, 41--48, 59--66, 79--86). Eight forced page breaks in one chapter
  is a large share of the layout whitespace noted as `LAYOUT-001`.

### 5.6 Section-level assessment

- **Purpose and alignment — partly meets.** Architecture is described thoroughly, but much of it is not
  connected to RQ1, RQ2 or the executed evaluation.
- **Evidence and accuracy — meets.** All seven requirement identifiers and the architecture, storage,
  workflow-stage and approval claims verify against `docs/` and `src/`.
- **Technical validity — meets.** Prototype status, absence of production authentication, and held live
  routes are stated repeatedly and correctly.
- **Critical analysis — partly meets.** Trade-offs are named but usually as end-of-paragraph
  disclaimers rather than as reasoned design argument.
- **Structure and coherence — partly meets.** Nine sections are logically ordered; within sections the
  prose is a dense field enumeration.
- **Academic style — does not meet.** Requirement identifiers as prose subjects, 20-plus unglossed
  acronyms and noun-stacked clauses breach the stated audience requirement.
- **Reproducibility — partly meets.** Versions, migrations and hashes are recorded; the described version
  is not the evaluated one.

### 5.7 Handoff

Resolve `SFR-SYS-001` and `SFR-SYS-002`. `SFR-SYS-001` should be resolved before the cuts required by
`SFR-XS-003`, because the register rewrite is also where the word savings come from.

---

## 6. Chapter 5 — Evaluation and Results

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 5 - Evaluation and Results"
  section_type: "results"
  round: 2
  scope: "Dissertation/chapters/05_evaluation_results.tex (1,724 citation-stripped words); exhibits eval_t1-t7, eval_t4a, eval_f1, appendix_f"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 6
    minor: 3
    optional: 0
  previous_findings:
    resolved: 0
    partially_resolved: 2
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: dissertation-expert
```

### 6.1 Decision

**REVISE.** The headline D0 result is fully verified and correctly hedged — this is the strongest
evidence work in the dissertation — but the chapter never mentions RQ1 or RQ2, the cited provenance
chain for the result does not resolve to any file in the repository, its engineering-validation figures
are superseded by a later gate in the same repository, and the executed condition and metric
names are not reconciled with the prose, and the worked accepted/rejected examples the supervisor asked
for are typeset but never referred to.

### 6.2 Scope and evidence consulted

- `chapters/05_evaluation_results.tex` in full, and all nine exhibits it reports or points to.
- `var/evaluation/smoke.json` — the only D0 output in the repository — recomputed from
  `case_results` and cross-checked against its own `summaries`.
- `fixtures/evaluation_cases.json`, `fixtures/evaluation_manifest.json`.
- `exhibits/eval_t1_implementation_evidence_snapshot.txt` (the text alternative retaining full hashes).
- `shasum -a 256` recomputed for `evaluation_cases.json`, `evaluation_manifest.json`, `pyproject.toml`,
  `requirements.lock`, `requirements-dev.lock`, `var/evaluation/smoke.json`.
- `git log` for the cited revision.

**Verified in full (`VERIFIED`).** Every headline D0 number reproduces exactly from
`var/evaluation/smoke.json`:

| Reported | C1 | C2 | Recomputed C1 | Recomputed C2 |
|---|---:|---:|---:|---:|
| Emitted claims | 11 | 5 | 11 | 5 |
| TP / FP / FN / TN | 5/6/0/3 | 5/0/0/9 | 5/6/0/3 | 5/0/0/9 |
| Precision | 0.455 | 1.000 | 0.4545 | 1.000 |
| Recall | 1.000 | 1.000 | 1.000 | 1.000 |
| F1 | 0.625 | 1.000 | 0.625 | 1.000 |
| Unsupported-claim rate | 0.545 | 0.000 | 0.5455 | 0.000 |
| Source-record completeness | 0.818 | 1.000 | 0.8182 | 1.000 |
| Verification / abstention accuracy | 0.571 | 1.000 | 0.5714 | 1.000 |
| Schema / normalisation accuracy | 1.000 | 1.000 | 1.000 | 1.000 |
| Repeat consistency (3 repeats) | 1.000 | 1.000 | 1.000 | 1.000 |
| Model cost | USD 0 | USD 0 | `"0"` | `"0"` |

The fourteen case identifiers, the `manual` and `multi_agent_hitl` all-null summaries, the
`benchmark:d0` namespace, the D1 `protocol_only` and D2 `sealed` states, and the fixture SHA-256
`f403d59e…c94b` also verify. `git HEAD` `6356aa4` matches the cited `6356aa49cb3b`.

**Material evidence expected but unavailable:** no file in the repository has the SHA-256 that
Chapter 5 and Appendix G cite for the three-repeat D0 output (see `SFR-RES-002`).

### 6.3 Blocking findings

#### `SFR-RES-001` — `MAJOR` — The results chapter never mentions the research questions, and the table that maps RQs to answers is buried unreferenced in an appendix

- **Status:** `NEW`
- **Location:** Whole chapter — all eight section headings (§5.1--§5.8) and the body prose;
  `exhibits/disc_t1_rq_evidence_status.tex`, placed in Appendix F.
- **Criterion:** Results rubric — "report results in the order needed to answer the research questions".
  Tables rubric — "referenced in the text". User requirement U3 (direct, traceable RQ addressing).
- **Problem:** The strings `RQ1` and `RQ2` appear zero times in Chapter 5. Every other body chapter
  mentions them (Chapter 1 four times each, Chapter 2 twice each, Chapters 3 and 4 once each, Chapter 6
  three and two times, Chapter 8 twice each). Chapter 5's eight sections are organised by artefact and
  run type — implementation snapshot, engineering validation, D0 design, D0 results, company-research
  adversarial, held comparison, manual comparison, negative outcomes — so a reader tracking the research
  contract has to reconstruct which results answer which question. Compounding this,
  `disc_t1_rq_evidence_status.tex`, the one table in the whole dissertation that maps each question to
  its available evidence, its supported answer and its limit, is placed in Appendix F ("Supplementary
  Evaluation Results") and is referenced by no `\ref` anywhere in the manuscript.
- **Why it matters:** The user asked specifically whether the report explicitly and traceably answers
  the stated research questions. At present the mapping is implicit in the results chapter and
  unreachable in the appendix. An examiner looking for "where are the answers" finds section headings
  about migrations and fixtures.
- **Evidence:** String search for `RQ1`/`RQ2` across `frontmatter/abstract.tex` and `chapters/*.tex`;
  `rg` for `\ref{tab:disc-rq-evidence-status}` returns no match in `chapters/` or `frontmatter/`;
  `appendices/appendix_structure.tex` line 23 places the exhibit in Appendix F.
- **Required revision:** Add an explicit RQ frame to Chapter 5 without reordering the evidence:
  a short opening statement of which sections supply evidence for RQ1 and which for RQ2, and one clause
  in each of §5.2, §5.4 and §5.8 naming the question the result bears on. Move
  `disc_t1_rq_evidence_status.tex` into the body — the natural home is the start of Chapter 6 or the end
  of Chapter 5 — and reference it in the prose.
- **Acceptance condition:** Chapter 5 names RQ1 and RQ2 explicitly and states which sections evidence
  each; `tab:disc-rq-evidence-status` appears in a body chapter and is referenced at the point where the
  reader needs it.

#### `SFR-RES-002` — `MAJOR` — The cited provenance chain for the headline result does not resolve to any file in the repository

- **Status:** `NEW`
- **Location:** §5.1 paragraph 1 ("The evaluation record was created on 28 August 2026…");
  `exhibits/eval_t4_d0_results.tex` source note ("Fresh three-repeat D0 evaluator output, SHA-256
  e3be8f62…cdda27"); `exhibits/eval_t1_implementation_evidence_snapshot.txt` lines 5, 9 and 11.
- **Criterion:** Reproducibility and provenance rubric — "data snapshot, code version, dependency
  environment … and output path are traceable for material results"; Results rubric — "make every table
  and figure traceable to an output".
- **Problem:** The values are correct, but the chain that is supposed to let a reader verify them is
  broken in four places.
  1. **The cited output file does not exist.** Chapter 5 and Appendix G cite the three-repeat D0 output
     as SHA-256 `e3be8f622189c4b5803970d0869c9993e60a11b4ee1238a09261303282cdda27`. The only D0 output
     in the repository is `var/evaluation/smoke.json`, which hashes to
     `1a1501db71464502957ffd98fb31bda358089b83ba19c42cd7d4b18d60b68984`. No file anywhere carries the
     cited hash.
  2. **The date does not match.** §5.1 states the record was created on 28 August 2026;
     `var/evaluation/smoke.json` records `generated_at: 2026-08-25T23:23:17Z`.
  3. **Two dependency checksums do not match, and one is malformed.** Appendix G cites
     `pyproject.toml` as `d8ed0555…01101`; the file hashes to `bcafa4e6…c1fc0a077c1f7`. It cites
     `requirements.lock` as `5cce8f8e824bf5e6f88d47308a51fbc946a873a1327157dd5af9054b9892f0`, which is
     62 hexadecimal characters and therefore not a valid SHA-256; the file hashes to
     `b8740c1d…fbda860`. `requirements-dev.lock` (`5e2469bc…85608`) does match.
  4. **The named external-model run manifest is absent.**
     `docs/IMPLEMENTATION_TRACEABILITY.md` names smoke run `run_239f57affa684c749e075ec296803d2e`;
     `var/experiments/` contains five other `openai-smoke-run_*.json` manifests but not that one.
  Items 2 and 3 are partly explained — §5.1 discloses that the working tree was dirty, and
  `pyproject.toml` and `requirements.lock` were both modified on 30 August, after the snapshot. Item 1
  is not explained by anything.
- **Why it matters:** Chapter 3 and Chapter 5 both rest their reproducibility argument on checksums, and
  Chapter 5 says explicitly that "a checksum detects byte changes but cannot establish truth". A
  checksum that resolves to no file provides neither. Because the values themselves are verifiable from
  the file that *is* present, this is a fixable documentation defect rather than a false result — but as
  it stands, an examiner following the stated provenance path finds nothing.
- **Evidence:** `shasum -a 256` on `var/evaluation/smoke.json`, `pyproject.toml`, `requirements.lock`,
  `requirements-dev.lock`, `fixtures/evaluation_cases.json`, `fixtures/evaluation_manifest.json`;
  `var/evaluation/smoke.json` field `generated_at`; `ls var/experiments/`;
  `docs/IMPLEMENTATION_TRACEABILITY.md` row P18; `git log --oneline`.
- **Required revision:** Regenerate the D0 evaluation record and re-derive every checksum and date in
  §5.1, `eval_t1` and the `eval_t4` source note from the file that actually exists, or commit the cited
  output file so the hash resolves. Correct the malformed `requirements.lock` value. State the output
  file's repository path alongside its hash so the chain is followable. If dependency files changed
  after the snapshot, cite the snapshot-time values and say so explicitly rather than mixing eras.
- **Acceptance condition:** Every checksum, file path and date cited in §5.1, `eval_t1` and the `eval_t4`
  source note resolves to a file present in the repository, recomputable by `shasum -a 256`; all cited
  SHA-256 values are 64 hexadecimal characters; and the record date matches the output file's generation
  timestamp.

#### `SFR-RES-003` — `MAJOR` — The executed condition and metric names are not reconciled with the prose, which matters because the dissertation denies the single-versus-multi-agent framing

- **Status:** `NEW`
- **Location:** §5.3 paragraph 2 and §5.4 throughout; `exhibits/eval_t3_d0_comparison_design.tex`;
  `chapters/03_methodology.tex` §3.2; and, dependently, `chapters/06_discussion.tex` §6.2 paragraph 3.
- **Criterion:** Results rubric — "define metrics, comparison direction, units"; cross-section rubric —
  "metric definitions … agree"; reproducibility — "tables and figures can be regenerated from recorded
  inputs".
- **Problem:** The saved evaluator output labels the two executed conditions
  `deterministic_single_agent` and `multi_agent_verification`, and names its unsupported-claim measure
  `hallucination_rate`. The dissertation renames these to C1, C2 and "unsupported-claim rate" without
  ever stating the mapping. The renaming is defensible and in two respects better — "unsupported-claim
  rate" is more accurate than "hallucination rate" for a deterministic pipeline, and C1/C2 avoid
  prejudging the comparison. But the dissertation also makes a strong claim that depends on this
  framing: §6.2 states the experiment "isolates the gate and its authority over composition, not the
  effect of a persona, conversation style or number of agents", and §5.4 says the improvement "comes
  from blocking the six candidates designed to be unsupported". A reader who opens the output file finds
  the comparison labelled, by the student's own evaluator, as single-agent versus multi-agent. Without a
  stated mapping, the prose looks like a post-hoc reframing of a single-versus-multi-agent experiment.
- **Why it matters:** This is the interpretive hinge of RQ2 and of the supervisor's first point. The
  dissertation's framing is the more careful one, but it must be reconciled with the artefact rather
  than substituted for it, or the reframing itself becomes a finding against the report.
- **Evidence:** `var/evaluation/smoke.json` — `condition` values `deterministic_single_agent` and
  `multi_agent_verification`; `summaries[].hallucination_rate`;
  `chapters/06_discussion.tex` lines 44--48; `chapters/05_evaluation_results.tex` lines 79--81.
- **Required revision:** State the mapping once, in §5.3 or `eval_t3`: which evaluator condition label
  corresponds to C1 and to C2, and which output field corresponds to each reported measure, with a brief
  note that the dissertation's names were chosen to avoid implying that the contrast is about agent
  count. Then confirm in §6.2 that the two conditions share one program, catalogue and normalisation
  route — which is already stated — so the reader can see why the evaluator's labels overstate the
  difference.
- **Acceptance condition:** §5.3 or `eval_t3` gives an explicit condition-label and metric-name mapping
  to the saved output fields, and the reason for the renaming is stated in one sentence.

#### `SFR-RES-004` — `MAJOR` — §5.8 reports one contradiction case where §5.4 and Table 5.4 report two

- **Status:** `NEW`
- **Location:** §5.8 "Negative, null, failed, and unavailable outcomes", paragraph 1: "C1 produced six
  incorrect positive claims in D0 and missed **the only conflict**." Against §5.4 paragraph 3: "C1
  missed **both** labelled contradictions and C2 found both… This result is based on just two
  contradictions"; `eval_t4` row "Contradiction accuracy … Two applicable conflict cases only";
  `chapters/03_methodology.tex` §3.5 "Contradiction accuracy has two applicable cases".
- **Criterion:** Results rubric — "inconsistent values across prose, tables, and figures";
  `APPROVED` requires "material numbers … are internally consistent".
- **Problem:** Chapter 5 states the number of contradiction cases as one in §5.8 and as two in §5.4 and
  in the results table. The correct figure is two: `conflicting_public_value` (GBP 100 claim against
  GBP 200 evidence) and `mixed_currency_conflict` (GBP 400 claim against USD 400 evidence), both listed
  in the Appendix F ledger and both included in C1's six false positives.
- **Why it matters:** Contradiction handling is one of the five effects RQ2 asks about, and this is the
  count that supports it. A results chapter that states the same count two different ways undermines the
  reader's confidence in the numbers that are, in fact, all correct.
- **Evidence:** `chapters/05_evaluation_results.tex` line 177 against lines 92--94;
  `exhibits/eval_t4_d0_results.tex` line 20; `exhibits/appendix_f_d0_case_ledger.tex` lines 26 and 33;
  `var/evaluation/smoke.json` case results for both identifiers.
- **Required revision:** Correct §5.8 to two contradictions and check the surrounding sentence for any
  dependent count.
- **Acceptance condition:** Every statement of the contradiction-case count in Chapters 3, 5, 6 and 8
  and in all exhibits reads two, matching `fixtures/evaluation_cases.json`.

#### `SFR-RES-005` — `MAJOR` — The worked accepted and rejected claim examples the supervisor asked for exist but are never referenced or narrated

- **Status:** `NEW`
- **Location:** `exhibits/eval_t4a_d0_case_examples.tex`, `\input` at `chapters/05_evaluation_results.tex`
  line 123; `exhibits/appendix_f_d0_case_ledger.tex`, `\input` at
  `appendices/appendix_structure.tex` line 19.
- **Criterion:** Tables rubric — "referenced in the text" and "the text explains the research-relevant
  meaning rather than merely saying the item exists". Supervisor point S5 (add clear worked examples of
  accepted and rejected claims).
- **Problem:** `eval_t4a` "Examples of accepted and held D0 claims" is exactly what the supervisor asked
  for: four rows giving the proposed claim, the evidence, the verification rule, the decision and the
  report consequence — one accepted (observed zero), three held (contradiction, stale period, prompt
  injection). It is typeset into Chapter 5 but `tab:eval-d0-case-examples` is referenced by no `\ref`
  anywhere. The complete fourteen-case ledger `tab:appendix-d0-case-ledger` is likewise unreferenced.
  §5.4 paragraph 5 does narrate the cases in prose, but as a list of category names ("the conflict, old
  evidence, unsupported evidence, inaccessible source, mixed currency and prompt injection cases")
  rather than as worked examples with values and rules. So a table floats into the chapter that the
  prose never introduces, while the prose gives an abstract version of the same content. Neither
  Chapter 6 nor Chapter 8 uses a concrete accepted/rejected example at all.
- **Why it matters:** The supervisor asked for worked examples because they are what makes the
  verification mechanism legible to a non-technical reader. The material is already written and verified;
  it is simply not connected to the argument. This is among the cheapest high-value fixes available.
- **Evidence:** `rg '\\ref\{tab:eval-d0-case-examples\}'` and
  `rg '\\ref\{tab:appendix-d0-case-ledger\}'` return no matches across `chapters/`, `frontmatter/` and
  `appendices/`; `exhibits/eval_t4a_d0_case_examples.tex` lines 12--15;
  `chapters/05_evaluation_results.tex` lines 106--112.
- **Required revision:** Reference `eval_t4a` at the point in §5.4 where the case-level explanation
  begins, and rewrite that paragraph to walk through two contrasting cases in full — the accepted
  observed zero and the held GBP 100 versus GBP 200 contradiction — naming the value, the evidence, the
  rule applied and what the report shows as a result. Reference the Appendix F ledger from §5.4 as the
  complete record. Carry one of the same two examples into Chapter 6 §6.1 where evidence preservation is
  interpreted, so the RQ1 answer has a concrete instance.
- **Acceptance condition:** `tab:eval-d0-case-examples` and `tab:appendix-d0-case-ledger` are each
  referenced in the prose; §5.4 narrates at least one accepted and one rejected claim end to end with
  values, rule and report consequence; and at least one worked example appears in Chapter 6.

#### `SFR-RES-006` — `MAJOR` — The engineering-validation numbers are superseded by a later in-repository validation gate that the project's own notes flagged as unreconciled

- **Status:** `NEW` — `origin: SUPERVISOR_FEEDBACK_FULL_REPORT_REVIEW round 2`
- **Location:** `Dissertation/chapters/05_evaluation_results.tex:11,23-25,35,40`;
  `Dissertation/exhibits/eval_t2_engineering_validation.txt:3,7`
- **Criterion:** Evidence and accuracy; verifiability; currency of reported measurement.
- **Problem:** The chapter reports the engineering-validation suite as **286 tests passed, 85.58 per cent
  statement coverage, 46 source files under strict MyPy, and migration head 0009**. A later validation
  record inside this same repository — `.agents/runs/nextjs-dashboard-docker-default.md:70-71`, a "Final
  validation" gate whose own summary line reads `Ready to freeze: YES`, last modified 30 August 17:30 —
  records **266 passed, 22 warnings, 85.55 per cent coverage** and **45 source files**. Chapter 5 was
  last modified 31 August 17:04, after that record. The chapter therefore reports superseded numbers.
- **Why it matters:** This is not a stale-draft accident that can be excused by the disclosed dirty tree.
  The project's own note at `.agents/runs/supervisor-feedback-parts-b-c-improvements.md:41` already
  identifies this exact set — "still cite 286 tests, 85.58% coverage, and 46 typed files;
  `.agents/runs/nextjs-dashboard-docker-default.md:70-75` later records 266 tests, 85.55% coverage, and
  45 typed files" — and states that "None of these values may be copied blindly into the final manuscript
  without current-contract reconciliation." The corresponding task is recorded as `PENDING` at line 215
  of that file. An examiner who reruns the suite will obtain neither figure, and the discrepancy is
  documented in the repository as a known unreconciled item.
- **Evidence:** `UNVERIFIED` for both candidate figures — the suite could not be re-executed in this
  review environment, so this review does **not** assert that either 286 or 266 is the true current
  count. What is `VERIFIED` is the documentary conflict: two different figures for the same measurement
  exist in the repository, the dissertation cites the earlier one, and the project's own record flags the
  conflict as pending. Independently confirmed: `alembic/versions/` head is `0010_hybrid_evidence_scope.py`,
  not 0009; and `docs/REQUIREMENTS.md:118` (FR-OBS-003) still specifies revisions `0001`–`0009`, giving a
  third inconsistent value alongside Chapter 4's `0001--0010` and Chapter 5's `0009`.
- **Required revision:** Re-run the validation suite once against a clean, committed tree and report the
  figures that run produces, with the command, the date and the commit. Do not reconcile by choosing
  whichever number is more favourable. Update `eval_t2` and every dependent statement together, including
  the migration head, and align FR-OBS-003. If the suite cannot be re-run before submission, report the
  latest recorded gate (266 / 85.55 per cent / 45) and state explicitly that the earlier figures were
  superseded.
- **Acceptance condition:** A single test count, coverage percentage, typed-file count and migration head
  appear consistently across `05_evaluation_results.tex`, `eval_t2`, Chapter 4 and
  `docs/REQUIREMENTS.md`; each traces to one named command executed on one stated commit; and no other
  figure for the same measurement remains anywhere in the manuscript or its exhibits.

### 6.4 Prior-finding reconciliation

`CHAPTER_5_CROSS_SECTION_REVIEW.md` and `SECTION_5_1_REVIEW.md`--`SECTION_5_8_REVIEW.md` predate the
31 August revision and record no open finding identifiers. All eight Chapter 5 sections are `PENDING`.
`FULL_REPORT_CROSS_SECTION_REVIEW.md` asserted "Chapter 5 values reconcile with the Abstract, Discussion
and Conclusion" — that assertion holds for the metric values, which this review independently confirms,
but not for the contradiction count (`SFR-RES-004`) or the provenance chain (`SFR-RES-002`), neither of
which that report examined.

| Prior ID | Prior severity | Source report | Status now | Basis |
|---|---|---|---|---|
| `ABSTRACT-002` | Minor | `REVIEW_LOG.md` round 2, 27 Aug | **STILL PARTIALLY RESOLVED** | Its required outcome was "archive the complete provenance package at final freeze". That archive still does not exist: the cited D0 output checksum resolves to no file, and the run manifests live only in gitignored `var/`. `SFR-RES-002` is the same underlying gap at higher severity, because the freeze has now been claimed rather than pending. |
| (unnumbered OPTIONAL) | Optional | `CHAPTER_5_CROSS_SECTION_REVIEW.md` | **STILL OPEN** | Same final-freeze archive request; subsumed by `SFR-RES-002`. |

### 6.5 Non-blocking notes

- **MINOR — `SFR-RES-M1`:** `eval_t1`'s text alternative cites the evaluation manifest as
  "schema evaluation-manifest-v2"; `fixtures/evaluation_manifest.json` declares
  `"schema_version": "evaluation-dataset-manifest-v1"`. The manifest's SHA-256 (`1c16234a…4254`) does
  match, so only the schema name is wrong.
- **MINOR — `SFR-RES-M2`:** §5.6 (78 words) and §5.7 (65 words) are sections whose entire content is
  that there is no content. Their material belongs as two sentences inside §5.8. See `SFR-DISC-002` and
  the remediation plan.
- **MINOR — `SFR-RES-M3`:** §5.4 at line 129 says the company-research case "composed profile version
  three". The tests assert `schema_version == "company-intelligence-deck-v3"`
  (`tests/.../test_company_research.py:424,444`, written at `company_research.py:2878`), which is a deck
  *schema* version, not the third version of a profile record. The integer `ProfileVersionModel.version`
  is computed as `max+1` (`company_research.py:2938-2950`) and no end-to-end test asserts it equals 3.
  The claim is defensible if it means the schema, but a reader will read it as "the third revision of
  this company's profile". Name the schema explicitly. The count of 37 company-research tests at line 127
  is `VERIFIED` by static count across the three relevant test modules.

### 6.6 Section-level assessment

- **Purpose and alignment — does not meet.** The chapter reports the right evidence but never connects it
  to RQ1 or RQ2.
- **Evidence and accuracy — meets.** Every reported metric value, count, confusion cell, repeat and null
  state reproduces exactly from the saved output. This is the strongest evidence work in the report.
- **Methodological validity — meets.** Negative results, the formatting failure, the 22 warnings, the
  truncated timings and every null measure are retained rather than smoothed.
- **Critical analysis — meets.** §5.4 correctly attributes C2's perfect scores to co-designed labels and
  refuses to generalise.
- **Structure and coherence — partly meets.** Ordered by artefact rather than by question; two sections
  carry no content.
- **Tables, figures and reproducibility — does not meet.** Two tables unreferenced; the cited output
  checksum resolves to nothing.

### 6.7 Handoff

Resolve in order: `SFR-RES-004` (one-word correction), `SFR-RES-005`, `SFR-RES-001`, `SFR-RES-003`,
`SFR-RES-002`. `SFR-RES-002` requires regenerating or committing an evidence artefact and may need the
evidence owner rather than the drafting agent.

---

## 7. Chapter 6 — Discussion

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 6 - Discussion"
  section_type: "discussion"
  round: 4
  scope: "Dissertation/chapters/06_discussion.tex (1,622 citation-stripped words); exhibits disc_t1-t3"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 3
    minor: 1
    optional: 0
  previous_findings:
    resolved: 4
    partially_resolved: 1
    unresolved: 0
    regression: 2
    user_waived: 0
  next_owner: dissertation-expert
```

Chapter 6 is also the joint primary location for the cross-section blocker `SFR-XS-002`
(multi-agent justification), through §6.3.

### 7.1 Decision

**REVISE.** Chapter 6 interprets rather than repeats the results and its pilot section is much stronger
than the supervisor's feedback implies, but the 31 August revision removed material that had previously
resolved two MAJOR findings, the pilot plan is not yet executable, and a quarter of the chapter's
remaining length is spent on an unimplemented vendor product.

### 7.2 Scope and evidence consulted

- `chapters/06_discussion.tex` in full and the three `disc_t*` exhibits.
- `chapters/05_evaluation_results.tex` and `var/evaluation/smoke.json` for every value restated here.
- `Dissertation/sources/CLAIM_LEDGER.md` rows `6.1-P1`--`6.7-P5`.
- `Dissertation/sources/SECTION_6_7_EVIDENCE.md`.
- `sources/html/spacexai_grok_bot_bots.pdf`, read in full.
- Prior reports `CHAPTER_6_SUPERVISOR_PRIORITY_REVIEW.md` and `CHAPTER_6_CROSS_SECTION_REVIEW.md`.

Verified: every D0 value restated in §6.1 and §6.2 matches `var/evaluation/smoke.json`. The Grok Bot
capability description in §6.4 is supported by the local capture pp. 3--5. Evidence status: `VERIFIED`.

### 7.3 Blocking findings

#### `SFR-DISC-001` — `MAJOR` — The pilot plan is not yet executable: no size or duration, no time-saving acceptance criterion, and the remaining testing is dispersed

- **Status:** `NEW`
- **Location:** §6.7 "Prospective business pilot", paragraphs 1--5, particularly paragraph 4 ("Before
  seeing outcomes, the pilot owner and reviewer set the minimum acceptable quality and completion values
  and the maximum acceptable false-acceptance, false-rejection and cost values").
- **Criterion:** Discussion rubric — "assess practical importance separately from statistical
  performance"; supervisor point S6, which requires integration, costs, staff responsibilities, time
  savings, success metrics and the testing still required.
- **Problem:** Assessed against the supervisor's six elements, §6.7 covers four well and two partially.
  **Integration — met:** the existing portfolio XLSX import is named as the input integration and the
  Next.js review interface as the downstream report interface, with versioned JSON and accessible HTML
  after approval. **Staff responsibilities — met, and the strongest part:** pilot owner, reporting
  analyst, technical operator, reviewer/approver, and data and security owner are each given a defined
  remit. **Costs — met as a measurement plan:** setup effort in staff-hours, analyst and reviewer active
  minutes, elapsed time, rework, retries, tokens, provider charges, licensing, storage and security, with
  cost per report defined as allocated setup plus staff time, API use, licences, storage and security
  divided by completed reports. **Success metrics — met:** quality and operational measures plus a frozen
  go/no-go rule and stop events. The two gaps are:
  1. **No pilot size or duration.** The pilot is described only as "a time-limited evaluation". There is
     no number of companies, no number of reporting periods, no calendar duration and no minimum
     completed-report count. Without these the cost-per-report formula cannot be applied, the paired
     manual baseline cannot be scheduled, and no one can tell whether the pilot is a week or a quarter.
  2. **Time saving has no acceptance criterion.** The frozen criteria in paragraph 4 cover quality,
     completion, false acceptance, false rejection and cost — but not time. Time saving is the element
     the supervisor named, and although the chapter correctly refuses to invent a target, it does not
     even say who sets the time threshold or that one must be set, which the other measures all get.
  Separately, the sixth element, **testing still required**, is present in the report but scattered
  across §5.6, §5.7, §7.5, §8.3 and Appendix H rather than consolidated where the pilot is defined.
- **Why it matters:** The supervisor asked for a *practical* pilot plan. A plan that a pilot owner cannot
  schedule or size is a specification of measurements rather than a plan. The gaps are small and can be
  closed without inventing any result.
- **Evidence:** `chapters/06_discussion.tex` lines 139--181; `sources/CLAIM_LEDGER.md` rows
  `6.7-P1`--`6.7-P5`; `docs/PROJECT_CHARTER.md` line 103 (which correctly bars invented thresholds but
  does not bar stating a scope).
- **Required revision:** Add the pilot's scope as a decision to be frozen, not as an invented result:
  the number of companies and reporting periods, the calendar window, and the minimum number of completed
  paired reports required for the comparison to be interpretable. Add time to the list of measures for
  which the pilot owner and reviewer must set an acceptance value before seeing outcomes, keeping the
  value itself unspecified. Consolidate the "testing still required" list into one short passage at the
  end of §6.7, with §5.6, §5.7, §7.5 and §8.3 pointing to it rather than restating it.
- **Acceptance condition:** §6.7 states the pilot's company count, reporting-period count, calendar
  window and minimum completed-report count as parameters to be frozen before collection; time appears
  in the pre-registered acceptance-criteria list; and the remaining-testing requirements appear in one
  place that the other four locations reference.

#### `SFR-DISC-002` — `MAJOR` — An unimplemented vendor product is given more space than several executed results

- **Status:** `NEW`
- **Location:** §6.4 paragraph 3 (the Grok Bot comparator paragraph, roughly 130 words);
  `chapters/02_literature_review.tex` §2.6 final paragraph (lines 299--306);
  `exhibits/lit_t5_solution_landscape.tex` row "Managed agent platform";
  `chapters/08_conclusion.tex` §8.3 paragraph 3 (lines 64--72).
- **Criterion:** Purpose and alignment rubric — "its scope matches the approved project scope and does
  not quietly expand the project"; "technical detail that is impressive but irrelevant to the research
  argument". Supervisor point S1; user requirement U2.
- **Problem:** Grok Bot is a vendor product that was not implemented, not tested and not evaluated. It
  receives roughly 350 words across four locations — a Chapter 2 literature paragraph, a row in the
  architecture-alternatives table, a Chapter 6 paragraph specifying an eleven-measure future comparison,
  and one of only three paragraphs in the Conclusion's future-work section. For comparison, the executed
  D0 results receive 488 words and the RQ1 and RQ2 answers together receive 479. The source is a vendor
  documentation page captured on 30 August 2026, the day before the revision. The citation is legitimate
  and verified, and naming a future comparator is reasonable; giving it a specified eleven-measure study
  design in the Discussion and a third of the Conclusion's future work is not. The Chapter 6 and
  Chapter 8 paragraphs are also near-duplicates of each other.
- **Why it matters:** This is the clearest remaining instance of the scope creep the supervisor called
  blocking, and it is also the clearest instance of generic filler: the same paragraph would fit any
  dissertation about any agent platform. Removing it funds the additions that Chapters 1 and 2 need.
- **Evidence:** Word counts from `audit/SECTION_LEDGER.md` (§5.4 488 words; §6.1 251 and §6.2 228);
  `sources/CLAIM_LEDGER.md` rows `2.6-P5`, `6.4-P3` and `8.3-P3`, all three with the same purpose
  ("future managed-platform comparator"); `sources/WEB_CAPTURES.csv` capture date 2026-08-31.
- **Required revision:** Reduce Grok Bot to a single mention. Keep the `lit_t5` row, since a managed
  platform is a genuine architecture alternative and the row is short and properly hedged. Keep one
  sentence in Chapter 8 §8.3 naming it as a candidate future comparator. Delete the Chapter 2 paragraph
  and the Chapter 6 §6.4 paragraph, or compress the two into one sentence in §6.4. Do not retain the
  eleven-measure comparison specification anywhere; the general requirement for equal inputs and
  scoring is already stated for the pilot.
- **Acceptance condition:** Grok Bot appears in at most two places outside `lit_t5`, occupies no more
  than 60 words of body prose in total, and no future study design is specified for it beyond a single
  sentence.

#### `SFR-DISC-003` — `MAJOR` — The 31 August revision removed material that had resolved two prior MAJOR findings

- **Status:** `REGRESSION`
- **Location:** §6.5 and §6.6, where the removed material previously sat; Chapter 6 as a whole, now
  1,622 words against 2,439 words at the time of the round-3 approval.
- **Criterion:** Re-review protocol — a revision must not reintroduce a resolved defect;
  Discussion rubric — "consider alternatives and trade-offs where the research decision is contestable".
- **Problem:** `CHAPTER_6_SUPERVISOR_PRIORITY_REVIEW.md` recorded seven MAJOR findings as RESOLVED. Two
  of those resolutions no longer hold, because the content that produced them has been cut.
  - `DISC-SUP-003` was resolved because "Versioned JSON is defended against PDF-first and JSON-only
    alternatives, including schema, migration, misuse and reviewer re-entry trade-offs". The current
    Chapter 6 contains one incidental mention of "versioned JSON and accessible HTML exported only after
    approval", inside the pilot section. The output-format design defence is gone.
  - `DISC-SUP-005` was resolved because "The contradiction ledger is interpreted as preserving competing
    support while transferring judgement and reading effort to the reviewer". The current Chapter 6
    mentions contradictions only once, in a list of what controlled tests covered. The interpretation is
    gone.
  Chapter 6 lost roughly 800 words in the revision, and these two arguments were among the casualties.
- **Why it matters:** The supervisor's feedback asked for focus and for de-duplication, not for the
  removal of design reasoning. Both of these arguments were genuine critical analysis of contestable
  design decisions — exactly what the Discussion rubric requires and what Chapter 6 is now thinner in.
  Under the re-review protocol a regression must be raised even when the revision was otherwise
  beneficial.
- **Evidence:** `reviews/CHAPTER_6_SUPERVISOR_PRIORITY_REVIEW.md` lines 55 and 57 (the resolution
  statements) and line 59 (Chapter 6 at 2,439 words); `audit/SECTION_LEDGER.md` (current §6.1--§6.7 sum
  to 1,604 words); string search of `chapters/06_discussion.tex` for `pdf`, `output format`,
  `contradiction`, `reviewer burden` and `reading effort`.
- **Required revision:** Restore both arguments in compressed form. The output-format defence belongs in
  §6.5 or §6.6 in roughly 70 words: why versioned JSON plus accessible HTML rather than a PDF-first or
  JSON-only export, and what the reviewer re-entry and misuse trade-offs are. The contradiction-ledger
  interpretation belongs in §6.1 or §6.2 in roughly 70 words: that retaining competing support preserves
  evidence but transfers judgement and reading effort to the reviewer, bounded to the two observed D0
  conflicts. Fund both from the `SFR-DISC-002` deletion.
- **Acceptance condition:** Chapter 6 again contains a reasoned defence of the export-format decision
  against at least one named alternative, and an interpretation of what retaining contradictions costs
  the reviewer, both bounded to the two D0 conflict cases.

### 7.4 Prior-finding reconciliation

| Finding | Previous severity | Status | Verification |
|---|---:|---|---|
| DISC-SUP-001 | MAJOR | RESOLVED | §6.7 specifies the pilot, contradiction decisions, version-bound exports, coverage, abstention, false acceptance and rejection, edits, review time and source failures. Gaps in size and time threshold are raised separately as `SFR-DISC-001`, not as a reopening of this finding. |
| DISC-SUP-002 | MAJOR | RESOLVED | §6.6 constrains interpretation and transfer with early-stage private-market limits, citing `kaplan2016vcdata` and `britishbusinessbank2025equity`. |
| DISC-SUP-003 | MAJOR | REGRESSION | The versioned-JSON defence against PDF-first and JSON-only alternatives is absent from the current chapter. See `SFR-DISC-003`. |
| DISC-SUP-004 | MAJOR | RESOLVED | §6.7 and §5.7 keep participant work absent for want of ethics, consent and protocol authority, and treat human evidence as future work. |
| DISC-SUP-005 | MAJOR | REGRESSION | The contradiction-ledger interpretation is absent from the current chapter. See `SFR-DISC-003`. |
| DISC-SUP-006 | MAJOR | RESOLVED | The mixed engineering record is reported in §5.2 and §5.8 and separated from usefulness and business value in §6.6. |
| DISC-SUP-007 | MAJOR | PARTIALLY_RESOLVED | The metadata no longer inherits the historical gate, but the resolution's basis — "Chapter 6 is 2,439 words within the explicit Literature/Discussion priority allocation" — no longer describes the chapter, which is now 1,622 words. See `SFR-XS-003`. |
| DISC-R3-001 | MINOR | RESOLVED | Superseded by the fresh count in `SFR-XS-003`. |

**Independence note.** `CHAPTER_6_SUPERVISOR_PRIORITY_REVIEW.md` returned `gate: PASS` against a
Chapter 6 answering RQ1--RQ3 in 2,439 words. It is void for the current draft.

### 7.5 Non-blocking notes

- **MINOR — `SFR-DISC-M1`:** §6.3 is titled "Why functional role separation was selected" and is the
  natural home for the design argument required by `SFR-XS-002`, but at 207 words it is the third
  shortest section in the chapter. Its content is sound; its weight is not proportionate to its role.

### 7.6 Section-level assessment

- **Purpose and alignment — partly meets.** §6.1 and §6.2 answer RQ1 and RQ2 directly and
  proportionately; §6.4 expands the scope beyond the executed work.
- **Evidence and accuracy — meets.** Every restated value matches the saved output.
- **Methodological validity — meets.** The chapter separates selective admission from improved coverage,
  and refuses to claim general multi-agent superiority.
- **Critical analysis — partly meets.** False rejection, coordination cost and over-reliance are all
  engaged; two previously present design defences have been lost.
- **Structure and coherence — meets.** Seven sections move from RQ answers to literature, transfer and
  the pilot.
- **Citations and scholarship — meets.** Interpretive claims are tied to admitted sources.
- **Academic style — meets.** Plain and calibrated; mean sentence length 15.2 words.

### 7.7 Handoff

Resolve `SFR-DISC-002` first, because it funds `SFR-DISC-003`; then `SFR-DISC-001`; then, jointly with
Chapter 1, the cross-section blocker `SFR-XS-002`.

---

## 8. Chapter 7 — Ethics, Governance and Limitations

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 7 - Ethics, Governance and Limitations"
  section_type: "ethics, governance, compliance and limitations"
  round: 2
  scope: "Dissertation/chapters/07_governance_limitations.tex (759 citation-stripped words); exhibit gov_t1"
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
  next_owner: dissertation-expert
```

### 8.1 Decision

**REVISE.** Chapter 7 states a false negative claim about external-model processing that is contradicted
by five saved run manifests in this repository, and although it is designated the authoritative location
for limitations, six other chapters restate the same boundaries.

### 8.2 Scope and evidence consulted

- `chapters/07_governance_limitations.tex` in full and `exhibits/gov_t1_governance_residual_risk.tex`.
- `docs/REQUIREMENTS.md` rows `FR-EXT-005`, `FR-EXT-006`, `FR-EXT-008`.
- `docs/IMPLEMENTATION_TRACEABILITY.md` row P18.
- `var/experiments/openai-smoke-run_*.json` — five manifests, one read in full.
- `src/portfolio_agent/experiments.py`, `src/portfolio_agent/llm/experiment.py`,
  `src/portfolio_agent/cli.py`, `src/portfolio_agent/bootstrap.py`, `src/portfolio_agent/config.py`.
- `docs/SECURITY_AND_DATA_GOVERNANCE.md`, `docs/ARCHITECTURE.md`, `docs/adr/`.
- Disclaimer-density analysis across the Abstract and all eight chapters.

### 8.3 Blocking findings

#### `SFR-GOV-001` — `BLOCKER` — "No live request occurred" is contradicted by five saved external-model run manifests that record observed tokens and latency

- **Status:** `NEW`
- **Location:** §7.2 "External-model processing and retention", paragraph 2, final sentence: "No live
  request occurred, so handling, tokens and retention status were unobserved; a future run must record
  the setting and confirming evidence." Also `exhibits/gov_t1_governance_residual_risk.tex`, row
  "External model", column "Current evidence": "Code and fake-provider tests; **no live request**". Also
  `chapters/05_evaluation_results.tex` §5.5 paragraph 3: "No OpenAI, Companies House, publisher or open
  website call occurred; delay, tokens, cost … remain unmeasured."
- **Criterion:** Truth and traceability — "no result, source … or implementation detail appears
  invented"; ethics and governance rubric — mitigation and exposure claims must match evidence; evidence
  status `CONTRADICTED` in the authoritative governance chapter.
- **Problem:** External model requests were made, succeeded, and were recorded with observed token
  counts and latency. `var/experiments/` contains five run manifests named
  `openai-smoke-run_*.json`. The one read in full
  (`openai-smoke-run_8923757de2d041de9c88f7460c957b39.json`) records:
  `"experiment": "bounded_synthetic_openai_smoke"`, `"created_at": "2026-08-26T20:17:15Z"`, and an
  `external_model_attempts` entry with `"status": "succeeded"`, `"duration_ms": 1400`,
  `"input_tokens": 449`, `"output_tokens": 79`, `"model": "gpt-5.4-mini-2026-03-17"`,
  `"provider": "openai_responses_structured_extractor"`. The requirements register agrees:
  `FR-EXT-005` status reads "Implemented; **one bounded synthetic live call exercised**", `FR-EXT-006`
  reads "primary route exercised in the bounded synthetic smoke", and `FR-EXT-008` reads "exact
  structured-value path exercised **live**, adversarial paths mocked".
  `docs/IMPLEMENTATION_TRACEABILITY.md` row P18 names a specific smoke run and its manifest checksum.
  The dissertation therefore states that tokens and handling were unobserved when the repository records
  449 input tokens, 79 output tokens and 1,400 ms for a succeeded request. A related omission
  compounds it: the dissertation never names the external model at all. `src/portfolio_agent/config.py`
  pins `APPROVED_OPENAI_MODEL`, ADR-0011 governs the routing, and `README.md` documents the route, but
  no model identity appears anywhere in the Abstract or Chapters 1--8, even though
  `mitchell2019modelcards` is cited four times for the principle that a system report should state its
  version and intended use.
- **Why it matters:** This is the dissertation's authoritative statement on external processing and data
  retention, and it is repeated in the governance residual-risk table. A false claim that no external
  request occurred understates the actual governance exposure, misdescribes what was and was not
  observed, and would be treated seriously by an examiner or an ethics reviewer. The input was synthetic
  and the run was bounded, so the underlying conduct appears entirely proper — which makes the reporting
  error avoidable and correctable rather than a research-integrity failure. It must nonetheless be
  corrected before submission.
- **Evidence:** `var/experiments/openai-smoke-run_155f8de35afa4a8b9d34997498fb787b.json`,
  `…409d4618a0284d66b4bb9b5fe9b54f0e.json`, `…54921df5758c4ffaba795456bd90a5e8.json`,
  `…6825a8c72416475aae0e1b1d31364311.json`, `…8923757de2d041de9c88f7460c957b39.json`;
  `docs/REQUIREMENTS.md` lines 67--69; `docs/IMPLEMENTATION_TRACEABILITY.md` row P18;
  `src/portfolio_agent/experiments.py` (`run_openai_synthetic_smoke`, output manifest at
  `openai-smoke-{run_id}.json`); `src/portfolio_agent/llm/experiment.py` (the live path accepts
  synthetic evidence and the checked-in fixture only); `src/portfolio_agent/bootstrap.py`
  (`PORTFOLIO_ALLOW_EXTERNAL_LLM` gate); `src/portfolio_agent/config.py` (pinned approved model).
- **Required revision:** Replace the false negative with the actual record. State in §7.2 that a bounded
  synthetic smoke run was executed against the external provider, on which date, with what input class
  (synthetic fixture only), under which gates, with the observed attempt count, latency and token
  counts, and what that does and does not tell the reader about provider retention. Correct the `gov_t1`
  "Current evidence" cell for the external-model row. Correct or scope the §5.5 sentence so that its
  denial applies only to the company-research adversarial test run it describes, if that is what was
  meant. Name the external model and its pinned route once, in Chapter 4 or Chapter 7, with a reference
  to the governing ADR. Do not overstate in the other direction: the smoke run is connectivity and
  persistence evidence, not performance, cost or quality evidence, and the repository's own manifest
  says so ("Development smoke evidence only; no performance or cost claim").
- **Acceptance condition:** No statement anywhere in the Abstract, Chapters 1--8 or any exhibit asserts
  that no external-model request occurred or that tokens, latency or handling were unobserved; §7.2
  records the executed synthetic smoke run with its date, input class, gates and observed attempt,
  latency and token counts; `gov_t1`'s external-model evidence cell matches; the external model and its
  pinned route are named once; and every retained claim about the smoke run is confined to connectivity
  and persistence.

#### `SFR-GOV-002` — `MAJOR` — Chapter 7 is designated the authoritative limitations location but six other chapters restate the same boundaries

- **Status:** `NEW`
- **Location:** §7.5 "Research and operational limitations" as the designated location, against
  `chapters/01_introduction.tex` §1.4 and §1.5; `chapters/03_methodology.tex` §3.1, §3.2 and §3.7;
  `chapters/04_system_design.tex` §4.2 paragraph 4 and the closing sentence of 20 of its 36 paragraphs;
  `chapters/05_evaluation_results.tex` §5.8; `chapters/06_discussion.tex` §6.6;
  `chapters/08_conclusion.tex` §8.1 paragraph 4.
- **Criterion:** Academic-style rubric — "repeated restatement of the same point"; ethics rubric —
  limitations must "affect interpretation" rather than be recited. Supervisor point S4 (remove repeated
  limitations).
- **Problem:** Chapter 1 §1.4 states that "Chapter~7 records this limitation once". It does not. The
  same boundary set — no real-company evidence, no manual baseline, no human study, no live source, no
  production readiness, no business benefit — is restated in every chapter. Measured across the Abstract
  and Chapters 1--8 there are roughly 60 explicit disclaimer sentences of the form "does not establish /
  cannot show / is not evidence that", and 101 of 182 substantive paragraphs (55 per cent) carry at
  least one negation of the report's own scope. The concentration is highest in Chapter 2 (31 of 36
  paragraphs, 86 per cent) and Chapter 7 itself (11 of 13, 85 per cent), and Chapter 4 carries 20 of 36.
  A contributing mechanism is the project's own rule, recorded in `sources/CLAIM_LEDGER.md`, that "every
  substantive body paragraph must contain at least two distinct citations", which pushes each paragraph
  towards a uniform claim-plus-hedge-plus-citation shape.
  The effect is threefold: the report reads defensively; the genuinely important limitations in §7.5
  (co-designed D0 labels and rules, single-researcher confirmation risk, no independent reference) lose
  prominence among dozens of routine ones; and roughly 600--700 words are spent restating boundaries
  that one authoritative statement would carry.
- **Why it matters:** The supervisor asked for this specifically. It is also the single largest available
  source of the words needed to fund the Chapter 1 and Chapter 2 additions, so resolving it makes the
  rest of the remediation affordable.
- **Evidence:** Disclaimer extraction across `frontmatter/abstract.tex` and `chapters/*.tex` (about 60
  explicit instances, listed by file and line); paragraph-level negation density per chapter (Abstract
  25 per cent, Ch1 38, Ch2 86, Ch3 42, Ch4 56, Ch5 36, Ch6 52, Ch7 85, Ch8 27);
  `chapters/01_introduction.tex` line 126; `sources/CLAIM_LEDGER.md` lines 3--5.
- **Required revision:** Make §7.5 genuinely authoritative and reduce the rest to cross-references.
  (a) Consolidate the study-level boundary set into one statement in §7.5, organised by what it prevents
  the reader from concluding rather than as a list of absent things. (b) Delete the routine restatements
  in Chapters 1--6 and 8, retaining a disclaimer only where it changes how an immediately adjacent
  result or claim must be read — most importantly the co-design caveat next to C2's perfect scores in
  §5.4, the false-rejection caveat in §6.2, and the scope-narrowing statement in §1.4. (c) Where a
  chapter needs the boundary, reference §7.5 rather than restate it. (d) Ask the user whether the
  two-citations-per-paragraph rule should be relaxed for paragraphs that carry the argument rather than
  an external claim; it is a project convention, not a university requirement, and it is shaping the
  prose rhythm the supervisor objected to.
- **Acceptance condition:** No more than 25 explicit "does not establish / cannot show" disclaimer
  sentences remain across the Abstract and Chapters 1--8; no chapter other than 7 restates the
  study-level boundary set in full; §7.5 contains a single consolidated statement of the boundaries
  organised by consequence; and every retained disclaimer sits adjacent to the specific claim it
  qualifies.

### 8.4 Prior-finding reconciliation

`CHAPTER_7_CROSS_SECTION_REVIEW.md` and `SECTION_7_1_REVIEW.md`--`SECTION_7_5_REVIEW.md` predate the
31 August revision and record no open findings. All five Chapter 7 sections are `PENDING`.
`FINAL_SUPERVISOR_PRIORITY_AND_AUTHORSHIP_AUDIT.md` recorded "Evidence and accuracy — meets" for the
whole manuscript; that judgement did not examine `var/experiments/` and is not sustainable given
`SFR-GOV-001`.

### 8.5 Non-blocking notes

- **MINOR — `SFR-GOV-M1`:** §7.5 paragraph 3 states "The dated snapshot recorded five formatting
  failures and 22 warnings; later changes remain unevaluated." Chapter 5 §5.2 gives the same figures.
  This is one of the few duplications worth keeping, because the governance chapter needs the fact; the
  wording should simply cross-reference §5.2 rather than restate the counts.

### 8.6 Section-level assessment

- **Purpose and alignment — partly meets.** The chapter covers classification, external processing,
  security, investment and person boundaries and study limits; it is not the single authoritative
  limitations location it claims to be.
- **Evidence and accuracy — does not meet.** The external-model claim is contradicted by five saved run
  manifests and by the requirements register.
- **Critical analysis — meets.** Residual risk, human classification error and the absence of provider
  deletion guarantees are all stated without claiming compliance.
- **Structure and coherence — meets.** Five sections are logically ordered.
- **Academic style — partly meets.** Plain and precise, but 11 of 13 paragraphs end on a negation.
- **Tables — partly meets.** `gov_t1` is well designed but contains the contradicted external-model
  cell, and it sits in Appendix H while §7.5 refers to it as though present.

### 8.7 Handoff

Resolve `SFR-GOV-001` first; it is the highest-priority item in this review. Then `SFR-GOV-002`, whose
consolidation supplies the word budget for the rest of the plan.

---

## 9. Chapter 8 — Conclusion and Future Work

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Chapter 8 - Conclusion and Future Work"
  section_type: "conclusion and future work"
  round: 2
  scope: "Dissertation/chapters/08_conclusion.tex (646 citation-stripped words); exhibit conc_t1"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 1
    minor: 1
    optional: 0
  previous_findings:
    resolved: 0
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: dissertation-expert
```

### 9.1 Decision

**REVISE.** Chapter 8 answers both research questions accurately and claims no more than the evidence
supports, but it restates Chapter 6 almost sentence for sentence, never states its own principal
limitations, and gives a third of its future work to an unimplemented vendor product.

### 9.2 Scope and evidence consulted

- `chapters/08_conclusion.tex` and `exhibits/conc_t1_sequenced_evidence.tex`.
- `chapters/06_discussion.tex` §6.1, §6.2 and §6.7 for overlap.
- `var/evaluation/smoke.json` for the restated values.
- `sources/CLAIM_LEDGER.md` rows `8.1-P1`--`8.3-P3`.

Verified: the restated D0 values (0.455 to 1.000 precision, 0.545 to 0.000 unsupported-claim rate,
recall 1.000 in both, six held candidates, five retained claims) all match the saved output.
Evidence status: `VERIFIED`.

### 9.3 Blocking findings

#### `SFR-CONC-001` — `MAJOR` — The conclusion duplicates Chapter 6, states no principal limitations of its own, and spends a third of its future work on an unimplemented product

- **Status:** `NEW`
- **Location:** §8.1 paragraphs 2 and 3 against `chapters/06_discussion.tex` §6.1 paragraph 2 and §6.2
  paragraphs 1--2; §8.1 as a whole (no limitations statement); §8.3 paragraph 3 (Grok Bot).
- **Criterion:** Conclusion rubric — "answer the research questions directly and proportionately";
  "state the principal limitations and scope of the conclusions"; "propose future work that follows from
  identified limitations"; academic-style rubric on repeated restatement. Supervisor points S1 and S4.
- **Problem:** Three connected defects.
  1. **Duplication.** §8.1 paragraph 3 reproduces §6.2's content with the same four figures in the same
     order and the same closing caveat. §8.1 paragraph 2 reproduces §6.1's traceability argument and the
     same four example categories (observed zero, contradiction, stale period, untrusted). A reader who
     has read Chapter 6 learns nothing new from §8.1, and at 646 words Chapter 8 has no room for
     duplication.
  2. **No principal limitations.** The Conclusion rubric requires the conclusion to state the principal
     limitations and the scope of its own conclusions. Chapter 8 states what the study does not
     establish (§8.1 paragraph 1 and 3) but never states the two limitations that actually bound its
     contribution — that D0's labels and rules were co-designed, and that the researcher designed,
     scored and interpreted the study alone. Both are in §7.5. A conclusion that defers its own
     limitations entirely to an earlier chapter leaves the reader's final impression uncalibrated.
  3. **Disproportionate future work.** §8.3 has three paragraphs. The first is the pilot, which follows
     directly from the stated limitations. The second is the live-source study and independent
     accessibility and security assessment, which also follow. The third is Grok Bot, which follows from
     nothing in the results and was never implemented. See `SFR-DISC-002`.
- **Why it matters:** The conclusion is the last thing an examiner reads and the place where
  proportionality is most visible. As written it repeats, omits its own limitations, and gives a vendor
  product equal billing with the pilot that the whole dissertation builds towards.
- **Evidence:** `chapters/08_conclusion.tex` lines 10--21 against `chapters/06_discussion.tex`
  lines 12--17 and 32--42; `audit/SECTION_LEDGER.md` (§8.1 238 words, §8.2 155, §8.3 229);
  `sources/CLAIM_LEDGER.md` rows `6.4-P3` and `8.3-P3` sharing one purpose.
- **Required revision:** Rewrite §8.1 so that it answers the primary question, RQ1 and RQ2 in the
  reader's terms and at the level of what it means, without repeating Chapter 6's figures more than once
  each. Add a short statement of the two principal limitations that bound the contribution, referencing
  §7.5 for the full set. Delete or reduce the Grok Bot paragraph per `SFR-DISC-002` and let §8.3 end on
  the pilot and the live-source study, which do follow from the limitations.
- **Acceptance condition:** No sentence in §8.1 duplicates a sentence in §6.1 or §6.2; each D0 figure
  appears at most once in Chapter 8; §8.1 states the co-design and single-researcher limitations and
  references §7.5; and §8.3's future work items each trace to a limitation stated in the report.

### 9.4 Prior-finding reconciliation

`CHAPTER_8_CROSS_SECTION_REVIEW.md` and `SECTION_8_1_REVIEW.md`--`SECTION_8_3_REVIEW.md` predate the
31 August revision and record no open findings. All three Chapter 8 sections are `PENDING`.

### 9.5 Non-blocking notes

- **MINOR — `SFR-CONC-M1`:** §8.3 refers to "the full evidence roadmap … in
  Appendix~\ref{app:supplementary-exhibits}" but `tab:conc-evidence-roadmap` is never referenced by
  label, so the reader is pointed at an appendix rather than at the table. See `SFR-XS-005`.

### 9.6 Section-level assessment

- **Purpose and alignment — partly meets.** Both questions are answered and no claim exceeds the
  evidence; proportionality and independence from Chapter 6 are lacking.
- **Evidence and accuracy — meets.** Every restated value matches the saved output.
- **Critical analysis — partly meets.** The narrowing of the contribution relative to the original
  contract is stated well; the conclusion's own limitations are absent.
- **Structure and coherence — meets.** Three sections: answers, contribution, sequenced future evidence.
- **Academic style — meets.** Calibrated and free of promotional language.

### 9.7 Handoff

Resolve `SFR-CONC-001` after `SFR-DISC-002`, since the two share the Grok Bot deletion.

---

## 10. Cross-section audit

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: FINAL_CROSS_SECTION_AUDIT
  section: "Complete dissertation candidate - cross-section consistency"
  section_type: "final cross-section audit"
  round: 2
  scope: "Dissertation/main.tex, frontmatter, metadata.tex, chapters 1-8, all 29 exhibits, references.tex, appendices/appendix_structure.tex, audit and sources ledgers"
  evidence_confidence: HIGH
  findings:
    blocker: 3
    major: 6
    minor: 5
    optional: 1
  previous_findings:
    resolved: 0
    partially_resolved: 0
    unresolved: 2
    regression: 0
    user_waived: 0
  next_owner: dissertation-expert
```

### 10.1 Decision

**REVISE.** Research questions, terminology, metric definitions and reported values are consistent
across the chapters, and the D0 numbers agree everywhere they appear. The cross-section failures are
elsewhere: the title promises impact and auditability that the body explicitly disclaims, the central
design decision is never justified, two submission-critical appendices are empty, and the exhibit set is
poorly integrated with the prose in both directions.

### 10.2 Consistency checks that pass

- **Research questions.** RQ1 and RQ2 are stated identically in `REPORT_STRUCTURE.md`, §1.4 and
  `intro_t1`. No `RQ3` remnant survives anywhere in the manuscript, so the scope narrowing was executed
  cleanly.
- **Reported values.** Every D0 figure agrees across the Abstract, §5.4, `eval_t4`, `eval_f1`, §6.1,
  §6.2, §8.1, `disc_t1` and `disc_t3`, and all reproduce from `var/evaluation/smoke.json`.
- **Metric definitions.** The denominators stated in §3.5 (supported emitted over all emitted; correctly
  emitted required over all required) match the recomputed values.
- **Evidence tiers.** D0 executable, D1 protocol-only, D2 sealed, C0 and C3 unobserved are consistent in
  §3.2, §3.3, §5.3, §5.7, `gov_t1` and `fixtures/evaluation_manifest.json`.
- **Citation integrity.** All 45 cited keys have a bibliography entry; all 45 bibliography entries are
  cited; no orphan and no duplicate. All resolve to local PDFs or web captures with matching manifest
  rows.
- **Figures.** All nine referenced PNGs exist and are current in `exhibits/MERMAID_MANIFEST.csv`.
- **Requirement identifiers.** All seven cited in Chapter 4 exist in `docs/REQUIREMENTS.md` with the
  attributed meanings.

### 10.3 Blocking findings

#### `SFR-XS-001` — `BLOCKER` — The title claims impact and auditability that the dissertation explicitly disclaims

- **Status:** `NEW`
- **Location:** `Dissertation/metadata.tex` line 1, `\DissertationTitle`: "From Ingestion to Impact:
  Design and Evaluation of an Evidence-First Multi-Agent AI Pipeline for Auditable UK Early-Stage
  Portfolio Reporting and Bounded Company Intelligence". Rendered on the title page and in the PDF
  metadata (`main.tex` line 6).
- **Criterion:** Truth and traceability — claims must not exceed evidence; calibration of claims;
  supervisor point S1 (focus on what was actually validated); user requirement U1.
- **Problem:** The title makes two claims the body denies and one the body cannot support.
  1. **"To Impact".** The word `impact` appears nowhere in the Abstract or Chapters 1--8 as a claim
     about the system. The body states the opposite: §8.1 says the results "do not establish operational
     usefulness or production readiness"; the Abstract says the work "does not establish … reduced
     analyst effort, better investment decisions or production readiness"; §6.6 says "practical
     usefulness remains a pilot hypothesis". The title therefore promises the one thing the
     dissertation is most careful to disclaim.
  2. **"Auditable".** No audit was performed. The only body use of the word is §4.5's narrow and hedged
     claim that the fixed state machine "makes failure locations auditable". Auditability of the
     reporting output is a design intention, not an evaluated property.
  3. **Register.** At 26 words the title is also the densest text in the document, opening on
     "Ingestion" and closing on "Bounded Company Intelligence" — precisely the vocabulary the user asked
     to remove for a non-technical reader.
- **Why it matters:** The title is the most visible claim in the dissertation and the first thing an
  examiner assesses. A title that over-claims while the body under-claims invites the reader to conclude
  that the hedging in the body is defensive rather than principled, and it is the most conspicuous
  instance of the scope creep the supervisor called blocking. It is also among the cheapest possible
  fixes.
- **Evidence:** `metadata.tex` line 1; string search for `impact` and `auditable` across
  `frontmatter/*.tex`, `chapters/*.tex` and `exhibits/*.tex` (two hits, both inside `lit_t2` describing
  what evidence *cannot* support, plus the single hedged §4.5 use);
  `chapters/08_conclusion.tex` line 7; `frontmatter/abstract.tex` line 10;
  `chapters/06_discussion.tex` line 136.
- **Required revision:** Retitle so that every element is supported by the executed work. The title
  should name the artefact, the reporting domain and the actual contribution — an evidence-first,
  role-separated reporting workflow and a controlled evaluation of a separate verification stage —
  without "Impact", without "Auditable", and in plainer words. Update `metadata.tex` and the
  `hypersetup` keywords in `main.tex` together.
- **Acceptance condition:** No word in the title asserts a property that the body disclaims or leaves
  unevaluated; `impact`, `auditable` and any equivalent are absent unless a corresponding evaluated
  result exists; the title is at most 20 words; and the PDF metadata matches.

#### `SFR-XS-002` — `BLOCKER` — The central design decision is never justified, and the report repeatedly concedes a simpler design would do the same job

- **Status:** `NEW`
- **Location:** Absent from `chapters/01_introduction.tex` entirely. Fragments in
  `frontmatter/abstract.tex` line 6; `chapters/02_literature_review.tex` §2.2.1 paragraph 5 (line 91)
  and §2.7 paragraph 3 (line 330); `exhibits/lit_t5_solution_landscape.tex`;
  `chapters/04_system_design.tex` §4.5 final paragraph; `chapters/06_discussion.tex` §6.2 paragraph 3
  (line 46) and §6.3 (207 words).
- **Criterion:** Introduction rubric — "identify the specific research gap or unresolved problem";
  Argument rubric — "alternatives and trade-offs are considered where the research decision is
  contestable"; System design rubric — "justify design choices". Supervisor point S2, which asks
  explicitly why a multi-agent system is needed instead of a simpler one.
- **Problem:** The supervisor asked whether the justification exists. It exists only in fragments, in
  the wrong places, and the report argues against itself.
  - **Chapter 1 contains no comparison of alternatives at all.** Where the supervisor expects business
    problem → users → as-is process → why this design, §1.5 states scope, contribution and exclusions
    and never asks why a role-separated workflow rather than a script, a single model call or a
    retrieval pipeline.
  - **The justification is deferred to the Discussion.** §6.3, "Why functional role separation was
    selected", is the only sustained argument, and at 207 words it is the third shortest section in
    Chapter 6. Justifying the design after presenting the results makes it read as rationalisation.
  - **The report concedes the alternatives are equivalent, three times.** §2.2.1: "one fixed process or
     several bounded roles can apply the same final support rule". §2.7: "a single process with the same
     fixed gate remains a credible alternative". §6.2: "A deterministic pipeline or single grounded agent
     could apply the same support rule". `lit_t5` records the single grounded agent as a "credible
     alternative; not compared empirically".
  - **The strongest available argument is stated once, in passing.** §6.3 paragraph 2 notes that
    "Public discovery, protected collection, local restricted-data processing and final approval do not
    share one unrestricted tool boundary". That is a separation-of-duties argument — the producer
    structurally cannot approve its own claim, and a single-context agent cannot guarantee that — and it
    is the one thing role separation buys that a simpler design cannot. It is never developed, never
    connected to the business problem, and never linked to a research question.
  - **The Abstract offers a denial in place of a justification:** "It was not selected on the assumption
    that several agents are generally better than one" says what the reason was not.
- **Why it matters:** The artefact is a role-separated multi-agent workflow; that is the dissertation's
  design contribution and the thing its title names. A dissertation that never argues why its central
  design decision was necessary, and that three times concedes a simpler design would serve, cannot
  defend that contribution at viva. The supervisor identified this as a suspected gap; it is a real one.
- **Evidence:** String search for `single`, `simpler`, `deterministic pipeline`, `script`, `RAG
  pipeline` and `why multi` across `frontmatter/abstract.tex`, `chapters/*.tex` and `lit_t5`, returning
  no hit anywhere in Chapter 1; `audit/SECTION_LEDGER.md` (§6.3 at 207 words);
  `docs/PROJECT_CHARTER.md` lines 19 and 25, which assume a multi-agent pipeline in the goal and the
  original research question without argument, confirming that no charter-side justification exists
  either.
- **Required revision:** Build one argument and place it before the design. In Chapter 1, after the
  business problem and before the research questions, state the design question explicitly — what
  properties the reporting problem requires — and answer it by reference to the alternatives: a manual
  process, a deterministic script, a single model call, a retrieval pipeline, and a role-separated
  workflow. Lead with separation of duties: the reporting risk is that a component which produces a
  claim also decides whether it is supported and whether it may be released, and role separation with
  bounded permissions is what structurally prevents that, whereas a single-context design must be
  trusted to police itself. Say plainly what this costs (more states, hand-offs, storage, tests and
  maintenance — now supportable by `sculley2015debt` per `SFR-LIT-001`) and what the dissertation does
  and does not demonstrate about it. Then reduce §6.3 to interpreting that argument against the D0
  result rather than introducing it. Do not remove the honest concessions in §2.7 and §6.2; reframe them
  as the reason the D0 comparison isolates the verification gate rather than the architecture, which is
  already the correct reading.
- **Acceptance condition:** Chapter 1 contains an explicit design-rationale passage that names at least
  four alternatives (manual, deterministic script, single model call, retrieval pipeline) and states in
  plain English what role separation provides that each cannot; the separation-of-duties argument is
  stated as the primary justification and linked to a named reporting risk from §1.1; §6.3 interprets
  rather than introduces that argument; and every remaining concession that a simpler design could apply
  the same rule is explicitly reconciled with the stated justification rather than left standing against
  it.

#### `AI-DISC-001` — `BLOCKER` — Required generative-AI use disclosure is still absent, and two submission-required appendices are empty

- **Status:** `UNRESOLVED` (preserved from `FINAL_SUPERVISOR_PRIORITY_AND_AUTHORSHIP_AUDIT.md`)
- **Location:** `appendices/appendix_structure.tex` line 36, `\chapter{Generative-AI Use Disclosure}` —
  a heading with no content and no label. Also line 1, `\chapter{Evidence of Required Ethics Training}`,
  and line 2, `\chapter{Ethical Approval or Waiver Confirmation}`, both empty. Also
  `frontmatter/submission_proforma.tex`, where all eight confirmation boxes are `\EmptyBox` and the
  ethics reference field is blank; and `metadata.tex` lines 3, 4, 6 and 7
  (`CandidateQualifications`, `StudentID`, `SubmissionMonthYear`, `EthicsReference` all empty).
- **Criterion:** University submission integrity and truthful declaration of permitted AI use; the
  submission pro-forma's own requirement for "An appendix containing email confirmation of ethical
  approval or waiver". Reviewer operating agreement: do not help conceal AI use.
- **Problem:** The prior audit raised this as a BLOCKER on 31 August and it is unchanged. Appendix I is
  still an empty heading. Appendices A and B, which the pro-forma explicitly requires, are also empty
  headings. Every confirmation box on the pro-forma is unticked and the ethics reference is blank. The
  dissertation is authored under a named candidate, and this repository contains extensive
  agent-generated review and drafting artefacts, so the disclosure is not optional.
- **Why it matters:** Leaving the heading present and empty, or deleting it, could turn a permitted use
  into a misleading submission. The ethics appendix is a stated submission requirement. Neither can be
  resolved by drafting: both need candidate-supplied evidence.
- **Evidence:** `appendices/appendix_structure.tex` lines 1, 2 and 36 (headings with no following
  content); `frontmatter/submission_proforma.tex` (eight `\EmptyBox` entries, blank
  `\EthicsReference`); `metadata.tex` lines 3--7;
  `reviews/FINAL_SUPERVISOR_PRIORITY_AND_AUTHORSHIP_AUDIT.md` finding `AI-DISC-001`.
- **Required revision:** Unchanged from the prior round, and deliberately not restated in weaker terms:
  obtain the assessment-specific declaration instruction, then supply a candidate-approved, factually
  complete inventory of AI tools, purposes, prompts, affected sections, technical tasks and candidate
  modifications, and complete the declaration in the specified location and format. Supply the ethics
  training evidence and the approval or waiver confirmation for Appendices A and B. Complete the
  pro-forma fields and metadata. Tick the first seven content confirmations only after their contents are
  present and verified. Leave the eighth, ethics-confirmation box unticked and the ethics reference blank
  until the candidate supplies that evidence. Do not silently delete any empty appendix heading.
- **Acceptance condition:** Appendix I contains the exact required, truthful, candidate-approved
  declaration consistent with the assessment brief, including the tools used, purposes, prompts and how
  the outputs were modified or checked; Appendix A contains the required training evidence; the first
  seven pro-forma confirmations are truthfully ticked. Appendix B, the eighth box and the ethics reference
  remain visibly pending until the candidate-supplied approval or waiver evidence is inserted; once it is
  inserted, the final box and reference can be completed. Candidate metadata is populated separately.

#### `AI-PERM-001` — `MAJOR` — The assessment-specific declaration rule is still not evidenced

- **Status:** `UNRESOLVED` (preserved)
- **Location:** Submission evidence set; Appendix I instructions.
- **Criterion:** Course-, module- and assessment-specific AI rules take precedence over general guidance.
- **Problem:** Unchanged. The applicable WMG brief or handbook wording defining how permitted AI use must
  be declared, and whether interaction records must be attached, is not in the repository.
- **Why it matters:** The correct disclosure format cannot be inferred, and `AI-DISC-001` cannot be
  closed without it.
- **Evidence:** `reviews/FINAL_SUPERVISOR_PRIORITY_AND_AUTHORSHIP_AUDIT.md` finding `AI-PERM-001`; no
  assessment brief or handbook extract present under `Dissertation/` or `docs/`.
- **Required revision:** Obtain and preserve the applicable brief, handbook text or written programme
  advice with the submission evidence.
- **Acceptance condition:** The declaration location, wording requirement and record-attachment rule are
  traceable to the current assessment instruction, held in the repository.

#### `SFR-XS-003` — `MAJOR` — The recorded word count is not reproducible, is below the stated floor, and the declared limit conflicts with the working range

- **Status:** `NEW`
- **Location:** `Dissertation/REPORT_STRUCTURE.md` lines 7--12 and the word-and-evidence-map table
  (lines 43--54); `Dissertation/metadata.tex` line 8 (`\WordLimit{15,000}`).
- **Criterion:** Explicit submission requirements take highest evidence priority; cross-section
  consistency of stated counts.
- **Problem:** `REPORT_STRUCTURE.md` states 14,376 citation-stripped words for the Abstract and
  Chapters 1--8, described as "within the supervisor's 14,000--16,000 working range", and attributes the
  figure to `check_sources.iter_prose_paragraphs` and `prose_word_count`. Applying those two functions
  to the same files gives **13,874** words — 502 fewer, and below the stated 14,000 floor. Per-chapter
  figures also diverge: Chapter 1 is recorded as 1,566 against 1,387 measured; Chapter 4 as 3,100
  against 2,941; the Abstract as 378 against 374. `scripts/check_sources.py` has no word-count entry
  point, so the recorded total is hand-assembled and not reproducible by any documented command.
  Separately, `metadata.tex` declares a 15,000-word limit while the brief for this review states a
  14,000--16,000 range. Those cannot both govern: if 15,000 is the limit, current headroom is about
  1,126 words, which materially constrains every addition this review requires.
- **Why it matters:** Word count is a hard submission requirement, the report may currently be under the
  stated minimum, and the remediation plan cannot be sized without resolving which limit applies. This
  is why the plan in section 12 funds additions from cuts rather than simply adding.
- **Evidence:** Re-execution of `check_sources.iter_prose_paragraphs` and
  `check_sources.prose_word_count` over `frontmatter/abstract.tex` and `chapters/*.tex`, giving
  Abstract 374, Ch1 1,387, Ch2 3,293, Ch3 1,128, Ch4 2,941, Ch5 1,724, Ch6 1,622, Ch7 759, Ch8 646,
  total 13,874; `REPORT_STRUCTURE.md` line 11 and table; `metadata.tex` line 8;
  `scripts/check_sources.py` (`prose_word_count` used only for a minimum-20-word paragraph check).
- **Required revision:** Add a reproducible word-count command to `scripts/` and regenerate every count
  in `REPORT_STRUCTURE.md` and `audit/SECTION_LEDGER.md` from it. Obtain from the user or the assessment
  brief which limit governs — the 15,000 in `metadata.tex` or the 14,000--16,000 working range — and
  record it in one place. Then apply the section 12 budget against that figure.
- **Acceptance condition:** A documented command reproduces the stated total and every per-chapter
  figure; the governing word limit is recorded once and is consistent between `metadata.tex` and
  `REPORT_STRUCTURE.md`; and the final total sits inside it with a stated margin.

#### `SFR-XS-004` — `MAJOR` — The reference audit claims complete coverage but omits two cited sources

- **Status:** `NEW`
- **Location:** `Dissertation/sources/REFERENCE_AUDIT.md`, opening sentence ("Every source cited in the
  dissertation has a local PDF") and the audit table (lines 17--61).
- **Criterion:** Citation and source rules — every cited source must be verified; evidence-control
  integrity.
- **Problem:** The audit table contains 43 rows. The manuscript cites 45 keys. `dibia2024autogenstudio`
  and `spacexai2026grokbot` are cited (four times each) but have no audit row, so the document's opening
  claim of complete coverage is false. Both are in fact fine: `sources/MANIFEST.csv` has rows for both,
  `sources/papers/44_dibia_et_al_autogen_studio.pdf` and `sources/html/spacexai_grok_bot_bots.pdf` both
  exist, and this review read the latter in full and confirmed it supports the attributed claims. The
  defect is in the audit record, not the sources.
- **Why it matters:** The reference audit is the document an examiner would rely on to confirm source
  integrity, and it is the control that `SFR-METH-001` and `SFR-LIT-001` will add rows to. A coverage
  claim that is false undermines the whole evidence-control apparatus even though the underlying sources
  are sound.
- **Evidence:** Set difference between the 45 keys extracted from `\cite*` commands in
  `chapters/*.tex`, `frontmatter/*.tex` and `exhibits/*.tex` and the keys present in
  `sources/REFERENCE_AUDIT.md`; `sources/MANIFEST.csv` rows for both keys;
  `sources/WEB_CAPTURES.csv` row for `spacexai2026grokbot` (six pages, both hashes, capture date
  2026-08-31).
- **Required revision:** Add audit rows for both keys with their local PDF, page count and verification
  note, matching the existing format. Extend `scripts/check_sources.py --strict-bibliography` to check
  `REFERENCE_AUDIT.md` coverage as well as manifest coverage, so the gap cannot recur when
  `SFR-METH-001` and `SFR-LIT-001` add sources.
- **Acceptance condition:** Every key cited in the manuscript has a row in `REFERENCE_AUDIT.md`, and an
  automated check fails if that is not true.

#### `SFR-XS-005` — `MAJOR` — Thirteen of twenty-nine exhibits and three of twelve figures are never referenced, and one exhibit is never included at all

- **Status:** `NEW`
- **Location:** Across all chapters and `appendices/appendix_structure.tex`. Full list in the evidence
  below.
- **Criterion:** Tables and figures rubric — "every item is numbered, titled or captioned, **referenced
  in the text**, and necessary"; "the text explains the research-relevant meaning rather than merely
  saying the item exists".
- **Problem:** The exhibit set has drifted from the prose. Thirteen exhibits define a `\label` and are
  typeset, but no `\ref` to them exists anywhere in the manuscript:
  `tab:signal-inference-boundary` (`lit_t2`), `tab:data-semantics-matrix` (`lit_t3`),
  `tab:eval-d0-case-examples` (`eval_t4a`), `tab:appendix-d0-case-ledger`,
  `tab:eval-held-company-comparison` (`eval_t6`), `tab:eval-human-comparison-status` (`eval_t7`),
  `tab:disc-rq-evidence-status` (`disc_t1`), `tab:disc-transfer-conditions` (`disc_t2`),
  `tab:disc-literature-result-alignment` (`disc_t3`), `tab:conc-evidence-roadmap` (`conc_t1`), and all
  four `tab:meth-*` matrices. One exhibit,
  `exhibits/lit_t1_review_source_admission.tex` (`tab:review-source-admission`, 414 words), is never
  `\input` anywhere, so it is a dead file that does not compile into the document at all. Three current,
  rendered, checksum-bound figures are unused: `intro_f1_problem_to_research_contract.png`,
  `meth_f2_dataset_freeze_timeline.png` and `meth_f3_analysis_decision_flow.png`. Several of these
  matter individually and are raised in their own chapters — `disc_t1` in `SFR-RES-001`, `eval_t4a` in
  `SFR-RES-005`, `intro_f1` in `SFR-INTRO-001` — but the pattern is one root cause and is listed here
  once.
- **Why it matters:** Unreferenced exhibits float into the document without the prose preparing the
  reader, which is a direct contributor to the supervisor's readability complaint; and a table the prose
  never uses is, by the rubric's test, not necessary. In three cases the unused artefact is exactly what
  a supervisor request needs.
- **Evidence:** Comparison of all `\label{tab:…}` and `\label{fig:…}` definitions in `exhibits/*.tex`
  and `chapters/*.tex` against all `\ref{…}` uses in `chapters/*.tex` and `frontmatter/*.tex`;
  comparison of `\input{exhibits/…}` commands in `chapters/*.tex` and `appendices/appendix_structure.tex`
  against the exhibit file list; comparison of `exhibits/MERMAID_MANIFEST.csv` against
  `\includegraphics` uses.
- **Required revision:** For each unreferenced exhibit, take one of three decisions and record it:
  reference it in the prose at the point where the reader needs it; delete it; or, for appendix
  material, reference it from the chapter that relies on it. Resolve `lit_t1` explicitly — either include
  it in an appendix and reference it, or delete the file. Use `intro_f1` per `SFR-INTRO-001` and
  consider `meth_f2` per `SFR-METH-O1`.
- **Acceptance condition:** Every exhibit that compiles into the document is referenced at least once in
  the prose of the chapter that relies on it; no exhibit file exists without either an `\input` or a
  recorded decision to retire it; and every figure in `MERMAID_MANIFEST.csv` is either used or removed
  from the manifest.

#### `SFR-XS-006` — `MAJOR` — Table placement fails in both directions: oversized tables remain in the body while the tables the body argues from sit in appendices

- **Status:** `NEW`
- **Location:** Body: `chapters/02_literature_review.tex` lines 104, 150, 308 and 355 (`lit_t2` 366
  words, `lit_t3` 397, `lit_t4` 458, `lit_t5` 235). Appendices, but referenced as though present:
  `chapters/04_system_design.tex` lines 8, 97 and 173 (`tab:sys-requirements-trust-boundary`,
  `tab:sys-adapter-capability-state`, `tab:sys-failure-recovery-status`, all in Appendix C);
  `chapters/05_evaluation_results.tex` lines 6 and 33 (`tab:eval-implementation-snapshot`,
  `tab:eval-engineering-validation`, both in Appendix G);
  `chapters/07_governance_limitations.tex` line 86 (`tab:gov-residual-risk`, in Appendix H).
- **Criterion:** Tables rubric — "essential reasoning is not hidden exclusively in an appendix";
  "the level of detail is proportionate to the section's purpose". Supervisor point S5 (move large tables
  to appendices).
- **Problem:** The supervisor's instruction has been applied unevenly, producing two opposite faults.
  1. **Oversized tables remain in the body.** Chapter 2 carries 1,456 words of tabular content in four
     tables. `lit_t2` and `lit_t3` are full-page `[p]` floats, each wrapped in `\clearpage`, and neither
     is referenced in the prose. They are the clearest candidates for the appendix.
  2. **The body's own argument tables were moved out.** Six tables that the prose actively argues from
     now sit in appendices while the chapters still refer to them as if adjacent. Chapter 4 says
     "Table~\ref{tab:sys-requirements-trust-boundary} maps these controls and holds…", then two lines
     later says "The full requirements and trust-boundary matrix is provided in
     Appendix~\ref{app:requirements-traceability}" — the same table, referred to twice, once as present
     and once as remote. The same double reference occurs for the connector-state matrix, the
     failure-recovery matrix, the implementation snapshot, the engineering-validation ledger and the
     governance residual-risk matrix. A reader following Chapter 4's argument must turn to an appendix
     six times, and the pattern makes the prose read as a set of pointers.
- **Why it matters:** The supervisor's aim was a more readable body, and the current arrangement is less
  readable than either extreme: the tables that interrupt reading stayed, and the tables that support
  reading left. This is also a substantial part of the whitespace problem recorded as `LAYOUT-001`.
- **Evidence:** Exhibit word and line counts; `\input` locations in `chapters/*.tex` and
  `appendices/appendix_structure.tex`; the paired in-text and appendix references listed above;
  `exhibits/lit_t2_signal_inference_boundary.tex` and `lit_t3_data_semantics_matrix.tex` lines 1--2 and
  closing `\clearpage`.
- **Required revision:** Apply one consistent rule and state it in `REPORT_STRUCTURE.md`: a table stays
  in the body only if the prose argues from it at that point and it fits within roughly half a page;
  everything else goes to an appendix and is referred to once, as an appendix item. Under that rule, move
  `lit_t2` and `lit_t3` to an appendix, keep `lit_t5` in the body (it carries the alternatives argument
  and is short), and decide `lit_t4` on the same test. For the six exiled tables, replace each pair of
  references with a single appendix-form reference, and where the prose genuinely needs a table at that
  point, bring a reduced version of it into the body. Remove the `\clearpage` pairs around any exhibit
  that moves.
- **Acceptance condition:** `REPORT_STRUCTURE.md` records the placement rule; no table is referred to
  both as present in the body and as provided in an appendix; Chapter 2's body tables total no more than
  700 words; and no body chapter contains a full-page table float that the prose does not reference.

#### `SFR-XS-007` — `MAJOR` — Two prior full-report approvals describe a superseded draft and must not be treated as current

- **Status:** `NEW_EVIDENCE`
- **Location:** `reviews/FULL_REPORT_CROSS_SECTION_REVIEW.md` (`gate: PASS`, zero findings);
  `reviews/FINAL_SUPERVISOR_PRIORITY_AND_AUTHORSHIP_AUDIT.md` (section 6, all dimensions "meets");
  `reviews/CHAPTER_2_COMPREHENSIVENESS_REVIEW.md` and
  `reviews/CHAPTER_6_SUPERVISOR_PRIORITY_REVIEW.md` (both `gate: PASS`).
- **Criterion:** Re-review protocol — verify the actual revised text rather than accepting a prior
  claim; approval must be traceable to the reviewed artefact.
- **Problem:** Four reports in the reviews folder record `PASS` or "meets" for material that no longer
  exists. `FULL_REPORT_CROSS_SECTION_REVIEW.md` approves a draft with "RQ1--RQ3", a 104-page PDF and a
  named PDF checksum. `FINAL_SUPERVISOR_PRIORITY_AND_AUTHORSHIP_AUDIT.md` records "RQ1--RQ3 remain
  stable", "15,824 words across the Abstract and Chapters 1--8", "3,201 words for the literature
  review", "2,439 for discussion", a "43-entry bibliography", "192 substantive manuscript paragraphs"
  and a 110-page PDF. The current draft has two sub-questions, 13,874 words, Chapter 2 at 3,293 and
  Chapter 6 at 1,622, a 45-entry bibliography and about 182 substantive paragraphs.
  `audit/SECTION_LEDGER.md` states the position correctly — "Older review files remain historical
  evidence but do not approve wording changed in this revision" — and records all 53 sections as
  `PENDING`. But the four PASS reports carry no superseded marker, and two of them make positive
  findings ("Critical analysis — meets", "Structure and coherence — meets" for Chapter 2) that the
  supervisor's feedback and this review both contradict.
- **Why it matters:** Anyone reading the reviews folder would reasonably conclude the report has passed a
  full-report gate. It has not. Two of the specific "meets" judgements concern exactly the dimensions the
  supervisor criticised, and leaving them unmarked risks the remediation work being treated as optional.
- **Evidence:** `reviews/FULL_REPORT_CROSS_SECTION_REVIEW.md` lines 3--8 and 14--21;
  `reviews/FINAL_SUPERVISOR_PRIORITY_AND_AUTHORSHIP_AUDIT.md` lines 98--113;
  `reviews/CHAPTER_2_COMPREHENSIVENESS_REVIEW.md` lines 31 and 55;
  `reviews/CHAPTER_6_SUPERVISOR_PRIORITY_REVIEW.md` lines 30 and 59;
  `audit/SECTION_LEDGER.md` header and the 53 `PENDING` rows; string search confirming no `RQ3` remains
  in the manuscript; re-executed word counts.
- **Required revision:** Mark the four reports as superseded at the top of each file, naming the draft
  they reviewed (RQ1--RQ3, 15,824 words) and pointing to this report as the current gate. Do not delete
  them; they are legitimate historical evidence. Record in `reviews/REVIEW_LOG.md` that no full-report
  approval is currently in force.
- **Acceptance condition:** Each superseded report carries a header stating the draft it reviewed and
  that it does not approve the current manuscript; `REVIEW_LOG.md` records that the current full-report
  gate is FAIL; and no reader of the reviews folder can mistake a historical PASS for a current one.

### 10.4 Prior-finding reconciliation (cross-section)

A full census of the prior reports identifies **44 stable finding identifiers** across ten review files.
The great majority are closed and were verified closed. The table below records every prior identifier
that is **not** cleanly resolved, plus the resolved families in aggregate. No prior identifier has been
renumbered, and no new identifier reuses a prior prefix: this review uses the previously unused `SFR-`
prefix throughout, so `LIT-COMP-001`, `-002` and `-004` — which are absent from both the reports and the
current tree — remain unallocated.

| Finding | Previous severity | Status | Verification |
|---|---:|---|---|
| AI-DISC-001 | BLOCKER | UNRESOLVED | Appendix I remains an empty heading; Appendices A and B are also empty; all pro-forma boxes unticked. Carried as a BLOCKER in this report. |
| AI-PERM-001 | MAJOR | UNRESOLVED | No assessment brief or handbook extract is present in the repository. Carried as a MAJOR in this report. |
| LIT-COMP-006 | MINOR | UNRESOLVED | Lower-page whitespace on physical pages 21 and 27 from forced exhibit pagination. Its own acceptance condition offers "accept or polish"; because `SFR-XS-006` and `SFR-LIT-002` both require moving the Chapter 2 tables that cause the forced breaks, resolving those resolves this. Not independently re-paginated in this review. |
| LAYOUT-001 | MINOR | UNRESOLVED | The same physical phenomenon as `LIT-COMP-006` under a second identifier. Recorded here as a duplicate pair rather than a third identifier. Resolution folded into `SFR-XS-006`. |
| ABSTRACT-002 | MINOR | STILL PARTIALLY RESOLVED | The final-freeze provenance archive it requires still does not exist. Escalated in substance as `SFR-RES-002`; see §6.4. |
| CH2-R3-001 | MINOR | AMBIGUOUS — retained | Its own text says the exact-total drift "was corrected"; the same report's handoff still counts it among two remaining polish items. Retained under its original identifier rather than reissued. Now superseded in substance by `SFR-XS-003`, since the word total it reconciled to is itself contradicted. |
| CH2-REG-001 | MAJOR | RE-OPENED | Re-opened on new evidence under re-review rule 7; reason recorded in §3.4. |
| DISC-SUP-003 | MAJOR | REGRESSION | See `SFR-DISC-003`. The versioned-JSON defence recorded as resolved is no longer present. |
| DISC-SUP-005 | MAJOR | REGRESSION | See `SFR-DISC-003`. The contradiction-ledger interpretation recorded as resolved is no longer present. |
| DISC-SUP-001 | MAJOR | RESOLVED, but scope not fully met | Correctly closed against its own acceptance condition, which never enumerated the supervisor's six pilot elements. The three missing elements are raised as new findings under `SFR-DISC-001` rather than by re-opening this identifier. |
| (unnumbered OPTIONAL, Ch5) | OPTIONAL | STILL OPEN | Final-freeze archive request; subsumed by `SFR-RES-002`. |
| STRUCT-001 … STRUCT-005 | Major/Minor | RESOLVED | Structure, applicability lists, glossary, DNS wording and fallback rules all verified against `main.tex` and `REPORT_STRUCTURE.md`. RQ3 is fully removed. |
| ABSTRACT-001; LIT24-001; LIT25-001/-002; LIT25-R2-001; LIT26-001 | Major/Minor | RESOLVED | Spot-verified: no universal recommendation wording survives; LIT-F2 is correctly placed and correctly describes the model-assisted channel. |
| METH33-001/-002; METH36-001/-002; METH37-001 | Major | RESOLVED | Spot-verified: the analysis protocol is no longer described as frozen when draft, and the cited ledger checksums resolve. |
| SYS41-001/-002; SYS44-001; SYS44-R2-001; SYS45-001; SYS47-001/-002 | Major/Minor | RESOLVED | Spot-verified: `NFR-RES-001` is used consistently and the sealed-hash drift is closed. |
| LIT-COMP-003; LIT-COMP-005; CH2-REG-002; DISC-SUP-002/-004/-006/-007; DISC-R3-001 | Major/Minor | RESOLVED | Verified closed. Note that `LIT-COMP-003` closed a *comparison-table* obligation and does **not** discharge the multi-agent design justification now raised as `SFR-XS-002`. |

Two corrections to how the prior record should be read. First, the current whole-report gate in force
before this review was `FINAL_SUPERVISOR_PRIORITY_AND_AUTHORSHIP_AUDIT.md` at `HOLD` /
`EVIDENCE_REQUIRED`, not any of the `PASS` gates; `REVIEW_LOG.md` stops at an earlier 104-page PASS and
never records `AI-DISC-001`, `AI-PERM-001`, `LIT-COMP-*`, `DISC-SUP-*` or `LAYOUT-001`. Second, none of
the prior reports contains a finding on repeated limitations, oversized body tables, worked
accepted/rejected examples, the as-is business process, or the multi-agent justification. Those five
supervisor concerns are genuinely new review axes, which is why they take new identifiers rather than
re-opened ones.

### 10.5 Non-blocking notes (cross-section)

- **MINOR — `SFR-XS-M1`:** `frontmatter/declaration.tex`'s project-definition paragraph describes the
  project as "creating public-company research with clear supporting evidence" starting from a Companies
  House number, and never mentions portfolio reporting, the D0 evaluation or the verification
  comparison. It therefore foregrounds the unvalidated public-web route and misaligns with the active
  research contract. Align it with the retitled scope when `SFR-XS-001` is resolved.
- **MINOR — `SFR-XS-M2`:** The glossary has 15 entries. `HITL`, `OOS` and standalone `RQ` never appear
  in the body; more than twenty acronyms that do appear are missing. Fold into `SFR-SYS-001`.
- **MINOR — `SFR-XS-M3`:** `REPORT_STRUCTURE.md`'s appendix map omits `disc_t1` and `eval_t7` from the
  Appendix F contents, and describes Chapter 2's body exhibits as "Evidence-boundary figures; concise
  alternatives table" when the chapter carries four tables.
- **MINOR — `SFR-XS-M4`:** `docs/IMPLEMENTATION_TRACEABILITY.md` describes company-research routing in
  one row as a two-tier `n.4`/`n.4-mini` design under ADR-0010 and in another as pinned to a single
  model under ADR-0011. This is a repository inconsistency rather than a dissertation defect, but it
  will need resolving before `SFR-GOV-001` can state the route accurately.
- **MINOR — `SFR-XS-M5`:** `audit/SECTION_LEDGER.md` records all 53 sections as `PENDING` with no review
  round. After this review, the ledger should record round and gate per section.
- **OPTIONAL — `SFR-XS-O1`:** Consider renaming C1 and C2 in reader-facing prose to "without a separate
  checking stage" and "with a separate checking stage", keeping C1/C2 as the formal labels. This would
  do more for the non-technical reader than any other single change, and it interacts usefully with
  `SFR-RES-003`.

### 10.6 Cross-section dimensions

- **Research questions and objectives — meets.** Stable and consistently stated; no `RQ3` remnant.
- **Terminology and definitions — partly meets.** Consistent between chapters, but the evaluator's
  condition and metric names are never reconciled with the prose (`SFR-RES-003`) and the glossary does
  not cover the body's vocabulary.
- **Method as planned versus implemented — partly meets.** Honestly distinguished, except that Chapter 4
  describes migration 0010 while the evaluation used 0009 (`SFR-SYS-002`).
- **Reported values and metric definitions — meets.** Every D0 value agrees across nine locations and
  reproduces from the saved output. The only inconsistency is the contradiction count in §5.8
  (`SFR-RES-004`).
- **Results versus interpretation — meets.** Chapter 6 interprets without inflating; selective admission
  is never presented as improved coverage.
- **Limitations versus conclusion — does not meet.** The limitations are everywhere and therefore
  nowhere (`SFR-GOV-002`), and Chapter 8 states none of its own (`SFR-CONC-001`).
- **Contributions versus evidence — does not meet.** The title claims impact and auditability that the
  body disclaims (`SFR-XS-001`), and the central design contribution is unjustified (`SFR-XS-002`).
- **Abstract versus body — partly meets.** Numerically faithful; omits the research questions and is
  written for a technical reader (`SFR-ABS-001`).
- **Appendices versus body — does not meet.** Placement fails in both directions (`SFR-XS-006`), thirteen
  exhibits are unreferenced (`SFR-XS-005`), and three required appendices are empty (`AI-DISC-001`).

---

## 11. Overall gate

```yaml
review:
  skill: dissertation-reviewer
  gate: FAIL
  verdict: REVISE
  mode: MULTI_SECTION_REVIEW
  section: "Abstract and Chapters 1-8, with cross-section audit"
  section_type: "complete dissertation candidate"
  round: 2
  scope: "Dissertation/ (Abstract, chapters 1-8, exhibits, appendices, front matter, metadata, references) verified against the repository implementation and evaluation artefacts"
  evidence_confidence: HIGH
  findings:
    blocker: 4
    major: 24
    minor: 23
    optional: 5
  previous_findings:
    total_prior_ids: 44
    resolved: 35
    partially_resolved: 1
    unresolved: 4
    regression: 2
    user_waived: 0
    ambiguous_retained: 1
    re_opened: 1
  next_owner: dissertation-expert
```

**REVISE.** No section passes. The dissertation's empirical core is sound — every reported D0 value
reproduces exactly from the saved evaluation output, the fixture and its fourteen cases verify by
checksum, and the implementation claims match the code and requirements register — but four blocking
defects remain: a governance statement contradicted by the repository, a title that claims what the body
disclaims, an unjustified central design decision, and required disclosure appendices that are empty.
Beyond those, the supervisor's six points are only partly addressed, and the specific mechanical causes
of the readability complaint are now identified and measurable.

`next_owner` is `dissertation-expert` for 25 of the 28 blocking findings. Three require the user or the
evidence owner: `AI-DISC-001` and `AI-PERM-001` need candidate-supplied evidence and the assessment
brief, and `SFR-RES-002` and `SFR-RES-006` need evaluation artefacts regenerated or committed and the
validation suite re-run. `SFR-XS-003` needs a user decision on which word limit governs.

### 11.1 Supervisor feedback: point-by-point status

| # | Supervisor point | Status | Basis |
|---|---|---|---|
| 1 | Focus on what was actually validated | **PARTLY ADDRESSED** | Research contract, evidence tiers and null states are handled well and RQ3 was cleanly removed. But the title claims impact (`SFR-XS-001`), Chapter 4 describes an unevaluated version (`SFR-SYS-002`), ~350 words go to an unimplemented product (`SFR-DISC-002`), two Chapter 5 sections report nothing, and the engineering-validation figures are superseded by a later in-repository gate the project's own notes flagged as unreconciled (`SFR-RES-006`). |
| 2 | Business problem, users, as-is process, why multi-agent | **NOT ADDRESSED** | The gap is real. Chapter 1 contains no design-alternatives argument; the justification sits in a 207-word Discussion section after the results; and the report concedes three times that a simpler design would apply the same rule (`SFR-XS-002`). The business problem rests on one self-authored note with no baseline (`SFR-INTRO-001`). |
| 3 | Literature review and technical sections lack flow, hard to read | **NOT ADDRESSED** | Causes now measured: 31 of 36 Chapter 2 paragraphs end on a prohibition; motivation is buried in the only subsection; two unreferenced full-page tables interrupt the chapter (`SFR-LIT-002`). Chapter 4 uses requirement identifiers as prose subjects with 20-plus unglossed acronyms (`SFR-SYS-001`). |
| 4 | Remove repeated limitations | **NOT ADDRESSED** | About 60 explicit disclaimer sentences; 101 of 182 paragraphs carry a scope negation; Chapter 2 at 86 per cent and Chapter 7 at 85 per cent. Chapter 1 claims Chapter 7 records the limitation "once"; six other chapters restate it (`SFR-GOV-002`). |
| 5 | Move large tables to appendices; add worked accepted/rejected examples | **PARTLY ADDRESSED** | Sixteen exhibits did move, but placement now fails in both directions — oversized unreferenced tables stayed in Chapter 2 while six tables the body argues from went to appendices and are double-referenced (`SFR-XS-006`). The worked-example table `eval_t4a` exists and is good, but is never referenced or narrated (`SFR-RES-005`). |
| 6 | Business pilot: integration, costs, staff, time savings, success metrics, remaining testing | **LARGELY ADDRESSED** | The strongest response to the feedback. Integration, staff responsibilities, cost measurement and success metrics with a frozen go/no-go rule are all present and specific. Gaps: no pilot size, duration or minimum completed-report count; no time-saving acceptance criterion among the frozen thresholds; remaining testing dispersed across five locations (`SFR-DISC-001`). |

### 11.2 Additional user requirements: status

| Requirement | Status | Basis |
|---|---|---|
| Register and audience (plain English, non-technical reader) | **NOT ADDRESSED** | Sentences are short (mean 15--17 words), so the problem is density and vocabulary, not length. The Abstract reports its headline result in undefined metrics; Chapter 4 uses seven unexplained requirement codes as sentence subjects; 20-plus used acronyms are absent from a 15-entry glossary that contains three unused entries (`SFR-ABS-001`, `SFR-SYS-001`). |
| Scoping to the implementation, not generic filler | **PARTLY ADDRESSED** | Most content is specifically grounded, which is a genuine strength. The exceptions are the Grok Bot thread, which would fit any dissertation (`SFR-DISC-002`), and the two empty Chapter 5 sections. |
| Direct, traceable RQ addressing | **PARTLY ADDRESSED** | RQ1 and RQ2 are stated, headed in Chapter 6 and answered in Chapter 8. But Chapter 5 never mentions them, and the RQ-to-answer table is unreferenced in an appendix (`SFR-RES-001`). |
| Expand the academic literature review | **NOT ADDRESSED** | Chapter 2 derives design criteria rather than synthesising research; no two sources are placed in tension. Five thematic gaps identified. Three admitted, checksum-verified local PDFs are unused, including `ribeiro2020checklist`, which would supply D0's missing methodological warrant (`SFR-LIT-001`, `SFR-METH-001`). |

### 11.3 Top eight must-fix items, in priority order

1. **`SFR-GOV-001` (BLOCKER)** — Correct §7.2, `gov_t1` and §5.5: a bounded synthetic external-model run
   did occur, with observed tokens and latency recorded in five run manifests. Name the model once.
2. **`AI-DISC-001` (BLOCKER)** — Complete the generative-AI use disclosure and the ethics appendices;
   needs candidate-supplied evidence and the assessment brief (`AI-PERM-001`).
3. **`SFR-XS-002` (BLOCKER)** — Build the multi-agent justification in Chapter 1, led by separation of
   duties, and reconcile the three concessions that a simpler design would serve.
4. **`SFR-XS-001` (BLOCKER)** — Retitle: remove "Impact" and "Auditable" and shorten to plain words.
5. **`SFR-GOV-002` (MAJOR)** — Consolidate the limitations into §7.5 and delete about 35 routine
   disclaimers. This also frees the words the other fixes need.
6. **`SFR-LIT-001` + `SFR-METH-001` (MAJOR)** — Deepen Chapter 2 into critical synthesis and give D0 a
   methodological warrant, using `ribeiro2020checklist`, `sculley2015debt`, `souppaya2022ssdf` and
   `hevner2004design`, all already admitted.
7. **`SFR-LIT-002` + `SFR-SYS-001` (MAJOR)** — Fix the readability mechanics: rewrite paragraph endings
   in Chapter 2, and remove requirement codes and unglossed acronyms from Chapter 4.
8. **`SFR-RES-001` + `SFR-RES-005` + `SFR-RES-004` + `SFR-RES-006` (MAJOR)** — Make Chapter 5 answer the
   research questions explicitly, narrate the accepted and rejected worked examples, bring `disc_t1` into
   the body, correct "the only conflict" to two, and settle the engineering-validation figures on one
   re-run rather than the superseded 286 / 85.58 per cent / 46-file set.

---

## 12. Prioritised remediation plan

Ordered by supervisor feedback point. The following candidate decisions, supplied on 1 September 2026,
now bind this plan:

1. The working target is **15,000 words, with a permitted planning range of 13,500--16,500 words for the
   main body**. The main-body count means Chapters 1--8 prose. It excludes the Abstract and other front
   matter, table bodies and captions, figure content and captions, references and appendices. An
   authenticated WMG counting rule takes precedence if it defines an exclusion differently. The final
   repository command must state and reproduce the applied convention.
2. On the submission pro-forma, the first seven content confirmations are to be ticked after their
   corresponding contents have been verified. The eighth confirmation, for the ethics approval or waiver
   appendix, remains unticked and the ethics reference remains blank until the candidate provides the
   screenshot or email evidence. This pending state must not be presented as approval.
3. The user-supplied WMG section 3.2 wording is the drafting requirement for the generative-AI
   acknowledgement. The declaration must name the actual tool or tools and state that AI was used only in
   support of report structure, visualisations, research, feedback and review, and technical
   implementation. Appendix I must list the actual prompts and explain how outputs were modified and
   checked. Tool names, URLs, prompt records and modifications must come from a candidate-approved
   inventory; they must not be reconstructed or invented. The example sentence claiming that no
   AI-generated content was presented as the candidate's work is included only if the candidate confirms
   that it is factually accurate.
4. Overclaims are not automatically deleted. Each one passes through the claim-remediation gate below.
   A bounded technical change may be proposed where it is within the research scope and can create
   relevant evidence. Implementation alone does not validate a claim: new behaviour must be followed by
   proportionate tests and the applicable evaluation. Claims about impact, time savings, usability,
   adoption or real-world reliability still require business or human evidence and cannot be repaired by
   code alone.

The previous **13,874** total included the 374-word Abstract. Under the confirmed main-body boundary, the
current measured baseline is therefore **13,500** citation-stripped prose words and the existing stage
deltas target about **14,364** main-body words. This is inside the confirmed 13,500--16,500 range. These
figures remain provisional until the reproducible counter implements the confirmed exclusions and
regenerates the chapter totals required by `SFR-XS-003`.

Every stage that adds words is funded by a stage that removes them, so the plan is executable in order
without relying on the upper tolerance as spare drafting space. Stages 1 and 2 are net negative and must
run first.

### Claim-remediation gate

| Claim state | Planned response | Evidence required before the wording can remain |
|---|---|---|
| Already implemented and evaluated for the stated population and condition | Keep, but align the wording exactly with the observed measure | Resolved artefact, denominator, condition, run identity and claim-ledger link |
| Implemented but not evaluated | Narrow the present-tense conclusion or add an in-scope evaluation | Targeted tests plus the relevant frozen evaluation; implementation evidence alone is insufficient |
| Not implemented, but a small coherent change could test a core research claim | Prepare a separately authorised implementation packet and compare its cost, risk and word impact with the wording-only correction | Code review, targeted tests, evaluation artefact, provenance update and manuscript reconciliation |
| Business-impact or human-use claim | Keep as a pilot hypothesis or remove | Authorised pilot or human study with pre-defined baseline, measure, threshold and result |
| Product-scale, production-readiness or broad generalisation claim | Remove or state as future work unless the full boundary is genuinely evaluated | Security, operations, integration, population and external-validity evidence appropriate to the claim |

For every suspected overclaim, record the exact sentence, present evidence, proposed wording-only fix,
possible implementation fix, further validation required, scope/cost decision and final disposition. A
technical implementation packet is a separate execution decision, not implied authority to change the
prototype during dissertation revision.

### Stage 0 — Evidence and decisions that block drafting

| # | Action | Findings | Owner |
|---|---|---|---|
| 0.1 | Implement and document a reproducible Chapters 1--8 main-body counter using the confirmed 13,500--16,500 range and exclusions; regenerate all chapter and ledger counts | `SFR-XS-003` | evidence-owner |
| 0.2 | Preserve or source-capture the user-supplied WMG section 3.2 instruction; supply a candidate-approved inventory of actual tools, URLs, purposes, prompts, affected sections/tasks and output modifications | `AI-DISC-001`, `AI-PERM-001` | user and evidence-owner |
| 0.3 | Supply ethics training evidence for Appendix A. Keep Appendix B, the eighth pro-forma box and the ethics reference pending until the approval/waiver screenshot or email is provided | `AI-DISC-001` | user |
| 0.4 | Regenerate or commit the D0 evaluation output so its cited checksum resolves; re-derive all §5.1 and `eval_t1` hashes and dates | `SFR-RES-002` | evidence-owner |
| 0.4b | Re-run the validation suite once on a clean committed tree and record the test count, coverage, typed-file count and migration head from that single run | `SFR-RES-006` | evidence-owner |
| 0.5 | Reconcile `docs/IMPLEMENTATION_TRACEABILITY.md` on the model route before §7.2 is rewritten | `SFR-GOV-001`, `SFR-XS-M4` | evidence-owner |
| 0.6 | Decide whether the two-citations-per-paragraph rule is relaxed for argument paragraphs | `SFR-GOV-002` | user |
| 0.7 | Create the overclaim ledger and apply the claim-remediation gate before retitling or narrowing technical claims; identify any bounded implementation packets for separate approval | `SFR-XS-001`, `SFR-XS-002`, all affected claim findings | writer and evidence-owner |

### Stage 1 — Supervisor point 1: focus on what was validated (net −260)

| # | Action | Findings | Words |
|---|---|---|---:|
| 1.1 | Apply the claim-remediation gate to the title, then update `metadata.tex`, `main.tex` keywords and `declaration.tex`. Remove "Impact" unless pilot evidence exists; retain "Auditable" only if a defined auditability claim is implemented and evaluated, otherwise narrow it | `SFR-XS-001`, `SFR-XS-M1` | 0 |
| 1.2 | Reduce Grok Bot to one `lit_t5` row plus one Chapter 8 sentence; delete the Chapter 2 and Chapter 6 paragraphs | `SFR-DISC-002` | −290 |
| 1.3 | Compress §5.6 and §5.7 into two sentences inside §5.8 | `SFR-RES-M2` | −100 |
| 1.4 | State Chapter 4's described versus evaluated migration head in its opening section; scope §3.2's evaluand claim | `SFR-SYS-002` | +30 |
| 1.5 | Add one statement of which components D0 exercised | `SFR-SYS-001` | +20 |
| 1.6 | Mark the four superseded review reports; update `REVIEW_LOG.md` and `SECTION_LEDGER.md` | `SFR-XS-007`, `SFR-XS-M5` | 0 |
| 1.7 | Correct "the only conflict" to two contradictions | `SFR-RES-004` | 0 |
| 1.8 | Correct §7.2, `gov_t1` and §5.5 on the external-model run; name the model and its route once | `SFR-GOV-001` | +80 |
| 1.9 | Add `REFERENCE_AUDIT.md` rows for the two missing keys and extend the automated check | `SFR-XS-004` | 0 |
| 1.10 | Replace the engineering-validation figures with the single re-run result; align `eval_t2`, Chapter 4 and FR-OBS-003 on one migration head | `SFR-RES-006`, `SFR-SYS-M4` | 0 |
| 1.11 | Qualify "only two deterministic adapters" as admitted external-source adapters; name the deck schema instead of "profile version three" | `SFR-SYS-M3`, `SFR-RES-M3` | 0 |
| | **Stage 1 net** | | **−260** |

### Stage 2 — Supervisor point 4: consolidate limitations (net −380)

Do this before Stages 3--5; it supplies their budget.

| # | Action | Findings | Words |
|---|---|---|---:|
| 2.1 | Write one consolidated boundary statement in §7.5, organised by what it prevents concluding | `SFR-GOV-002` | +120 |
| 2.2 | Delete about 35 routine disclaimers across Chapters 1--6 and 8; keep the three that qualify an adjacent claim | `SFR-GOV-002` | −500 |
| 2.3 | Replace remaining restatements with cross-references to §7.5 | `SFR-GOV-002`, `SFR-INTRO-M1`, `SFR-GOV-M1` | 0 |
| | **Stage 2 net** | | **−380** |

### Stage 3 — Supervisor point 2: business problem, users and design justification (net +450)

| # | Action | Findings | Words |
|---|---|---|---:|
| 3.1 | Declare in §1.1 what business evidence was and was not available, and its source class | `SFR-INTRO-001` | +60 |
| 3.2 | Add one illustrative end-to-end reporting case from the synthetic fixture, labelled as such | `SFR-INTRO-001` | +140 |
| 3.3 | Place `intro_f1_problem_to_research_contract.png` in Chapter 1 and reference it | `SFR-INTRO-001`, `SFR-XS-005` | +20 |
| 3.4 | Add the design-rationale passage: four named alternatives, separation of duties as the lead argument, costs stated | `SFR-XS-002` | +260 |
| 3.5 | Reduce §6.3 to interpreting that argument against the D0 result; reconcile the §2.7 and §6.2 concessions | `SFR-XS-002`, `SFR-DISC-M1` | −30 |
| | **Stage 3 net** | | **+450** |

### Stage 4 — Supervisor point 3 and register: flow and readability (net −110)

| # | Action | Findings | Words |
|---|---|---|---:|
| 4.1 | Rewrite Chapter 2 paragraph endings so they hand off; retain at most six prohibition endings | `SFR-LIT-002` | +80 |
| 4.2 | Move §2.2.1's sector-importance and product material to the front of Chapter 2 or to Chapter 1 | `SFR-LIT-002` | 0 |
| 4.3 | Compress §2.1 and §2.7 to about 380 words combined | `SFR-LIT-002` | −280 |
| 4.4 | Remove requirement identifiers as sentence subjects; open each Chapter 4 section with a plain purpose sentence | `SFR-SYS-001` | +150 |
| 4.5 | Compress Chapter 4's longest field enumerations into purpose sentences plus appendix pointers | `SFR-SYS-001` | −250 |
| 4.6 | Extend the glossary to every used acronym and term; remove `HITL`, `OOS` and standalone `RQ` | `SFR-SYS-001`, `SFR-XS-M2` | 0 |
| 4.7 | Rewrite the Abstract: counts before metrics, metrics glossed, RQs named, stack demoted | `SFR-ABS-001`, `SFR-ABS-M1`, `SFR-ABS-M2` | +6 |
| 4.8 | Apply the plain-language condition naming in reader-facing prose | `SFR-XS-O1` | +10 |
| 4.9 | Restore the export-format defence and the contradiction-burden interpretation in compressed form | `SFR-DISC-003` | +140 |
| 4.10 | Remove Chapter 8's duplication of Chapter 6; add its two principal limitations | `SFR-CONC-001` | +34 |
| | **Stage 4 net** | | **−110** |

### Stage 5 — Supervisor point 5: exhibits and worked examples (net +170)

| # | Action | Findings | Words |
|---|---|---|---:|
| 5.1 | Record the body-versus-appendix placement rule and the requirement that every table, figure and graph caption appears below its content in `REPORT_STRUCTURE.md` | `SFR-XS-006`; user layout requirement | 0 |
| 5.2 | Move `lit_t2` and `lit_t3` to an appendix; remove their `\clearpage` pairs; decide `lit_t4` on the same test | `SFR-XS-006`, `LIT-COMP-006`, `LAYOUT-001` | 0 |
| 5.3 | Replace each double reference to the six exiled tables with one appendix-form reference | `SFR-XS-006` | −40 |
| 5.4 | Reference `eval_t4a` and the Appendix F ledger; narrate one accepted and one rejected claim end to end in §5.4 | `SFR-RES-005` | +140 |
| 5.5 | Carry one worked example into §6.1 | `SFR-RES-005` | +50 |
| 5.6 | Resolve or retire `lit_t1`; reference or remove the remaining unreferenced exhibits and figures | `SFR-XS-005` | +20 |
| 5.7 | Correct the `eval_t1` manifest schema name and the `REPORT_STRUCTURE.md` appendix map | `SFR-RES-M1`, `SFR-XS-M3` | 0 |
| 5.8 | Audit every table, figure and graph, beginning with Table 1.2; move each caption and its description below the content, keep the label attached to the caption, and verify the result in the rendered PDF | user layout requirement | 0 |
| | **Stage 5 net** | | **+170** |

### Stage 6 — Supervisor point 6 and RQ traceability (net +450)

| # | Action | Findings | Words |
|---|---|---|---:|
| 6.1 | Add the pilot's company count, period count, calendar window and minimum completed-report count as parameters to freeze | `SFR-DISC-001` | +90 |
| 6.2 | Add time to the pre-registered acceptance-criteria list | `SFR-DISC-001` | +20 |
| 6.3 | Consolidate "testing still required" at the end of §6.7; point §5.6, §5.7, §7.5 and §8.3 at it | `SFR-DISC-001` | +70 |
| 6.4 | Add the RQ frame to Chapter 5 and one RQ clause each to §5.2, §5.4 and §5.8 | `SFR-RES-001` | +90 |
| 6.5 | Move `disc_t1` into the body and reference it | `SFR-RES-001`, `SFR-XS-005` | +10 |
| 6.6 | State the condition-label and metric-name mapping to the saved output | `SFR-RES-003` | +50 |
| 6.7 | Cite `ribeiro2020checklist` in §3.3; state the single-case-per-category decision | `SFR-METH-001` | +120 |
| | **Stage 6 net** | | **+450** |

### Stage 7 — Literature depth (net +550)

| # | Action | Findings | Words |
|---|---|---|---:|
| 7.1 | Introduce `ribeiro2020checklist` as the behavioural-testing paradigm in Chapter 2 | `SFR-LIT-001` | +90 |
| 7.2 | Introduce `sculley2015debt` for the maintenance-cost trade-off | `SFR-LIT-001`, `SFR-XS-002` | +90 |
| 7.3 | Introduce `souppaya2022ssdf` where secure-development practice is claimed | `SFR-LIT-001` | +60 |
| 7.4 | Bring `hevner2004design`, `cddo2023genai` and `autio2024genai` into Chapter 2 | `SFR-LIT-001` | +130 |
| 7.5 | Create three explicit points of tension between existing sources and adjudicate them | `SFR-LIT-001` | +180 |
| 7.6 | Declare any thematic gap not closed as a review boundary; reduce reliance on the two procedural warrants | `SFR-LIT-001` | 0 |
| 7.7 | Add bibliography, `REFERENCE_AUDIT.md` and `CLAIM_LEDGER.md` rows for the three newly cited keys | `SFR-XS-004` | 0 |
| | **Stage 7 net** | | **+550** |

### Stage 8 — Submission integrity, AI disclosure and pro-forma (main-body words +0)

| # | Action | Findings | Main-body words |
|---|---|---|---:|
| 8.1 | Add a candidate-approved acknowledgement in the student declaration naming every actual GAIT and limiting the description to the five confirmed use categories | `AI-DISC-001`, `AI-PERM-001` | 0 |
| 8.2 | Complete Appendix I with the actual prompt inventory and, for each material use, the purpose, output used, candidate modification or rejection, verification performed and affected section or technical artefact | `AI-DISC-001`, `AI-PERM-001` | 0 |
| 8.3 | Verify the Abstract, contribution declaration, contents, figure/table list, glossary, objectives and references, then change their seven pro-forma markers from empty to ticked | `AI-DISC-001` | 0 |
| 8.4 | Leave the ethics-approval/waiver marker unticked and the ethics reference blank; after the candidate supplies the evidence, insert it in Appendix B, populate the reference and tick the final box | `AI-DISC-001` | 0 |
| 8.5 | Populate the remaining candidate metadata and verify that Appendix A contains the required ethics-training evidence | `AI-DISC-001` | 0 |
| | **Stage 8 main-body net** | | **0** |

### Word budget by chapter

The Stage 2 disclaimer reduction (−500) is distributed across chapters in proportion to current
disclaimer density: Chapter 1 −60, Chapter 2 −180, Chapter 4 −130, Chapter 5 −60, Chapter 6 −50,
Chapter 8 −20.

| Part | Measured now | Target | Delta | Main driver |
|---|---:|---:|---:|---|
| Abstract | 374 | 380 | +6 | Rewrite for register and RQs |
| 1. Introduction | 1,387 | 1,850 | +463 | Business problem, worked case, design justification; −60 disclaimers |
| 2. Literature Review | 3,293 | 3,355 | +62 | +550 depth, +80 flow, −280 bookends, −110 Grok Bot, −180 disclaimers |
| 3. Methodology | 1,128 | 1,248 | +120 | D0 methodological warrant |
| 4. System Design | 2,941 | 2,746 | −195 | +185 plain language, −250 enumeration compression, −130 disclaimers |
| 5. Evaluation and Results | 1,724 | 1,834 | +110 | +290 RQ frame and worked examples, −120 empty sections and table refs, −60 disclaimers |
| 6. Discussion | 1,622 | 1,782 | +160 | +230 pilot, +190 restored defences and worked example, −160 Grok Bot and §6.3 trim, −50 disclaimers |
| 7. Ethics, Governance and Limitations | 759 | 939 | +180 | Consolidated boundary statement; corrected §7.2 |
| 8. Conclusion | 646 | 610 | −36 | +34 limitations and rebalance, −50 Grok Bot, −20 disclaimers |
| **Main body subtotal: Chapters 1--8** | **13,500** | **14,364** | **+864** | Inside the confirmed 13,500--16,500 range; excludes Abstract, tables, figures, references and appendices |
| **Review counter total, shown only for reconciliation** | **13,874** | **14,744** | **+870** | Includes the Abstract; not the governing main-body total |

Note that Chapter 2 grows by only 62 words net while gaining roughly 630 words of genuine literature
content, because the framing bookends and the hedging are what pay for it. That is the intended outcome:
the supervisor asked for a deeper literature review and a more readable one, and both are achieved by
substitution rather than by expansion.

### Re-review scope

On return, submit the revised Abstract and Chapters 1--8 with a finding-by-finding change log. The
re-review will verify, in this order: `SFR-GOV-001` against `var/experiments/`; `AI-DISC-001` against
the declaration, Appendix I and the seven-ticked/one-pending pro-forma state; `SFR-XS-002` against
Chapter 1; `SFR-XS-001` against the overclaim ledger, `metadata.tex` and any separately authorised
implementation evidence; then the disclaimer count, the Chapter 2 paragraph endings, the exhibit
reference audit, below-content caption placement on every table, figure and graph, the Chapter 5 RQ frame
and the regenerated Chapters 1--8 main-body word count. Ethics approval remains an explicit submission
hold until Appendix B evidence is supplied. Do not change an acceptance condition between rounds without
recording the reason.

---

## 13. Reviewer statement

This review made no change to any dissertation file. It introduced no new claim, source, number or
result. Where evidence could not be traced, the finding says so explicitly rather than assuming the
claim true or false. Two claims fall in that category. The cited three-repeat D0 output checksum resolves
to no file in the repository, although the values it is cited for are independently verified from
`var/evaluation/smoke.json`. And the validation suite could not be re-executed in this environment, so
`SFR-RES-006` asserts only the documentary conflict between two recorded figures, not which figure is
correct.

Two claims were investigated and **not** raised as findings, because the evidence did not support them.
A report that the five external-model run manifests were absent proved to be an artefact of searching
only git-tracked files: `var/` is gitignored, and all five manifests are present on disk, which is what
`SFR-GOV-001` rests on. A report that Chapter 4 still described a retired FastAPI/Jinja presentation
path proved already remediated in the chapters, with the only surviving references in superseded review
reports and one exhibit JSON that explicitly labels the asset historical.

Forty-four prior finding identifiers were reconciled; 35 are verified closed. Four are preserved
unresolved with their original identifiers and acceptance conditions (`AI-DISC-001`, `AI-PERM-001`,
`LIT-COMP-006`, `LAYOUT-001`, the last two being one physical issue under two identifiers). One
(`ABSTRACT-002`) remains partially resolved. Two (`DISC-SUP-003`, `DISC-SUP-005`) are recorded as
regressions caused by the 31 August revision. One (`CH2-REG-001`) is re-opened on new evidence under
re-review rule 7, with the reason recorded. One (`CH2-R3-001`) is retained under its original identifier
despite an ambiguous prior status rather than being reissued. No identifier was renumbered, and no new
identifier reuses a prior prefix. Four prior `PASS` gates are treated as void because they reviewed a
draft with three sub-questions and 15,824 words; that judgement is recorded as `SFR-XS-007` rather than
applied silently. The whole-report gate actually in force before this review was `HOLD` /
`EVIDENCE_REQUIRED`, not any of those `PASS` gates.

This gate does not estimate a mark or classification, and it does not certify legal compliance, ethical
approval, accessibility conformance, field accuracy, human benefit or production readiness.
