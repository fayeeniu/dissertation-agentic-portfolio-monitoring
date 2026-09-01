# Product and research requirements

## Requirement conventions

- **P0** — required for the dissertation vertical slice and implemented in this repository.
- **P1** — useful extension only after P0 evidence is frozen.
- **P2** — explicitly outside the dissertation prototype.
- **Implemented** means source exists and local checks exercise the contract.
- **Protocol-only** means the study is designed but empirical data is not yet collected.

Requirements use stable IDs so design, code, tests, and dissertation evidence can be traced.

## P0 functional requirements

### Ingestion, immutability, and provenance

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-ING-001 | Import exactly one reporting period from XLSX, CSV, or canonical JSON. | Integration tests exercise all three formats; XLSX/CSV reject missing period labels. | Implemented |
| FR-ING-002 | Hash the supplied bytes and derive a period-bound dataset ID. | `RawSubmission.sha256` and `dataset_id`; idempotence test. | Implemented |
| FR-ING-003 | Store an immutable local raw snapshot with a non-user-controlled filename and restrictive permissions. | Snapshot uses create-once semantics and mode `0600`; test inspects mode. | Implemented |
| FR-ING-004 | Re-importing identical bytes for the same period must reuse the dataset and create no duplicate observations. | Importer returns `reused_existing=true`; unique constraints. | Implemented |
| FR-ING-005 | Preserve original values and source locations separately from normalized values. | Observation model fields and export provenance. | Implemented |
| FR-ING-006 | Validate format/schema and return structured severity, code, message, and location issues. | `ImportIssue`; malformed/unknown/duplicate paths. | Implemented |
| FR-ING-007 | Never evaluate workbook formulas as executable logic during ingestion. | XLSX loaded with `data_only=False`; formula text normalizes or is held invalid. | Implemented |

### Canonical catalogue and semantics

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-MET-001 | Every observation must resolve to a version-controlled metric definition before becoming canonical. | Seeded catalogue and foreign key. | Implemented |
| FR-MET-002 | Metric definitions must specify key, label, category, data type, unit, sourceability, period semantics, aliases, and description. | Pydantic/SQLAlchemy contracts; catalogue test rejects unspecified period semantics. | Implemented |
| FR-MET-003 | Blank, zero, none stated, N/A, not reported, not found publicly, invalid, and observed must remain distinct. | `MissingState` and parameterised tests. | Implemented |
| FR-MET-004 | Integer metrics must reject fractional values rather than rounding. | `non_integral_count` normalization issue. | Implemented |
| FR-MET-005 | Percentage-point values must not be silently scaled from ratios. | Values are retained as entered within 0–100; test documents rule. | Implemented |
| FR-MET-006 | Currency values must retain explicit ISO currency; no currency may be guessed. | Symbol/code parser; `currency_missing` issue. | Implemented |
| FR-MET-007 | Unknown or ambiguous labels must be reported and not silently mapped. | Unknown-metric warning and alias collision protection. | Implemented |

### Company identity resolution

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-ID-001 | Resolve and collect only through an exact, source-scoped identifier; newly supplied public identifiers require a named review decision, and normalized names only order candidates. | `CompanyIdentifier`, identity queue, cross-company/unreviewed/expired rejection tests. | Implemented |
| FR-ID-002 | Do not fuzzy-merge companies automatically. | No fuzzy matcher exists in P0. | Implemented |
| FR-ID-003 | Conflicting identifier/name pairs must enter an ambiguity hold and skip affected observations. | Ambiguity integration test. | Implemented |
| FR-ID-004 | A workflow must stop before collection if any included company remains ambiguous. | Resolve stage invariant. | Implemented |

