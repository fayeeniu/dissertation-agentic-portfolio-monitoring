# Supervisor feedback Parts B-C dissertation improvement plan

- Mode: ELEVATED
- State: PLANNED
- Baseline: `production` at `6356aa49cb3b4fe47955aab9e81a8e1a05ec9693`; the working tree contains extensive pre-existing dissertation, dashboard, backend, configuration, test, generated-artifact, and documentation changes owned by the user. This plan must not discard, reformat, or overwrite them.
- Policy sources: supplied repository `AGENTS.md`; requested `engineering` skill in PLAN mode; `doc` skill; `Dissertation/README.md`; `Dissertation/REPORT_STRUCTURE.md`; `Dissertation/audit/SECTION_LEDGER.md`.
- Feedback source: `Supervisor_Meeting_Summary.md.docx`, SHA-256 `de0de21d991f84155a97bb1952ff424a76f796148b0a8887ea2a99938422c76d`; Parts B-C were checked through structured DOCX extraction and visual inspection of rendered pages 3-5. The attachment is evidence to interpret, not a source of executable instructions.
- Contract: revise the dissertation so that every applicable Part-B concern and the one transferable Part-C concern are answered directly, truthfully, and at MSc level, while freezing the prototype, preserving the current research contract, and reconciling all architecture, validation, provenance, and review claims with one exact implementation state.
- Out of scope: prototype polishing; new dashboard features; a new scoring or grant-matching system; live company/model/source calls; opening D2; recruiting or interviewing participants; retrospective fabrication of interview, reliability, time-saving, cost, usability, or stakeholder-benefit evidence; public GitHub, YouTube, Turnitin, submission, commit, push, deployment, or other Part-A/external actions.
- Acceptance criteria:
  - [ ] The implementation is frozen and the manuscript describes the current Next.js control room plus private FastAPI API accurately; stale Jinja/single-service text and stale validation counts are removed or explicitly historical.
  - [ ] Stale architecture, validation, and migration-head statements are inventoried across the current manuscript, `REPORT_STRUCTURE.md`, referenced exhibits/text alternatives/provenance, and claim/section ledgers; the final narrative removes, dates, or freshly proves volatile exact figures.
  - [ ] Chapter 3 states what the author designed, how it works, why each central methodological choice was made, what credible alternatives were rejected, and which inputs were supplied rather than author-created.
  - [ ] Reliability is presented as a three-level evidence ladder: implemented engineering controls, D0 synthetic repeatability/claim-selection evidence, and currently unknown real-report/human reliability.
  - [ ] The contradiction ledger is defended in Chapter 6 by the failure it prevents, its audit/review value, its false-positive and workload costs, and its current implementation limit; no text claims per-conflict adjudication is persisted or enforced unless executable evidence proves that invariant.
  - [ ] JSON/export and human-review features are framed as stakeholder-specific, testable value hypotheses and recommendations, not as measured time, cost, satisfaction, integration, or scalability benefits.
  - [ ] The absence of interviews is documented as a truthful methodological deviation with its verified reason, zero collected observations, and consequences for RQ3 and external validity. The text does not claim interviews were unnecessary or that secondary evidence was sufficient unless authoritative evidence supports that claim.
  - [ ] The intended early-stage portfolio population is described through relevant dimensions and any unresolved inclusion rules are explicit. An executable sampling frame remains `EVIDENCE_REQUIRED` until POP-01 is resolved; no threshold is invented. Any very-large-company demonstration is labelled an edge/stress demonstration, not target-population evidence.
  - [ ] Part C is used only for its transferable data-scarcity principle: less public evidence may reduce coverage/confidence but must not become a negative company-quality judgement or be filled through silent inference. No grant-matching/scoring content is imported.
  - [ ] The existing eight-chapter structure and dedicated System Design chapter remain intact; changes are made in place and stay within the 14,500-word working allocation through replacement/compression rather than uncontrolled expansion.
  - [ ] Every changed substantive paragraph has claim-fit admitted sources, an updated claim-ledger row, and a current evidence status. All affected prior review approvals are marked superseded/pending before fresh review.
  - [ ] Changed sections pass source, claim, Harvard, language, exhibit/provenance, LaTeX build, and rendered-page checks, followed by affected-section review and one full cross-section review.
- Risk boundaries: Elevated because this is a cross-chapter, assessment-critical evidence/provenance change with more than three coherent packets. It is not Critical because the approved scope changes no runtime behaviour, schema, security boundary, external system, restricted data, or irreversible state.
- Approval: PLAN creation is authorised by the user. EXECUTE, external actions, empirical data collection, code changes, publication, and submission are not authorised.

