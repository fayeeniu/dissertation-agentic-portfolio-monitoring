# UK public-evidence implementation traceability

Snapshot date: 2026-08-26. This matrix describes repository implementation evidence, not real
portfolio accuracy, source-law approval, human-study results, or production readiness.

| Packet / requirements | Implementation | Narrow proof | Dissertation artifact / boundary |
|---|---|---|---|
| P00, NFR-REL-001 | ORM metadata aligned; runtime Alembic; revisions `0001`–`0007`; lossful 0001 downgrade rejected before mutation | `test_schema_equivalence.py`; legacy 0001→head→0001→head FK round trip; duplicate legacy identifier migration; non-null v1-hash 0006→0007 replay; duplicate-name downgrade preflight; `alembic check` | Migration method; explicit rollback/data-integrity boundary |
| P01, FR-CBIT-001 | `cbit_contract.py`, version/hash catalogue and admitted source definitions | `test_cbit_contract.py` exact rows/aliases/profile/source rules | `DATA_DICTIONARY.md`; ADR-0006 |
| P02, FR-CBIT-002 | CBIT detector, cutoff, programme membership, formula/mixed holds, narratives, aggregate issues | `test_cbit_importer.py`; invalid/future programme-date tests; restricted counts/codes-only local smoke | Input profile, programme-window, and missingness tables; no names/values in Git |
| P03, FR-ID-001–004 | source-scoped identifiers, non-unique name search, candidates/decisions; public IDs stay unresolved until named review | `test_identity_migration.py`; source-registry cross-company/unreviewed/expired rejection; UI identity route | Figure 4 identity funnel; G2 authority still open |
| P04, FR-SRC-001–002 | source manifests/registry with fact-key→metric/method/schema/unit/currency binding, bounded GET client, immutable fingerprints/snapshots, versioned derivation hashes, stable event locators, complete fact provenance | `test_connector_contracts.py` including cross-metric rejection, retry/bounds, missing provenance, v1/v2 hashes, raw/derived drift, replay, multi-fact, concurrent disagreement/file publication, metadata-failure retention | Source admission register; no default network |
| P05, FR-TIME-001–002, FR-QUAL-001 | UK cutoff time, persisted programme intervals, run-relative evidence decisions, quality v2 rules/violations, distinct no-record/unavailable/failure outcomes | `test_temporal_quality.py`; same evidence across two cutoffs; cumulative-window/abstention tests; terminal-state `test_quality_workflow.py`; verifier permutations | Figures 5, 8, 9; no global quality score |
| P06, FR-CH-001 | exact-number Companies House replay plus gated read-only API adapter | `test_companies_house_connector.py` | Identity/filing/event method only; live G2 held |
| P07, FR-UKRI-001 | corrected UKRI lifecycle, stable-ID event locators, canonical snapshot-event associations, complete-GBP-only metric totals, restricted private-funding events | `test_ukri_events.py`; missing/non-GBP abstention; June→December→December replay; source-workflow tests | Figure 10; association is explicitly non-causal |
| P08, FR-DOC-001, FR-EXT-005–008 | structured/iXBRL/text extraction; exact locators and complete finite value spans/leaves; bounded model attempts | `test_document_extraction.py`; adversarial mocked `test_llm_boundary.py`; non-finite normalization/event tests | Figures 13–14; no real OpenAI call (G4 open) |
| P09, FR-CTX-001, FR-REP-001–002 | period-semantics/exposure-aware changes, segmented within-portfolio minimum-N five-number context, source/quality/run-scoped event tables | `test_context_reporting.py` equal-duration/programme-origin/cohort segmentation; `test_source_workflow_integration.py`; workflow/report tests | Figures 6–11 and report tables; illustrative context labelled; no external UK benchmark claim |
| P10, FR-UI-001–004, FR-REP-008–009 | identity/evidence UI, run-relative temporal provenance, run-scoped event view, CSRF/Host/loopback, configured actor, lock version, atomic export | `test_web.py`; later-cutoff non-leakage UI/export test; `test_reporting.py` stale/failure paths | Visual report dashboard; browser accessibility audit unrun |
| P11, FR-EVAL-001, NFR-RES-002 | hashed namespaced D0, protocol D1, pathless sealed D2, layer outcomes/nulls | `test_evaluation.py` manifest/leakage/seal/repeats/parity | Figure 12; D0 mechanism evidence only |
| P12, FR-VIZ-001 | requirements/data/security/source/docs reconciliation; deterministic visual pack with checkout-independent manifest | `test_visualizations.py`; relocation determinism; link/ID traceability test; final gates/reviews | 15 SVGs, CSV/JSON manifests, textual alternatives |

## Frozen local manifests at this snapshot

| Artifact | SHA-256 | Meaning |
|---|---|---|
| `fixtures/evaluation_manifest.json` | `1c16234a0dbb965ba0db882531389ddcc52c588c9d7904ba964d480f1ce24254` | D0/D1/D2 admission state; does not unlock D2 |
| `fixtures/visualisation_pack.json` | `51fc848e921eb734c6ed3e54de44ffba5a4f1aef3fba66d20b5607597ca05869` | Synthetic/illustrative figure inputs |
| `docs/figures/generated/manifest.json` | `1e134851acc908d7f57c0de8db7ec00d40280e2a69adf84e319536c9e631e763` | 15 accessible SVG filenames, sources, N/cutoff, and per-file hashes; no checkout path |

These hashes change when the underlying artifacts are intentionally regenerated. Recompute them
for the final submitted revision; do not quote this development snapshot as the final Git evidence.

## Explicit evidence holds

| Gate | State | Prohibited claim/action |
|---|---|---|
| G2 | Open | No live Companies House/UKRI/other source retrieval or claim of licence admission |
| G3 | Open | No director/PSC personal-data graph |
| G4 | Open | No real OpenAI experiment or performance/cost claim |
| G5 | Open | No supplied-data scoring, participant observation, or manual/HITL result |
| G6 | Open | No D2 access, tuning, or final comparative result |

Final completion of the engineering packet requires the exact-state full validation and two
independent reviews recorded in the engineering ledger. Dissertation empirical completion remains
a later governed research process described in `WAYFINDER.md`.