### Sourceability and connectors

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-CON-001 | Classify metrics as publicly sourceable, internal-only, mixed, or derived. | Catalogue and data dictionary. | Implemented |
| FR-CON-002 | Use a source-oriented connector protocol independent of extraction and verification; one snapshot may yield several facts/events. | `SourceRequest`, `SourceCollection`, registry contract tests. | Implemented |
| FR-CON-003 | Connector evidence must include source type, locator, publisher, retrieval/publication times, checksum, version, classification, trust state, structured fact locator, extraction method, and extraction-schema version. Every fact key is manifest-bound to its only allowed metric(s), method, schema, unit, and currency. | Strict source-fact contract validation, cross-metric rejection, and persisted `EvidenceItem`/`EvidenceFact` provenance. | Implemented |
| FR-CON-004 | P0 must run without network access using fictional evidence fixtures. | Fixture connector and tests. | Implemented |
| FR-CON-005 | A missing public result must remain missing; it must not be inferred from company text or model priors. | No-evidence verification state; protocol cases. | Implemented |
| FR-CON-006 | Evidence, source snapshots, and public events gathered for one run must be explicitly associated with that run and cutoff. | `run_evidence`, `run_source_snapshots`, `source_snapshot_events`; cross-cutoff integration tests. | Implemented |

### Extraction, normalization, and optional models

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-EXT-001 | Apply deterministic structured extraction before considering an LLM. | Default deterministic provider. | Implemented |
| FR-EXT-002 | Every extraction must satisfy a strict typed schema and expected company/metric identity. | `StrictExtraction`; identity checks. | Implemented |
| FR-EXT-003 | Keep extracted and normalized values separate and preserve provider/schema version. | `Extraction` model. | Implemented |
| FR-EXT-004 | Reject instruction-like/untrusted evidence before extraction or model processing. | Injection detector; workflow and security tests. | Implemented |
| FR-EXT-005 | External model use must be opt-in, limited to public/synthetic evidence, use `store=False`, and use bounded attempts. | OpenAI provider policy gates. | Implemented; one bounded synthetic live call exercised |
| FR-EXT-006 | Model routing must enforce `gpt-5.6-luna` for every external call and permit at most one same-model repair only after strict-validation failure; any model outside the pinned route fails before client construction. | Settings and provider adapter. | Implemented; primary route exercised in the bounded synthetic smoke, repair path mocked |
| FR-EXT-007 | Model name, attempts, tokens, and errors must be observable; unknown monetary cost must remain null. | Agent/extraction records; no invented pricing. | Implemented |
| FR-EXT-008 | Every non-null model extraction must cite a complete finite numeric token or exact structured value leaf present in the supplied evidence whose parsed value/currency/unit agree; substrings, scaled/percentage truncation, and non-finite values fail closed. Nulls require an abstention reason. | `StrictExtraction` v2 and adversarial mocked-provider tests. | Implemented; exact structured-value path exercised live, adversarial paths mocked |

### Bounded multi-agent workflow

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-AGT-001 | Execute only the ordered states plan → resolve → collect → extract → normalize → verify → compose → human review. | Eight stage records in integration test. | Implemented |
| FR-AGT-002 | Each stage must have a named functional role, typed/persistent inputs and outputs, status, timing, and hashes. | `AgentRun` ledger. | Implemented |
| FR-AGT-003 | No agent may create an open-ended loop or publish/export directly. | Orchestrator has fixed stage tuple; report service owns export. | Implemented |
| FR-AGT-004 | A stage exception must mark the run and stage failed and stop downstream work. | `_execute_stage`/pipeline failure handling. | Implemented |
| FR-AGT-005 | The verifier must be a separate role from extractor and composer. | Role order and independent verifier tests. | Implemented |

### Claims and independent verification

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-VER-001 | Every report candidate must be represented as a Claim with company, metric, period, value, text, and status. | Claim model and workflow. | Implemented |
| FR-VER-002 | Every Claim must have at least one Verification before approval. | Approval invariant and integration assertion. | Implemented |
| FR-VER-003 | Verification states must include supported, contradicted, insufficient evidence, stale, and rejected-untrusted. | Enum, pure verifier, tests. | Implemented |
| FR-VER-004 | Support requires exact normalized value, period match, eligible sourceability, and provenance completeness. | `verify_claim`. | Implemented |
| FR-VER-005 | A current public conflict must be surfaced, not averaged or silently overridden. | Contradiction rule and fixture conflicts. | Implemented |
| FR-VER-006 | Currency conflicts must not invoke an implicit conversion. | Mixed-currency test. | Implemented |
| FR-VER-007 | Supported claim-evidence links must be exported without embedding raw evidence content. | Export provenance object. | Implemented |

