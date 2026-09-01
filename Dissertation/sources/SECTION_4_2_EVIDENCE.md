# Section 4.2 verified evidence packet

Scope: `4.2 Architecture and local deployment` only. Page numbers are PDF page numbers in the
hash-pinned local files. Literature claim fit and the cited repository surfaces were rechecked on
31 August 2026. Repository paths establish this artefact's current implementation; the literature
supports the design and reporting principles, not the existence or effectiveness of the artefact.

## Paragraph 1: local application and service boundaries

- `hevner2004design`, PDF pp. 4, 9 and 11: design science distinguishes construction of a viable
  artefact from rigorous evaluation of its utility, quality and efficacy.
- `peffers2007dsrm`, PDF pp. 16--18: design and development include the artefact's desired
  functionality and architecture; demonstration and evaluation remain separate activities.
- Repository evidence: `dashboard/src/app/dash-api/[...path]/route.ts` is the same-origin server-side
  proxy; `src/portfolio_agent/web.py` constructs the private FastAPI service and
  `src/portfolio_agent/api.py` delegates API requests through selected domain services;
  `src/portfolio_agent/bootstrap.py` assembles importer, workflow, reports, sources and intake
  services; the CLI uses that Runtime for non-dashboard operations. `docs/ARCHITECTURE.md` and
  ADR-0013 record the sole Next.js dashboard and the private API boundary.

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
- Repository evidence: ADR-0013 defines native and Compose execution as separate Next.js and
  FastAPI processes. `compose.yaml` publishes only the dashboard at host loopback, exposes the API
  only inside the Compose network, mounts `portfolio-state` only on the API and makes both roots
  read-only. The Next.js proxy applies same-origin checks before attaching the private API's CSRF
  credentials; `web.py` enforces exact Host/client boundaries. Requirements and the source-admission
  register keep the implemented public-web path's live smoke and evaluation unrun.

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

The current non-empirical architecture figure shows the request and data path, not measured
performance: loopback browser to Next.js; server-side proxy to private FastAPI; shared Runtime and
CLI; SQLAlchemy/SQLite and local files; the two-service Compose boundary; the implemented but
live-unrun public-research path; held direct registry retrieval; and explicit production non-goals.
The manuscript integrates the PNG with label `fig:sys-architecture-deployment-boundary`. SHA-256
values are MMD `667b4358131ce517b6ad016b481e277da57f0b7b0ef553f982a2602fe4d14d5a`, PNG
`3f1e100e25e4e583253c94391edf8ceffec074a1bde465ae89882caaac7bd7af`, TXT
`3b5e8cd03b6566bab18e95f366527e3296834cb3365846bd9a50117c7654fce2`, and provenance JSON
`3c89446e602caa07f545cc4d834efdf81db1a262f4d838ac0c661e5ba01dfcfb`. The prior SVG/PDF/Python
assets are explicitly superseded and are not referenced by the manuscript.

## Prohibited overreach

- Do not call the system a microservice, distributed, asynchronous, multi-user or production
  architecture.
- Do not claim that Docker, loopback binding, hashing, tests or a health endpoint prove production
  security, resilience, backup or external validity.
- Do not imply the public-web company-research path has completed a live smoke or evaluation.
- Do not imply implementation evidence answers RQ1--RQ3 or establishes user benefit.

## Author validation record

- Six focused current-candidate tests pass: the Docker/Next.js topology contract, proxy credential
  guards, private FastAPI route/security checks and Alembic-head/ORM schema equivalence. One
  dependency deprecation warning remains. These are local static/API/schema checks; no browser,
  Compose runtime, live source or model call was run for this refresh.
- The Mermaid source/render manifest passes with the refreshed SYS-F1 source and PNG hashes. The
  current PNG was inspected directly and is legible without clipping or overlap.
- Whole-dissertation source, citation, build and integrated-page results are recorded by the final
  document sweep rather than inferred here.
