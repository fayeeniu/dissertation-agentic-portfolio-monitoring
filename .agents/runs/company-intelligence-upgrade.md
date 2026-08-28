# Company Intelligence Upgrade

- Mode: CRITICAL
- State: COMPLETE — first offline slice and approved bounded live-research slice implemented
- Baseline: `production` at `32783b0303778086788cd00e0ee94b88291cec91`; the checkout already contains 19 modified tracked files and 13 untracked files from the completed Evidence Control Room/OpenAI smoke work plus the user-provided upgrade plan. These changes are preserved and treated as the live baseline, not rewritten or discarded.
- Policy sources: user-provided `AGENTS.md`; `/Users/oskarrodziewicz/.agents/skills/engineering/SKILL.md`; `docs/COMPANY_INTELLIGENCE_UPGRADE_PLAN.md`; `docs/ARCHITECTURE.md`; `docs/SECURITY_AND_DATA_GOVERNANCE.md`; `docs/SOURCE_ADMISSION_REGISTER.md`; `docs/REQUIREMENTS.md`; `docs/IMPLEMENTATION_TRACEABILITY.md`
- Contract: Progressively add a local, evidence-first company research case with hybrid intake and Company 360 views while preserving exact identity review, immutable provenance, explicit contradictions, model/data separation, named human approval, and all existing import/run/report routes.
- Out of scope for the first approved implementation slice: live network retrieval; G2 admission; external-model calls; public officer/PSC or other person-level collection; durable workers, queues, leases, parallel execution, background jobs, or cancellation; production auth/RBAC/tenancy/deployment; broad public-source packs; embeddings/vector storage/OCR; automated publication; commercial aggregators; dependency additions/upgrades; mutable-environment migrations.
- Acceptance criteria for the first implementation slice:
  - [x] A Companies House number alone can create an unresolved local company research case without requiring a name or website.
  - [x] Website-only, name-plus-jurisdiction, uploaded-document, and CSV/XLSX bulk rows create independently reviewable intake artifacts and never auto-merge an identity.
  - [x] Existing exact identifier decisions remain authoritative; domain linkage requires a named decision and preserves history.
  - [x] Research case, intake artifact, company-domain, research-template/version, and profile-version records are migration-backed, typed, and replay-safe.
  - [x] Duplicate intake is idempotent under an explicit immutable request fingerprint.
  - [x] Existing import, workflow-run, report-review, approval, and export behaviour remains compatible.
  - [x] A server-rendered Companies ledger and Company 360 identity/documents skeleton expose blockers and the next safe human action from persisted state.
  - [x] Live retrieval and external-model routing remain fail-closed.
- Risk boundaries: Critical because the programme includes schema migration/persisted identity semantics, privacy/public-person data, outbound fetch/SSRF, durable concurrency, and future auth/deployment. The proposed first slice deliberately excludes the network, personal-data, concurrency, auth, external-model, and deployment boundaries; its remaining Critical surface is migration and persisted identity integrity.
- Approval: GRANTED by the user on 2026-08-27 for the first implementation slice, the seven decisions below, the stated recovery and validation/review plan, and no external actions. Later phases require new material-change review and, where Critical, a renewed approval gate.

## Proposed approval decisions

1. First release remains local, single-user, loopback-only, synchronous, and SQLite-backed.
2. The first slice is fixture/offline only. Companies House and first-party website live retrieval remain G2-held; no network smoke is authorised.
3. Store company-level facts only. Do not collect or persist officer, PSC, trustee, personal contact, or sensitive-person data in this slice.
4. External-model use remains public/synthetic-only in principle and disabled for this slice; restricted/internal uploads never cross that boundary.
5. The first research objective is the core company profile template.
6. Commercial/secondary aggregators and all additional source packs remain excluded.
7. Existing uncommitted dashboard/OpenAI-smoke work is user-owned live baseline. New changes must layer on it without resetting, stashing, committing, or rewriting it.

## Recovery boundary

- Add one forward Alembic revision after `0007`; exercise upgrade and downgrade only on disposable temporary databases before any normal local database is touched.
- Preserve current tables and routes; use additive nullable/defaulted fields and new tables. No rename/drop or inferred backfill in this slice.
- A failed upgrade must leave the prior schema usable; a downgrade must remove only records/tables introduced by this slice and must fail closed if that cannot be guaranteed.
- No external action, live-source request, production/shared mutation, dependency install, commit, push, deployment, or release is authorised.