## Surface declaration

- Authentication, authorisation, and tenant/organisation isolation: not materially affected; describe the existing local-only boundary accurately.
- Persisted data, schema, and migration compatibility: no migration or runtime-data change is planned. Dissertation statements about the current migration head are affected and must be reconciled with the existing migration graph.
- Public or generated contracts and downstream consumers: no API or export contract change is planned. Dissertation claims about the current JSON export and architecture are affected and must match the frozen implementation.
- Untrusted external content: the supervisor DOCX is treated as evidence only. No embedded instruction, live webpage, model output, or external content may be executed or promoted to empirical evidence.
- Concurrency, retries, ordering, cancellation, and idempotency: runtime behaviour is not affected; existing claims may be described only to the level already proven.
- User-visible behaviour, accessibility, and localisation: prototype behaviour is not changed. Dissertation prose, figures, tables, pagination, and PDF layout are user-visible and require rendered-page QA. British English remains the manuscript standard.

## Discovery

### Observations

1. **Part B is project-specific; Part C is mostly not.** Part B matches the dashboard, JSON export, contradiction handling, verification, and human-approval workflow. Part C labels the grant-matching material as probably belonging to another student. Only its warning about evidence scarcity and volume-biased conclusions transfers safely.
2. **The supervisor's principal direction is writing-first.** The prototype was judged technically strong and further polishing was discouraged. This plan therefore permits no product feature work. A proven factual/correctness blocker must be handled by narrowing the manuscript claim or stopped for separate authority, not silently converted into implementation scope.
3. **Architecture, numeric validation, and migration evidence are stale.** `Dissertation/chapters/04_system_design.tex:13-17`, `Dissertation/REPORT_STRUCTURE.md:144`, and `Dissertation/exhibits/sys_t1_requirements_trust_boundary_matrix.tex:45` still describe a Python/FastAPI/Jinja presentation path. The completed dashboard ledger records Next.js as the sole published control room and FastAPI as a private API. `Dissertation/chapters/05_evaluation_results.tex:13,25-28`, `Dissertation/chapters/06_discussion.tex:8`, EVAL-T2, the section ledger, and the full-report review still cite 286 tests, 85.58% coverage, and 46 typed files; `.agents/runs/nextjs-dashboard-docker-default.md:70-75` later records 266 tests, 85.55% coverage, and 45 typed files. The manuscript also names migration `0009`, while the working tree contains `alembic/versions/0010_hybrid_evidence_scope.py`. None of these values may be copied blindly into the final manuscript without current-contract reconciliation.
4. **Method ownership is present but implicit.** Chapter 3 justifies design science and names the student as builder/evaluator, but it does not clearly distinguish supplied criteria from the author-developed matching, evidence-admission, verification, condition, denominator, and stop-rule method or compare those choices with credible alternatives.
5. **The contradiction rationale is distributed rather than defended.** Chapters 2, 4, and 6 explain conflict preservation, no averaging, and named review. Chapter 6 does not explicitly defend the named contradiction-ledger feature in examiner-facing terms. Current company-profile approval records one overall reviewer and reason; it does not persist or block on a separate disposition for every contradiction candidate. The dissertation must not imply otherwise.
6. **Business value is mostly a missing hypothesis, not a missing result.** The manuscript accurately says time, cost, usability, and human benefit are unmeasured. It describes JSON/Markdown/HTML export mechanics but does not explain a portfolio operator's intended downstream use, reduced re-entry hypothesis, auditability value, or integration conditions.
7. **Reliability is conceptually strong but hard to read as a direct answer.** Chapter 3 defines precision, recall, unsupported-claim rate, report completeness, factual-error severity, repeated-run consistency, schema validity, failures, and human measures. Chapter 5 and Chapter 6 preserve important evidence limits. The improvement is a direct evidence ladder and exact-state reconciliation, not invented validation.
8. **Interview omission is not explained.** The repository records C0/C3 and participant evidence as held or absent, but no actual ethics approval, consent form, participant information, or interview record is present. The dissertation does not state the verified reason the planned one-to-one interviews were not undertaken or identify this as a protocol deviation.
9. **The early-stage target is named but not operationalised.** The aim and charter say early-stage portfolio reporting, but the D1/D2 protocol has no domain-approved stage, age, headcount/turnover, sector, legal-form, filing-regime, or source-availability inclusion criteria. No numerical threshold may be invented from the supervisor summary.
10. **Fail-closed data-scarcity behaviour is already implemented.** Missing states, no-record/source-unavailable distinctions, abstention, exact spans, and exclusion of unsupported/conflicted claims already exist. The missing dissertation point is that evidence volume and company quality are different constructs, and coverage denominators must expose scarcity.
11. **Current review state is internally inconsistent.** Section 1.3 is currently approved; Sections 1.4 and 2.1 remain pending, while the older full-report review still says PASS. This plan avoids editing Sections 1.3, 1.4, and 2.1 unless cross-section reconciliation proves a necessary conflict, and requires a fresh full-report decision after the planned changes.

