# ADR-0001: Python 3.12 local FastAPI stack

- Status: Accepted
- Date: 2026-08-26
- Scope: P0 dissertation prototype

## Context

The artifact must ingest spreadsheets/JSON, enforce typed contracts, persist provenance/audit,
serve an accessible HITL interface, and run reproducibly on one local machine without required
network services. The research contribution is workflow/evaluation, so the stack should minimise
platform code and make validation inspectable.

## Decision

Use:

- Python 3.12;
- FastAPI for local HTTP routing and form/file boundaries;
- server-rendered Jinja templates and CSS without a client framework;
- Pydantic v2 for strict external/domain contracts;
- SQLAlchemy 2 plus Alembic for persistence and migration;
- SQLite for the single-user local study;
- OpenPyXL/csv/json for input parsing;
- the official OpenAI Python SDK behind an optional provider interface; and
- pytest, coverage, Ruff, and mypy for validation.

Pin exact project dependency versions in `pyproject.toml`. Bind the app only to loopback.

## Options considered

1. **Python/FastAPI local service** — chosen for typed API contracts, spreadsheet/AI ecosystem,
   simple server rendering, and test seams.
2. **Django** — stronger built-in auth/admin but unnecessary production surface for a loopback P0.
3. **Node/TypeScript full-stack application** — viable, but adds a second ecosystem for the
   spreadsheet/research pipeline and more UI/build complexity.
4. **Notebook-only prototype** — good for exploratory analysis, insufficient for versioned HITL,
   migrations, contracts, and repeatable workflow state.

## Consequences

Positive:

- one language covers ingestion, workflow, evaluation, and service;
- typed boundaries and pytest support reproducible evidence;
- server rendering improves auditability and accessibility with little runtime surface; and
- SQLite keeps core execution offline.

Negative/limits:

- synchronous stages are not suited to long live crawls;
- SQLite is not a production concurrency/tenant solution;
- loopback/Host/CSRF controls exist, but authenticated sessions and production operations remain
  deliberately absent; and
- exact pins require an explicit update/security process.

## Validation and revisit trigger

Validate via an empty-database migration, test suite, coverage, type/lint checks, and local e2e
run. Revisit only if an authorised P1 connector needs durable async jobs, concurrent reviewers,
or a production deployment—none is evidence needed for the current RQ.
