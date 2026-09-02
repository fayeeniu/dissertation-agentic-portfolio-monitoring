# Dissertation structure and evidence map

Status: **seven-chapter rebuild to the supervisor-agreed 7ch outline, 2 September 2026; final review pending**. The active research contract now matches
the implementation and D0 observations. Manual, participant, live-web and managed-platform
comparisons are prospective work rather than active research questions.

## Working count

The reproducible command `python3 scripts/word_count.py --check` applies the candidate-confirmed
convention to Chapters 1--7 prose. It excludes the Abstract and other front matter, table bodies and
captions, figure content and captions, references and appendices. The current main-body total is
**13,603 words**, within the required **13,500--16,500** range around the 15,000-word target.
`metadata.tex` states the 15,000-word target. Authenticated WMG instructions take precedence if they
later define any exclusion differently.

## Exhibit placement rule

A table stays in a body chapter only if the prose argues from it at that point and it fits within
roughly half a page. Everything else goes to an appendix and is referred to exactly once, in appendix
form (`Table~\ref{...}, in Appendix~\ref{...}, ...`). No table is referred to both as present in the
body and as provided in an appendix. Under this rule `lit_t2` and `lit_t3`, which no prose referenced,
moved to Appendix H; `lit_t4` and Figures 2.1--2.2 sit in the appendices; `lit_t5` and
`lit_t6` stay in Chapter 2 because its argument uses them. Every
table, figure and graph caption is placed below its content.

## Figure and caption disclaimer rule

Each epistemic scope statement appears exactly once across the whole figure set, at the figure where
it actually operates, and Section~\ref{sec:limitations} in Chapter 6 carries the full statement of the study's limits. Failure-state
labels inside a diagram (`Blocked: held`, `EXPORT FAILED`, `Any failure: unresolved`) are part of the
gating logic and are retained. Captions state what the figure shows and where it came from, and do not
repeat the limitations.

## Active research contract

### Primary research question

> How can an evidence-first, role-separated workflow produce traceable early-stage portfolio
> reporting claims, and what effect does a separate verification stage have on claim admission in
> controlled cases?

### Sub-questions

1. **RQ1, evidence preservation:** How does the implemented workflow preserve company identity,
   reporting time, missing states, source provenance and approval boundaries from input to report?
2. **RQ2, separate verification:** What effect does a separately recorded verification stage have on
   supported-claim precision, unsupported claims, conflict handling, source-record completeness and
   repeatability in D0?

Both questions are answered by current evidence. RQ1 uses repository artefacts, engineering checks
and labelled D0 behaviour. RQ2 uses the paired C1/C2 D0 comparison across three repeats. The result
does not establish multi-agent superiority, real-company accuracy or business benefit.

## Prospective evaluation boundary

The original manual C0 and named-review C3 conditions are retained as protocol history and as inputs
to the business pilot. Live-source and managed-platform comparisons are also future studies. They
require separate authority, equivalent inputs, frozen source windows, independent reference
decisions and recorded human, cost and operational observations.

## Word and evidence map

| Part | Current words | Main purpose | Main evidence | Body exhibits |
|---|---:|---|---|---|
| Abstract (excluded) | 400 | Stand-alone problem, method, D0 result, contribution and main limit | Current implementation and D0 output | None |
| 1. Introduction | 1,430 | Business problem, why it matters, active questions and one-paragraph scope | Project charter and admitted literature | Business-process table; research contract |
| 2. Literature Review | 3,381 | 7ch seven-section argument; search method; architecture argument in §2.6 | Admitted papers and immutable primary captures | Competitor and settled/gap tables; figures in appendix |
| 3. Research Design and Methodology | 2,297 | C1/C2 method, evidence-scope table, D0 fixture, sequencing of unrun work, ethics | Evaluation fixture, protocol and methods literature | Design-science evidence chain; evidence-scope table |
| 4. The artefact: the life of a claim | 1,740 | Eight stages of one claim; two end-to-end examples | Requirements, ADRs, code, migrations and tests | Architecture and verification-state figures |
| 5. Evaluation and Results | 1,687 | Engineering record, D0 results answering RQ1/RQ2, honesty on C2 vs published detectors | Frozen run outputs and D0 fixture | Results tables; no metric-profile figure |
| 6. Discussion | 2,238 | Answer RQ1/RQ2; operator screens; six-part pilot; only limitations section | Chapter 5 results and admitted literature | Transfer and literature-alignment tables |
| 7. Conclusion | 830 | Bounded contribution, sequenced next evidence and closing statement | RQ findings and pilot plan | None |
| **Main-body total** | **13,603** |  |  |  |

## Narrative spine

1. Business process and users.
2. Evidence risks.
3. Design criteria and architecture alternatives.
4. Implemented role-separated workflow.
5. Executed engineering and D0 evaluation.
6. Results and interpretation.
7. Prospective business pilot and future comparison.

## Appendix map

- **Appendix A:** evidence of required ethics training.
- **Appendix B:** ethics approval or waiver confirmation.
- **Appendix C:** requirements, trust boundaries, connectors, failure-state traceability and moved pipeline figures.
- **Appendix D:** condition and reference-parity matrices.
- **Appendix E:** source admission, ethics, leakage, repeatability and provider data controls.
- **Appendix F:** metric denominators, complete D0 case ledger, adversarial results
  and held comparison records.
- **Appendix G:** implementation snapshot and engineering-validation ledger.
- **Appendix H:** remaining literature and residual-risk tables (transfer and alignment tables now sit in Chapter 6).
- **Appendix I:** literature search, PRISMA-style flow and screened-out table.
- **Appendix J:** generative-AI use disclosure.

## Claim-control rule

Every substantive paragraph must have a matching claim-ledger row with the exact citation set and
verified local page evidence. Plans, tests, synthetic fixtures and code must not be presented as
live-source, human-study, production or investment-performance findings.
