# Section 4.4 evidence packet: Intake and legal-identity control

Checked: 28 August 2026  
Draft state: SYS44-001 corrected; awaiting round-two review  
Target: exactly 350 citation-stripped words in four substantive paragraphs

## Claim boundary

Section 4.4 describes implemented local intake and identity controls. It distinguishes structural identifier validation from registry verification, submitted identity claims from accepted legal identity, synchronous idempotent reuse from distributed exactly-once processing, and offline replay from current live-registry truth. It does not claim that a checksum proves factual correctness, that names or domains establish legal identity, that fuzzy linkage is error-free, or that direct Companies House retrieval has run.

## Paragraph evidence map

### 4.4-P1 — portfolio-file admission and explicit holds

Claim purpose: describe XLSX/CSV/JSON admission, original-byte hashing, create-once snapshots, hash-and-period reuse, compatibility checks, deterministic identity resolution and counted conflict holds. State that checksums aid integrity and repeatability but do not prove truth.

- Academic evidence: `pineau2021reproducibility`, PDF pp. 1--4 and 9--13; `gebru2021datasheets`, PDF pp. 4--7.
- Repository evidence: `src/portfolio_agent/importers.py:189--250,263--329,343--363,520--545,553--590`.
- Test evidence: `tests/integration/test_importers.py:18--48,140--166`.

### 4.4-P2 — exact company-intelligence intake without live verification

Claim purpose: explain Companies House-number-only admission and exact structural normalisation; separate new unresolved placeholders from confirmed registry identity; preserve submitted website/name/document claims, pending domains and untrusted checksum-bound documents.

- Academic evidence: `galanakis2026chrt`, PDF pp. 1--3 and 6; `hardman2023small`, PDF pp. 3, 5--6 and 21--25.
- Repository evidence: `src/portfolio_agent/company_intelligence.py:113--150,442--545,678--801`.
- Test evidence: `tests/integration/test_company_intelligence.py:50--229`.

### 4.4-P3 — named exact-identifier decision and conflict handling

Claim purpose: require a named accept/reject decision with reason before identity readiness; preserve identifier/name, classification and domain conflicts; exclude fuzzy automatic merging and name-only legal identity; expose the conservative recall trade-off and residual linkage error.

- Academic evidence: `thorne2026funding`, PDF pp. 5--6; `surak2026gateways`, PDF p. 6; `galanakis2026chrt`, PDF pp. 1--3 and 6.
- Repository evidence: `src/portfolio_agent/identity.py:1--5,50--70,107--206,289--612`; `src/portfolio_agent/company_intelligence.py:361--440`; `src/portfolio_agent/models.py:125--194,287--330`.
- Test evidence: `tests/integration/test_identity_migration.py:152--245`.

### 4.4-P4 — local reuse, downstream source authority and live hold

Claim purpose: describe fingerprint-backed artefact/case reuse, the database uniqueness boundary and create-once document-race handling; avoid claiming multi-worker exactly-once operation; require reviewed identifier/source/company agreement; keep direct live Companies House access at the documented G2 hold.

- Academic evidence: `pineau2021reproducibility`, PDF pp. 1--4 and 9--13; `gebru2021datasheets`, PDF pp. 4--7; `galanakis2026chrt`, PDF pp. 1--3 and 6.
- Repository evidence: `src/portfolio_agent/company_intelligence.py:520--565,759--801`; `src/portfolio_agent/models.py:260--281`; `src/portfolio_agent/connectors/registry.py:697--756`; `src/portfolio_agent/connectors/companies_house.py:81--153,196--200`; `docs/REQUIREMENTS.md:161--169,197--205`; `docs/SECURITY_AND_DATA_GOVERNANCE.md:42--54`.

## Visual boundary

SYS-F3 is integrated immediately after the prose and before Section 4.5 as Figure `fig:sys-legal-identity-decision-flow`. It is an author synthesis of implemented local controls and held live-source boundaries, and is conceptual and non-empirical. The visual-track seal is: renderer PY `ed1cf107c12cca113849caef0e815d374db53379657f14f26b48a0101b3ac923`; source SVG `d1b8021e25339361f691f16e4e7953d8658fb75451cafb17cbd747d9aee5bcca`; PDF `95bda14a1832977fd847f5e698f3fbe47ab21dd1484102139fd9bd7c5a378ff4`; TXT alternative `3a9f0d9e0a3e1905f1abf1b0958672fa4f50ba4bd3168c9364ca1ff28c066cb4`; refreshed provenance JSON `a119b67b132f2b81ccc2f75cff53b741d10e481efb1fd6eb75b0a6dc1a8e8b98`. All 27 declared stable inputs and four outputs match. The separately checked workflow files remain outside that narrow stable seal. The provenance records a passing fake/synthetic workflow snapshot with `src/portfolio_agent/company_research.py` SHA `4988b8f03601d0432da6e1753677fbee299c5102a492511273839b243c5986b7` and `tests/integration/test_company_research.py` SHA `5cc13f1c1168c496b516f42a6be309c545cc706b6c525bf112273842a1a9ff9c`; this is supplementary engineering evidence, not live-source, empirical or production evidence. The two selected `tests/integration/test_control_room_api.py` checks are also supplementary unpinned validation: that mutable test file is not a sealed input.

## Validation state

- Citation-stripped prose: exactly 350 words in four substantive paragraphs; distinct citation counts 2/2/3/3, including the substantive Figure reference.
- SYS-F3 focused selection: 15 local test cases passed on 28 August 2026 with no live Companies House, public-web or model call. This selection includes two passing `test_control_room_api.py` checks as supplementary unpinned validation; it does not seal that file. The separately named full fake/synthetic workflow case also passed at the provenance-recorded snapshot above. These mutable workflow and control-room surfaces are not members of the 27-input seal, and neither validation is evidence of live-source quality, empirical effectiveness or production readiness.
- Strict bibliography/source gate: passed on 28 August 2026; 38 local PDFs and hashes, two immutable web captures, 89 substantive body paragraphs and 34 distinct cited sources verified.
- Tectonic build: passed, producing a 72-page PDF. No warning originated in Section 4.4 or SYS-F3; the emitted underfull warnings belong to earlier admitted tables, references and an appendix.
- Targeted order/render inspection: physical page 54 contains the complete Section 4.4 prose, page 55 contains the complete dedicated Figure 4.3 and caption, and page 56 begins Section 4.5 followed by the still-empty later Chapter 4 headings. The 150-dpi renders show no clipping, overlap, stray blank page or float-order regression. The Poppler wrapper emitted local font-cache configuration messages while successfully producing the inspected images; these are renderer-environment messages, not PDF layout warnings.
- SYS44-001 status search: only the refreshed provenance and passing workflow state remain on the Section 4.4 evidence-packet, claim-ledger and section-ledger surfaces.
- Live registry, public-web and model calls: prohibited for this section and not run.
