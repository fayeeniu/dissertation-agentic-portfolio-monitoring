```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: SECTION_REVIEW
  section: "4.3 Canonical data, persistence, and provenance"
  section_type: "system design and implementation"
  round: 1
  scope: "Dissertation/chapters/04_system_design.tex lines 29-47, including Figure 4.2 SYS-F2"
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

# Section 4.3 independent review

## 1. Decision

**APPROVED.** Section 4.3 accurately describes the implemented canonical-data, provenance,
approval and export contracts while separating the locally tested report path, the live-unrun
company-research path and protocol-only evaluation records; SYS-F2 is traceable, deterministic and
cleanly rendered.

## 2. Scope and evidence consulted

- `Dissertation/chapters/04_system_design.tex` lines 29--47, claim-ledger rows
  `4.3-P1`--`4.3-P5`, the Section 4.3 evidence packet, report structure and audit-ledger row.
- Exact hash-pinned pages from Nikiforova et al., Gebru et al., Pineau et al., Gao et al. (ALCE),
  Gao et al. (RARR), NIST AI RMF 1.0 and Amershi et al., plus bibliography, manifest and checksum
  bindings.
- Current data dictionary, requirements, architecture, project charter, evaluation protocol and
  local-storage/public-research ADRs; SQLAlchemy models, enums, normalisation, import, source-
  registry, reporting, verification and company-research code; Alembic revisions 0006--0009 and
  the selected migration/schema tests.
- `sys_f2_canonical_data_provenance_model.{py,svg,pdf,txt}` and provenance JSON; independent
  input/output hash audit, three repeat renders, PDF vector/resource inspection and SVG
  accessibility inspection.
- Twenty focused unit, integration, schema and migration cases, the strict source checker, a fresh
  Tectonic build, PDF text-order extraction and fresh raster inspection of physical pages 52--54.

No material evidence expected for this scoped system-design review was unavailable. No live
research, public-source retrieval, participant action or external-model call was executed or
inferred.

## 3. Blocking findings

None.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose and alignment — meets.** Exactly 450 citation-stripped words across five substantive
  paragraphs, with 2/2/2/2/3 distinct admitted citations, fulfil the planned canonical-data,
  persistence and provenance role without pre-empting later source-adapter or review sections.
- **Evidence and accuracy — meets.** The versioned catalogue, company/metric/period observation
  identity, original-versus-normalised values and complete 12-state `MissingState` taxonomy match
  the current data dictionary, enums, normaliser, models and importer. The prose names eight
  representative typed states without implying that this is the exhaustive taxonomy; SYS-F2 and
  its TXT alternative state all 12.
- **Technical validity — meets.** SQLite relationships and application-validated string/JSON
  semantics, migrations through 0009, create-once local snapshots, source and derivation hashes,
  exact fact locators, many-to-many claim/evidence links, separate verification records, append-
  versioned report sections, optimistic locking, approval invalidation and manifest-verified
  export agree with current code and focused tests. Schema equivalence and populated-downgrade
  preflight behaviour are tested rather than inferred from migration prose.
- **Critical analysis — meets.** The text explicitly states that hashes and citations do not prove
  truth, source availability or correctness; database consistency does not establish business
  meaning or concurrent production use; named human resolution remains fallible; and the current
  implementation does not demonstrate review benefit.
- **Evidence-state discipline — meets.** The canonical report path is implemented and locally
  tested. Guarded public-web capture, exact-span company-research claims, contradiction candidates
  and named profile review are implemented with fake, synthetic and adversarial tests but remain
  live-unrun. Gold labels, reviewer outcomes, D1/D2 and C0/C3 observations remain protocol-only or
  null pending authority. No result, production, cloud-storage, source-truth or legal-compliance
  claim is made.
- **Structure and coherence — meets.** The argument proceeds from semantics to relational
  persistence, immutable evidence, claim verification, and finally approval-bound export. The
  figure reference closes the argument and the subsequent page break preserves the intended
  chapter sequence.
- **Citations and scholarship — meets.** Every paragraph has at least two credible local sources
  with exact page fit. Nikiforova and Gebru support use-context and documentation boundaries;
  Pineau supports explicit versioned artefacts and reproducibility controls; ALCE and RARR support
  separating attribution/citation support from correctness; and NIST, Amershi and Pineau support
  documented oversight, correction and reproducible reporting. Repository-specific statements
  remain grounded in repository evidence rather than attributed to those sources.
- **Academic style — meets.** The prose is calibrated British MSc-level technical writing with
  clear limitations and no anthropomorphism, promotional language, causal user-benefit claim or
  unjustified empirical generalisation.
- **Figure and reproducibility — meets.** SYS-F2 redundantly encodes implemented/local,
  implemented/live-unrun and protocol-only/unpopulated states; its model agrees with code and
  contracts. The caption, label and prose reference resolve as Figure 4.2. Renderer, SVG, PDF and
  TXT SHA-256 values are respectively `9da2d43019c40537f0eef7f19aba14d6a0e2818777becc2bfe74d8a8eae27fc3`,
  `c13f246401c859f205d2e1719f673dd2e87e524d3ec3f81379c9880ab1945e71`,
  `b29e1a06a9a5150d9531a4c6d2e76381fa04422e5efe3f09bdd60d298302999d` and
  `49393351182322e038eb02cd0658a5445137af46c089ad846a3ae723d3b57a92`; provenance SHA-256 is
  `45b2d5951e6c6bb19f684b982ed0a355d2d8585491de2166605288cee48f72c8`.
  All 34 inputs and four outputs match, including current `company_research.py` and its focused
  integration test. Three fresh renders using the provenance-declared Python runtime are byte-
  identical to the admitted PDF. The one-page PDF has no image XObjects; SVG role, title,
  description, textual status labels, line-pattern redundancy and complete TXT alternative
  preserve the declared accessibility boundary.
- **Validation and placement — meets.** All 20 selected cases pass with one pre-existing Starlette
  TestClient deprecation warning. The strict source gate passes with 38 local PDFs and hashes, two
  immutable captures, 85 substantive paragraphs and 34 cited sources. Tectonic builds the 70-page
  A4 report successfully with no Section 4.3 or SYS-F2 warning. Physical page 52 contains the
  complete prose, page 53 contains the complete figure and caption, and Section 4.4 begins on page
  54; fresh visual inspection found no blank inserted page, clipping, overlap, unreadable element
  or float-order defect.

## 7. Handoff

No unresolved blocker or major finding remains. This section passes the reviewer gate for the
stated scope and evidence available.

No non-blocking note remains. This approval does not review or pre-approve Section 4.4.