### Reporting and human-in-the-loop control

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-REP-001 | Compose a deterministic report with supported claims, comparable changes, exceptions, source coverage, quality, event timeline, descriptive context, and limitations. | Composer/context/report tests and UI. | Implemented |
| FR-REP-002 | Supported narrative must exclude contradicted/insufficient claims while showing their states as exceptions. | Composer rules. | Implemented |
| FR-REP-003 | Report and section versions must be preserved; edits create new section versions. | Edit service and test. | Implemented |
| FR-REP-004 | Approve, reject, and edit decisions must record named actor, rationale, report version, and time. | `ReviewDecision`. | Implemented |
| FR-REP-005 | Export must fail unless the current report version has explicit approval. | Report-state test. | Implemented |
| FR-REP-006 | Post-approval export must produce versioned JSON, Markdown, and accessible HTML. | End-to-end test. | Implemented |
| FR-REP-007 | Editing an approved report must revoke approval and require re-review. | Edit transition and test. | Implemented |
| FR-REP-008 | A stale browser/service mutation must fail by optimistic version token. | `lock_version` compare-and-swap and concurrency tests. | Implemented |
| FR-REP-009 | Filesystem artifacts and database export state must finalize through a manifest-backed staging transition. | `ReportExport`, pending/finalized/failed states, atomic export tests. | Implemented |

### Interface, observability, and reproducibility

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-UI-001 | Provide a keyboard-operable Next.js control room for company intake, run trace, profile review, decisions, and approved downloads. | Next.js type/lint/build gates and control-room API tests. | Implemented; formal browser audit pending |
| FR-UI-002 | Communicate state in text, not colour alone, with labels, semantic headings, and reduced-motion parity. | Next.js components/styles and static inspection. | Implemented; formal accessibility audit pending |
| FR-UI-003 | Publish only Next.js on loopback; reject non-private FastAPI clients/unexpected Host headers and require CSRF on every API mutation. | Compose contract, web middleware negatives, and control-room API tests. | Implemented |
| FR-UI-004 | Derive reviewer identity from local configuration, never an action form field. | `PORTFOLIO_REVIEWER_NAME`; mutation tests. | Implemented |
| FR-OBS-001 | Give every dataset, workflow, agent action, evidence item, extraction, claim, report, and review a stable ID. | Data model. | Implemented |
| FR-OBS-002 | Retain input/output hashes, duration, attempts, provider/model, tokens, errors, and bounded metadata. | Agent ledger. | Implemented |
| FR-OBS-003 | Pin dependencies and maintain reversible, model-equivalent Alembic history; a downgrade that cannot satisfy a legacy constraint must fail before any mutation. | `pyproject.toml`; revisions `0001`–`0009`; schema/round-trip/legacy-hash/duplicate-name/first-slice/live-research-data preflight tests. | Implemented with documented loss boundaries |
| FR-OBS-004 | Core tests and evaluation must run without a network or API key. | Full test suite and deterministic evaluation. | Implemented |

## P0 non-functional requirements

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| NFR-SEC-001 | Bind the prototype only to loopback and document that it has no production authentication. | CLI host guard; security document. | Implemented |
| NFR-SEC-002 | Keep secrets, databases, imported data, raw snapshots, runtime outputs, and exports outside version control. | `.gitignore`; secret scan gate. | Implemented |
| NFR-SEC-003 | Never place raw restricted values in agent trace metadata or application logs. | Stage summaries contain counts/IDs/hashes only. | Implemented |
| NFR-SEC-004 | Render user/source text through React text nodes and explicitly escape generated HTML. | Next.js rendering boundary and export escaping tests. | Implemented |
| NFR-SEC-005 | Benchmark IDs must be namespaced and impossible to attach to operational source snapshots. | Evaluation registry/SourceRegistry guards. | Implemented |
| NFR-REL-001 | Enforce relational foreign keys and uniqueness invariants. | SQLite FK pragma, constraints, migration. | Implemented |
| NFR-REL-002 | Repeat deterministic synthetic evaluation and report consistency. | Three-run comparison. | Implemented |
| NFR-PERF-001 | Measure stage and condition durations without setting an invented performance threshold. | Agent/evaluation duration fields. | Implemented |
| NFR-RES-001 | Separate synthetic engineering evidence, authorised restricted-data evidence, and participant findings. | Evidence map and protocol-only conditions. | Implemented |
| NFR-RES-002 | Prevent tuning leakage through a hashed D0 manifest, protocol-only D1, and application-inaccessible sealed D2. | `evaluation_manifest.json`, loader and sealed-access tests. | D0 implemented; D1/D2 execution held |
| NFR-RES-003 | Report negative and null findings and confidence intervals where the sample supports them. | Analysis plan. | Protocol-only |

