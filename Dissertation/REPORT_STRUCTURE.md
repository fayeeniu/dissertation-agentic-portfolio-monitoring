# Reviewer-approved dissertation structure

Status: **round 2 independent reviewer gate PASS on 27 August 2026**. This approval covers the
full-report structure and the populated Abstract only; it does not approve future chapter prose or
currently unavailable live, human, production, or accessibility evidence.

## Planning convention

The user supplied a 15,000-word ceiling. Until WMG confirms the exact counting convention, this
plan conservatively allocates 14,500 words across the Abstract and numbered chapters, leaving a
500-word contingency. The current Abstract contains 398 plain-text words and fits its 400-word
allocation. The Project Submission Pro-Forma, title page, Declaration, contents, lists,
glossary, references, and appendices are treated as outside this planning total only as a working
assumption; the final count must follow the authenticated submission rule.

Only the Abstract is drafted at this stage. Every other item below is a structure and evidence plan,
not completed dissertation content.

## Research contract

### Primary research question

> To what extent can a multi-agent AI pipeline automate the end-to-end data ingestion, validation,
> and report-generation workflow for early-stage portfolio reporting, and how does quality and
> reliability compare with manually produced reports?

### Operational sub-questions

1. **RQ1 - data and evidence fidelity:** How accurately and reliably can the bounded workflow
   transform heterogeneous portfolio inputs into typed, temporally eligible, provenance-complete,
   and reviewable claims without collapsing uncertainty?
2. **RQ2 - independent verification:** Under the same information boundary, how does a separate
   verifier change supported-claim precision, recall, unsupported-claim rate, contradiction
   handling, abstention, provenance completeness, and repeat consistency relative to a deterministic
   path without independent verification?
3. **RQ3 - efficiency and human review:** Where separately authorised, how do automated and named-
   review conditions compare with the manual workflow in report correctness, completeness, active
   and elapsed time, edit burden, approval time, and reviewer utility?

### Implemented case study and held future evaluation

The bounded public-web company-research path is an implemented but live-unrun engineering case
study. It is not an authorised research question in the frozen charter or evaluation protocol.
System design, adversarial fake-provider tests, pinned-transport tests, and local approval controls
may be reported as implementation evidence, but not as an empirical answer alongside RQ1-RQ3.

Subject to a separately authorised protocol amendment and a newly frozen benchmark, future work may
ask what coverage, claim-quality, failure, latency, token, and cost differences arise between
admitted official-source adapters and bounded LLM-assisted discovery. That comparison remains held;
it must not be presented as part of the current research contract or silently executed on D0.

### Current go/no-go state - 27 August 2026

The manual and human-in-the-loop comparison is currently **NO-GO** because ethics confirmation,
restricted-data authority, participant approval, and the final observation protocol are not verified.
If those authorities are recorded before protocol freeze, C0 and C3 may proceed exactly under the
pre-specified protocol. If they are absent at freeze, the final report must state that the manual
comparison is unanswered and that the primary research question is only partially answered. It must
retain null C0/C3 outcomes and must not substitute D0 synthetic measurements for human or operational
evidence.

## Word and evidence map

