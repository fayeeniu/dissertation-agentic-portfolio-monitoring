# Section 4.2 verified evidence packet

Scope: `4.2 Architecture and local deployment` only. Page numbers are PDF page numbers in the
hash-pinned local files. Literature claim fit and the cited repository surfaces were checked on
27 August 2026. Repository paths establish this artefact's current implementation; the literature
supports the design and reporting principles, not the existence or effectiveness of the artefact.

## Paragraph 1: local application and service boundaries

- `hevner2004design`, PDF pp. 4, 9 and 11: design science distinguishes construction of a viable
  artefact from rigorous evaluation of its utility, quality and efficacy.
- `peffers2007dsrm`, PDF pp. 16--18: design and development include the artefact's desired
  functionality and architecture; demonstration and evaluation remain separate activities.
- Repository evidence: `src/portfolio_agent/web.py:825--840, 910--1006, 1273--1477` constructs the
  FastAPI/Jinja surface and delegates through the selected runtime; `src/portfolio_agent/bootstrap.py:
  45--110` assembles importer, workflow, reports, sources and intake services; `src/portfolio_agent/
  cli.py:62--173, 212--235, 274--327` exposes local serve/import/run/review/export operations through
  the same runtime; `docs/ARCHITECTURE.md:75--95` records component ownership.

Safe synthesis: describe a modular local artefact whose presentation, service and persistence
responsibilities are explicit. Do not infer utility, empirical quality or production suitability
from the code structure.

## Paragraph 2: relational state, schema lifecycle and immutable local files

- `pineau2021reproducibility`, PDF pp. 1--4 and 9--13: reproducibility depends on sufficiently
  specified code, data, procedures, environments and reporting, and is not a single binary score.
- `gebru2021datasheets`, PDF pp. 4--7: documentation should expose composition, collection,
  preprocessing, access, uses, limitations and maintenance rather than leave material context
  implicit.
- Repository evidence: `src/portfolio_agent/config.py:18--60` sets local SQLite/raw/source paths;
  `src/portfolio_agent/db.py:18--56` creates the engine, enables SQLite foreign keys and upgrades
  through Alembic; `src/portfolio_agent/importers.py:250--329, 573--590` binds database metadata to a
  checksum and create-once raw file; `src/portfolio_agent/connectors/registry.py:98--190,
  1121--1159` records source metadata and checksum-addressed snapshots; `src/portfolio_agent/
  reporting.py:520--607` verifies and stages manifest-backed exports.

Safe synthesis: local SQLite carries mutable relational state while checksum-addressed files retain
evidence/export bytes. Hashes and version records support integrity and traceability; they do not
prove truth, encryption, lawful authority or external reproducibility.

## Paragraph 3: loopback and Docker-local execution with held live evidence

- `pineau2021reproducibility`, PDF pp. 1--4 and 9--13: environment and execution detail should be
  recorded so implementation evidence can be rerun and qualified.
- `nist2023airmf`, PDF pp. 20--23 and 33--35: deployment context, security, resilience, testing,
  documentation and operational monitoring are distinct risk-management concerns.
- Repository evidence: `src/portfolio_agent/cli.py:153--170, 212--235` restricts native binding and
  defines Docker-local mode; `src/portfolio_agent/web.py:842--872, 911--918` enforces local clients,
  Host allowlisting, headers and health state; `Dockerfile:1--33` pins the base image and runs the
  CLI health-checked service as a non-root user; `compose.yaml:1--29, 49--50` publishes the port on
  host loopback, mounts `portfolio-state`, uses a read-only root filesystem and applies container
  restrictions; `docs/REQUIREMENTS.md:175--181, 197--217` and `README.md:527--535` keep the
  implemented public-web path's live smoke/evaluation unrun.

Safe synthesis: report the native and Docker-local mechanisms and checks separately from a live
company-research result. Configuration and engineering tests do not establish hosted behaviour.

## Paragraph 4: research-prototype boundary and production gaps

- `nist2023airmf`, PDF pp. 20--23 and 33--35: accountability, transparency, security, resilience,
  monitoring and documented deployment limitations remain lifecycle responsibilities.