## UK public-evidence upgrade requirements

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-CBIT-001 | Encode every nonblank CBIT profile row and distinguish sections, inputs, narratives, held mixed fields, and derived formulas. | `cbit_contract.py`; exhaustive alias/profile tests. | Implemented |
| FR-CBIT-002 | Preserve paired narratives and programme-start membership with cell provenance, aggregate unknown labels once, and never execute formulas. | Synthetic structural twin, invalid/future programme-start tests, and restricted counts-only smoke test. | Implemented |
| FR-SRC-001 | Admit sources through versioned capabilities and fail closed without exact reviewed ID, cutoff, source, mode, or declared fact/event/media contract. | Source registry and connector contract suite. | Implemented offline |
| FR-SRC-002 | Bound GET-only retrieval by allowlist, size, media type, time, attempts, rate, and retry class. | Local transport tests for 404/429/5xx/timeout/oversize/type. | Implemented; no live run |
| FR-TIME-001 | Decide and persist evidence eligibility per run from publication/effective time relative to a UK civil cutoff. | Time/DST/boundary tests plus same-evidence/different-cutoff integration test. | Implemented |
| FR-TIME-002 | Bind cumulative metrics to their declared interval; `since_programme_start` public facts must exactly cover the persisted programme start through the reporting cutoff or abstain. | UKRI window, missing-start abstention, future/pre-programme exclusion, and source-registry contract tests. | Implemented offline |
| FR-QUAL-001 | Persist and display versioned trusted/provenance/time/conflict/missingness outcomes. `no_record`, temporary source unavailability, and terminal source failure must remain distinct warning/warning/hold states rather than silent passes or zeros. | Quality v2 unit/workflow/report terminal-state tests. | Implemented |
| FR-CH-001 | Replay exact-number Companies House identity/status/filing/charge facts without inferring valuation/private funding. | Synthetic connector tests. | Implemented offline; live held by G2 |
| FR-UKRI-001 | Replay exact-organisation UKRI lifecycle, latest corrections, stable event locators, explicit amount/currency coverage, and non-causal association. A grant total is claim-eligible only when every in-window award has a finite explicit GBP amount; otherwise the system records diagnostics/missingness and abstains. | UKRI missing/non-GBP, cross-cutoff replay, and end-to-end claim tests. | Implemented offline |
| FR-DOC-001 | Extract JSON/iXBRL/text with exact locator, sign, scale, currency, period, total/maximum distinction, and abstention. | Adversarial document tests. | Implemented |
| FR-CTX-001 | Produce only compatible-period changes and minimum-N five-number context for the imported portfolio, retaining period semantics/exposure window, definition, N, cutoff, and source versions without claiming an external UK benchmark. Cumulative windows with different programme origins must be segmented or suppressed. | Context/report period-duration and programme-origin tests. | Implemented |
| FR-VIZ-001 | Generate multiple accessible dissertation visuals with source/N/cutoff/text alternative and immutable hash; manifests must be byte-identical across checkout paths. | 15-SVG pack, pathless manifest, relocation determinism, and XML tests. | Implemented synthetic/illustrative |
| FR-EVAL-001 | Report identity/extraction/time/quality/contradiction/provenance/abstention/event/report/reviewer outcomes with explicit nulls. | Evaluation v2 schemas/tests. | D0 automated; human/event empirical outcomes null |