### Feedback-to-change map

| ID | Supervisor concern | Current state | Planned disposition | Primary surfaces |
|---|---|---|---|---|
| B0 | Stop polishing the prototype | Direction aligns with project policy; current dissertation is stale after the completed UI migration | Freeze implementation; writing and evidence reconciliation only | task ledger; exact-state evidence |
| B1 | Own and defend the methodology | Partial | Add author/supplied provenance and a what-how-why-alternative rationale for core choices | Chapter 3, claim ledger |
| B2 | Explain why the contradiction ledger exists | Partial | Add explicit defence, failure prevented, costs, measurement, and current per-conflict limitation | Chapters 4 and 6 |
| B3 | Frame value for stakeholders, not as a sales pitch | Mostly missing | Add conditional portfolio-operator recommendations and measurable value hypotheses; no benefit claims | Chapters 6 and 8 if needed |
| B4 | Answer whether report generation is reliable and how it is validated | Strong method, stale evidence | Reconcile exact run evidence and present the engineering/D0/real-world evidence ladder | Chapters 3, 5, and 6; EVAL-T1/T2/T4 |
| B5 | Explain why interviews were not completed | Missing | Verify the actual ethics/feasibility history, record the deviation and consequence, keep RQ3 unanswered | Chapters 3, 5, 6, and 7; ethics appendix status |
| B6 | Keep System Design; make Discussion defend choices | Structure covered | Preserve chapter structure; revise content in place | Chapters 4 and 6 |
| B7 | Evaluate the intended smaller/early-stage companies | Partial | Define target-population criteria or explicit unresolved fields; treat large-company demo as non-representative | evaluation protocol; Chapters 3, 5, 6, and 7 |
| B8 | Submit early | Operational constraint, not manuscript evidence | Complete freeze, review, build, and handoff before any separately authorised submission; no submit action in this task | execution schedule only |
| C1 | Do not reward data-rich firms or infer through scarcity | Applicable principle only | Separate coverage from quality, expose scarcity denominators, preserve abstention; add no score or grant-matching logic | Chapters 3 and 6; evaluation protocol |

### Inferences

- The smallest defensible response is a manuscript-and-evidence revision, not new product behaviour.
- The supervisor's suggested business outcomes should be written as intended-use hypotheses and future measures because the repository contains no downstream JSON consumer, time-saving experiment, stakeholder-satisfaction result, or authorised human study.
- Claim downgrading is preferable to last-minute feature work where the implementation is weaker than current prose. In particular, the contradiction ledger surfaces candidates but does not enforce a persisted decision for each candidate.
- The existing chapter sequence is suitable. A new chapter, RQ4, company score, or competitor/grant-matching feature would broaden scope without answering Part B.
- Because section word allocations are already tight, each packet should replace weaker descriptive text with decision rationale rather than append prose.

### Unknowns and decision gates

1. **INT-01 - interview/ethics history:** inspect the actual submitted ethics application and any approval/waiver correspondence, or obtain the candidate's factual confirmation. Required facts are what was approved, whether recruitment began, why interviews were not undertaken, and whether any data were collected. If unavailable, state only that authority and execution were not verified; do not invent scheduling or sufficiency claims.
2. **POP-01 - target population:** obtain a domain-approved description of the intended early-stage/venture-builder portfolio population. If numerical stage/size thresholds are unavailable, record the dimensions and the absence of approved thresholds rather than inventing them.
3. **STATE-01 - implementation candidate:** determine whether the completed Next.js ledger's frozen candidate still matches the current backend, dashboard, tests, configuration, and Compose files. Prefer static inspection and removing or dating volatile counts. If an exact current count materially supports the dissertation and is intentionally retained, run one explicitly no-fix pre-edit baseline; do not turn this writing task into a product-validation loop.
4. **MIG-01 - migration identity:** inspect the current migration graph and every active manuscript/exhibit claim. Remove volatile ordinal wording by default; if an exact head is retained, prove it against a disposable database without changing project data.
5. **COUNT-01 - word-count rule:** preserve the current 14,500-word working allocation unless authenticated WMG rules prove a different convention.

