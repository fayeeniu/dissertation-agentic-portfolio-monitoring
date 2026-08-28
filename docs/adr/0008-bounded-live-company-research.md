# ADR 0008: Bounded live company research and cited deck

- Status: Accepted
- Date: 2026-08-27

## Context

The offline Company 360 foundation deliberately held live retrieval and external models. The user
subsequently approved a public-only path in which a reviewed Companies House number is sufficient
to discover broad public evidence and build a comprehensive, cited company-intelligence deck.
Directly allowing a model to browse and write a narrative would bypass source admission,
provenance, classification, contradiction, and named-review controls.

## Decision

1. Keep the application local, loopback-only, single-user, and SQLite-backed.
2. Require a public research case with a named-reviewed Companies House identifier.
3. Use OpenAI Responses web search only to discover HTTPS URLs. Do not treat snippets or model prose
   as evidence.
4. Advance four persisted serial tasks: discovery, guarded capture, strict exact-span extraction,
   and deterministic deck composition. Each task has an immutable fingerprint, bounded attempts,
   hashes, failure state, telemetry, and cancellation boundary.
5. Capture pages with a single HTTPS fetch boundary enforcing public DNS/IP and connection pinning,
   redirects, robots, media/byte/time limits, and source-owned create-once snapshots. Unsupported or
   blocked pages remain visible coverage gaps.
6. Redact personal contacts before persisting a clearly identified immutable public-text
   derivative or sending it to the approved model with `store=False`. Retain only substantive
   verbatim spans; reject semantic mismatch, post-cutoff text, prompt injection, personal contacts,
   and investment-recommendation language.
7. Compose profile content deterministically, surface source-separated potential contradictions,
   reconcile interrupted stages explicitly, fence cancellation/finalization, and require named
   optimistic review plus content-hash verification before every HTML/JSON download.

## Consequences

- A Companies House number can seed broad source discovery without weakening identity authority.
- Search breadth is measurable through attempted/captured/failed source and category coverage; it is
  never described as literally exhaustive.
- Source availability, robots policy, publisher terms, model quality, cost, and provider retention
  remain explicit residuals. `store=False` is not represented as Zero Data Retention.
- Direct Companies House/UKRI live adapters, personal-data graphs, commercial scraping, native
  PPTX/PDF, parallel workers, hosted auth/tenancy, and production egress remain separate phases.