## Company-intelligence first-slice requirements

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-CASE-001 | Persist a company research case pinned to one declared purpose, classification, and immutable core-company-profile template version. | `ResearchCase`, template/version constraints, migration and intake tests. | Implemented offline |
| FR-CASE-002 | Preserve versioned profile records separately from reports so a later Company 360 synthesis cannot overwrite prior approved content. | `ProfileVersion` case/version uniqueness and immutable content hash. | Foundation implemented; synthesis deferred |
| FR-INT-001 | Accept a structurally valid Companies House number without requiring a company name or website, but hold identity until a named decision. | Number-only intake and decision tests, including prefixed numbers. | Implemented offline |
| FR-INT-002 | Accept HTTPS website, name-plus-jurisdiction, and declared-company document inputs as reviewable claims without auto-merging legal identity. | Domain/name/document negative merge and validation tests. | Implemented offline |
| FR-INT-003 | Parse CSV/XLSX bulk rows independently through the same normalized intake contract and fail atomically on malformed input. | Frozen synthetic bulk fixture and atomicity tests. | Implemented offline |
| FR-INT-004 | Fingerprint normalized intake requests and reuse the original artifact/case for exact duplicates. | Duplicate single and bulk intake tests plus unique constraint. | Implemented offline |
| FR-INT-005 | Store uploaded bytes create-once with safe basename, `0600` mode, checksum, classification, purpose, and actor; do not execute or externally process content. | Snapshot mode/hash and fail-closed boundary tests. | Implemented local-only |
| FR-INT-006 | Identifier and domain linkage require configured named accept/reject decisions with substantive rationale, preserving the append-only decision history. | Identifier/domain decision service and route tests. | Implemented local-only |
| FR-C360-001 | Provide a Companies ledger whose counts, identity state, verified domain, case state, artifacts, and next safe action derive from persisted records. | View-model and route tests. | Implemented local-only |
| FR-C360-002 | Provide a Company 360 identity/documents skeleton that distinguishes submitted claims, verified links, holds, and unavailable evidence without inventing facts. | Semantic HTML, empty/error, and persisted-state tests. | Implemented local-only |
| NFR-CI-001 | Keep live retrieval, external models, person-level public data, background workers, production auth/tenancy, and deployment fail-closed in the first slice. | Bootstrap/config negative tests and architecture review. | Implemented boundary |

## Approved live company-research requirements

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-RES-001 | Create an idempotent research run only for a public case with a reviewed Companies House number, pinned cutoff, model, prompt, policy, and budgets. | `test_company_research.py`; revision `0009`. | Implemented |
| FR-RES-002 | Use OpenAI Responses web search for source discovery while preventing search snippets or uncaptured model prose from becoming evidence. | Fake Responses source test and persisted discovery/source states. | Implemented; live smoke unrun |
| FR-RES-003 | Capture discovered pages only through the HTTPS, connection-pinned DNS/IP, redirect, robots, MIME, timeout, and byte-bounded fetcher; retain blocked/unsupported/failed as distinct gaps. | Safe-fetcher and pinned-transport adversarial tests. | Implemented local-only |
| FR-RES-004 | Redact personal contacts before immutable derivative persistence and extraction with `store=False`; reject restricted cases, invalid schemas, tiny/mismatched/post-cutoff spans, prompt injection, personal contacts, and recommendation language. | Classification, redaction, cutoff, and verbatim-span safety tests. | Implemented |
| FR-RES-005 | Persist serial discovery, capture, extraction, and composition tasks with fingerprints, bounded attempts, telemetry, explicit failure, fenced cancellation, and named interrupted-task recovery. | Task/attempt/run interruption and cancellation assertions. | Implemented local synchronous worker boundary |
| FR-RES-006 | Compose a deterministic Company 360 deck from accepted verbatim-span claims only, preserving source URL, perspective, category, contradiction candidates, coverage gaps, limitations, and content hash. | Deck/contradiction/hash/XSS-safe HTML tests. | Implemented |
| FR-RES-007 | Require configured named approval with optimistic locking and content-hash verification before every HTML/JSON deck view or download. | Web review/tamper/download integration test. | Implemented |