### Affected callers and boundaries

- Primary manuscript: `Dissertation/chapters/03_methodology.tex`, `04_system_design.tex`, `05_evaluation_results.tex`, `06_discussion.tex`, `07_governance_limitations.tex`; inspect `08_conclusion.tex` and change only if cross-section alignment requires it.
- Protocol and structure: `docs/EVALUATION_PROTOCOL.md`, `Dissertation/REPORT_STRUCTURE.md`.
- Affected exhibits only: architecture/evidence snapshot/engineering validation, including `Dissertation/exhibits/sys_t1_requirements_trust_boundary_matrix.tex`, and any methodology/discussion table whose semantics change, together with `.mmd`, `.png`, `.tex`, `.txt`, manifest, and provenance files as applicable.
- Evidence and governance: `Dissertation/sources/CLAIM_LEDGER.md`, `Dissertation/audit/SECTION_LEDGER.md`, `Dissertation/reviews/REVIEW_LOG.md`, affected section-review files, chapter cross-section review, and full-report cross-section review.
- Current runtime contracts are read-only evidence. `src/`, `tests/`, `dashboard/`, migrations, Compose, and dependency files are not change surfaces for this plan.

### Baseline fingerprints

| Surface | SHA-256 at planning time |
|---|---|
| `03_methodology.tex` | `fc161498bf0476c97134ee723a07a10a3e8fb0fe96c5775c9854409c61165a88` |
| `04_system_design.tex` | `aa4f3b48f5fd29514c6be523fcb16f1b1d40f2542aa0f4d2ed792b3698e5df1d` |
| `05_evaluation_results.tex` | `9399a2665ea3553707f4856dad304d7a90082367645eb436a388759901e41a12` |
| `06_discussion.tex` | `540dfef9e3248c14661dcfe0d5fd76aef0511712fac81b10e955ae0fd2750f8f` |
| `07_governance_limitations.tex` | `6c1772d28b43976781e18a9695ca25810e9b2c54d04a1ec6d3be087d7658faea` |
| `08_conclusion.tex` | `628da606e7c8f627743a30539c5376a7456e32fd2d645c925eff7b803b39fec8` |
| `REPORT_STRUCTURE.md` | `19dc04c2c27b72b6c8c9d502f83fa4ab51fca4e83bc3a9a3633d4f03d6467574` |
| `SECTION_LEDGER.md` | `6b4d9230bd7dda639db6ec350aff5680a67c44b85c094e20d80a79e21fe446fe` |
| `CLAIM_LEDGER.md` | `a9943a4c6b7f8c1339ff5b26d68d9bb690dad8171c26a3f4d3c4b966111f2da3` |
| `REVIEW_LOG.md` | `d56709b5ef2de402f669aef58f06a6830c34e8d565cd1b0a3547e95df500f044` |

Any drift in a planned surface requires re-reading the changed content and updating this contract before EXECUTE. Do not restore these hashes or discard newer work.

## Packets

1. **Freeze the artefact and resolve factual prerequisites.**
   - Writer: primary agent; one writer only.
   - Objective: establish one implementation identity and resolve INT-01, POP-01, and STATE-01 before prose asserts facts.
   - Files or symbols: read-only Git/worktree state; `.agents/runs/nextjs-dashboard-docker-default.md`; actual ethics/waiver material if supplied; current project charter and evaluation protocol.
   - Method:
     1. inventory current in-scope and implementation drift without resetting or cleaning;
     2. compare the current implementation surface with the completed Next.js candidate;
     3. prefer static implementation/contract inspection and remove or date volatile numeric claims; only if exact figures are intentionally retained, run one explicitly no-fix pre-edit baseline and record its candidate identity;
     4. record the verified interview/ethics facts and target-population definition without copying private participant data into the repository.
   - Proof: exact hashes/status plus authoritative ethics evidence or explicit `EVIDENCE_REQUIRED`; domain-approved population description or explicit unresolved dimensions.
   - Stop condition: any request to collect data, contact participants, open D2, change code, or infer missing ethics/population facts.
   - Status: PENDING.

