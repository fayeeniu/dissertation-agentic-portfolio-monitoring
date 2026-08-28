# ADR 0007: Offline company-intelligence case and hybrid-intake foundation

- Status: Accepted for the approved first implementation slice
- Date: 2026-08-27
- Supersedes: no prior ADR; extends ADRs 0001, 0003, and 0006

## Context

The portfolio workflow currently begins with a reporting-period file. The approved company-
intelligence slice must also accept a Companies House number, verified-domain candidate,
declared-company document, or name and jurisdiction without weakening exact identity, provenance,
classification, or human-review boundaries. The wider upgrade programme also proposes live
retrieval, durable workers, public-person data, and production deployment, but those are separate
Critical changes and are not authorised by this decision.

## Decision

1. Retain the local, loopback-only, synchronous FastAPI/Jinja and SQLite deployment boundary.
2. Add an additive company research-case model. A case pins one company, declared purpose,
   classification, and immutable core-company-profile template version.
3. Persist every intake as an immutable, SHA-256-fingerprinted artifact. Duplicate normalized
   requests reuse their original artifact and case rather than creating parallel identities.
4. Permit Companies House-number-only intake, but keep the company and identifier unresolved until
   a configured named reviewer records an accept decision with rationale. Structural validity is
   not identity authority.
5. Treat a website as a domain-link claim, never as legal identity. Only HTTPS public hostnames are
   accepted, no network request is made, and a named decision is required before the domain becomes
   verified.
6. Treat name-plus-jurisdiction and declared-company documents as unresolved candidates. Names and
   filenames never trigger automatic merges.
7. Parse bulk CSV/XLSX rows independently through the same normalized intake contract. A malformed
   row fails the bulk request atomically in this slice; no partly declared portfolio is persisted.
8. Store uploaded bytes create-once in ignored local storage with mode `0600`, classification,
   purpose, actor, checksum, and safe basename. Evidence content remains untrusted and no document
   extraction, malware scanning, OCR, model call, or network action is implied.
9. Preserve every existing import, workflow, report, approval, and export route unchanged while
   adding server-rendered Companies and Company 360 identity/documents views.
10. Keep live public retrieval, G2 admission, external models, public officer/PSC data, durable
    tasks, production authentication/tenancy, secondary sources, and deployment out of scope.

## Consequences

- The first slice creates reviewable company workspaces but does not yet run public research.
- Placeholder company labels are visibly unresolved and must not be presented as official names.
- Additive revision `0008` preserves revision-`0007` rows without inferred backfill. Empty schemas
  can downgrade; a database containing first-slice records rejects downgrade before mutation.
- Domain and identifier decision tables retain review history independently of mutable current
  status fields.
- A future live-source or task-DAG implementation must pass a new material-change and Critical-risk
  approval gate.

## Rejected alternatives

- Closing G2 from public documentation alone: rejected because source purpose, retention, licence,
  attribution, and reviewer authority are not implementation facts.
- Auto-resolving a structurally valid company number: rejected because exact syntax is not named
  identity confirmation.
- Inferring identity from a domain, filename, or name match: rejected because false merges pollute
  every downstream fact.
- Adding a queue, crawler, vector store, or external model to the intake slice: rejected because
  none is required to prove the case and review contracts.

## Validation

Migration equivalence/round-trip tests, normalized intake/idempotency tests, negative no-auto-merge
and classification tests, existing route/security regressions, server-rendered UI tests, offline
runtime-gate tests, and an independent migration/data-integrity review exercise this decision.
