# Section 4.3 verified evidence packet

Scope: `4.3 Canonical data, persistence, and provenance` only. Academic page numbers are PDF
page numbers in the hash-pinned local files. Repository locators describe the current checkout on
27 August 2026. The implementation statements below are engineering-state claims, not empirical
quality, user-benefit, live-source, or production-readiness findings.

## Paragraph 1: canonical semantics and typed missingness

- `nikiforova2020quality`, PDF pp. 2--3 and 15--17: data quality is task- and object-specific;
  dimensions and executable requirements should be chosen for the intended use rather than reduced
  to one context-free score.
- `gebru2021datasheets`, PDF pp. 4--7 and 9--10: documentation should expose composition,
  collection, processing, missing information, external dependencies, errors, versions and
  maintenance limits.
- Repository: `src/portfolio_agent/catalogue.py:23--27,30--84,279--381` defines and hash-binds
  metric keys, types, units, sourceability, aliases and period semantics;
  `src/portfolio_agent/models.py:507--545,519--631` persists catalogue versions, periods and typed
  observations; `src/portfolio_agent/enums.py:29--41` and
  `src/portfolio_agent/normalization.py:11--27,81--174` keep blank, zero and other absence/error
  meanings distinct; `tests/unit/test_normalization.py:10--29` and
  `tests/integration/test_importers.py:18--48` exercise those distinctions.

Safe claim: these are versioned project semantics. They aid interpretability and prevent known
collapses, but they are not a universal taxonomy and do not replace domain approval.

## Paragraph 2: relational schema, migrations and application boundary

- `pineau2021reproducibility`, PDF pp. 1--4 and 9--13: repeatable work requires explicit artefacts,
  procedures, versions and reporting; reproducibility is not equivalent to external validity.
- `gebru2021datasheets`, PDF pp. 4--7: structured documentation should preserve how data was
  acquired, processed and validated, including relevant limitations.
- Repository: `src/portfolio_agent/db.py:18--56` enables SQLite foreign keys and upgrades through
  Alembic head; `src/portfolio_agent/models.py:106--142,507--696,787--993,1128--1144` defines
  canonical identity, observation, evidence, claim/report and export relationships plus uniqueness
  constraints; `alembic/versions/0001_initial_schema.py:14--379`,
  `0003_public_evidence_and_quality.py:16--358`, `0006_source_derivation_hash.py:15--31`,
  `0007_period_and_fact_provenance.py:15--58`, `0008_company_intelligence_foundation.py:16--220`
  and `0009_company_research_runs.py:16--215` provide the incremental migration path;
  `tests/integration/test_schema_equivalence.py:15--67` compares ORM and migrated schemas.

Safe claim: foreign keys, uniqueness and migration checks protect relational invariants. Several
semantic states remain strings or JSON validated by services, so schema consistency does not prove
source truth, full business meaning or production concurrency safety.

## Paragraph 3: immutable snapshots, capture metadata and derivation lineage

- `pineau2021reproducibility`, PDF pp. 1--4: repeatability depends on retaining sufficient data,
  code, procedures and configuration to reconstruct work.
- `gebru2021datasheets`, PDF pp. 6 and 9--10: external dependencies, archival versions, updates,
  errata and maintenance should be made visible.
- Repository: `src/portfolio_agent/importers.py:250--329,573--600` hashes imports and publishes
  checksum-checked create-once snapshots; `src/portfolio_agent/models.py:915--993` persists source,
  cutoff, locator, content hash, retrieval/publication times, derivation contract/hash and exact
  fact locators; `src/portfolio_agent/connectors/registry.py:115--260,300--440,670--701,1126--1159`
  writes, replays and verifies snapshots and their derivations;
  `tests/integration/test_connector_contracts.py:175--216,300--366` checks idempotent replay,
  structured provenance and derivation drift.
- The public-web engineering case records redacted visible-text hashes and capture metadata in
  `src/portfolio_agent/models.py:448--477` and `src/portfolio_agent/company_research.py:1581--1681,
  1702--1727`; its live smoke remains unrun (`docs/REQUIREMENTS.md:175--181`).

Safe claim: hashes and create-once storage support internal traceability and tamper/drift detection;
they do not prove content true, lawful to retain indefinitely, or permanently available upstream.

## Paragraph 4: claims, evidence, citations, contradiction and versions

- `gao2023alce`, PDF pp. 3--4 and 10: answer correctness, citation support and citation completeness
  are separate, and automated citation assessment has stated limitations.
- `gao2023rarr`, PDF pp. 1--2: retrieved evidence may be ignored or contradicted, while attribution
  does not establish that an attributed source is correct.