## Discovery

- Observations:
  - Current runtime is a local FastAPI/Jinja, synchronous SQLite application with Alembic revisions `0001` through `0007`.
  - Existing identity resolution uses exact identifiers and explicit decisions; name ambiguity stops the workflow.
  - Existing source registry supports immutable snapshots and exact source keys, while all live public retrieval remains G2-held.
  - Current work queue/run/report UI changes are uncommitted and overlap `web.py`, templates, CSS, bootstrap, tests, and documentation.
  - The upgrade plan itself labels API names as planning-level contracts and lists six decisions that materially change implementation authority.
- Inferences:
  - The smallest coherent executable slice is Phase 1's offline company-case/hybrid-intake foundation, not the full seven-phase programme.
  - Preserving synchronous fixture replay and existing routes avoids falsely presenting request-bound SQLite execution as durable parallelism.
  - Live-source admission cannot be inferred from public documentation; named reviewer purpose, retention, attribution, correction/deletion, and licence decisions are external prerequisites.
- Unknowns:
  - Named business-purpose/retention authority for public personal data.
  - Approval to admit Companies House and first-party website access under G2.
  - Desired hosted deployment, if any, and its auth/tenancy/storage design.
  - Whether the currently uncommitted Evidence Control Room work will be committed separately; implementation can preserve it but cannot manufacture a clean immutable baseline.
- Affected callers and boundaries:
  - `models.py`, Alembic schema, identity/import services, `create_app()` routes and CSRF/loopback boundary, Jinja view models/templates, workflow/report compatibility, bootstrap live-source/model gates, repository requirements/traceability.
- Existing proof:
  - The completed Evidence Control Room ledger records 189 tests and its package gates passing on the current uncommitted work; this is historical evidence and will be refreshed before implementation.

## Packets

1. Freeze first-slice contracts and executable acceptance fixtures
   - Writer: primary agent only
   - Files or symbols: requirement/data/security/ADR/traceability documents; fixture manifests and focused contract tests only
   - Proof: requirement-link audit, fixture hash check, focused contract tests
   - Stop condition: any request to admit live retrieval, person-level data, external models, or hosted deployment
   - Status: COMPLETE
2. Additive persistence foundation
   - Writer: primary agent only
   - Files or symbols: ORM models; Alembic `0008`; typed enums/domain records; migration/schema tests
   - Proof: upgrade from `0007`, schema equivalence, disposable downgrade/upgrade, model invariant tests
   - Stop condition: destructive migration, inferred backfill, incompatible existing route/workflow semantics, or unclear ownership of an overlapping edit
   - Status: COMPLETE
3. Hybrid intake service and compatibility layer
   - Writer: primary agent only
   - Files or symbols: intake validation/service; exact identity/domain decisions; file/bulk adapters; focused tests
   - Proof: CH-number-only, URL, document, name/jurisdiction, bulk, malformed, duplicate, no-auto-merge, classification/MIME/size tests
   - Stop condition: network access, fuzzy merge, archive/malware capability requiring a new dependency, or restricted-data boundary change
   - Status: COMPLETE
4. Local API/UI vertical slice
   - Writer: primary agent only
   - Files or symbols: additive FastAPI routes/view models; Companies ledger; Company 360 identity/documents skeleton; CSS/templates; integration/UI tests
   - Proof: CSRF/Host/client/optimistic decision tests, current-route regression tests, semantic/keyboard/mobile/empty/error rendering checks
   - Stop condition: production auth/tenancy, background execution, or browser/live-source requirement
   - Status: COMPLETE
5. Final compatibility and proof gate
   - Writer: primary agent; independent reviewer remains read-only
   - Files or symbols: exact final state only
   - Proof: all narrow acceptance tests, migration gate, format/lint/mypy/full pytest coverage, deterministic replay/hash, `git diff --check`, complete diff/status review
   - Stop condition: unresolved P0/P1/P2 review finding, failed compatibility proof, or material contract drift
   - Status: COMPLETE

## Remaining programme phases (not yet authorised)

- Phase 2 remainder: direct Companies House and first-party website connectors remain held pending source-specific G2 decisions; the approved live slice admits only OpenAI URL discovery plus guarded public-page capture.
- Phase 3: durable task DAG/worker, only after a separate persistence/concurrency architecture and recovery approval.
- Phase 4: document intelligence/model-assisted synthesis, only after format dependencies, malware/OCR, retrieval, and model-boundary evaluation are approved.
- Phase 5: one source pack at a time after source-specific admission and incremental-value proof.
- Phase 6: hosted production and monitoring only after a separate auth/tenancy/privacy/operations programme.

