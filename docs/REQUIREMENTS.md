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
| FR-MET-002 | Metric definitions must specify key, label, category, data type, unit, sourceability, aliases, and description. | Pydantic/SQLAlchemy contracts. | Implemented |
| FR-MET-003 | Blank, zero, none stated, N/A, not reported, not found publicly, invalid, and observed must remain distinct. | `MissingState` and parameterised tests. | Implemented |
| FR-MET-004 | Integer metrics must reject fractional values rather than rounding. | `non_integral_count` normalization issue. | Implemented |
| FR-MET-005 | Percentage-point values must not be silently scaled from ratios. | Values are retained as entered within 0–100; test documents rule. | Implemented |
| FR-MET-006 | Currency values must retain explicit ISO currency; no currency may be guessed. | Symbol/code parser; `currency_missing` issue. | Implemented |
| FR-MET-007 | Unknown or ambiguous labels must be reported and not silently mapped. | Unknown-metric warning and alias collision protection. | Implemented |

### Company identity resolution

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-ID-001 | Resolve a company by exact external identifier when supplied, then exact normalized name. | Deterministic resolver. | Implemented |
| FR-ID-002 | Do not fuzzy-merge companies automatically. | No fuzzy matcher exists in P0. | Implemented |
| FR-ID-003 | Conflicting identifier/name pairs must enter an ambiguity hold and skip affected observations. | Ambiguity integration test. | Implemented |
| FR-ID-004 | A workflow must stop before collection if any included company remains ambiguous. | Resolve stage invariant. | Implemented |

### Sourceability and connectors

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-CON-001 | Classify metrics as publicly sourceable, internal-only, mixed, or derived. | Catalogue and data dictionary. | Implemented |
| FR-CON-002 | Use a connector protocol independent of extraction and verification. | `Connector.collect(ConnectorQuery)`. | Implemented |
| FR-CON-003 | Connector evidence must include source type, locator, publisher, retrieval/publication times, checksum, version, classification, and trust state. | Strict `EvidenceItem`. | Implemented |
| FR-CON-004 | P0 must run without network access using fictional evidence fixtures. | Fixture connector and tests. | Implemented |
| FR-CON-005 | A missing public result must remain missing; it must not be inferred from company text or model priors. | No-evidence verification state; protocol cases. | Implemented |
| FR-CON-006 | Evidence gathered for one run must be explicitly associated with that run. | `run_evidence` association. | Implemented |

### Extraction, normalization, and optional models

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-EXT-001 | Apply deterministic structured extraction before considering an LLM. | Default deterministic provider. | Implemented |
| FR-EXT-002 | Every extraction must satisfy a strict typed schema and expected company/metric identity. | `StrictExtraction`; identity checks. | Implemented |
| FR-EXT-003 | Keep extracted and normalized values separate and preserve provider/schema version. | `Extraction` model. | Implemented |
| FR-EXT-004 | Reject instruction-like/untrusted evidence before extraction or model processing. | Injection detector; workflow and security tests. | Implemented |
| FR-EXT-005 | External model use must be opt-in, limited to public/synthetic evidence, use `store=False`, and use bounded attempts. | OpenAI provider policy gates. | Implemented, not externally exercised |
| FR-EXT-006 | Model routing must default to `gpt-5.4-mini` and escalate once to `gpt-5.4` only after strict-validation failure. | Settings and provider adapter. | Implemented, not externally exercised |
| FR-EXT-007 | Model name, attempts, tokens, and errors must be observable; unknown monetary cost must remain null. | Agent/extraction records; no invented pricing. | Implemented |

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
| FR-REP-001 | Compose a deterministic report with executive summary, company sections, verification outcomes, data quality, and limitations. | Composer and UI. | Implemented |
| FR-REP-002 | Supported narrative must exclude contradicted/insufficient claims while showing their states as exceptions. | Composer rules. | Implemented |
| FR-REP-003 | Report and section versions must be preserved; edits create new section versions. | Edit service and test. | Implemented |
| FR-REP-004 | Approve, reject, and edit decisions must record named actor, rationale, report version, and time. | `ReviewDecision`. | Implemented |
| FR-REP-005 | Export must fail unless the current report version has explicit approval. | Report-state test. | Implemented |
| FR-REP-006 | Post-approval export must produce versioned JSON, Markdown, and accessible HTML. | End-to-end test. | Implemented |
| FR-REP-007 | Editing an approved report must revoke approval and require re-review. | Edit transition and test. | Implemented |