| Part | Words | Purpose and research-question link | Evidence to use | Planned exhibits | Current status |
|---|---:|---|---|---|---|
| Abstract | 400 | Stand-alone problem, aim, method, principal synthetic result, contribution, and limits | Current repository, 14-case D0 run, explicit evidence holds | None | Reviewer-approved in round 2 |
| 1. Introduction | 1,400 | Establish the concrete portfolio-reporting problem, primary RQ, RQ1-RQ3, objectives, scope, and contribution | `docs/PROJECT_CHARTER.md`, source-evidence matrix, stakeholder evidence, requirements | Problem-to-research-contract diagram; objective/RQ table | Structure only |
| 2. Literature Review | 2,500 | Critically synthesise early-stage evidence, data quality, provenance, grounded LLM use, agents, and HITL; derive the gap | Hash-pinned ten-paper corpus, page-cited synthesis, primary/official sources added under a dated search protocol | Literature concept matrix; claim-evidence gap table | Structure only |
| 3. Research Design and Methodology | 2,300 | Define the artefact evaluand, C0-C3 conditions, D0-D2 tiers, gold labels, measures, analysis, ethics, and leakage controls | `docs/EVALUATION_PROTOCOL.md`, manifests, governance, data dictionary | Condition matrix; dataset-freeze timeline; metric/denominator table | Structure only |
| 4. System Design and Implementation | 2,850 | Explain architecture needed to support RQ1-RQ3 and document the bounded company-research case study as engineering evidence | Requirements, ADRs, code, migrations 0001-0009, tests, architecture and traceability | Trust-boundary architecture; provenance chain; research-task state machine; Company 360 flow | Structure only |
| 5. Evaluation and Results | 2,200 | Report engineering validation and synthetic results, the live-unrun case-study boundary, and authorised human evidence only if it exists | Frozen run outputs and hashes; test/migration records; future D1/D2 artefacts | D0 comparison; case-study adversarial-control results; failure taxonomy | Structure only |
| 6. Discussion | 1,600 | Answer RQ1-RQ3 proportionately; separate mechanism evidence, empirical inference, case-study engineering evidence, and alternative explanations | Results chapter plus relevant literature | RQ-to-evidence synthesis table; trade-off matrix | Structure only |
| 7. Ethics, Governance and Limitations | 800 | Integrate privacy, model retention, security, source rights, investment-decision exclusions, residual risk, and validity limits | Governance document, source register, threat tests, ethics evidence when authorised | Trust/residual-risk table | Structure only |
| 8. Conclusion and Future Work | 450 | State demonstrated contribution, bounded answers, unresolved evidence, and sequenced next work without introducing new claims | RQ findings and evidence-status map | None | Structure only |
| **Total** | **14,500** |  |  |  |  |

## Detailed chapter plan

### 1. Introduction - 1,400 words

- **1.1 Early-stage portfolio reporting and company intelligence (250):** decision context,
  heterogeneous inputs, public/private evidence boundary, and why fluent prose is not the core
  problem.
- **1.2 Problem definition and motivation (300):** identity errors, blank-versus-zero collapse,
  temporal mismatch, contradictions, unsupported synthesis, provenance loss, and manual effort.
- **1.3 Aim and research questions (250):** primary RQ and RQ1-RQ3, with each question tied to an
  observable outcome rather than a feature list.
- **1.4 Research objectives (200):** design, implementation, controlled comparison, human-control
  evaluation, and evidence-calibrated reporting objectives.
- **1.5 Scope, contribution, and exclusions (250):** local research prototype; public/restricted
  separation; no investment recommendation, speculative valuation, person profiling, production
  claim, or automatic publication.
- **1.6 Dissertation roadmap (150):** argument and evidence progression.

### 2. Literature Review - 2,500 words

- **2.1 Review method and evidence boundary (250):** inclusion, access, date, source quality,
  reconstruction limits, and non-exhaustive status.
- **2.2 Early-stage finance, portfolio reporting, and public company intelligence (400):** information
  asymmetry, funding/award/contract signals, and the distinction between evidence and investment
  inference.
- **2.3 Data quality, entity identity, missingness, and time (450):** data-quality dimensions,
  source-scoped identity, availability time, corrections, and semantically distinct missing states.
- **2.4 Provenance, source admission, contradiction, and auditable synthesis (450):** exact locators,
  immutable capture, source tiers, competing claims, and abstention.
- **2.5 LLM-assisted discovery and grounded extraction (400):** web search as candidate discovery,
  structured output, citation/span verification, prompt injection, model/provider retention, and
  hallucination limits.
- **2.6 Bounded multi-agent systems and human review (350):** decomposition, independent verification,
  orchestration overhead, HITL authority, and governance evidence.
- **2.7 Critical synthesis and research gap (200):** the untested combination addressed by RQ1-RQ3,
  the separate engineering relevance of bounded public-web research, and why implementation alone
  cannot answer an empirical question.

### 3. Research Design and Methodology - 2,300 words

- **3.1 Applied design-science strategy (250):** artefact plus evaluation, researcher role, and
  distinction between implementation evidence and findings.
