# Dissertation evidence map

## Evidence-state legend

| State | Meaning |
|---|---|
| `SOURCE-SUPPORTED` | Directly grounded in supplied source material, with limits noted |
| `IMPLEMENTED` | Current artifact/code and local validation demonstrate it |
| `SYNTHETIC-MEASURED` | Measured only on labelled fictional fixtures |
| `PROTOCOL-ONLY` | Designed but not empirically executed |
| `EVIDENCE-REQUIRED` | Cannot be claimed until a named artifact/study exists |
| `HELD` | Blocked by ethics, security, authority, or leakage boundary |

These states should appear in research notes and table-generation scripts. Remove them from final
prose only when the associated evidence is genuinely present—not to make a chapter sound complete.

## Chapter wayfinding

| Chapter | Core question | Current evidence/assets | Claims safe now | Evidence still required |
|---|---|---|---|---|
| 1. Introduction | What problem, context, RQ, contribution, and scope? | `PROJECT_CHARTER.md`; MAT-01; TR-01/05; source register | Manual workflow is stakeholder-described; RQ and artifact scope are defined | Published context/industry evidence; approved final wording |
| 2. Literature review | What is known about UK early-stage evidence, extraction, provenance, quality, identity, and HITL? | Ten-paper accessible-data review, manifest, hashes, rejected candidates, page-cited synthesis | Included-paper claims may be used within stated reconstruction/access caveats | Broader search/generalisation claims and any later literature update require a dated protocol amendment |
| 3. Methodology | How will conditions, data, gold labels, metrics, ethics, and analysis answer the RQ? | `EVALUATION_PROTOCOL.md`; governance; fixture taxonomy | Protocol is specified; synthetic and empirical evidence are separated | Ethics confirmation, D1 pilot, sample/precision plan, final protocol registration |
| 4. Design and implementation | Why this architecture and how does it work? | Requirements, data dictionary, architecture, contracts, ADRs, public-source register, tests, migrations, 15-figure pack | Offline design and current implementation can be described | Final exact-state validation/review output and known limitations |
| 5. Evaluation/results | What happened in C0–C3? | Automated D0 harness and case outputs | Only synthetic mechanism/regression results may be reported as such | C0/C3 observations, D2 outputs, gold scores, uncertainty, failure accounting |
| 6. Discussion | What explains effects; what are trade-offs and validity limits? | Predicted mechanisms and documented risks only | Design trade-offs may be argued; empirical causal claims are unsafe | Actual condition results/error taxonomy/qualitative themes |
| 7. Conclusion | What can be concluded and what should happen next? | RQ, intended contribution, Wayfinder | Artifact contribution can be stated after final checks | RQ answer bounded by empirical results; no “success” claim in advance |

## Claim-evidence register

| Claim ID | Candidate dissertation claim | Required evidence | Current state | Safe wording now |
|---|---|---|---|---|
| DC-01 | Portfolio reporting inputs are heterogeneous and incomplete. | Workbook structural/type profile plus stakeholder context | SOURCE-SUPPORTED | “The supplied Q2 workbook contains mixed numeric/text types and blank fields across metric rows.” |
| DC-02 | The existing workflow has material manual collection/aggregation activity. | Stakeholder transcript; ideally observed C0 process data | SOURCE-SUPPORTED, empirical extent required | “A stakeholder described collection and aggregation as manual”; not “takes X hours.” |
| DC-03 | An evidence-first multi-agent P0 can execute end to end locally. | Passing e2e test, migration proof, run/report/export artifacts | IMPLEMENTED after final gate | “The prototype executed the defined synthetic vertical slice.” |
| DC-04 | The verifier prevents unsupported/stale/injected synthetic claims in designed cases. | D0 case-level outputs and fixture manifest | SYNTHETIC-MEASURED | “On labelled synthetic adversarial cases…” |
| DC-05 | Multi-agent verification is more accurate than a simpler baseline. | Paired C1/C2 results on frozen non-development data with uncertainty | EVIDENCE-REQUIRED | Do not claim; D0 is mechanism validation, not general performance evidence. |
| DC-06 | Automation reduces cycle time relative to manual reporting. | Comparable C0/C1/C2/C3 timing, active/elapsed definitions, paired units | PROTOCOL-ONLY | “The protocol will estimate…” |
| DC-07 | HITL improves final quality/usability. | Pre/post C2/C3 scores, event logs, approved participant study | HELD | Do not claim until ethics-approved data exist. |
| DC-08 | The architecture is cheaper/more expensive than one agent. | Tokens, calls, official dated prices, human time, failures across conditions | EVIDENCE-REQUIRED | Discuss expected trade-off only; stakeholder preference is not cost evidence. |
| DC-09 | `gpt-5.4-mini`/`gpt-5.4` are appropriate routes. | Dated official capability docs plus public/synthetic benchmark under frozen schema | IMPLEMENTED route, performance untested | “The adapter is configured for these routes”; not “they perform best.” |
| DC-10 | The system is secure/production-ready. | Full product controls, threat tests, auth, DPIA, deployment review | HELD / explicitly false for P0 | “The prototype is loopback-only and not production-ready.” |

## Research artifact map