2. **Reconcile architecture and engineering evidence before interpretive rewriting.**
   - Writer: primary agent.
   - Objective: make Chapters 4-6 and all active supporting surfaces describe the frozen Next.js/private-API architecture and validation state without relying on unnecessary volatile counts.
   - Files or symbols: `04_system_design.tex` Section 4.2 and architecture figure/source/provenance; `05_evaluation_results.tex` Sections 5.1-5.2; `06_discussion.tex` Section 6.1; `REPORT_STRUCTURE.md`; `sys_t1_requirements_trust_boundary_matrix.tex`; EVAL-T1/EVAL-T2; migration statements; related text alternatives, provenance, claim/audit rows.
   - Method:
     1. inventory stale `Jinja`, `286`, `85.58`, `46 source files`, and `0009` statements across the current manuscript, `REPORT_STRUCTURE.md`, referenced exhibits/text alternatives/provenance, and claim/section ledgers;
     2. align the architecture wording with static inspection of the current dashboard, private API, Compose, and contract documentation;
     3. remove volatile validation counts or date them as historical by default; only when an exact current value materially supports the argument, decide to retain it before prose editing and run one no-fix pre-edit baseline;
     4. remove the exact migration ordinal or reconcile it with the current graph; if an exact head remains, run `alembic heads` and `alembic upgrade head`, `alembic current`, and `alembic check` against a fresh, validated SQLite URL under `/private/tmp`;
     5. refresh every changed architecture/exhibit text alternative and provenance record.
   - Proof: targeted stale-contract search; static architecture comparison against Compose/current docs; optional exact baseline only where explicitly retained; migration proof when an exact head is retained; affected exhibit hashes and text alternatives agree.
   - Stop condition: an engineering gate fails or architecture differs materially from both the current manuscript and completed ledger. Record the gap; do not fix product code under this plan.
   - Status: PENDING.

3. **Make the methodology visibly author-owned and examiner-defensible.**
   - Writer: primary agent.
   - Objective: restructure Chapter 3 around concise what-how-why-alternative reasoning while preserving the frozen research questions and evidence boundaries.
   - Files or symbols: `03_methodology.tex` Sections 3.1, 3.2, 3.3, 3.5, and 3.7; `docs/EVALUATION_PROTOCOL.md`; affected methodology exhibit/text/provenance only if semantics change; claim/audit rows.
   - Required decisions to explain:
     - design science rather than a build demonstration, purely statistical study, or systematic literature review;
     - fixed C0-C3 conditions and a separate verifier rather than an unconstrained multi-agent conversation;
     - explicit denominators and abstention rather than a composite score or silent exclusion;
     - source/period parity and independent references rather than treating the manual report, supervisor, or system as ground truth;
     - early-stage target-population and scarcity strata rather than an unbounded large-company sample;
     - the interview deviation, its verified reason, and why no ad-hoc late substitute was used.
   - Proof: reviewer can identify author-created method, supplied inputs, alternative considered, rationale, evidence status, and limitation for each central choice; no RQ or evidence-tier drift; word allocation remains controlled.
   - Stop condition: INT-01 or POP-01 remains unresolved and proposed wording would assert a fact rather than disclose the gap.
   - Status: PENDING.

4. **Turn reliability into a direct, bounded answer.**
   - Writer: primary agent.
   - Objective: make the response to “is this a reliable way to generate the real report?” impossible to misread.
   - Files or symbols: Chapter 3 Section 3.5; Chapter 5 Sections 5.2, 5.4, 5.7, and 5.8 as needed; Chapter 6 Sections 6.1-6.3; EVAL-T2/EVAL-T4/EVAL-T7 only if their displayed status changes.
   - Required ladder:
     1. **Engineering mechanism:** schema, approval/export, failure, and repeatability controls tested on the frozen local implementation.
     2. **Synthetic D0 evidence:** claim-selection and represented contradiction/abstention cases only; deterministic equality is not real-world reliability.
     3. **Unavailable evidence:** real-report completeness/factual error, new-document extraction, discoverable-source miss rate, human correction, time, usability, and normal-operation failure remain unmeasured.
   - Proof: every metric has a unit, denominator, observed/protocol-only/null status, and claim boundary; no passing test is described as external validity.
   - Stop condition: a desired headline requires an unrun condition, unavailable label, or invented value.
   - Status: PENDING.

