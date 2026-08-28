# ADR 0012: Public signals and the evidence-led diligence dossier

- Status: Accepted
- Date: 2026-08-28
- Extends ADRs [0008](0008-bounded-live-company-research.md) and
  [0010](0010-two-tier-research-model-routing.md)

## Context

The research ledger can contain useful company evidence that does not answer a canonical CBIT
metric exactly. Examples include a financing event that is not demonstrably the complete
since-programme private-funding total, a named partnership that is not a quarterly customer count,
or a security certification that does not establish technology readiness level. The first HTML
deck placed this evidence below a large metric table, while the table showed only "not found" or
"document required". This was truthful but made the report appear empty and obscured useful public
diligence.

## Decision

1. Keep exact metric completion strict. A public or mixed metric is evidenced only when an admitted
   claim uses its canonical key and satisfies the existing exact-span, value, source, cutoff and
   period controls.
2. Add a separate category-level `supporting_public_evidence` projection for admitted claims that
   are relevant to a metric family but do not complete a metric. The projection is deterministic;
   it never changes claim verification or the canonical metric status.
3. Expand prompt version `company-research-web-v9` so discovery explicitly covers financing,
   customers, partnerships, procurement, products, technology, certifications, operating scale,
   expansion, awards, performance and adverse evidence, and includes the canonical public/mixed
   metric roster with value shape, unit and period semantics.
4. Render the approved HTML as a human-review dossier: coverage summary, admitted evidence by
   decision section, contradiction callout, metric appendix, captured source register and stated
   limitations. Use colour plus persistent text labels for evidence, public context, document
   requests, missing public evidence and contradictions.
5. Recompute presentation-only report metadata from the already validated canonical claim ledger
   when an older approved profile is viewed. Do not mutate its reviewed JSON or content hash.

## Consequences

- Existing approved reports become easier to scan without invalidating their approval record.
- Useful public context is visible beside the relevant metric family while remaining explicitly
  weaker than metric evidence.
- A richer prompt may increase source and claim yield, but no completeness or investment-quality
  improvement is claimed without representative repeated-run evaluation.
- The report remains an evidence organisation and diligence aid, not a valuation, investment score
  or recommendation.
