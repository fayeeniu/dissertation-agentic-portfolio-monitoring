# ADR 0010: Two-tier model routing for company research

- Status: Superseded for active model identity by [ADR 0011](0011-gpt-5-6-luna-routing.md)
- Date: 2026-08-27
- Extends ADRs [0004](0004-deterministic-first-model-routing.md) and
  [0008](0008-bounded-live-company-research.md)

## Context

ADR 0004 fixed the route for the *portfolio extraction* provider: a small model attempts one field
against one evidence item, and a single guarded escalation follows a strict-schema failure. That
task is genuinely small, and the ADR remains correct for it.

Company research is a different shape. Discovery and evidence selection have different workloads:

- **Discovery** has to plan coverage across ten claim categories from one Companies House number,
  distinguish the right legal entity from name collisions, and rank official registers above press.
- **Extraction** receives only the bounded captured corpus and has to select exact spans against a
  schema that the application re-checks deterministically. It does not browse, rank companies,
  value the business, or decide whether an investment is attractive.

The v2 route used the larger model for both tasks. The expanded source bucket makes that unnecessary
for extraction: the small model can perform the bounded selection pass while deterministic exact-span,
cutoff, privacy, recommendation-language, and contradiction checks remain authoritative.

## Decision

1. Route by stage, in code. Broad source discovery runs on `gpt-5.4` at a configured reasoning
   effort (`medium` by default). Exact-span extraction runs on `gpt-5.4-mini` at `low`. Capture and
   composition use no model.
2. Route a repeat attempt to `gpt-5.4-mini` at `low` effort with a corrective brief. A second
   attempt is a mechanical correction against a contract the application already enforces, not a
   harder instance of the original problem.
3. No model selects the route. `route_for()` is a pure function of settings, stage, and attempt
   number, and both the adapter and the projection layer read it, so the dashboard cannot show a
   route the adapter would not take.
4. Reject any configured pair other than the approved `gpt-5.4-mini` / `gpt-5.4` before the client
   is constructed, and reject a reasoning effort outside `low`/`medium`/`high`.
5. State the validator's acceptance rules verbatim in the extraction brief, and the identity,
   source-priority, and prohibited-source rules verbatim in the discovery brief. Anything the
   application enforces but the brief omits becomes wasted output and silently missing evidence.
6. Record the model on every attempt. `company_research_task_attempts.model` already holds it, so
   the audit record is what actually ran, not what was configured.
7. Bump the prompt version to `company-research-web-v3` for the expanded discovery brief and
   selection route, while continuing to admit v1 and v2 for read/review/export.
8. Bump the prompt version again to `company-research-web-v4` when the extraction contract gains
   the canonical public/mixed CBIT metric vocabulary; continue admitting v1-v3 for historical
   read/review/export. Keep separate checks that were
   conflated in `_validate_run_contract`:
   - **tamper**: the run's fingerprint must reproduce from the run's own persisted fields, and its
     versions must be admitted. This governs reading, reviewing, cancelling, and downloading.
   - **freshness**: executing a stage additionally requires the run to be pinned to the *current*
     prompt and source policy, because the code that would run it has changed.

## Consequences

- Discovery is the only large-model stage; corpus selection stays on the approved small model.
  `PORTFOLIO_OPENAI_REASONING_EFFORT` applies only to discovery.
- A run created under `company-research-web-v1` can still be read, reviewed, cancelled, and its
  approved deck downloaded. It cannot be advanced or recovered; the reviewer starts a new run.
  Before this ADR, a version bump would have made historical approved decks undownloadable.
- Higher reasoning effort raises discovery latency. The control room reports real elapsed time per
  stage, so this is visible rather than hidden.
- No claim is made that the larger model produces better evidence. The exact-span validator,
  contradiction ledger, and named approval gate are unchanged and remain the controls that decide
  what counts. Whether the route improves admitted-claim yield is an empirical question for the
  frozen evaluation, not something this ADR asserts.
