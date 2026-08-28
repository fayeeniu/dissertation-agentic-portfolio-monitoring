# Agentic Evidence Control Room

- Mode: ELEVATED
- State: COMPLETE
- Baseline: `production` at `32783b0303778086788cd00e0ee94b88291cec91`; only pre-existing change is untracked user-owned `docs/AGENTIC_DASHBOARD_BUILD_BRIEF.md`
- Policy sources: user-provided `AGENTS.md` instructions; `/Users/oskarrodziewicz/.agents/skills/engineering/SKILL.md`; `docs/AGENTIC_DASHBOARD_BUILD_BRIEF.md`; `docs/ARCHITECTURE.md`; `docs/AGENT_CONTRACTS.md`; `docs/SECURITY_AND_DATA_GOVERNANCE.md`; `docs/WAYFINDER.md`
- Contract: Recompose the existing server-rendered work queue, run trace, and report review routes into a coherent Evidence Control Room derived exclusively from persisted repository state.
- Out of scope: live/SSE execution, background jobs, a free-form graph editor, third-party fonts or assets, fabricated activity, and workflow/data/approval contract changes.
- Acceptance criteria:
  - [x] Every work-queue, run, and report page exposes one truthful next safe action.
  - [x] The run page presents the fixed eight-stage lifecycle as semantic HTML with persisted status, safe summaries, activity, evidence health, and exceptions.
  - [x] Stage summaries allowlist counts and hashes and omit raw values, prompts, source text, and credentials.
  - [x] The report page distinguishes completion, claim support, and named approval while preserving all mutation forms and export gating.
  - [x] Critical content and controls remain keyboard-accessible, no-script complete, high-contrast compatible, reduced-motion safe, and responsive at 390, 820, 1280, and 1440 pixels.
  - [x] Existing web security, reviewer identity, optimistic locking, and export-gate behaviour remains green.
- Risk boundaries: User-facing multi-route UI and persisted-state presentation across the local review boundary; privacy is preserved through explicit safe metadata allowlisting. No auth, schema, migration, dependency, workflow, external API, or deployment changes.
- Approval: AUTO Elevated work does not require a stop; task-scoped local edits and validation were explicitly requested by the user.

## Discovery

- Observations: FastAPI/Jinja server rendering; synchronous eight-stage workflow; `AgentRunModel.metadata_json` contains stage-produced dictionaries; existing UI has no JavaScript; CSP, loopback, CSRF, configured reviewer, lock version, and approval-gated export already exist.
- Inferences: A pure presentation module plus server-side query assembly is the narrowest safe seam. Recorded replay is optional and omitted because the static lifecycle already provides the honest minimum and avoids new CSP/package-data surface.
- Unknowns: Manual empirical usability remains outside the authorised dissertation protocol. Forced-colour and 200% zoom behaviour were assessed structurally but not emulated by the available browser surface.
- Affected callers and boundaries: `create_app()` route contexts, four Jinja templates, semantic CSS, package test suite. Approval/reporting services and database models are invariant.
- Existing proof: `.venv/bin/pytest tests/integration/test_web.py` -> 4 passed, 1 upstream Starlette deprecation warning.

## Packets

1. Persisted-state dashboard view model
   - Writer: primary agent
   - Files or symbols: new `portfolio_agent.dashboard`; `web.py`; focused view-model/integration tests
   - Proof: targeted dashboard and web tests
   - Status: COMPLETE
2. Work queue, control room, and review desk composition
   - Writer: primary agent
   - Files or symbols: `base.html`, `index.html`, `run.html`, `report.html`, `styles.css`
   - Proof: targeted web integration tests and rendered semantic assertions
   - Status: COMPLETE
3. Final verification and rendered validation
   - Writer: primary agent
   - Files or symbols: final state only
   - Proof: relevant package gates, synthetic browser widths/accessibility checks, diff inspection, independent review
   - Status: COMPLETE

## Validation

