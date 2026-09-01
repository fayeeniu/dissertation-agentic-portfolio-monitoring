# Project charter

## Status and evidence boundary

Status: **P0 research prototype implemented; empirical dissertation evaluation pending**.

This charter distinguishes four states throughout:

1. **Source evidence** — what the supplied materials and stakeholder transcript state.
2. **Implemented artifact** — what the current code and tests demonstrate locally.
3. **Protocol** — what should be measured in an authorised study.
4. **Finding** — a result that may be claimed only after that protocol is executed.

No synthetic observation, automated test, stakeholder assertion, or design intention is
represented as a real-world finding.

## Goal

Design, implement, and evaluate a reproducible, evidence-first multi-agent pipeline that
automates a material portion of early-stage portfolio reporting while making missingness,
conflicts, provenance, agent actions, and human decisions visible.

## Research question

> To what extent can a multi-agent AI pipeline automate the end-to-end data ingestion,
> validation, and report-generation workflow for early-stage portfolio reporting, and
> how does quality/reliability compare to manually produced reports?

## Problem definition

The supplied evidence describes a workflow with three broad manual activities: collecting
company data, aggregating/analysing it into an executive summary, and preparing a
presentation. The supervisor explicitly placed presentation generation outside the core
dissertation concern. The workbook shows that reporting inputs mix numeric, textual,
blank, formula, and semantically ambiguous values across company columns. Some claims are
publicly sourceable; many operational and financial metrics remain internal-only.

The technical problem is therefore not “generate fluent prose.” It is:

- preserve the original submission and reporting-period boundary;
- convert heterogeneous values into explicit typed observations without silent inference;
- resolve which company and metric each observation belongs to;
- collect eligible external evidence without treating web content as trusted instructions;
- create only source-linked candidate claims;
- independently verify each claim and expose conflicts;
- require a named human decision before an export becomes an approved artifact; and
- produce evidence that permits fair comparison with simpler and manual workflows.

## Intended contribution

The dissertation contribution is a design-and-evaluation package, not a claim to have
built a production investment platform. It consists of:

1. a sourceability-aware canonical portfolio metric model;
2. a bounded agent state machine with functional role separation;
3. an independent claim-verification and provenance contract;
4. a human-review interface with version and decision audit;
5. a reproducible multi-condition evaluation protocol; and
6. an evidence map that prevents engineering checks from becoming overstated findings.

## P0 scope

- One reporting period per import.
- XLSX, CSV, and canonical JSON ingestion.
- Immutable raw snapshot, source hash, dataset ID, run ID, and schema validation.
- Exact/identifier-based company resolution with explicit ambiguity holds.
- Canonical metrics, types, units, aliases, sourceability, and missing-state semantics.
- Pluggable connector protocol and synthetic public-evidence connector.
- Deterministic extraction and normalization before optional model use.
- Bounded stages: plan → resolve → collect → extract → normalize → verify → compose →
  human review → approve/export.
- Independent verifier, claim status, provenance, and contradiction handling.
- Accessible local Next.js control room, versioned profiles, and review audit.
- JSON, Markdown, and accessible HTML reports after approval.
- Synthetic baselines, adversarial fixtures, metrics, repeat runs, tests, and migrations.

## Explicit non-goals

- Accessing the supplied dashboard or using its exposed credential.
- Live authenticated sources, scheduling, multi-tenancy, or production identity/auth.
- Social-media scraping, autonomous publication, financial decision-making, or advice.
- Inferring absent public facts or converting currencies without an authorised rate source.
- Fine-tuning, slide-deck generation, or polishing a dashboard as the dissertation outcome.
- Recruiting participants or using restricted data beyond the documented ethics approval.

## Stakeholders and authority

| Stakeholder | Legitimate interest | Authority boundary |
|---|---|---|
| Student/researcher | Build, evaluate, analyse, and write the dissertation | Must follow ethics, data governance, and evidence boundaries |
| Dissertation supervisor | Academic direction and domain context | Stakeholder statements are not automatically ground truth |
| Portfolio/reporting staff | Workflow usability and report quality | May review or supply gold labels only with authorisation |
| Portfolio companies | Confidentiality and accurate representation | Their restricted data must remain local and purpose-limited |
| University/ethics body | Lawful, ethical research | Approval controls participant/restricted-data activities |

## Constraints

- Python 3.12, local-first FastAPI/Pydantic/SQLAlchemy/SQLite stack.
- No required network access for core execution or tests.
- No secret or restricted raw data in Git, logs, prompts, evaluation fixtures, or exports
  without the defined local approval path.
- Bounded attempts and explicit failure states; no open-ended autonomous loops.
- No invented acceptance thresholds, baseline timings, participant results, or costs.
- Final out-of-sample evaluation data must remain untouched until the protocol is frozen.

## Success definition

### Engineering success

The P0 artifact is successful when the acceptance checks in `REQUIREMENTS.md` pass on a
clean local environment; a fictional reporting period reaches `pending_review`; every
candidate claim has a verifier record and provenance state; and export fails before an
audited approval but succeeds afterwards in all three required formats.

### Research success

Research success is not pre-defined as “the multi-agent system wins.” It means that:

- all four conditions are operationally defined and applied to comparable units of work;
- a frozen, independently checked reference set exists;
- quality, reliability, time, edit, and cost measures are collected without leakage;
- uncertainty and failure categories are reported, including negative results; and
- conclusions remain within the population, data, and protocol actually studied.

Effect-size or quality thresholds may be pre-registered later, but are deliberately absent
until domain reviewers define what is materially acceptable.

## Primary risks

| Risk | Consequence | Current control |
|---|---|---|
| Sensitive data leakage | Harm and ethics breach | Local ignored storage; classification gate; external LLM off |
| Prompt injection in public evidence | Agent manipulation | Evidence treated as untrusted data; detection and rejection |
| Hallucinated/misattributed claim | Misleading report | Source-linked claims; independent verifier; HITL export gate |
| Blank/zero collapse | Incorrect impact measurement | Explicit missing-state enum and tests |
| Entity collision | Cross-company contamination | Exact identifiers and ambiguity hold; no fuzzy auto-merge |
| Temporal leakage | Inflated evaluation | Period fields, frozen split protocol, no final-OOS tuning |
| Confirmation bias | Overstated dissertation conclusion | Fixed conditions/metrics and evidence-status map |
| Prototype mistaken for production | Security/operational risk | Loopback-only server; no auth/live connectors; explicit status |

## Change control

P0 changes require a requirement ID, affected invariant, relevant test, and documentation
update. P1/P2 work begins only after P0 evidence is frozen and the dissertation timeline
permits it. Data access, participant recruitment, external model processing, deployment,
or publication requires separate explicit authority.