- **3.2 Evaluand and conditions (350):** C0 manual, C1 deterministic/no independent verifier, C2
  bounded multi-agent verification, and C3 C2 plus HITL. The live-unrun company-research path is not
  an experimental condition in the frozen protocol.
- **3.3 Dataset tiers and freeze protocol (350):** D0 synthetic engineering set, D1 authorised pilot,
  and D2 sealed final holdout; entity/period grouping and no post-holdout tuning. Any participant
  observations belong to authorised C0/C3 execution, not an invented additional dataset tier.
- **3.4 Gold/reference construction and source parity (300):** two-reviewer labelling where possible,
  adjudication, availability cutoff, equal information access, inaccessible/paywalled states, and
  exact span/source policy.
- **3.5 Measures and denominators (400):** identity, acquisition, extraction, verification,
  provenance, synthesis, reliability, latency, tokens/cost, review edits, and usability; explicit
  null and zero-denominator rules.
- **3.6 Statistical and qualitative analysis (350):** paired units, clustered/dependence-aware
  uncertainty, effect sizes, failure-inclusive sensitivity, pre-specified error taxonomy, and
  negative/null findings.
- **3.7 Ethics, leakage prevention, and reproducibility (300):** data authority, classification,
  participant consent, prompt/rule freeze, manifests, hashes, environment, deviations, and stop
  conditions.

### 4. System Design and Implementation - 2,850 words

- **4.1 Requirements and trust boundaries (250):** local/single-user goal, data classifications,
  authority owners, and non-goals.
- **4.2 Architecture and deployment (300):** FastAPI/Jinja, SQLite/Alembic, immutable local storage,
  Docker/loopback runtime, and why this is not a production architecture.
- **4.3 Canonical data, persistence, and provenance (450):** metrics, period semantics, missing-state
  types, source snapshots, derivation hashes, claim/evidence links, and versioned exports.
- **4.4 Intake and legal-identity control (350):** portfolio files, Companies House-number-only case,
  name/domain/document claims, idempotency, exact identifier decision, and no fuzzy auto-merge.
- **4.5 Fixed portfolio workflow and independent verification (400):** plan through human review,
  typed stage records, fail-closed transitions, contradiction/status logic, and approval binding.
- **4.6 Deterministic source adapters, time, and quality (350):** offline Companies House/UKRI replay,
  source-capability admission, cumulative-window rules, exact locators, and distinct no-record,
  unavailable, and failure states.
- **4.7 Bounded public-web company-research case study (400):** Responses web discovery, URL-only
  admission, guarded HTTPS/robots/DNS/redirect/MIME/byte capture, connection-to-resolved-public-IP
  pinning with hostname TLS verification, immutable snapshots, public-text redaction, strict
  exact-span extraction, serial persisted tasks, coverage gaps, deterministic cited deck,
  cancellation/budgets/telemetry, and the unrun-live boundary. This is implementation evidence, not
  an additional empirical research question.
- **4.8 Human review and outputs (200):** optimistic locks, named decision, version revocation,
  approved HTML/JSON/Markdown outputs, and no autonomous publication.
- **4.9 Failure, recovery, and implementation-status ledger (150):** retries, tamper/hash failure,
  blocked sources, downgrade preflights, and implemented-versus-deferred matrix.

### 5. Evaluation and Results - 2,200 words

- **5.1 Exact implementation snapshot (200):** revision/diff state, environment, dependency and
  migration versions, manifests, and unrun checks.
- **5.2 Engineering validation (250):** targeted/full tests, schema equivalence, migration round trips,
  security/contract checks, deterministic replay, and PDF/accessibility status.
- **5.3 D0 fixture and comparison design (250):** fourteen labelled adversarial cases and equal-input
  C1/C2 comparison across three repeats.
- **5.4 D0 results (450):** claim precision/recall/F1, unsupported-claim rate, contradiction,
  abstention, provenance, schema validity, and repeat consistency, labelled as constructed mechanism
  evidence only.
