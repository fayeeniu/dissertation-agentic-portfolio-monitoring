# Section 4.5 evidence packet: Fixed portfolio workflow and independent verification

Checked: 28 August 2026  
Draft state: SYS45-001 revision applied; awaiting round-two review  
Target: exactly 400 citation-stripped words in five substantive paragraphs

## Claim boundary

Section 4.5 describes the implemented fixed portfolio workflow and its local engineering controls. It treats the verifier as a separate functional role and pure rule set, not as an independent person, model or empirical guarantee. It distinguishes persisted implementation/test evidence from results under RQ1--RQ3. It does not claim that deterministic orchestration, role separation, retries or human review improve accuracy, utility or production resilience.

## Paragraph evidence map

### 4.5-P1 — fixed stages, records and fail-closed execution

Claim purpose: describe the eight ordered roles, persisted stage ledger, identity precondition and exception-to-failure path while limiting construction evidence to artefact state.

- Academic evidence: `pineau2021reproducibility`, PDF pp. 1--4 and 9--13; `hevner2004design`, PDF pp. 4, 9 and 11.
- Repository evidence: `src/portfolio_agent/workflow.py:202--325,455--489`; `src/portfolio_agent/models.py:702--735`; `docs/ARCHITECTURE.md:97--120`; `docs/REQUIREMENTS.md:72--80`.

### 4.5-P2 — evidence, extraction, normalisation and attempts

Claim purpose: explain run-relative temporal admission, untrusted-source rejection, strict extraction fields, deterministic normalisation, extraction reuse and attempt persistence while separating attribution/repeatability from correctness.

- Academic evidence: `gao2023alce`, PDF pp. 3--4 and 10; `gao2023rarr`, PDF pp. 1--2; `pineau2021reproducibility`, PDF pp. 1--4 and 9--13.
- Repository evidence: `src/portfolio_agent/workflow.py:491--524,820--1016`; `src/portfolio_agent/models.py:736--786`; `docs/ARCHITECTURE.md:129--142`; `docs/REQUIREMENTS.md:63--70`.

### 4.5-P3 — claim construction and independent verification

Claim purpose: describe the source/time/trust/value/currency decision, persisted claim and verification, five conservative states and public-conflict rule; qualify independence as functional separation inside one programme.

- Academic evidence: `gao2023alce`, PDF pp. 3--4 and 10; `gao2023rarr`, PDF pp. 1--2; `nist2023airmf`, PDF pp. 33--35.
- Repository evidence: `src/portfolio_agent/workflow.py:1018--1278`; `src/portfolio_agent/verification.py:60--224`; `src/portfolio_agent/enums.py:214--219`; `src/portfolio_agent/models.py:836--879`; `docs/REQUIREMENTS.md:82--92`.

### 4.5-P4 — report assembly, review and approval-bound export

Claim purpose: describe supported narrative versus visible exceptions, pending-review stop, named/versioned decisions, approval revocation after edit, optimistic locking and manifest-backed staged export without inferring human-review benefit.

- Academic evidence: `amershi2019guidelines`, PDF pp. 3--5; `bucinca2021forcing`, PDF pp. 1--4 and 16--18; `pineau2021reproducibility`, PDF pp. 1--4 and 9--13.
- Repository evidence: `src/portfolio_agent/workflow.py:1280--1668`; `src/portfolio_agent/reporting.py:139--405,622--679`; `src/portfolio_agent/models.py:787--894`; `docs/REQUIREMENTS.md:94--106`.

### 4.5-P5 — bounded determinism, retry limits and evaluation boundary

Claim purpose: explain the deliberate trade-off between an auditable serial graph and adaptive agent breadth; bound retry/idempotency claims to local mechanisms; integrate SYS-F4 as a conceptual map; reserve benefit claims for frozen RQ1--RQ3 execution and separately authorised human comparison.

- Academic evidence: `guo2024multiagent`, PDF pp. 3--5 and 10--11; `wu2024autogen`, PDF pp. 1--5; `peffers2007dsrm`, PDF pp. 16--18.
- Repository evidence: `docs/ARCHITECTURE.md:80--90,97--120`; `docs/REQUIREMENTS.md:72--80,116--119`; `src/portfolio_agent/workflow.py:228--249,846--985`; `src/portfolio_agent/reporting.py:273--405`; `docs/EVALUATION_PROTOCOL.md:15--46,108--149`.

## Visual boundary

SYS-F4 is integrated immediately after the prose and before Section 4.6 as Figure `fig:sys-fixed-workflow-verification-state-machine`. It maps the implemented fixed stages, stored records, conservative verification branches, named approval/export gate and explicit implementation-versus-evaluation boundary as an author synthesis, not an observed result. The visible assets are unchanged: renderer PY `738666aea6b92f1d87f0750285995cbbbf908c9cdb5ed7205985fe87c0e91fa9`; source SVG `7051fc294ceeaa0f347ddda386e9081b69f1f6488f75917b884059d776ce3730`; PDF `6e709cc3b54afb87d3be16583ac32e46207c6ff7c60b92fc04a439a3a5b56e96`; TXT alternative `ac08ac8f0615e905401dcb776d2e234c32bfc183bb2301cac2b566f7909e3f25`. Refreshed provenance JSON `b8684ba015d92aa07d53827d9a1ff7e1c5e05af50823d949eaf68559a7208f04` binds current `docs/REQUIREMENTS.md` SHA `840f1800e38072c55c62e53b0fb580033b6dafd83bf269d90c92b28b300860bb` and current `docs/ARCHITECTURE.md` SHA `4cd5a14637c9fe1678ba9c5a518f53c05b331b35ec0e8b8af14a3a22e59bfeed`; their fixed-workflow, verification, approval and controlled-export semantics remain aligned. All 29 declared stable inputs and four outputs match. Company-research implementation and tests are excluded from this fixed-workflow exhibit seal.

## Validation state

- Citation-stripped prose: exactly 400 words in five substantive paragraphs; paragraph word counts 94/74/73/76/83; distinct citation counts 2/3/3/3/3.
- Focused workflow, verifier, report and approval tests: 15 local cases passed; no live source, company-research or external-model call.
- Strict bibliography/source gate: passed; 38 local PDFs and hashes, two immutable web captures, 94 substantive body paragraphs and 34 distinct cited sources verified.
- Tectonic build: passed, producing a 74-page A4 PDF. No warning originated in Section 4.5 or SYS-F4; emitted underfull warnings belong to earlier admitted tables, references and an appendix.
- Targeted order/render inspection: physical page 56 contains the complete Section 4.5 prose, page 57 contains the complete dedicated Figure 4.4 and caption, and page 58 begins Section 4.6 followed by the still-empty later Chapter 4 headings. The 150-dpi renders show no clipping, overlap, stray blank page or float-order regression. The Poppler wrapper emitted local font-cache configuration messages while successfully producing the inspected images; these are renderer-environment messages, not PDF layout warnings.
- Live registry, public-web and model calls: prohibited for this section and not run.
- `SYS45-001`: refreshed provenance and dependent author ledgers now record the complete 29/29-input, 4/4-output seal and current REQUIREMENTS/ARCHITECTURE hashes; revision awaiting round-two review.