## Validation

| Status | Command | Result |
|---|---|---|
| PASSED | `.venv/bin/pytest --cov=portfolio_agent --cov-report=term-missing` | Current dirty-state baseline: 196 tests passed with 86.99% coverage and 19 known Starlette/SQLite deprecation warnings. |
| PASSED | `.venv/bin/ruff format --check src tests alembic/versions` | Current dirty-state baseline: 75 files already formatted. |
| PASSED | `.venv/bin/ruff check src tests alembic/versions --output-format concise` | Current dirty-state baseline: all checks passed. |
| PASSED | `.venv/bin/mypy src` | Current dirty-state baseline: no issues in 41 source files. |
| PASSED | `git status --short` and `git diff --stat` | Exact dirty baseline captured before task edits; no production edit made by this task. |
| PASSED | `.venv/bin/pytest tests/integration/test_company_intelligence_migration.py tests/integration/test_schema_equivalence.py` | Revision `0008` additive preservation, metadata equivalence, empty downgrade/re-upgrade, and populated fail-before-mutation proof passed. |
| PASSED | `.venv/bin/pytest tests/integration/test_company_intelligence.py` | Number/URL/name/document/CSV/XLSX, idempotency, no-auto-merge, decision, MIME/archive, and local snapshot contract passed. |
| PASSED | `.venv/bin/pytest tests/integration/test_company_intelligence_web.py tests/integration/test_web.py` | New and existing CSRF/reviewer/security/routes plus persisted Companies and Company 360 rendering passed. |
| PASSED | `.venv/bin/pytest tests/unit/test_documentation_traceability.py tests/integration/test_company_intelligence.py tests/integration/test_company_intelligence_migration.py tests/integration/test_company_intelligence_web.py tests/integration/test_schema_equivalence.py tests/integration/test_web.py` | Combined packet proof: 25 tests passed with three known upstream/SQLite warnings. |
| PASSED | `shasum -a 256 fixtures/company_intelligence_intakes.json` | Frozen synthetic intake fixture hash is `4c474e7fff4898df87e727156c710d0928b1fe747d230fa804a6c819b57d9cbb`. |
| PASSED | `.venv/bin/pytest tests/integration/test_company_intelligence_web.py tests/integration/test_company_intelligence.py -q` | Final focused proof: 21 tests passed, including write-phase fsync cleanup, candidate-scoped authority, accepted-case synchronization, established-target rejection, and multiple-candidate hold projection. |
| PASSED | `.venv/bin/pytest --cov=portfolio_agent --cov-report=term-missing` | Exact final implementation state: 221 tests passed, 86.95% total coverage, and 22 known Starlette/SQLite deprecation warnings. |
| PASSED | `.venv/bin/ruff format --check src tests alembic/versions` and `.venv/bin/ruff check src tests alembic/versions --output-format concise` | 80 files formatted; all lint checks passed. |
| PASSED | `.venv/bin/mypy src` | No issues in 42 source files. |
| PASSED | `PORTFOLIO_DATABASE_URL=<disposable SQLite URL> .venv/bin/alembic upgrade head` followed by `alembic check` | Fresh disposable database upgraded through `0008`; no metadata drift or new upgrade operations detected. |
| PASSED | `PORTFOLIO_DATABASE_URL=<disposable SQLite URL> ... .venv/bin/portfolio-agent demo` | Existing deterministic import/run/report path completed to `human_review`; no automatic approval or export occurred. |
| PASSED | `.venv/bin/portfolio-agent visualize --output <disposable path>` | 15 deterministic figures and a manifest were generated without browser/static-export execution. |
| PASSED | In-app Browser at 1440x1000 and 390x844 against disposable loopback databases | Companies intake, candidate-scoped and standalone Company 360 identity holds, configured named accept and reject decisions, persisted rationale/history, resolved and closed-rejection transitions, G2-held research state, and accessible text states rendered correctly; remediated mobile `scrollWidth` 375 at `innerWidth` 390, no stale decision form, and no browser warnings/errors. |
| PASSED | `git diff --check` | No whitespace errors in the exact state frozen for review. |

## Review

