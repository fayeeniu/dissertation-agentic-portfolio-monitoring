# Make the Next.js control room the Docker default

- Mode: ELEVATED
- State: COMPLETE
- Baseline: `production` at `6356aa49cb3b4fe47955aab9e81a8e1a05ec9693`; substantial pre-existing dissertation, configuration, model-routing, and generated-artifact changes are outside this task and must be preserved.
- Policy sources: supplied repository `AGENTS.md`; `dashboard/AGENTS.md`; `dashboard/CLAUDE.md`; requested `engineering` AUTO skill and its Elevated/UI references.
- Contract: `docker compose up --build --wait` builds and opens the Next.js control room as the only dashboard on the configured loopback port, while FastAPI remains a private Compose backend for JSON API and approved deck downloads.
- Out of scope: dashboard redesign; API/business-rule changes; authentication or hosted deployment; dependency upgrades; migration or data-model changes; external calls; Git delivery.
- Acceptance criteria:
  - [x] Compose builds the Next.js dashboard as the default loopback-published service; the complete stack built and reached healthy state.
  - [x] The Next.js server-side proxy is configured for private `api:8000`; only the Next service is host-published.
  - [x] The original Jinja dashboard assets and routes are removed; focused tests retain the API, health check, and approved deck download.
  - [x] Configuration retains read-only filesystems, non-root images, dropped capabilities, named-volume state, runtime-only secret injection, and local-only publication; runtime inspection confirms both containers and the private API port boundary.
  - [x] Setup and architecture documentation describe the single Docker command and Next.js default.
- Risk boundaries: operational Docker topology changes from one Python service to a Next.js frontend plus private Python API; rollback is the scoped Docker/Compose/web diff. No data migration, auth, tenancy, external-content, concurrency, retry, or public-contract semantics change. User-visible default changes from Jinja to Next.js; accessibility/interaction code itself is unchanged.
- Approval: implementation authorised by the user's explicit `engineering AUTO` request; no remote or production action authorised.

## Discovery

- Observations: current `Dockerfile` excludes `dashboard/` and builds only Python; `compose.yaml` publishes the Python/Jinja service at the default port; Next.js already proxies `/dash-api` and deck downloads through `PORTFOLIO_API_ORIGIN`.
- Inferences: two private-networked services are the smallest coherent topology; publishing only Next.js preserves the browser/API separation.
- Unknowns: local Docker daemon availability and whether required base images are cached.
- Affected callers and boundaries: `docker compose up`, Docker build context, Next.js proxy, FastAPI health/API/deck routes, README startup commands, Python web tests/package data.
- Existing proof: Next.js has `typecheck`, `lint`, and `build` scripts; Python has focused control-room API and web/security tests.

## Packets

1. Encode the Docker/Compose contract and build the Next.js runtime target.
   - Writer: primary agent
   - Files or symbols: `Dockerfile`, `.dockerignore`, `compose.yaml`, Docker contract test
   - Proof: focused Docker contract test plus `docker compose config`
   - Status: PASSED — contract test and Compose configuration.
2. Remove the legacy Jinja dashboard while retaining the private API boundary.
   - Writer: primary agent
   - Files or symbols: `web.py`, `dashboard.py`, templates/static assets, focused web tests, package data
   - Proof: focused API/security/deck tests and absence checks
   - Status: PASSED — focused API/security/research/source tests; interrupted-composition projection regression added.
3. Reconcile operator and architecture documentation.
   - Writer: primary agent
   - Files or symbols: `README.md`, architecture/ADR/requirements/traceability/security documents as directly affected
   - Proof: targeted text search and documentation tests where present
   - Status: PASSED — current documentation reconciled; historical superseded ADRs/build briefs retained as history.

## Validation map