5. **Rewrite the Discussion as the written defence and consultant-style interpretation.**
   - Writer: primary agent.
   - Objective: answer B2-B3 directly without a sales pitch or unmeasured benefit claim.
   - Files or symbols: `04_system_design.tex` contradiction/review wording where needed; `06_discussion.tex` Sections 6.2, 6.3, 6.5, and 6.6; inspect `08_conclusion.tex` Sections 8.2-8.3 for consistency.
   - Required contradiction-ledger defence:
     - purpose: prevent a later source, majority, fluent narrative, or reviewer memory from silently erasing supported disagreement;
     - mechanism: retain claims, sources, periods, and contradiction status for review;
     - benefit hypothesis: traceability and explicit release accountability;
     - costs: abstention/recall loss, false-positive paraphrase grouping, reviewer workload, and no persisted per-conflict adjudication in the current profile approval;
     - evaluation: gold conflict cases, false-positive/false-negative detection, time/edit burden, and resolution quality in an authorised study.
   - Required stakeholder framing:
     - portfolio operator/investment team, not a named bank unless the intended user is verified;
     - approved structured JSON could reduce re-keying and support consistent downstream transfer, but no consumer contract or measured benefit exists;
     - recommendation: use the artefact for evidence preparation and controlled review, not ranking, investment advice, or autonomous publication;
     - adoption conditions: versioned schema/consumer test, target-population evaluation, human authority, accessibility, security, and observed time/error evidence.
   - Proof: each recommendation states audience, action, rationale, evidence, limitation, and next measurement; candidate reviewer finds no promotional or causal overclaim.
   - Stop condition: wording implies HSBC adoption, integration success, time/cost savings, stakeholder satisfaction, scalability, or per-conflict resolution as observed facts.
   - Status: PENDING.

6. **Integrate the target-population and Part-C scarcity boundary without adding a score.**
   - Writer: primary agent.
   - Objective: align methodology, future evaluation, discussion, and limitations with the early-stage/data-scarce use case while separating a truthful target profile from an as-yet unapproved executable sampling frame.
   - Files or symbols: `docs/EVALUATION_PROTOCOL.md`; Chapter 3 sampling/analysis; Chapter 5 held-comparison labels; Chapter 6 generalisability; Chapter 7 limitations; related tables only if semantics change.
   - Method:
     - define or explicitly leave approval-pending the population dimensions: stage, age, headcount/turnover, sector, legal form, filing regime, and expected source availability;
     - pre-specify coverage/scarcity strata and separate correct abstention from missed discoverable evidence;
     - report eligible, found, inaccessible, blocked, not-reported, internal-only, supported, and failed denominators;
     - state that limited public evidence lowers coverage/confidence, not company quality or investment merit;
     - label very-large-company runs as edge/stress demonstrations only.
   - Proof: the current write-up names the intended population dimensions and unresolved inclusion rules without claiming an executable frame; the frame remains `EVIDENCE_REQUIRED` until POP-01 is resolved. No metric rewards source volume as company quality; no silent inference, score, or grant-matching logic is introduced; Part C is clearly identified as a transferable caution rather than project-specific feedback.
   - Stop condition: population thresholds lack domain authority or the change would modify the frozen D0/D2 contract.
   - Status: PENDING.

7. **Synchronise sources, provenance, word allocation, and review state.**
   - Writer: primary agent for manuscript/evidence ledgers; independent reviewer owns review verdicts.
   - Objective: make every changed claim auditable and prevent historical PASS records from being presented as current approval.
   - Files or symbols: `Dissertation/sources/CLAIM_LEDGER.md`; `Dissertation/audit/SECTION_LEDGER.md`; `Dissertation/REPORT_STRUCTURE.md`; `Dissertation/reviews/REVIEW_LOG.md`; affected review files; affected exhibit manifests/provenance/text alternatives.
   - Method:
     1. mark each changed section's previous approval superseded/pending before review;
     2. retain unchanged historical records as history rather than rewriting them;
     3. update paragraph IDs, claim purposes, exact local source pages, exhibit inputs/hashes, and word counts;
     4. keep Sections 1.4 and 2.1 pending until their own fresh reviews complete;
     5. run affected-section review, then a whole-report cross-section review against the actual candidate.
   - Proof: claim-ledger bijection; section/review status agreement; no stale PASS or stale hash; net word allocation remains within the current working contract.
   - Stop condition: a paragraph needs citation padding, an unverified source, or a review verdict written by the implementation author.
   - Status: PENDING.

## Validation map