- Review cycle 1: engineering reviewer and Critical migration/data-integrity risk reviewer both returned FAIL on the pre-remediation state. Unique findings were lossy downgrade of populated company metadata (P1); orphaned document bytes on failed commit (P1); semantic template tamper not detected (P1); MIME-equivalent duplicate intake (P2); bypass of the existing identity-candidate authority (P1); stale identifier/domain overwrite plus rejected-as-pending rendering (P2); and unbounded/materialized bulk XLSX parsing (P2).
- Remediation: downgrade now preflights all added state; newly created checksum-matching snapshots are removed on transaction failure; persisted template semantics are rehashed; MIME is normalized before persistence/fingerprinting; legacy candidate decisions remain authoritative and are rendered in Company 360; identifier/domain decisions are single-final; rejected identifiers are closed; and bulk XLSX uses archive, row, and column bounds with streaming row iteration.
- Review cycle 2: the repeat reviewers found that the first authority bridge still aggregated candidate decisions and could revoke an established reviewed target on claimant rejection (P1), while candidate acceptance through the existing queue did not synchronize first-slice case/lifecycle state (P1). The risk reviewer also reproduced an orphan when write/fsync/chmod failed before snapshot creation returned (P1).
- Final correction: legacy decisions are now rendered and submitted one candidate at a time through the existing candidate route; candidate projection is scoped to the imported company, a rejected claimant never mutates its proposed authoritative target, candidate/company/case readiness is derived from all remaining candidate decisions, and exclusive snapshot creation removes partial bytes on any pre-return failure. Resolved legacy companies without a first-slice case now truthfully show `No research case`.
- Cycle-2 targeted confirmation: the engineering reviewer passed the candidate-scoped authority correction. The risk reviewer confirmed target rejection and write-phase cleanup, then found one remaining multi-candidate projection P1; that invariant is now derived from the full remaining projection and covered by an accepted-plus-pending hold test.
- Reviewer: engineering reviewer and Critical migration/data-integrity risk reviewer completed the cycle-2 targeted confirmation on the exact final implementation state.
- Exact final state reviewed: yes; both reviewers returned PASS after the final multi-candidate correction.
- Findings: no open in-scope P0/P1/P2. All cycle-1 and cycle-2 findings have focused regression coverage.
- Residual risks: all later-phase privacy, SSRF, concurrency, auth, source-admission, and deployment risks remain explicitly held.
- Handoff: Approved first slice is complete. Any change to the seven decisions or recovery/external-action boundary, or work on a later programme phase, must revise this ledger and stop for renewed approval before edits.

## Approved live-search and cited-deck slice — 2026-08-27

- Material-change approval: GRANTED by the user on 2026-08-27 for the seven decisions proposed in the follow-up approval packet.
- Outcome: A reviewed Companies House number can seed a real, bounded OpenAI web-search research run whose discovered URLs are independently collected, immutably captured, model-extracted into exact-span claims, deterministically composed into a Company 360 deck, and held for named human review.
- Scope boundary:
  1. Keep the release local, loopback-only, single-user, and SQLite-backed.
  2. Require a reviewed Companies House number before live research; never resolve identity from a name-only search result.
  3. Use OpenAI Responses web search for public-source discovery and bounded public-text extraction only.
  4. Permit only public company-level material across the model boundary; keep restricted/internal uploads and person profiling excluded.
  5. Treat search URLs as discovery candidates until a policy-controlled HTTPS fetch creates immutable source evidence; search snippets and unsupported model prose are not evidence.
  6. Compose the deck only from exact-span validated claims and expose coverage, failures, contradictions, and limitations; do not produce buy/sell advice, target prices, or speculative valuations.
  7. Persist budgeted tasks, attempts, hashes, failures, cancellation, token/tool-call telemetry, and named profile review before export.
- Source-policy boundary: this slice admits a versioned local-research `openai_web_search` discovery capability and bounded public-web page capture. It does not admit forms, authentication, paywall/CAPTCHA bypass, arbitrary code, commercial-platform scraping, personal-contact retention, or reuse of search snippets as evidence. Publisher-specific blocked/unsupported pages remain explicit coverage gaps.
- OpenAI data boundary: `store=False`; public company number/name/query text and bounded public page text only; API credentials remain environment-only; default provider retention limitations remain documented and are not represented as ZDR unless the account is actually approved/configured for it.
- Execution boundary: synchronous one-stage-at-a-time advancement over persisted tasks. No background process, fan-out worker pool, or fabricated parallel activity.

### Recovery boundary for the live-search slice

