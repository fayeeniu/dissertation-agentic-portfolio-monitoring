# ADR 0013: Next.js dashboard as the sole Docker UI

- Status: Accepted
- Date: 2026-08-30
- Supersedes the dual-dashboard decision in [ADR 0009](0009-agent-control-room-front-end.md)

## Context

The repository had two user interfaces over the same local service. The Docker image excluded the
Next.js control room and published the original FastAPI/Jinja dashboard, while the newer control
room required a separate host Node process. The documented one-command path therefore opened the
older UI rather than the maintained operator surface.

## Decision

1. Keep the FastAPI process as a private JSON API and approved-deck download service. Remove its
   Jinja routes, templates, browser forms, and legacy presentation helpers.
2. Build the Next.js application with `output: "standalone"` and run the standalone server as a
   non-root, read-only Docker target.
3. Run two Compose services: private `api` with the persistent state volume, and `app` for Next.js.
   Publish only `app` on `127.0.0.1:${PORTFOLIO_PORT:-8000}`.
4. Set `PORTFOLIO_API_ORIGIN=http://api:8000` so only the Next.js server-side proxy reaches FastAPI.
   Allow the exact `api` Host value and private container clients only in explicit Docker-local
   mode; arbitrary hosts and public client addresses remain rejected. The Next.js request proxy
   itself accepts only loopback Host values and same-origin state-changing requests before any
   handler can attach FastAPI's private CSRF credentials.
5. Preserve CSRF, configured reviewer identity, optimistic profile locks, named approval, secret
   injection, capability dropping, read-only roots, and the `/app/var` named volume.

## Consequences

- `docker compose up --build --wait` opens the Next.js dashboard at the existing configurable host
  URL; the backend has no host-published port.
- The original portfolio-import and generic report-review browser forms are removed. Their domain
  services and CLI remain, but the maintained browser workflow is company research and profile
  review.
- Native development still uses two processes, matching the production-shaped Docker topology.
- The OpenAI smoke command emits separate API and dashboard commands so its private experiment
  runtime opens through the maintained UI rather than the removed FastAPI root page.
- This remains a loopback-only research prototype without production authentication, tenancy,
  durable workers, or deployment authority.

## Validation

Validate the Docker contract test, focused FastAPI API/security tests, Next.js type/lint/build
gates, Compose configuration, a full Compose build/health wait, and browser checks against the
published Next.js surface.