- **5.5 Company-research contract and adversarial engineering results (300):** fake Responses source
  discovery, exact spans, restricted-case rejection, robots/redirect/MIME/byte/SSRF tests,
  connection-to-validated-public-IP pinning, and the approval/export gate. The actual residual is
  that hosted, multi-tenant, and production-egress guarantees remain unproven.
- **5.6 Held future public-company source-discovery comparison (350):** an official-adapter-only
  versus LLM-assisted coverage/quality/cost comparison may be designed only after separate authority,
  protocol amendment, source admission, and benchmark freeze. The present chapter must record it as
  held rather than promise or fabricate a result.
- **5.7 Manual and HITL comparison (250):** C0/C3 quality, time, edits, agreement, and usability;
  currently NO-GO. If authorisation is absent at protocol freeze, results remain null, the manual
  comparison is unanswered, and the primary research question is reported as partially answered.
- **5.8 Negative, null, failed, and unavailable outcomes (150):** no silent omission or zero filling.

### 6. Discussion - 1,600 words

- **6.1 RQ1 - what the artefact establishes (300):** controlled feasibility and auditability, not
  automation effectiveness.
- **6.2 RQ2 - verification benefit and cost (300):** synthetic mechanism result, precision-recall
  trade-off, conservatism, fixture construction, and required external validation.
- **6.3 RQ3 - efficiency and role of named review (200):** implemented authority and audit versus
  unmeasured human benefit and efficiency.
- **6.4 Bounded company-research case study and held future evaluation (300):** discuss web-search
  candidates, immutable capture, official-source precedence, open-web instability, and local control
  evidence without presenting an RQ answer. State what a separately authorised future paired
  benchmark would need to decide.
- **6.5 Relationship to literature and design trade-offs (300):** deterministic-first controls,
  bounded agents, failure visibility, architectural overhead, and alternative single-agent designs.
- **6.6 Generalisability and practical interpretation (200):** one local prototype, constructed
  fixtures, changing sources/models, no investment-performance inference, and transfer conditions.

### 7. Ethics, Governance and Limitations - 800 words

- **7.1 Data classification, privacy, and purpose limitation (180).**
- **7.2 External-model processing and retention caveat (140):** `store=False` is not Zero Data
  Retention; account/project controls and provider policy remain execution-time evidence.
- **7.3 Security and failure threats (180):** prompt injection, SSRF/DNS rebinding, redirects,
  malformed sources, tampering, rate/cost exhaustion, and fail-closed recovery.
- **7.4 Investment and public-person boundaries (120):** no recommendation, scoring, speculative
  valuation, person profiling, or causal inference from public events.
- **7.5 Research and operational limitations (180):** synthetic development evidence, unrun public
  and human studies, source/licence drift, accessibility gap, SQLite/synchronous/local constraints,
  and researcher confirmation bias.

### 8. Conclusion and Future Work - 450 words

- **8.1 Proportionate answers to the primary RQ and RQ1-RQ3 (200).**
- **8.2 Demonstrated design and empirical contribution (120).**
- **8.3 Sequenced next evidence (130):** content-free live smoke, frozen public benchmark, admitted
  official adapters, authorised D1/D2 and C0/C3 evaluation, accessibility audit, and production work only if
  required.

## Appendices outside the provisional body allocation

- **Appendix A:** evidence of required ethics training.
- **Appendix B:** ethics approval or waiver confirmation email.
- **Appendix C:** requirements-to-implementation-to-test traceability.
- **Appendix D:** dataset/source manifests, hashes, codebook, and freeze record.
- **Appendix E:** source-admission and provider-data-control evidence.
- **Appendix F:** complete evaluation tables, denominators, error taxonomy, and sensitivity output.
- **Appendix G:** configuration, environment, migration, build, and reproducibility manifest.
- **Appendix H:** supplementary figures/tables and accessible text alternatives.
- **Appendix I:** generative-AI use disclosure if required by the applicable WMG policy.

## Claim-control rule

Every drafted subsection must classify its central statements as source-supported, implemented,
synthetic-measured, protocol-only, evidence-required, or held while drafting. Final prose may omit
those labels only after the referenced evidence exists. Plans, tests, synthetic fixtures, and code
must never be rewritten as live-source, human-study, production, or investment-performance findings.