- Add one forward Alembic revision after `0008`; validate upgrade/downgrade only against disposable databases. Downgrade must fail before mutation if new research state exists.
- New runtime capabilities stay fail-closed unless live retrieval and external LLM flags are both enabled, a reviewer identity is configured, an API key is present, the case is public, and exact Companies House identity is reviewed.
- Each stage has an immutable request fingerprint, one accepted output, bounded attempts, explicit failure state, and a cancellation gate between stages.
- New source bytes use create-once checksum paths; database or write failures remove only files created by the failed attempt.
- No live company run, production/shared mutation, commit, push, deployment, or release is authorised by implementation approval. A live smoke remains a separately visible user action.

### Live-search packets

1. Contract, policy, schema, and migration
   - Status: COMPLETE
   - Proof: documentation traceability, metadata equivalence, disposable upgrade/downgrade, populated downgrade preflight
2. Guarded OpenAI discovery and public fetch boundary
   - Status: COMPLETE
   - Proof: fake Responses client, URL/source extraction, SSRF/DNS/redirect/robots/MIME/byte/prompt-injection tests, no secret or restricted-data persistence
3. Persisted research tasks, claims, deck profile, and named review
   - Status: COMPLETE
   - Proof: idempotency, resume/retry/cancel, exact-span validation, unsupported-claim rejection, deterministic deck/hash, review lock
4. Company 360 controls and evidence/deck presentation
   - Status: COMPLETE
   - Proof: CSRF/Host/reviewer gates, accessible states, coverage/failure rendering, no automatic external call on page load
5. Final proof and independent exact-state review
   - Status: COMPLETE
   - Proof: focused tests, migration gate, lint/format/mypy/full pytest/coverage, diff check, no in-scope P0/P1/P2

### Live-search validation and review

| Status | Command or review | Result |
|---|---|---|
| PASSED | `.venv/bin/pytest tests/integration/test_company_research.py tests/integration/test_company_research_migration.py tests/integration/test_company_intelligence.py tests/integration/test_company_intelligence_web.py tests/integration/test_llm_boundary.py tests/integration/test_web.py tests/integration/test_schema_equivalence.py -q` | Final focused research, migration, compatibility, web, and model-boundary gate passed. |
| PASSED | `PORTFOLIO_DATABASE_URL=<fresh disposable SQLite URL> .venv/bin/alembic upgrade head` and `alembic check` | Fresh database upgraded from `0001` through `0009`; no metadata drift or pending upgrade operation was detected. |
| PASSED | `.venv/bin/ruff format --check src tests alembic/versions`; `.venv/bin/ruff check src tests alembic/versions`; `.venv/bin/mypy src` | Formatting, lint, and typing gates passed on the final implementation state. |
| PASSED | `.venv/bin/pytest --cov=portfolio_agent --cov-report=term-missing` | Exact final implementation state: 244 tests passed with 85.27% total coverage and 22 known Starlette/SQLite deprecation warnings. |
| PASSED | `git diff --check` | No whitespace errors in the final implementation state. |
| NOT RUN | Live OpenAI/company research smoke | Intentionally omitted under the approved no-external-actions boundary; no empirical completeness, quality, latency, cost, or live-source-access claim is made. |

- Review cycle 1 found recovery/finalization races, cross-run snapshot cleanup, export hash bypass, weak span/cutoff grounding, personal-contact persistence, missing contradiction surfacing, and DNS rebinding exposure. These were remediated with named recovery, ownership fences, source-owned redacted derivatives, validated exports, exact substantive verbatim spans, explicit contradiction candidates, and IP-pinned TLS transport.
- Review cycle 2 found encoded-contact and same-year date bypasses plus stale-attempt and config-drift integrity defects. These were remediated with decoded visible-text redaction, multi-format cutoff parsing, attempt-generation fencing, and persisted/fingerprinted budget replay.
- Final exact-state review found and then verified corrections for run/task contract tamper, retry-inclusive model-call accounting, rejected/schema-invalid response telemetry, zero-redirect replay, and discovery output-token budget enforcement.
- Independent engineering reviewer: PASS; no open in-scope P0/P1/P2.
- Independent migration/data-integrity reviewer: PASS; no open in-scope P0/P1/P2.
- Residual boundary: the implementation remains local, synchronous, loopback-only, public-company-only, and human-reviewed. Direct source connectors, hosted workers/auth/tenancy, native PPTX/PDF, live empirical evaluation, and automated publication remain outside this approval.
