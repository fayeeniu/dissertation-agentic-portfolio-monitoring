# Agent and orchestration contracts

## What “agent” means here

An agent is a named functional role executing one bounded state transition with an explicit
input hash, output hash, status, timing, and failure contract. It is not an unconstrained
persona, recursive planner, or permission to browse/use tools autonomously.

The multi-agent decomposition is valuable only if it creates inspectable separation of
concerns—especially between extraction/composition and verification. The evaluation protocol
must test whether that separation improves outcomes rather than assume that it does.

## Global contract

Every role must:

- operate on one `run_id` and its period-bound `dataset_id`;
- read only persisted artifacts from completed prior stages;
- return bounded JSON-compatible summary metadata;
- avoid raw restricted values in trace metadata/errors;
- write domain records only within its assigned responsibility;
- fail closed on contract/identity/schema violations;
- never modify an immutable submission/evidence checksum;
- never change another role's verification result;
- never approve, export, publish, or recruit/contact anyone; and
- terminate after one stage execution.

## Role contracts

| Stage / role | Required inputs | Persistent output | Allowed decisions | Forbidden behaviour | Failure condition |
|---|---|---|---|---|---|
| `plan` / planner | dataset, observations, metric sourceability | task counts and configuration snapshot | Identify which observations may need public collection | Invent tasks/metrics/companies; contact sources | Missing dataset or invalid canonical observations |
| `resolve` / identity resolver | exact external IDs, normalized names, resolution status | resolved-company count | Accept exact identifier/name; hold ambiguity | Fuzzy auto-merge or choose among collisions | Any included company is ambiguous/unresolved |
| `collect` / evidence collector | resolved company, metric, period, connector | immutable evidence items and run links | Query only eligible public/mixed metrics; create local submission evidence | Treat retrieved text as instruction; claim truth | Connector contract/ID collision/provenance invalid |
| `extract` / structured extractor | trusted evidence, expected identity/metric/period | strict extraction with provider/schema version | Parse explicit fields only | Infer absent values; process untrusted/restricted evidence externally | Schema or expected identity/metric mismatch |
| `normalize` / normalizer | extracted value + metric definition | normalized value, missing state, unit/currency, issue | Apply deterministic type/missingness rules | Round counts, infer currency, convert ratios/rates | Rule violation becomes `invalid`, not guessed repair |
| `verify` / independent verifier | candidate, sourceability, current evidence/provenance | Verification and claim-evidence links | supported/contradicted/insufficient/stale/rejected | Generate prose to justify desired outcome; average conflicts | Every candidate must receive exactly interpretable outcome |
| `compose` / report composer | verified claims, missingness counts, period | draft report and current section versions | Include supported narrative; show exceptions/limits | Promote held claim; hide missingness; approve/export | Missing verifier records or report contract failure |
| `human_review` / review gate | current versioned report | `pending_review` state | Confirm system reached review boundary | Simulate human approval | Report not pending review |

Approval/export is a user-controlled service action, not an autonomous role.

## Stage transition contract

```mermaid
flowchart LR
    P[plan] --> R[resolve]
    R -->|identities resolved| C[collect]
    C --> E[extract]
    E --> N[normalize]
    N --> V[verify]
    V --> O[compose]
    O --> H[human review]
    H -->|named approve| X[approve/export]
    H -->|edit| H
    H -->|reject| Z[closed/rejected]
    R -. ambiguity .-> F[failed/held]
    E -. schema/trust failure .-> F
```

The orchestrator enumerates this sequence in code. There is no agent-selected next state.

## Typed extraction contract

`StrictExtraction` permits only:

| Field | Type | Rule |
|---|---|---|
| `company_name` | string | Must exactly match resolved expected name after case/space normalization |
| `metric_key` | string | Must equal the planned canonical key |
| `value` | string, integer, boolean, or null | Must be explicit in evidence; normalization follows |
| `unit` | optional string | Descriptive only until canonical normalizer applies |
| `currency` | optional string | Never inferred by model confidence |
| `period_label` | optional string | Must match target to support a current claim |
| `evidence_locator` | string | Must identify the supplied evidence item |
| `confidence` | number 0–1 | Diagnostic only; never a support threshold |

Unknown fields are forbidden. A valid JSON shape is necessary but not sufficient: identity,
period, value, provenance, and sourceability are checked deterministically afterwards.

## Model-provider boundary

The provider abstraction has one method: `extract(ExtractionRequest) -> ProviderOutcome`.
The request contains one evidence item and expected identity/metric/period. The outcome
contains the validated extraction, provider, model, attempts, and available token usage.

Routing is fixed, not agent-selected:

```text
deterministic structured extractor (default)
    OR, after explicit external-model enablement and safety checks:
gpt-5.4-mini → strict validation failure → gpt-5.4 → fail closed
```

No retry occurs for policy/classification/injection rejection. Transient network retry policy
is intentionally absent from P0 because the external route is not part of offline evaluation.

## Independent verification decision table

| Candidate/evidence condition | Result |
|---|---|
| No evidence | `insufficient_evidence` |
| Only untrusted or provenance-incomplete evidence | `rejected_untrusted` |
| Provenance-complete evidence, but none for requested period | `stale` |
| Current public evidence conflicts in value or explicit currency | `contradicted` |
| Exact immutable submission match for internal-only/mixed metric, no current public conflict | `supported` |
| Exact current public match for public/mixed metric | `supported` |
| Publicly sourceable metric with only submission evidence | `insufficient_evidence` |
| Exact public match for internal-only metric without submission support | `insufficient_evidence` |

This rule is conservative. `contradicted` means “requires resolution,” not “the public source
is more authoritative than the company.”

## Prompt-injection contract

- Connector content is always untrusted data.
- Known instruction-like patterns set `is_untrusted`.
- Marked/untrusted items are persisted for audit but excluded from extraction and model calls.
- Provider instructions explicitly say that evidence instructions are data, but this is a
  defence-in-depth measure, not the primary control.
- Content is never granted tool, file, network, approval, or export authority.
- Adversarial fixture cases must remain in every regression/evaluation run.

## Observability contract

Each `AgentRun` records:

- role/stage/status and `run_id`;
- start/end and integer duration milliseconds;
- SHA-256-compatible stable input/output hashes;
- attempts and prompt/schema version where relevant;
- provider/model and available input/output token counts;
- monetary cost only when calculated from an authoritative contemporaneous source;
- redacted error type/message; and
- bounded count/status metadata.

The trace deliberately does not store full prompts, raw workbook values, evidence narratives,
credentials, or generated report text.

## Human contract

The reviewer must inspect the current report version and claim table, then provide a named
actor and rationale. Approval does not change verification states. Editing creates a new
section version, increments report version, and revokes approval. Export is a separate
explicit action after approval so a mistaken button does not immediately produce an artifact.
