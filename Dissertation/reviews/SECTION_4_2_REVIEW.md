```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: SECTION_REVIEW
  section: "4.2 Architecture and local deployment"
  section_type: "system design and implementation"
  round: 1
  scope: "Dissertation/chapters/04_system_design.tex lines 11-27, including Figure 4.1 SYS-F1"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 0
    minor: 0
    optional: 0
  previous_findings:
    resolved: 0
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: none
```

# Section 4.2 independent review

## 1. Decision

**APPROVED.** Section 4.2 accurately explains the implemented local architecture and current
Docker-local runtime while keeping construction, local checks, live-unrun research, held connectors
and absent production capability distinct; SYS-F1 is traceable, deterministic and cleanly rendered.

## 2. Scope and evidence consulted

- `Dissertation/chapters/04_system_design.tex` lines 11--27, claim-ledger rows
  `4.2-P1`--`4.2-P4`, the Section 4.2 evidence packet, report structure and audit-ledger row.
- Exact hash-pinned pages from Hevner et al., Peffers et al., Pineau et al., Gebru et al., NIST AI
  RMF 1.0 and the CDDO Generative AI Framework, plus bibliography, manifest and checksum bindings.
- Current runtime, FastAPI/Jinja, CLI, SQLite/Alembic, importer, source-registry, reporting and
  company-research code; Dockerfile, Compose configuration, architecture, requirements, security
  and project-scope contracts; and the selected tests named by SYS-F1.
- `sys_f1_architecture_deployment_boundary.{py,svg,pdf,txt}` and provenance JSON; independent
  input/output hash audit, three repeat renders, PDF vector/resource inspection and SVG
  accessibility inspection.
- Current Compose configuration hash and read-only inspection of the running container, loopback
  health endpoint, strict source checker, eight focused tests, fresh Tectonic build, PDF text-order
  extraction and fresh raster inspection of physical pages 50--52.

No material evidence expected for this scoped architecture review was unavailable. No live research,
public-source retrieval or model call was executed or inferred.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose and alignment — meets.** Exactly 300 citation-stripped words across four substantive
  paragraphs, with 2/2/2/2 distinct admitted citations, fulfil the planned architecture/deployment
  role without duplicating later component sections.
- **Evidence and accuracy — meets.** FastAPI/Jinja and CLI entry points use the shared
  `Runtime`; SQLite foreign keys and Alembic-to-head startup, create-once checksum-bound raw/source
  files, and staged manifest-backed exports match the current implementation. The text does not
  convert code or health checks into utility, source truth or empirical evidence.
- **Technical validity — meets.** Dockerfile and Compose pin the Python base image, invoke the same
  CLI service, publish the host port on loopback, retain writable state only in the
  `portfolio-state` volume and keep the root filesystem read-only. The current Compose application
  hash is `836f4bf5e9f70b8e5dbea13d3cd4c83443530b11c624c764012e5310d2c0f150`;
  the running container is healthy with the declared mount and `127.0.0.1:8000` publication.
  Its `external_llm=enabled` health field is correctly treated as configuration state only.
- **Critical analysis — meets.** The section explicitly identifies absent authentication,
  authorisation, tenancy, scaling, managed secrets/storage, durable jobs, backup, observability and
  demonstrated recovery. Local controls are presented as attack-surface reductions, not hosted
  security, resilience or production readiness.
- **Structure and coherence — meets.** The argument moves from application/service boundaries to
  persistence, then deployment evidence and finally production exclusions; Figure 4.1 is introduced
  at the relevant transition.
- **Citations and scholarship — meets.** Each paragraph has two credible local sources and exact
  page fit: design-science sources separate artefact construction from evaluation; reproducibility
  and datasheet sources support explicit code/data/environment documentation; NIST and CDDO support
  deployment-context, testing, security, resilience, accountability and operational-control
  boundaries. Repository-specific architecture facts remain grounded in repository evidence.
- **Academic style — meets.** The prose is clear, calibrated British MSc-level writing with no
  promotional, anthropomorphic, live-result, production, compliance or user-benefit overclaim.
- **Figure and reproducibility — meets.** SYS-F1 clearly and redundantly encodes implemented/local,
  implemented/live-unrun, held and non-goal states; flows and boundaries agree with code and
  contracts. The caption, label and prose reference resolve as Figure 4.1. Renderer, SVG, PDF and
  TXT SHA-256 values are respectively `2624fb20c86fe34150e2e6acae244d2818d614d3323cf7cfd2cc4b35dae5a7e9`,
  `6aef9ac65c5d8112066e1ea9a97ada4a2444398aa5b5f71da1cca325a292f46d`,
  `3e2fe6bcd8839b0d558f57379d75e3176450383435ec37aefc146323b3d83a14` and
  `089711806de53be22b7e921a4b6e65091fb05b2f3bbad65ed0f45e06d38c69a0`; provenance SHA-256 is
  `4a17e8be4ec851ed3768b79f1626ea98ca5c7bc0ec980cd78ace22c84a7298a4`.
  All 30 inputs and four outputs match. Three fresh renders are byte-identical to the admitted PDF;
  the one-page vector PDF contains no image XObjects, while the SVG title, description, line-style
  redundancy and complete TXT alternative preserve the declared accessibility boundary.
- **Validation and placement — meets.** All eight selected tests pass with one pre-existing
  Starlette TestClient deprecation warning. The strict source gate passes with 38 local PDFs and
  hashes, two immutable captures, 80 substantive paragraphs and 34 cited sources. Tectonic builds
  the 68-page A4 report successfully with no Section 4.2 or SYS-F1 warning. Physical page 50 contains
  the prose, page 51 contains the complete figure and caption, and Section 4.3 begins on page 52;
  fresh visual inspection found no blank page, clipping, overlap, unreadable element or float-order
  defect.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the stated
scope and evidence available.

No non-blocking note remains. This approval does not review or pre-approve Section 4.3.
