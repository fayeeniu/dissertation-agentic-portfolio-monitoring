# ADR-0002: Bounded functional agents with an independent verifier

- Status: Accepted
- Date: 2026-08-26
- Scope: Workflow decomposition and experimental condition

## Context

The materials ask for an agentic/multi-agent pipeline and independent verification. The
supervisor also expresses a one-agent preference motivated by perceived token/cost and leaves
evaluation design open. A collection of LLM personas would make responsibility and causality
hard to test; a monolith would make independent verification less credible.

## Decision

Represent agents as fixed functional roles in an orchestrated state machine:

`planner → identity resolver → collector → extractor → normalizer → independent verifier →
report composer → human-review gate`.

Each role executes once per run stage, has a bounded contract, persistent status/timing/hashes,
and no authority to choose the next stage or export. Roles may be deterministic; “agent” does not
imply an LLM call. The verifier is a separate pure decision component from extraction and
composition. C1 evaluates a simpler no-independent-verifier baseline, so the dissertation tests
rather than assumes the benefit of decomposition.

## Options considered

1. **Bounded functional roles** — chosen for traceability, failure isolation, and experimental
   comparability.
2. **One monolithic extractor/composer agent** — retained as an evaluation baseline; lower
   orchestration overhead but weaker separation.
3. **Conversational persona swarm with free delegation** — rejected for P0 due to uncontrolled
   loops, prompt/tool authority, poor reproducibility, and difficult attribution.
4. **Pure ETL with no agent abstraction** — too narrow to evaluate role decomposition/HITL RQ,
   though deterministic logic remains the implementation substrate.

## Consequences

Positive:

- every failure/action can be attributed to a role and stage;
- verifier independence is structural rather than a prompt sentence;
- deterministic and model providers can be swapped without changing workflow semantics; and
- C1/C2 comparison isolates part of the verification effect.

Negative/limits:

- more persisted records/orchestration than a monolith;
- stage boundaries alone do not guarantee statistical independence or accuracy;
- the synthetic baseline can become a straw man unless independently reviewed; and
- role naming may overstate autonomy unless the dissertation uses this contract definition.

## Validation and revisit trigger

Tests require eight ordered successful stage records and a separate verifier before composer.
Evaluation must report cost/time as well as quality. Revisit decomposition only after frozen
evidence identifies an unnecessary/harmful boundary; do not tune based on final OOS outcomes.