| Artifact | Dissertation use | Validation/evidence |
|---|---|---|
| `SOURCE_EVIDENCE_MATRIX.md` | Problem derivation and evidence limitations | Source hashes, locators, credential hold |
| `REQUIREMENTS.md` | Traceable design specification | Stable requirement IDs and acceptance mapping |
| `DATA_DICTIONARY.md` | Construct operationalisation | Missingness/types/sourceability/invariants |
| `ARCHITECTURE.md` | Design chapter figures and component rationale | Mermaid context/state/ER diagrams, code mapping |
| `AGENT_CONTRACTS.md` | Agentic-method definition | Bounded role contracts and verification table |
| `SECURITY_AND_DATA_GOVERNANCE.md` | Ethics, trust boundaries, responsible AI | Classification matrix and threat model |
| `EVALUATION_PROTOCOL.md` | Methodology and analysis plan | Four conditions, metrics, partition and leakage rules |
| `SOURCE_ADMISSION_REGISTER.md` | Separates source mechanics from live legal/identity authority | Versions, explicit evidence holds, G2 checklist |
| `research/literature/` | Literature chapter and design rationale | 10-paper manifest, PDFs/checksums, inclusion/rejection record, page-cited synthesis |
| `docs/figures/generated/` | Design/evaluation figures and textual alternatives | 15 deterministic accessible SVGs plus JSON/CSV SHA-256 manifest |
| `docs/adr/*.md` | Decision audit | Options, decisions, consequences |
| `fixtures/` | Reproducible D0 case design | Fictional labels and SHA-256 at execution |
| `tests/` | Engineering validity | Unit/integration/web/e2e checks and coverage |
| `alembic/versions/` | Reproducible persistence and transition safety | Empty-head equivalence plus 0001↔head legacy round trip |
| `var/evaluation/<frozen>.json` | D0 results appendix/table source | Ignored runtime artifact; freeze/hash after final version |
| `var/exports/<report>/vN/` | Demonstration report artifact | Requires audited synthetic approval; freeze/hash |

## Dissertation figures and tables

| ID | Item | Source of truth | State |
|---|---|---|---|
| Fig 1–3 | Trust-boundary architecture, bounded workflow, and provenance chain | Generated figure manifest; code/docs contracts | Implemented diagrammatic evidence |
| Fig 4–6 | Identity holds, temporal eligibility, and source coverage | Structural counts or synthetic workflow, labelled per figure | Implemented; not real performance evidence |
| Fig 7–10 | Verification stack, missingness heatmap, quality dispositions, UKRI lifecycle | Deterministic synthetic run/source fixture | SYNTHETIC-MEASURED / mechanism only |
| Fig 11 | Five-number cohort context | Explicit illustrative synthetic vector | Illustration only; never empirical result |
| Fig 12–15 | D0 condition comparison, extraction attempts/abstention, review states | Hashed D0/synthetic run and code contracts | SYNTHETIC-MEASURED or design diagram |
| Table 1 | Source evidence matrix | `SOURCE_EVIDENCE_MATRIX.md` | Implemented |
| Table 2 | Metric/sourceability/missingness model | `DATA_DICTIONARY.md` | Initial; domain approval pending |
| Table 3 | C0–C3 quality/efficiency/reliability outcomes | Frozen result tables | EVIDENCE-REQUIRED |
| Table 4 | Error taxonomy by condition | Gold scoring output | EVIDENCE-REQUIRED |
| Table 5 | Threats to validity and mitigations | Protocol + observed study deviations | Partly draftable |

Never manually transcribe final numeric results into multiple files. Generate tables/figures from
one frozen analysis dataset and record its hash.

## Literature evidence boundary

The supplied materials are not themselves a literature review. The separate
`research/literature/UK_EARLY_STAGE_AGENTIC_PORTFOLIO_LITERATURE_REVIEW.md` is a targeted,
implementation-led accessible-data synthesis, not an exhaustive PRISMA review. Its ten-paper
corpus, source URLs, page counts, UK/data-access verdicts, local PDF hashes, released datasets, and
rejected candidates are frozen beside it. Use its page-level citations and caveats; do not widen
“reconstructible from public sources” into “exactly reproducible” or generalise D0 engineering
results into empirical literature support.

## Evidence capture checklist for final implementation snapshot

```bash
git status --short --branch
.venv/bin/alembic upgrade head
.venv/bin/ruff format --check src tests
.venv/bin/ruff check src tests
.venv/bin/mypy src
.venv/bin/pytest --cov=portfolio_agent --cov-report=term-missing
.venv/bin/portfolio-agent evaluate --manifest fixtures/evaluation_manifest.json --repeats 3
.venv/bin/portfolio-agent visualize
```

Additionally record dependency versions, OS/Python, migration table equivalence, fixture hashes,
secret-scan result, report artifact hashes, and any unrun browser/accessibility/security checks.

## Submission claim gate

Before marking the dissertation ready, search the manuscript for absolute wording such as
“proved,” “eliminated hallucinations,” “reduced time,” “improved accuracy,” “users preferred,”
“secure,” or “production-ready.” Each occurrence needs a direct, current evidence row above or
must be narrowed to the actual synthetic/implemented/protocol state.
