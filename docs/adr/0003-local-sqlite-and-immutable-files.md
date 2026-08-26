# ADR-0003: Local SQLite metadata with immutable file snapshots

- Status: Accepted
- Date: 2026-08-26
- Scope: P0 storage and provenance

## Context

The study needs relational identity/period/claim/provenance/version invariants and must preserve
source bytes. Inputs may be restricted. A cloud database/object store would add processors,
credentials, deployment risk, and reproducibility dependencies not needed for a single-user P0.
Putting raw files into database JSON would make immutable byte-level audit and lifecycle controls
less clear.

## Decision

- Store canonical metadata/audit in local SQLite with foreign keys enabled.
- Manage schema with explicit Alembic migrations.
- Store imported raw bytes in create-once dataset directories below ignored `var/raw` with mode
  `0600`; record SHA-256 and path in `RawSubmission`.
- Store exports below ignored `var/exports/<report>/v<version>/`. Commit a pending manifest,
  write/fsync restrictive files into a staging directory, atomically rename the complete bundle,
  and finalize database state only afterwards.
- Keep only fictional fixtures in Git.
- Treat hashes as integrity/provenance—not encryption, anonymisation, or lawful authority.

## Options considered

1. **SQLite + local immutable files** — chosen for offline reproducibility and relational/file
   separation.
2. **JSON/files only** — simple, but weak foreign keys, idempotence, queries, audit/versioning.
3. **All content inside SQLite blobs** — transactional, but less transparent byte snapshots and
   harder retention/access separation.
4. **PostgreSQL + object storage** — appropriate for production concurrency but unnecessary and
   governance-heavy for P0.

## Consequences

Positive:

- core workflow runs offline without accounts or infrastructure;
- raw bytes remain hash-verifiable and are not silently rewritten;
- parsed source facts/events are bound to terminal source metadata by a separate canonical
  derivation hash, detecting same-byte parser drift and concurrent disagreement;
- relational constraints support claim/evidence/version audit; and
- runtime data stays outside source control.

Negative/limits:

- local disk/SQLite are not automatically encrypted, backed up, or multi-user safe;
- filesystem and database can diverge after external/manual deletion, which finalized-manifest
  checks detect but do not automatically repair;
- runtime startup always runs Alembic to head; an unstamped legacy schema is deliberately not
  guessed or stamped silently; and
- retention/secure deletion require an approved operational procedure before real data.

## Validation and revisit trigger

Migration from an empty temporary database must produce the same table set as SQLAlchemy
metadata. Import tests check idempotence and file mode. Revisit for authorised concurrent/team or
production work only after security/operations requirements are defined.