| Status | Command | Result |
|---|---|---|
| PASSED | `.venv/bin/pytest tests/integration/test_web.py` | Baseline: 4 passed; one known upstream Starlette deprecation warning. |
| PASSED | `.venv/bin/pytest tests/unit/test_dashboard.py tests/integration/test_web.py tests/integration/test_reporting.py tests/integration/test_workflow.py` | Final state: 20 targeted tests passed; one known upstream Starlette deprecation warning. |
| PASSED | `.venv/bin/ruff format --check src tests alembic/versions` | 73 files already formatted. |
| PASSED | `.venv/bin/ruff check src tests alembic/versions --output-format concise` | All checks passed. |
| PASSED | `.venv/bin/mypy src` | No issues in 39 source files. |
| PASSED | `.venv/bin/pytest --cov=portfolio_agent --cov-report=term-missing` | Final state: 182 passed; 86.35% coverage; 19 known upstream/SQLite deprecation warnings. |
| PASSED | `PORTFOLIO_*=<fresh /private/tmp paths> .venv/bin/portfolio-agent demo` | Fresh migrations reached 0007; the unchanged workflow stopped at `pending_review` with 13 supported and 2 insufficient-evidence claims. An earlier repeat demo also passed idempotently. |
| PASSED | `node --check src/portfolio_agent/static/control-room.js` | The local stage-inspector enhancement is syntactically valid. |
| PASSED | `node /private/tmp/control-room-behavior-check.mjs` | Dependency-free DOM proof passed initial fragment/mobile placement, wide-to-narrow restoration, ordinary activation, reduced-motion scrolling, hash changes, and native modified-click handling. |
| PASSED | In-app Browser responsive matrix at 390x844, 820x1180, 1280x800, and 1440x900 | Work queue, run, and report pages had `scrollWidth == clientWidth`; visible buttons were at least 49px high; 8 semantic stage links and 8 inspectors rendered; no browser console warnings/errors. |
| PASSED | Rendered screenshot review with synthetic data | Reviewed work queue, desktop/tablet/mobile control room, horizontal/vertical rails, report context, and bounded decision dock; fixed provider overflow, mobile report overflow, outline wrapping, and human-checkpoint truth mapping. |
| PASSED | `git diff --check` | Clean before final review handoff. |
| BLOCKED | Final in-app Browser click proof after review fixes | The local server was healthy and reachable by `curl`, but two fresh app-browser tabs rejected both loopback spellings with `ERR_BLOCKED_BY_CLIENT`. Tabs were closed and the viewport reset. The previous responsive matrix remains valid for the unchanged layout; direct activation is covered by external-script markup, CSP/package-data assertions, syntax checking, and independent source review. |

## Review

- Reviewer: engineering reviewer `dashboard_final_review`
- Cycle 1 exact state: reviewed before the five fixes below.
- Cycle 1 findings and disposition:
  1. P2 stage nodes did not directly open their inspector: fixed with a same-origin external enhancement, semantic anchor fallback, default-open no-script state, and narrow-layout inline placement.
  2. P2 queue labels described incomplete or failed runs as complete: fixed with persisted-status-specific action derivation and tests.
  3. P2 pending-report exception action targeted the decision dock: fixed to target claim/evidence inspection first, with tests.
  4. P2 health groups showed empty zero scaffolding and hid unknown states: fixed to render empty state and explicit status-unavailable rows, with exact-denominator tests.
  5. P2 full identifiers were available only through pointer hover: fixed by placing full IDs and hashes in DOM text with visual ellipsis only.
- Cycle 2 findings and disposition:
  1. P2 initial/deep-link mobile inspector placement: fixed by selecting the fragment or initial inspector during enhancement, placing it on initialization and media changes, preserving native modified-click behavior, and handling hash changes.
  2. P2 report action omitted quality/source exception targets: fixed by linking to the run exception ledger that contains every counted category.
  3. P2 activation ignored reduced motion: fixed with an explicit reduced-motion media query and immediate scrolling.
- Exact final state reviewed: yes. The same independent reviewer found no actionable P0, P1, or P2 findings after the second permitted review/fix/re-review cycle.
- Residual risks: forced-colour and 200% zoom remain structurally assessed rather than emulated; the app-browser direct click rerun was blocked as recorded above, with dependency-free DOM behavior proof used instead.
- Handoff: implementation complete; no commit or push requested.

## OpenAI synthetic smoke follow-up

- Outcome: COMPLETE. The exact documented `openai-smoke --acknowledge-synthetic-only` command now
  reads only `OPENAI_API_KEY` from a private ignored `.env` when the process environment does not
  provide it, uses isolated private database/raw/source state, and executes one checksum-pinned
  synthetic extraction inside the fixed eight-stage workflow. The persisted runtime can be opened
  with the emitted `serve_command` without touching `var/portfolio.db`.
- Guardrails: the default runtime remains deterministic; live public retrieval remains false;
  restricted/internal evidence is prohibited; one validation escalation maximum; 512 output-token
  cap; `store=False`; strict OpenAI schema; independent exact-value grounding; human review remains
  the terminal state; the local key is removed from process state after the command.
- Corrections made during live proof: normalize the Pydantic schema to OpenAI's all-fields-required
  strict subset while retaining nullable unions, and state the exact scalar grounding contract in
  prompt version `extract-public-evidence-v4`.
- Live proof: `run_8923757de2d041de9c88f7460c957b39`, one successful
  `gpt-5.4-mini-2026-03-17` attempt, 449 input tokens, 79 output tokens, strict extraction persisted,
  report `rep_4656b0933bad45948ea6b501637cf016` stopped at `pending_review`; content-free manifest SHA-256
  `864984ba092f6dac5c07bc57f2f27d5816a9aa216fa67da0a55c3d0a71aea4af`. The persisted work queue,
  run trace, and report routes each returned HTTP 200; the run rendered seven completed stages and
  a final `Needs human review` stage.
- Final validation: Ruff format check passed (75 files); Ruff lint passed; mypy passed (41 source
  files); pytest passed (189 tests, 86.73% coverage, 19 known upstream/SQLite warnings);
  `git diff --check` and the control-room JavaScript syntax check passed; `.env` mode verified as
  `0600`.
- Evidence boundary: G4 remains open. This smoke proves connectivity and strict persistence only;
  it does not establish model quality, portfolio performance, retention, or monetary cost.
- Handoff: no commit or push requested.
