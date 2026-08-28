# ADR-0004: Deterministic-first extraction with guarded GPT-5.4 routing

- Status: Superseded for active model identity by [ADR 0011](0011-gpt-5-6-luna-routing.md)
- Date: 2026-08-26
- Scope: Optional unstructured public/synthetic extraction

## Context

The source workbook is structurally heterogeneous, but many values can be parsed deterministically.
An LLM may help with unstructured public evidence; it also creates privacy, injection, schema,
cost, non-determinism, and retention risks. The user requested `gpt-5.4-mini` or `gpt-5.4` if an
LLM is needed.

Official pages checked on 2026-08-26 list both exact model IDs and support for the Responses API,
function calling, and structured outputs:

- [GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini)
- [GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4)
- [Responses API quickstart](https://platform.openai.com/docs/quickstart/make-your-first-api-request)

## Decision

1. Default to deterministic extraction and normalization; core tests/evaluation need no model.
2. Keep external use disabled; while G4 is open the default runtime refuses
   `PORTFOLIO_ALLOW_EXTERNAL_LLM=true`. An approved experiment injects the guarded provider
   explicitly.
   The `openai-smoke --acknowledge-synthetic-only` entrypoint is that bounded injection seam: it
   permits one checksum-pinned synthetic fixture target, leaves all other extraction deterministic,
   caps each response at 512 output tokens, and produces a content-free local audit manifest.
3. Reject restricted/internal or untrusted/injection-like evidence before provider invocation.
4. Send one minimal public/synthetic evidence item with expected identity/metric/period.
5. Use Responses API with `store=False` and strict JSON Schema output.
6. Route first to `gpt-5.4-mini`; on parsing/schema validation failure only, make at most one
   escalation to `gpt-5.4`; then fail closed.
7. Treat that ordered pair as an exact allowlist. Reject arbitrary, reversed, or duplicate model
   configuration before constructing the external client.
8. Use an opaque reference derived only from admitted public snapshot provenance as the expected
   company field; never copy a restricted portfolio company name into the model request.
7. Require an exact bounded evidence span for every non-null value and deterministically validate
   its occurrence plus parsed value/currency/unit before identity, normalization, period, and
   independent-verification checks.
8. Record model/attempts/tokens; leave cost null unless calculated from a dated authoritative
   price during the run.

## Options considered

1. **Deterministic-first with bounded mini→full escalation** — chosen; cost/risk-conscious and
   compatible with strict contracts.
2. **Always use `gpt-5.4`** — potentially capable but unnecessary for structured fields and a poor
   default for reproducibility/cost research.
3. **Always use `gpt-5.4-mini` with no escalation** — simpler, but cannot test a bounded recovery
   route for genuinely unstructured eligible evidence.
4. **Automatic multi-provider fallback** — rejected; expands processors, policy surfaces, and
   comparability without source evidence.
5. **Fine-tuning** — P2; insufficient approved labelled data and unnecessary for the RQ.

## Consequences

Positive:

- P0 remains offline/repeatable and avoids sending the supplied workbook to any provider;
- model use has a clear, testable purpose rather than decorative generation;
- strict outputs and downstream verifier limit—not eliminate—model error impact; and
- routing can be evaluated for public/synthetic data later without changing domain contracts.

Negative/limits:

- the external adapter is statically checked but not live-tested in P0;
- a successful synthetic smoke establishes connectivity and contract execution only, not model
  performance, comparative quality, cost, retention, or production readiness;
- model IDs/capabilities/pricing/retention can change and require execution-date verification;
- `store=False` is not a complete privacy/legal control; and
- a strict valid output can still be factually wrong, so verification remains mandatory.

## Revisit trigger

Revisit only after Gate 1 authority, a frozen public/synthetic benchmark, budget, execution-date
official documentation, and a reason deterministic extraction is insufficient. Do not route
restricted data externally even if a model benchmark is favourable.