## Agent control-room requirements

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-ACR-001 | Project run, company, and portfolio state through a read-only JSON layer that derives no value the database does not hold and reports an unknown denominator as `Not available`, never as zero. | `test_control_room_api.py` closed-gate, hold, and graph projections. | Implemented |
| FR-ACR-002 | Render the execution graph from persisted tasks and source rows, including per-source captured, blocked, unsupported, and failed lanes and their claim linkage. | `test_control_room_api.py` node, lane, and claim-linkage assertions. | Implemented |
| FR-ACR-003 | Apply the existing double-submit CSRF contract and locally configured reviewer identity to every JSON mutation, and refuse a research run while the live gates are closed. | `test_control_room_api.py` CSRF and closed-gate refusals. | Implemented |
| FR-ACR-004 | Preserve named optimistic-locked profile approval through the JSON boundary; a stale lock version must fail. | `test_control_room_api.py` lock-version approval test. | Implemented |
| FR-ACR-005 | Reserve colour, glow, and motion for real execution state, express every state in text as well as colour, and remove all motion under `prefers-reduced-motion` without removing information. | `AgentGraph` reduced-motion gating; rendered desktop and mobile checks. | Implemented |
| FR-ACR-006 | Provide an offline fixture research mode that exercises the real orchestrator, snapshot checksums, exact-span validator, contradiction ledger, and approval gate without a model call or an outbound request, and label every such run as synthetic. | `test_company_research_fixtures.py`; `test_control_room_api.py` fixture run. | Implemented |
| FR-ACR-007 | Route every company-research model call to the approved `gpt-5.6-luna` model with configured `high`/`max` effort: configured effort for first-pass discovery and `high` for selection and correction; choose the route in code, never by model choice, and record the model that actually ran on every attempt. | `test_model_routing.py` route, sent-parameter, and approved-route tests. | Implemented |
| FR-ACR-008 | State the exact-span, cutoff, privacy, perspective, and prohibited-source acceptance rules verbatim in the model briefs. | `test_model_routing.py` brief-content tests. | Implemented |
| FR-ACR-009 | Keep a run readable, reviewable, cancellable, and its approved deck downloadable after the prompt or source-policy version moves on, while refusing to execute a further stage on it. | `test_control_room_api.py` superseded-run and approved-deck tests. | Implemented |
| FR-ACR-010 | Direct source planning toward company identity, financing, customers, partnerships, products, technology, certifications, operating scale, expansion, awards, public performance, and adverse evidence, while retaining the canonical public/mixed CBIT metric definitions in the prompt. | `test_model_routing.py` prompt-contract tests. | Implemented |
| FR-ACR-011 | Present direct metric evidence, related public signals, company-input requirements, bounded-search gaps, contradictions, and source provenance as separate text-labelled visual states in responsive and print-safe HTML. | `test_investment_metrics.py`; `test_company_research.py`; rendered report inspection. | Implemented |

## P1 backlog — deferred until evidence freeze

| ID | Candidate feature | Entry condition |
|---|---|---|
| P1-CON-001 | Execute gated read-only Companies House or other admitted live public retrieval | G2 legal/terms review, exact identifier map, cutoff, credential/storage approval |
| P1-SCH-001 | Scheduled recurring collection | Approved operations model, idempotency, alerting, failure recovery |
| P1-ID-001 | Broader alias adjudication and registry-search assistance | Gold identities, authority, precision study; no auto-merge |
| P1-MET-001 | Versioned catalogue editor and domain sign-off | Catalogue governance owner identified |
| P1-LLM-001 | Run and evaluate the approved live company-research path | Separately authorised live smoke, frozen benchmark, cost/coverage evidence |
| P1-REP-001 | Reviewer comparisons and structured comment threads | User-study design or product need |
| P1-EXP-001 | PDF export | Accessible PDF template and visual QA process |

## P2 exclusions

- Dashboard access or reuse of any supplied credential.
- Production authentication, multi-tenancy, or fine-grained organisation roles.
- Social scraping, unrestricted crawling, autonomous emails/posts/publication.
- Automatic investment recommendations or portfolio-company scoring.
- Fine-tuning, autonomous code execution, or arbitrary tool use by agents.
- Native PPTX/PDF rendering and presentation polish; the approved slice exports printable HTML and evidence JSON.
- Cloud deployment or external storage.

## Definition of done for P0

P0 is done only when:

1. the migration upgrades an empty SQLite database to the model-equivalent schema;
2. formatting, lint, type checking, tests, coverage, and secret scan pass on final state;
3. the fictional vertical slice stops at human review;
4. pre-approval export is proven to fail;
5. explicit test approval produces JSON/Markdown/HTML with provenance and audit history;
6. the synthetic evaluation is repeatable and labelled as synthetic;
7. all required documents and ADRs agree with the implemented system; and
8. empirical/user-study claims remain marked pending.
