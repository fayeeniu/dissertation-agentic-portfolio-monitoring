# Dissertation structure and evidence map

Status: **revised full-report candidate, 1 September 2026; final review pending**. The active research contract now matches
the implementation and D0 observations. Manual, participant, live-web and managed-platform
comparisons are prospective work rather than active research questions.

## Working count

The reproducible command `python3 scripts/word_count.py --check` applies the candidate-confirmed
convention to Chapters 1--8 prose. It excludes the Abstract and other front matter, table bodies and
captions, figure content and captions, references and appendices. The current main-body total is
**15,660 words**, within the required **13,500--16,500** range around the 15,000-word target.
`metadata.tex` states the 15,000-word target. Authenticated WMG instructions take precedence if they
later define any exclusion differently.

## Exhibit placement rule

A table stays in a body chapter only if the prose argues from it at that point and it fits within
roughly half a page. Everything else goes to an appendix and is referred to exactly once, in appendix
form (`Table~\ref{...}, in Appendix~\ref{...}, ...`). No table is referred to both as present in the
body and as provided in an appendix. Under this rule `lit_t2` and `lit_t3`, which no prose referenced,
moved to Appendix H; `lit_t4` and `lit_t5` stay in Chapter 2 because its argument uses them. Every
table, figure and graph caption is placed below its content.

## Figure and caption disclaimer rule

Each epistemic scope statement appears exactly once across the whole figure set, at the figure where
it actually operates, and Section 7.5 carries the full statement of the study's limits. Failure-state
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
| 1. Introduction | 2,168 | Business problem, evidence risks, active questions, design alternatives and scope | Project charter and admitted literature | Business-process table; research contract |
| 2. Literature Review | 3,501 | Critical synthesis of evidence risks, design criteria and architecture alternatives | Admitted papers and immutable primary captures | Evidence-boundary figures; concise alternatives table |
| 3. Research Design and Methodology | 1,174 | Executed C1/C2 method, D0 fixture and its behavioural-testing warrant | Evaluation fixture, protocol and methods literature | Design-science evidence boundary |
| 4. System Design and Implementation | 3,001 | Implemented role-separated architecture and controls | Requirements, ADRs, code, migrations and tests | Architecture and workflow figures |
| 5. Evaluation and Results | 2,090 | Engineering record, D0 results answering RQ1/RQ2, and narrated worked examples | Frozen run outputs and D0 fixture | D0 design, results, examples and metric figure |
| 6. Discussion | 1,843 | Answer RQ1/RQ2, interpret architecture, and define the pilot | Chapter 5 results and admitted literature | Body prose; supporting tables moved to appendices |
| 7. Ethics, Governance and Limitations | 1,274 | Authoritative ethics, external-model record, security and consolidated validity boundary | Governance records, run manifests and admitted guidance | Supporting risk matrix moved to appendix |
| 8. Conclusion and Future Work | 609 | Bounded contribution and sequenced next evidence | RQ findings and pilot plan | Roadmap moved to appendix |
| **Main-body total** | **15,660** |  |  |  |

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
- **Appendix C:** requirements, trust boundaries, connectors and failure-state traceability.
- **Appendix D:** condition and reference-parity matrices.
- **Appendix E:** source admission, ethics, leakage, repeatability and provider data controls.
- **Appendix F:** metric denominators, complete D0 case ledger, adversarial results
  and held comparison records.
- **Appendix G:** implementation snapshot and engineering-validation ledger.
- **Appendix H:** transfer, literature-alignment, residual-risk and future-evidence tables.
- **Appendix I:** generative-AI use disclosure.

## Claim-control rule

Every substantive paragraph must have a matching claim-ledger row with the exact citation set and
verified local page evidence. Plans, tests, synthetic fixtures and code must not be presented as
live-source, human-study, production or investment-performance findings.
