# ADR 0011: GPT-5.6 Luna for all active model calls

- Status: Accepted
- Date: 2026-08-28
- Supersedes the active model identity in ADRs [0004](0004-deterministic-first-model-routing.md),
  [0006](0006-uk-public-evidence-boundaries.md), and
  [0010](0010-two-tier-research-model-routing.md)

## Context

The application had two pinned model identities: GPT-5.4 for broad source planning and GPT-5.4
mini for bounded evidence selection and repair. The user requested GPT-5.6 Luna for every API call
to reduce inference cost. OpenAI's official model documentation lists the exact API identifier
`gpt-5.6-luna` and support for the Responses API, structured outputs, web search, and the reasoning
efforts used here.

## Decision

1. Pin both existing configuration boundaries to `gpt-5.6-luna`. The
   `PORTFOLIO_OPENAI_ESCALATION_MODEL` name remains temporarily for environment and persisted API
   compatibility; it no longer denotes a different model family.
2. Preserve stage-specific effort: discovery uses `PORTFOLIO_OPENAI_REASONING_EFFORT` (`medium` by
   default), company claim selection and company-research repair use `low`, and scalar portfolio
   extraction uses `none`.
3. Preserve the bounded repair contract. Portfolio extraction may call Luna once more after a
   parsing or strict-validation failure; using the same model must not deduplicate that attempt.
4. Continue to reject any configured model outside the pinned route before constructing an
   external client. Keep `store=False`, strict schemas, source capture, exact-span validation,
   deterministic admission, and named review unchanged.
5. Keep historical runs and migration fixtures with their recorded GPT-5.4 model identities
   readable. A new run records Luna through the existing model and attempt fields.

## Consequences

- Every active external request uses one model identity, while effort still reflects task shape.
- A bounded synthetic-only smoke confirms account access, strict persistence, and the exact model
  returned by the API. Repository evidence still does not establish realised comparative cost,
  latency, source yield, or report quality; those require representative evaluation.
- The compatibility field name `openai_escalation_model` is imperfect but avoids an unrelated
  configuration/API migration. It can be renamed separately with an explicit deprecation path.

## Authoritative references

- [GPT-5.6 Luna model](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [Model guidance](https://developers.openai.com/api/docs/guides/model-selection)