| Obligation | Source | Proving command or observation | Phase | Subsumed by | Invalidated by | Status |
|---|---|---|---|---|---|---|
| Docker selects Next.js and private API topology | User request, Compose contract | focused Docker contract test; `docker compose config` | packet | final Compose build/runtime | Dockerfile, Compose, ignore or test changes | PASSED |
| Legacy dashboard is removed without losing required API/deck routes | User request, Next proxy callers | focused Python API/security/deck tests and filesystem absence assertions | packet | final Python gate | `web.py`, `api.py`, removed assets/tests | PASSED |
| Next.js candidate remains buildable | `dashboard/package.json` | `npm run typecheck && npm run lint && npm run build` | final local | none | dashboard sources/config/dependencies | PASSED |
| Complete local Docker stack builds and serves Next.js | User request, README Docker contract | `docker compose up --build --wait` plus loopback HTTP observations | final local | none | Docker/Compose/dashboard/backend/runtime environment | PASSED |
| Scoped diff is coherent | Engineering workflow | independent candidate review; `git diff --check`; scoped status/diff inspection | review/final | none | any in-scope change | PASSED |

## Candidate review

- Reviewer: independent engineering reviewer `/root/docker_dashboard_review`
- Candidate identity: baseline `6356aa49cb3b4fe47955aab9e81a8e1a05ec9693`; scoped tracked diff `eb7077b00877908ab1bf432e03233b19d634890583641037b26185fb04f4d4de`; untracked `proxy.ts` `4c812653...`, ADR 0013 `aad74894...`, Docker contract test `88fad22d...`.
- Full-review findings and dispositions: P1 Next proxy CSRF/Host confused deputy fixed with loopback Host, Fetch Metadata, and exact Origin checks; P2 native launch commands fixed with separate API/dashboard commands; P2 deck download fixed by forwarding `Content-Disposition`.
- Focused re-review surface and verdict: all three findings resolved; behavioral diagnostic passed same-origin/read-only and rejected cross-site, forged Host, and missing-Origin mutations; no new P0/P1.
- Unresolved P0/P1: none.
- P2/P3 dispositions: both P2 findings fixed; no P3 findings.
- Ready to freeze: YES

## Final validation

- Frozen candidate identity: baseline and fingerprints recorded above; ledger excluded as process metadata.

| Status | Command or observation | Covered obligations | Result |
|---|---|---|---|
| PASSED | `.venv/bin/ruff check src tests && .venv/bin/mypy src` | Python static correctness | Ruff clean; strict mypy succeeded for 45 source files. |
| PASSED | `.venv/bin/pytest --cov=portfolio_agent --cov-report=term-missing` | Python behavior and regression coverage | 266 passed, 22 warnings, 85.55% coverage. |
| PASSED | `npm --prefix dashboard run lint && npm --prefix dashboard run build` | Next.js static analysis and production build | ESLint and Next.js 16.3.3 production build succeeded, including the request proxy. |
| PASSED | `docker compose config --quiet` and `docker compose up --build --wait` | Resolved topology, complete image builds, runtime health | Both the private API and default Next.js dashboard images built and became healthy. |
| PASSED | loopback HTTP and browser observations | Actual default surface and request boundary | Root and proxied session returned 200; forged Host, cross-site mutation, and missing-Origin mutation returned 403; browser displayed the Next.js control room with no console errors or mobile horizontal overflow at 390x844. |
| PASSED | `docker compose ps`; explicit `docker inspect`; `git diff --check` | Runtime isolation and diff hygiene | Next publishes only `127.0.0.1:8000`; API port is private; both run non-root, read-only, and with all capabilities dropped; diff check clean. |

- Reused evidence and why it remains valid: focused 54-test packet gate remained valid because the later proxy TypeScript correction and Ruff-only test cleanup did not alter the covered Python behavior; the full Python gate subsequently subsumed it.
- Invalidation decisions after failures or corrections: initial TypeScript strict-indexing and Ruff unused-variable/import-layout failures were corrected, independently re-reviewed as semantically neutral where applicable, and their full owning gates were rerun successfully. A sandboxed host-network curl could not reach Docker due isolation; the same observations were rerun with approved host-network access and passed.
- Remote CI or delivery evidence: UNRUN; not authorised.
- Residual proof gaps: remote CI, multi-browser compatibility, and a formal accessibility audit were not run; keyboard focus automation in the in-app browser was inconclusive, while static focus-visible and reduced-motion rules remain present.
- Residual risks: the Node base image is exact-version tagged rather than digest pinned; Docker services remain running locally for user inspection.
- Handoff: scope complete; no commit, push, deployment, or unrelated worktree changes performed.
