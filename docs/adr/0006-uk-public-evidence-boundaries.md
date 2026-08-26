# ADR 0006: UK public-evidence, identity, time, and evaluation boundaries

- Status: Accepted for offline dissertation prototype
- Date: 2026-08-26
- Supersedes: no prior ADR; narrows and extends ADRs 0002–0005

## Context

The supplied CBIT workbook is a transposed, heterogeneous questionnaire whose row semantics do
not match a generic flat metric importer. Most company columns have no exact public identifier.
UK public records also have source-specific availability, filing-lag, lifecycle, and licence
constraints. Treating names, a global stale flag, or fluent model output as truth would contaminate
the portfolio and weaken the dissertation evaluation.

## Decision

1. Freeze the workbook as a versioned exact row contract. Sections, explanations, mixed fields,
   formulas, and aggregates are not silently coerced into observations.
2. Make company identity source-scoped. Exact identifiers can resolve automatically; normalized
   names create review candidates only. A named decision cannot cross classification boundaries.
3. Admit public sources through versioned capability manifests. One exact-ID company/source/cutoff
   snapshot may yield several typed facts and append-only events.
4. Keep submissions, public facts, and derived statistics separate. Public evidence can
   corroborate or contradict a submission but never overwrite it.
5. Evaluate publication/effective time relative to the frozen claim cutoff. Persist filing-not-due,
   dormant, not-required, source-unavailable, and other missing states without coercing to zero;
   surface expected states as explicit not-defect warnings and source failures as coverage warnings.
6. Apply deterministic structured extraction first. Optional OpenAI processing is public/synthetic
   only, `store=False`, `gpt-5.4-mini`, and at most one `gpt-5.4` schema-validation retry.
7. Compose exception-led reports with source coverage, quality, events, compatible changes, and
   minimum-N five-number context. Do not rank companies or claim causal impact.
8. Require configured reviewer identity, CSRF, optimistic report concurrency, approval, and a
   staged SHA-256 export manifest.
9. Namespace D0 benchmark records, leave D1 protocol-only, and make D2 inaccessible while sealed.
   Human/event outcomes without observations remain null.
10. Persist explicit metric period semantics and programme membership. A cumulative public fact
    must cover programme start through cutoff exactly or produce no claim.
11. Require every connector fact to carry a structured locator and extraction method/schema in the
    versioned derivation hash. Model grounding accepts only complete finite numeric tokens or exact
    structured value leaves, never provenance-envelope text.
12. Bind each source fact key to its only allowed metric(s), unit, currency, extraction method, and
    schema in the manifest. Incomplete/mixed-currency UKRI award coverage remains diagnostic and
    cannot support a zero or complete-total claim.
13. Use stable public identifiers in event locators and require locator equality when a canonical
    event is reused. Separate no-record, temporary unavailability, and terminal failure outcomes.
14. Compare/report only compatible semantic intervals: equal-duration reporting periods, ordered
    point-in-time cutoffs, or cumulative windows with the same programme origin. Segment context by
    exposure window and suppress small groups.
15. A downgrade to the legacy unique-name schema must fail before any revision mutation when valid
    duplicate normalized names make that downgrade lossful.

## Consequences

- Coverage is deliberately lower when exact identity or evidence is absent; this is a measurable
  precision-first outcome, not an implementation defect.
- Source v2 and the legacy metric-oriented synthetic adapter coexist temporarily so the existing
  workflow remains reproducible while source-oriented orchestration is evaluated.
- Companies House and UKRI/GtR are implemented only as immutable synthetic replay in the default
  research path. Live retrieval requires the separate G2 source/identity authority gate.
- The optional model adapter exists but no real model call is evidence until G4 is granted.
- SQLite remains suitable only for controlled local work despite stale-write protection.
- D0 scores establish functional behavior on designed cases, not superiority or real-portfolio
  performance.

## Rejected alternatives

- Fuzzy/name-only automatic company joins: rejected because one false merge can contaminate every
  downstream metric and event.
- Metric-by-metric public retrieval: rejected because it duplicates requests and loses snapshot
  coherence.
- One global stale flag or period-label equality: rejected because evidence eligibility is
  claim-relative and source-time dependent.
- Mean-only context or portfolio scores: rejected because small samples/outliers and construct
  ambiguity would be hidden.
- General web crawling, director/PSC graph, valuation/dilution inference, and runtime OCR: held
  behind explicit evidence, privacy, licence, or benchmark gates.

## Validation

The decision is exercised by CBIT-contract/import tests, migration round trips, identity collision
tests, source contract and offline connector suites, temporal/quality permutations, document and
mocked model-boundary tests, context/report/UI/export tests, evaluation leakage/seal tests, and the
deterministic accessible SVG manifest.
