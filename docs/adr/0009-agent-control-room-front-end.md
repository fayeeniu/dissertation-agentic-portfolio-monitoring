# ADR 0009: Separate Next.js control room over a read-only JSON projection

- Status: Accepted
- Date: 2026-08-27
- Extends ADRs [0001](0001-python-fastapi-stack.md), [0002](0002-bounded-functional-agents.md),
  and [0008](0008-bounded-live-company-research.md)

## Context

The bounded multi-agent research workflow in
[`company_research.py`](../../src/portfolio_agent/company_research.py) persists a genuine execution
record: four ordered tasks with input and output hashes, per-source acquisition outcomes, exact
evidence spans, a contradiction ledger and a named human approval gate. The server-rendered Jinja
surface presented that record as static tables, so the operator could read the result of a run but
could not see the system working, could not tell which role was active or blocked, and had no path
from a claim back to the snapshot that admitted it. Every stage advance was a full page reload.

The workflow *is* the product. Making it legible needs live state, orchestrated motion and
progressive disclosure — all client-side concerns that Jinja templates and a synchronous request
cycle serve badly.

## Decision

1. Add a read-only JSON projection layer, [`api.py`](../../src/portfolio_agent/api.py), mounted at
   `/api` on the existing application. It contains no business logic: every status, hash, count,
   duration and error it returns is read from a persisted row. Mutations delegate to the same
   services the Jinja routes call and reuse the same double-submit CSRF contract and the locally
   configured reviewer identity.
2. Build the operator surface as a separate Next.js application in `dashboard/`. It renders the
   agent topology from the persisted task and source rows rather than from a hard-coded diagram, and
   it reaches the research service only through a server-side proxy, so the browser never holds the
   CSRF token and the service keeps its loopback-only boundary.
3. Keep the Jinja surface in place. The two read the same records, and the research service remains
   usable without Node.
4. Reserve colour, glow and motion for real execution state. A node pulses only while its stage
   holds a claim on the run, a packet travels an edge only while work flows along it, and a lane
   changes state only when its persisted acquisition outcome changes. Reduced-motion preferences
   remove all of it without removing information.
5. Draw the execution graph as measured inline SVG over HTML nodes rather than adopting a graph
   library. The topology is a fixed six-stage spine with one fan-out band, so a layout engine would
   add a dependency and remove control over the state semantics that matter here.
6. Add an offline fixture research mode (`serve --fixture-research`) so the workflow can be
   rehearsed and regression tested without a model call or an outbound request. It replays recorded
   pages through the real orchestrator, the real snapshot checksums, the real exact-span validator
   and the real approval gate; it does not mock their results.

## Consequences

- The dashboard cannot show anything the workflow did not persist. A value with no recorded source
  reads as `Not recorded`, never as zero.
- Two processes now run in development. The control room degrades to an explicit service-unreachable
  message rather than a blank screen when the research service is down.
- Fixture runs are synthetic by construction. Every surface labels the mode, the intake
  classification stays `synthetic` or `public`, and the composed profile keeps its stated
  limitations.
- Adding a stage to the workflow requires a matching entry in the agent roster in `api.py`; the
  graph itself needs no change, because it is rendered from the persisted tasks.
- A production deployment still needs the authentication, tenant isolation and durable worker
  boundary that ADR 0008 defers. This ADR does not open any of those.
