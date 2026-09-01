# Architecture decision records

Accepted decisions describe the P0 research prototype, not irreversible production choices.
Supersede an ADR with a new record; do not rewrite the original rationale after empirical results
are known.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-python-fastapi-stack.md) | Python/FastAPI/Pydantic/SQLAlchemy local stack | Accepted |
| [0002](0002-bounded-functional-agents.md) | Bounded functional roles with independent verifier | Accepted |
| [0003](0003-local-sqlite-and-immutable-files.md) | SQLite metadata plus immutable ignored files | Accepted |
| [0004](0004-deterministic-first-model-routing.md) | Deterministic-first, guarded `gpt-5.4-mini` → `gpt-5.4` route | Superseded by 0011 |
| [0005](0005-json-markdown-html-reports.md) | Canonical JSON plus Markdown and accessible HTML | Accepted |
| [0006](0006-uk-public-evidence-boundaries.md) | Exact UK identity/source/time boundaries, descriptive context, and sealed evaluation | Accepted offline; live gates open |
| [0007](0007-offline-company-intelligence-foundation.md) | Offline company-intelligence case and hybrid-intake foundation | Accepted |
| [0008](0008-bounded-live-company-research.md) | Bounded live company research and cited deck | Accepted |
| [0009](0009-agent-control-room-front-end.md) | Next.js control room over a read-only JSON projection | Superseded by 0013 |
| [0010](0010-two-tier-research-model-routing.md) | `gpt-5.4` reasoning stages, `gpt-5.4-mini` repair attempts | Superseded by 0011 |
| [0011](0011-gpt-5-6-luna-routing.md) | `gpt-5.6-luna` for every active model call, differentiated by reasoning effort | Accepted |
| [0012](0012-public-signals-and-evidence-dossier.md) | Separate exact metric evidence from related public signals in an evidence-led HTML dossier | Accepted |
| [0013](0013-nextjs-dashboard-docker-default.md) | Next.js dashboard as the sole Docker UI over a private FastAPI service | Accepted |