| Obligation | Source | Proving command or observation | Phase | Subsumed by | Invalidated by | Status |
|---|---|---|---|---|---|---|
| Exact implementation identity and current architecture | B0, repository, completed dashboard ledger | `git status --short`; scoped hashes/diff; static inspection of the current dashboard, private API, Compose, and architecture contracts | packet 1-2 | none | backend/dashboard/Compose/config/dependency change | PENDING |
| Active stale-contract inventory | B0/B4; current repository | Targeted search for `Jinja`, `286`, `85.58`, `46 source files`, and `0009` across current chapters, `REPORT_STRUCTURE.md`, referenced exhibits/text alternatives/provenance, and claim/section ledgers; classify each as remove, update, or explicitly historical | packet 2 | none | any active manuscript/exhibit/ledger change | PENDING |
| Volatile Python validation figures | Chapter 5 claim contract | Remove or date exact counts by default. If exact current figures are intentionally retained, run `.venv/bin/ruff check src tests`, `.venv/bin/mypy src`, and `.venv/bin/pytest --cov=portfolio_agent --cov-report=term-missing` once as a no-fix pre-edit baseline tied to the frozen candidate | pre-edit packet 2 only if retained | none | source/test/config/dependency/environment change | PENDING |
| Volatile Next.js build figures | architecture/result claim contract | Prefer static contract inspection and omit volatile counts. If an exact current build claim is intentionally retained, run `npm --prefix dashboard run lint && npm --prefix dashboard run build` once as part of the no-fix pre-edit baseline | pre-edit packet 2 only if retained | none | dashboard/config/dependency change | PENDING |
| Current Compose topology | architecture claim contract | Run `docker compose config --quiet` for static topology. Do not start services unless a current runtime claim is intentionally retained and that separate runtime action is authorised | packet 2 | none | Dockerfile/Compose/env/runtime change | PENDING |
| Current migration statement | current migration graph; Chapter 5/exhibit claim contract | Prefer removing the exact ordinal; otherwise run `alembic heads` and prove `upgrade head`, `current`, and `check` using a fresh validated SQLite URL under `/private/tmp` | packet 2 only if exact head retained | none | migration/model/database-configuration change | PENDING |
| Method ownership and alternative rationale | Part B B1 | feedback-to-change audit plus fresh dissertation-reviewer inspection of Chapter 3 | candidate review | full cross-section review | Chapter 3/protocol change | PENDING |
| Reliability ladder and evidence status | Part B B4; RQ1-RQ3 | metric/status matrix inspection against Chapter 3, Chapter 5, evaluation schemas/output, and Chapter 6 | packet 4 / candidate review | full cross-section review | evaluation/manuscript/evidence change | PENDING |
| Truthful interview deviation | Part B B5; ethics boundary | authoritative ethics/waiver evidence or explicit `EVIDENCE_REQUIRED`; cross-section check of Chapters 3, 5, 6, 7 and appendix status | packet 3 / candidate review | full cross-section review | new ethics/participant evidence | PENDING |
| Contradiction-ledger defence matches implementation | Part B B2 | source/claim-to-code inspection of verification, company profile review, Chapter 4, and Chapter 6; reviewer checks per-conflict limitation | packet 5 / candidate review | full cross-section review | contradiction/approval implementation or prose change | PENDING |
| Stakeholder framing is useful but non-promotional | Part B B3 | recommendation audit: audience/action/rationale/evidence/limit/measure present; no measured-benefit language | packet 5 / candidate review | full cross-section review | Discussion/Conclusion change | PENDING |
| Target population and scarcity boundary | Part B B7; Part C C1 | population/scarcity matrix inspection against protocol, Chapters 3/5/6/7, and no-score/no-inference contracts; unresolved executable sampling criteria remain `EVIDENCE_REQUIRED` | packet 6 / candidate review | full cross-section review | sampling/protocol/manuscript change | PENDING |
| Source admission and bibliography integrity | `Dissertation/README.md` | `cd Dissertation && python3 scripts/check_sources.py --strict-bibliography` | post-candidate final local | none | manuscript/reference/manifest/source change | PENDING |
| Paragraph claim-ledger integrity | `Dissertation/README.md` | `cd Dissertation && python3 scripts/check_claim_ledger.py` | post-candidate final local | none | manuscript/claim-ledger change | PENDING |
| Harvard WMS and British-language rules | `Dissertation/README.md` | `cd Dissertation && python3 scripts/check_harvard.py && python3 scripts/check_language.py` | post-candidate final local | none | manuscript/reference change | PENDING |
| Changed Mermaid architecture/provenance assets | repository AGENTS macOS browser rule; `Dissertation/README.md` | If Mermaid source changes, run `cd Dissertation && ./scripts/render_mermaid_figures.sh` with `sandbox_permissions=require_escalated` on the first launch, then `python3 scripts/check_mermaid_figures.py`; do not probe the Chromium renderer in the sandbox | post-candidate final local | none | Mermaid/config/style/manuscript/provenance change | PENDING |
| PDF compiles and changed pages are legible | `Dissertation/README.md`; DOC/PDF quality contract | `cd Dissertation && tectonic main.tex --outdir build`; inspect `pdfinfo build/main.pdf`; render and visually inspect every affected page at readable scale | post-candidate final local | final exact build | TeX/exhibit/style/reference change | PENDING |
| Word allocation remains controlled | `REPORT_STRUCTURE.md` | reproduce the existing citation-stripped section count used by the dissertation review workflow; record each changed section and total in `SECTION_LEDGER.md` | packet 7 / candidate review | full cross-section review | changed prose/captions | PENDING |
| Fresh independent section and full-report review | repository dissertation workflow; engineering candidate review | reviewer receives the verbatim user request, Part-B/C map, plan, complete diff, evidence outputs, and pending final gates; inspect affected sections, then one full cross-section review | candidate review | none | any later manuscript/evidence/provenance change | PENDING |
| Final diff and status are coherent | engineering workflow | `git diff --check`; scoped complete diff/untracked inspection; `git status --short` | final local | none | any later change | PENDING |