- `cddo2023genai`, PDF pp. 52--55 and 72: accountability, purpose limitation, security, access
  control and human oversight require owned, risk-based operational controls.
- Repository evidence: `docs/PROJECT_CHARTER.md:77--84, 96--104, 128--146` limits the artefact and
  requires separate deployment authority; `docs/ARCHITECTURE.md:249--255` lists the synchronous/
  SQLite production gaps; `docs/SECURITY_AND_DATA_GOVERNANCE.md:197--218` prohibits remote exposure
  and identifies missing authentication, authorisation, tenancy, managed storage, logging,
  monitoring, backup/restore and reviewed recovery controls.

Safe synthesis: loopback, CSRF, file permissions and container restrictions reduce the bounded
local attack surface. They do not prove remote, multi-user, production-egress or disaster-recovery
properties.

## SYS-F1 integration boundary

The sealed non-empirical architecture figure shows the request and data path, not measured
performance: local browser and CLI entry points; FastAPI/Jinja/API presentation; shared runtime and
service layer; SQLAlchemy/SQLite metadata and audit; immutable local raw/source/export stores;
Alembic startup; Docker-local loopback/persistent-volume boundary; optional external research path
marked implemented but live-unrun; and a visible production-boundary stop. The integrated PDF is
`Dissertation/exhibits/sys_f1_architecture_deployment_boundary.pdf` with label
`fig:sys-architecture-deployment-boundary`. Verified SHA-256 values are: renderer PY
`2624fb20c86fe34150e2e6acae244d2818d614d3323cf7cfd2cc4b35dae5a7e9`; source SVG
`6aef9ac65c5d8112066e1ea9a97ada4a2444398aa5b5f71da1cca325a292f46d`; PDF
`3e2fe6bcd8839b0d558f57379d75e3176450383435ec37aefc146323b3d83a14`; TXT alternative
`089711806de53be22b7e921a4b6e65091fb05b2f3bbad65ed0f45e06d38c69a0`; and provenance JSON
`4a17e8be4ec851ed3768b79f1626ea98ca5c7bc0ec980cd78ace22c84a7298a4`. All 30 recorded inputs
and four outputs independently match their provenance hashes.

## Prohibited overreach

- Do not call the system a microservice, distributed, asynchronous, multi-user or production
  architecture.
- Do not claim that Docker, loopback binding, hashing, tests or a health endpoint prove production
  security, resilience, backup or external validity.
- Do not imply the public-web company-research path has completed a live smoke or evaluation.
- Do not imply implementation evidence answers RQ1--RQ3 or establishes user benefit.

## Author validation record

- Eight focused local tests passed: server-rendered pages/security headers, Host/CSRF/reviewer
  rejection, Docker-private-client filtering, immutable/idempotent import, Alembic/ORM schema
  equivalence, `0008` and `0009` empty-schema downgrade/re-upgrade, and finalized-export checksum
  verification. The only test diagnostic was the pre-existing Starlette TestClient/httpx deprecation
  warning.
- `docker compose config --quiet` passed. The current Compose app hash
  `836f4bf5e9f70b8e5dbea13d3cd4c83443530b11c624c764012e5310d2c0f150` matched the running
  `agentic-portfolio-app-1` label. Read-only root, the read/write `portfolio-state` mount at
  `/app/var`, `127.0.0.1:8000` publication and healthy status were inspected; the loopback health
  response was `{"status":"ok","external_llm":"enabled"}`. Enabled is configuration state only;
  no research stage, public-source retrieval or model call was executed.
- Strict source validation passed: 38 local PDFs and hashes, two immutable web captures, 80
  substantive body paragraphs and 34 distinct cited sources.
- Tectonic produced a 68-page PDF. No warning originated in Section 4.2 or SYS-F1; existing
  underfull-box warnings elsewhere remain non-blocking. Physical page 50 contains Section 4.2,
  page 51 contains the complete figure and caption, and page 52 begins Section 4.3. Targeted renders
  show no blank intervening page, clipping, overlap or heading-before-figure regression.