- Repository: `src/portfolio_agent/models.py:30--45,667--696,836--879` links claims to evidence and
  independent verification; `src/portfolio_agent/enums.py:214--219` preserves supported,
  contradicted, insufficient, stale and untrusted outcomes; `src/portfolio_agent/reporting.py:
  636--760` serialises claim provenance without raw evidence bodies. The separate engineering case
  persists exact-span claims in `src/portfolio_agent/models.py:480--504`, validates them in
  `src/portfolio_agent/company_research.py:1781--1818`, and records multi-source contradiction
  candidates in `src/portfolio_agent/company_research.py:1916--1963`.

Safe claim: the artefact preserves traceability and unresolved conflicts. The public-web path is
live-unrun, and neither citations, hashes nor named review guarantee correctness.

## Paragraph 5: report versions, approval and controlled export

- `nist2023airmf`, PDF pp. 33--35: risk measurement, testing, documentation, limitations and
  independent review should be explicit and proportionate to evaluated conditions.
- `amershi2019guidelines`, PDF pp. 3--5: human--AI interfaces should communicate capability and
  uncertainty and support correction, while the guidelines do not establish measured benefit for
  this artefact.
- `pineau2021reproducibility`, PDF pp. 1--4 and 9--13: retained procedures, artefacts, versions and
  limitations support repeatable reporting.
- Repository: `src/portfolio_agent/models.py:787--894,1128--1144` stores report/section versions,
  optimistic locks, content hash, named decisions and versioned manifests;
  `src/portfolio_agent/reporting.py:139--169,202--405,467--550,622--679` revokes approval after an
  edit, requires verified claims, stages versioned exports and re-checks manifests/files;
  `tests/integration/test_reporting.py:15--61,89--139,165--182` covers pre-approval refusal,
  reapproval, atomic failure and tamper detection. `docs/EVALUATION_PROTOCOL.md:5--10,37--46,
  108--130,146--149` keeps gold/reference and human outcomes protocol-only or null until authority
  and freeze.

Safe claim: version, optimistic lock, content hash and manifest checks bind controlled output state;
they do not demonstrate that review improves outcomes or that protocol-only evidence exists.

## SYS-F2 integration and provenance

Figure~`fig:sys-canonical-data-provenance-model` is integrated from
`exhibits/sys_f2_canonical_data_provenance_model.pdf`. It maps canonical meaning to persisted
evidence, derivation, claim, verification, versioned report and approval-bound export. The figure
distinguishes database constraints from application validation, implemented local/offline controls
from the live-unrun public capture route, and protocol-only evaluation fields from observed data.
Its caption identifies the exhibit as author synthesis and non-empirical, not an implementation
result or proof of source truth.

Sealed artefact hashes verified on 27 August 2026 and provenance refreshed on 28 August 2026:

- renderer: `9da2d43019c40537f0eef7f19aba14d6a0e2818777becc2bfe74d8a8eae27fc3`;
- SVG: `c13f246401c859f205d2e1719f673dd2e87e524d3ec3f81379c9880ab1945e71`;
- PDF: `b29e1a06a9a5150d9531a4c6d2e76381fa04422e5efe3f09bdd60d298302999d`;
- text alternative: `49393351182322e038eb02cd0658a5445137af46c089ad846a3ae723d3b57a92`;
- provenance: `45b2d5951e6c6bb19f684b982ed0a355d2d8585491de2166605288cee48f72c8`.

The final provenance binds `src/portfolio_agent/company_research.py` SHA-256
`dc3a71ef0633083a4ae84f4ff6eae571295f23f00daa45a3eea4cd702fb3643d` and
`tests/integration/test_company_research.py` SHA-256
`4011e0616598f52c76094331388f715c411b9e2a9c8582d6fbd680628a83d2e7`. The audit matches all
34 declared inputs and all four declared outputs; the PY, SVG, PDF and TXT hashes did not change. The final
section contains exactly 450 citation-stripped words in five substantive paragraphs, with
2/2/2/2/3 distinct admitted citations. Twenty focused model, snapshot, migration, provenance,
company-research and controlled-export tests passed without a live web or model call. The strict
source gate passed; Tectonic produced a 70-page manuscript. Physical pages 52--54 show Section 4.3
prose, the complete dedicated Figure 4.2 page, then Section 4.4, with no blank intervening page,
clipping, overlap, overfull box or scoped figure warning. Renderer Fontconfig cache diagnostics did
not affect the generated pages.

## Prohibited overreach

- Do not collapse blank, zero, absent, unavailable, invalid or not-applicable states.
- Do not equate a hash, constraint, citation, locator, provenance chain or named review with truth.
- Do not describe the public-web capture route as live-tested or exhaustively covering the web.
- Do not claim migrations establish production resilience, concurrency safety or legal compliance.
- Do not present protocol-only gold labels, reviewer outcomes or held conditions as persisted
  empirical evidence.