The Python test suite currently has no test-source reference to Playwright, Chrome, Chromium, Kaleido, Choreographer, `write_image`, or `to_image`; the optional Playwright name appears only in the dashboard lockfile. Re-enumerate before any unscoped test run. If browser/static-export tests are added or discovered, follow the repository macOS rule and run the owning command with escalation on its first launch.

## Plan review

- Reviewer: independent engineering reviewer `/root/plan_candidate_review`.
- Initial verdict: no P0; one P1 and three related P2 planning defects.
- Dispositions:
  - P1 resolved by removing the unrelated, project-specific `dissertation-expert` skill from the policy sources.
  - P2 validation scope resolved by making static reconciliation and removal/dating of volatile counts the default; exact software gates are optional one-shot, no-fix pre-edit baselines only when the figures are intentionally retained.
  - P2 stale-contract coverage resolved by adding `REPORT_STRUCTURE.md`, `sys_t1_requirements_trust_boundary_matrix.tex`, active text/provenance/ledger mirrors, and migration `0010` to the inventory and proof obligations.
  - P2 population acceptance resolved by separating a truthful target-population description from an executable sampling frame, which remains `EVIDENCE_REQUIRED` until POP-01 is resolved.
- Focused re-review verdict: PASS; no remaining P0, P1, or P2 findings. The ledger is ready as a planning artifact, with INT-01, POP-01, candidate evidence, and final validation retained as execution-time holds.

## Candidate review

- Reviewer: fresh `dissertation-reviewer` or configured independent engineering reviewer with dissertation competence; not the writer.
- Candidate identity: PENDING; record `HEAD` plus fingerprints for all changed tracked and relevant untracked manuscript, exhibit, evidence, and review-input files.
- Required review questions:
  1. Does the candidate answer every applicable Part-B item without importing irrelevant Part-C material?
  2. Is author ownership explicit without claiming unsupported novelty or misrepresenting supervisor input?
  3. Are contradiction handling, JSON integration value, reliability, interviews, and target population described no more strongly than the frozen evidence permits?
  4. Are Sections 1.4/2.1 and all changed-section approvals represented with current status?
  5. Are word, citation, provenance, exhibit, and architecture claims internally consistent?
- Full-review findings and dispositions: PENDING.
- Focused re-review surface and verdict: PENDING.
- Unresolved P0/P1: PENDING.
- P2/P3 dispositions: PENDING.
- Ready to freeze: NO.

## Final validation

- Frozen candidate identity: PENDING.

| Status | Command or observation | Covered obligations | Result |
|---|---|---|---|
| UNRUN | exact-state implementation reconciliation | architecture and numeric engineering claims | Planning only |
| UNRUN | dissertation source/claim/Harvard/language checks | citation, evidence, and style integrity | Planning only |
| UNRUN | affected Mermaid render/check when required | current architecture figure and provenance | Planning only |
| UNRUN | Tectonic build and changed-page visual inspection | compilation, pagination, and legibility | Planning only |
| UNRUN | independent affected-section and full cross-section reviews | requirement fidelity and whole-report coherence | Planning only |
| UNRUN | `git diff --check` and final scoped diff/status inspection | diff hygiene and scope | Planning only |

- Reused evidence and why it remains valid: none yet. The completed Next.js ledger is a candidate evidence source, not automatically current proof.
- Invalidation decisions after failures or corrections: none; planning only.
- Remote CI or delivery evidence: UNRUN and out of scope.
- Residual proof gaps: actual ethics/interview history, approved target-population criteria, current exact implementation gate, changed-section evidence/reviews, and final PDF QA.
- Residual risks: imminent submission pressure could tempt unverified wording, stale counts, review-status reuse, or last-minute product work. The stop rules above are intended to prevent those failure modes.
- Handoff: execute only after the user authorises `engineering EXECUTE .agents/runs/supervisor-feedback-parts-b-c-improvements.md` and provides or confirms INT-01/POP-01 where available.