### Interface, observability, and reproducibility

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| FR-UI-001 | Provide server-rendered, keyboard-operable pages for import, run trace, report review, decisions, and downloads. | FastAPI/Jinja views and web tests. | Implemented |
| FR-UI-002 | Communicate state in text, not colour alone, with labels, captions, semantic headings, and skip navigation. | Templates/CSS and static inspection. | Implemented; formal accessibility audit pending |
| FR-OBS-001 | Give every dataset, workflow, agent action, evidence item, extraction, claim, report, and review a stable ID. | Data model. | Implemented |
| FR-OBS-002 | Retain input/output hashes, duration, attempts, provider/model, tokens, errors, and bounded metadata. | Agent ledger. | Implemented |
| FR-OBS-003 | Pin runtime and development dependency versions and provide an explicit database migration. | `pyproject.toml`; Alembic `0001`. | Implemented |
| FR-OBS-004 | Core tests and evaluation must run without a network or API key. | Full test suite and deterministic evaluation. | Implemented |

## P0 non-functional requirements

| ID | Requirement | Acceptance evidence | Status |
|---|---|---|---|
| NFR-SEC-001 | Bind the prototype only to loopback and document that it has no production authentication. | CLI host guard; security document. | Implemented |
| NFR-SEC-002 | Keep secrets, databases, imported data, raw snapshots, runtime outputs, and exports outside version control. | `.gitignore`; secret scan gate. | Implemented |
| NFR-SEC-003 | Never place raw restricted values in agent trace metadata or application logs. | Stage summaries contain counts/IDs/hashes only. | Implemented |
| NFR-SEC-004 | Auto-escape user/source text in the UI and generated HTML. | Jinja auto-escape and explicit HTML escaping. | Implemented |
| NFR-REL-001 | Enforce relational foreign keys and uniqueness invariants. | SQLite FK pragma, constraints, migration. | Implemented |
| NFR-REL-002 | Repeat deterministic synthetic evaluation and report consistency. | Three-run comparison. | Implemented |
| NFR-PERF-001 | Measure stage and condition durations without setting an invented performance threshold. | Agent/evaluation duration fields. | Implemented |
| NFR-RES-001 | Separate synthetic engineering evidence, authorised restricted-data evidence, and participant findings. | Evidence map and protocol-only conditions. | Implemented |
| NFR-RES-002 | Prevent training/evaluation leakage by freezing catalogue, prompts/rules, labels, and final OOS set before access. | Evaluation protocol; empirical execution pending. | Protocol-only |
| NFR-RES-003 | Report negative and null findings and confidence intervals where the sample supports them. | Analysis plan. | Protocol-only |

## P1 backlog — deferred until P0 evidence freeze

| ID | Candidate feature | Entry condition |
|---|---|---|
| P1-CON-001 | Read-only live public connectors such as a public funding registry and curated news API | Legal/ToS review, connector-specific fixtures, rate limits, provenance tests |
| P1-SCH-001 | Scheduled recurring collection | Approved operations model, idempotency, alerting, failure recovery |
| P1-ID-001 | Human-assisted alias/registry identity management | Gold identities and reviewer workflow |
| P1-MET-001 | Versioned catalogue editor and domain sign-off | Catalogue governance owner identified |
| P1-LLM-001 | Execute the opt-in OpenAI path on public/synthetic evidence | Budget, data approval, frozen prompt/schema, API integration tests |
| P1-REP-001 | Reviewer comparisons and structured comment threads | User-study design or product need |
| P1-EXP-001 | PDF export | Accessible PDF template and visual QA process |

## P2 exclusions

- Dashboard access or reuse of any supplied credential.
- Production authentication, multi-tenancy, or fine-grained organisation roles.
- Social scraping, unrestricted crawling, autonomous emails/posts/publication.
- Automatic investment recommendations or portfolio-company scoring.
- Fine-tuning, autonomous code execution, or arbitrary tool use by agents.
- Slide-deck generation and presentation polish.
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

