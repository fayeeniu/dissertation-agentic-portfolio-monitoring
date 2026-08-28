# Section 4.6 evidence packet: Deterministic source adapters, time, and quality

Checked: 28 August 2026  
Draft state: SYS-T2 integrated and author checks complete; awaiting independent review  
Target: exactly 350 citation-stripped words in five substantive paragraphs

## Claim boundary

Section 4.6 describes the implemented, offline source-registry path and its synthetic Companies
House and UKRI replay adapters. It distinguishes pre-invocation capability or policy rejection from
persisted collection outcomes and downstream typed missingness. The prose does not claim live
registry access, current source truth, complete company coverage, evaluated benefit or production
fitness. The separately conditioned public-web path belongs to Section 4.7 and is not treated as a
registry-adapter result here.

## Paragraph evidence map

### 4.6-P1 — source-capability and pre-invocation boundary

Claim purpose: define the versioned request/manifest contract, exact reviewed identity and
fail-closed live-admission gate; keep a policy block distinct from a publisher no-record outcome.

- Academic evidence: `gebru2021datasheets`, PDF pp. 4--7 and 9--10;
  `pineau2021reproducibility`, PDF pp. 1--4 and 9--13.
- Repository evidence: `src/portfolio_agent/connectors/base.py:43--72`;
  `src/portfolio_agent/connectors/registry.py:98--130,697--756`;
  `docs/SOURCE_ADMISSION_REGISTER.md:19--45`; `docs/REQUIREMENTS.md:143--144`.

### 4.6-P2 — offline Companies House and UKRI replay

Claim purpose: describe the two exact-identifier synthetic replay adapters, their current manifest
versions, deterministic locators/corrections and persisted capture/derivation metadata while
withholding current-registry and coverage claims.

- Academic evidence: `galanakis2026chrt`, PDF pp. 1--3 and 6; `hardman2023small`, PDF pp. 3,
  5--6 and 21--25; `pineau2021reproducibility`, PDF pp. 1--4 and 9--13.
- Repository evidence: `src/portfolio_agent/connectors/companies_house.py:81--194,254--419`;
  `src/portfolio_agent/connectors/ukri.py:81--171,175--371`;
  `src/portfolio_agent/connectors/registry.py:98--230`;
  `docs/SOURCE_ADMISSION_REGISTER.md:8--12,36--53`.

### 4.6-P3 — cutoff, availability and cumulative-window rules

Claim purpose: separate publication/availability, effective, retrieval and value-period time;
exclude future or unavailable-at-cutoff evidence; require exact programme-start-to-cutoff coverage
and complete finite GBP awards before UKRI metric binding.

- Academic evidence: `hardman2023small`, PDF pp. 3, 5--6 and 21--25;
  `kapoor2023leakage`, PDF pp. 3 and 5; `nikiforova2020quality`, PDF pp. 1--3 and 15--17.
- Repository evidence: `src/portfolio_agent/temporal.py:42--101`;
  `src/portfolio_agent/connectors/companies_house.py:315--406`;
  `src/portfolio_agent/connectors/ukri.py:145--171,175--291,296--371`;
  `src/portfolio_agent/connectors/registry.py:839--867`;
  `docs/REQUIREMENTS.md:145--149`; `docs/SOURCE_ADMISSION_REGISTER.md:44--59`.

### 4.6-P4 — exact provenance and distinct terminal or missing states

Claim purpose: describe exact structured-locator and fact-contract validation, and distinguish
`no_record`, `source_unavailable`, pre-invocation block, typed `invalid` missingness and terminal
`failed` collection rather than collapsing all absence into one source result.

- Academic evidence: `gao2023alce`, PDF pp. 3--4 and 10; `gebru2021datasheets`, PDF pp. 4--7 and
  9--10; `nikiforova2020quality`, PDF pp. 2--3 and 15--17.
- Repository evidence: `src/portfolio_agent/connectors/base.py:75--118`;
  `src/portfolio_agent/connectors/registry.py:758--867`;
  `src/portfolio_agent/connectors/companies_house.py:155--200`;
  `src/portfolio_agent/enums.py:29--41,163--168`;
  `src/portfolio_agent/normalization.py:81--174`; `src/portfolio_agent/quality.py:214--251`.

### 4.6-P5 — quality dispositions, repeatability and residual limits

Claim purpose: explain the versioned exclude/hold/warn quality decisions, integrate SYS-T2 as a
non-empirical control map, and limit deterministic repeatability to admitted offline snapshots while
direct live registry access and source completeness remain unproven.

- Academic evidence: `nikiforova2020quality`, PDF pp. 1--3 and 15--17;
  `pineau2021reproducibility`, PDF pp. 1--4 and 9--13; `nist2023airmf`, PDF pp. 33--35.
- Repository evidence: `src/portfolio_agent/quality.py:18--60,161--285`;
  `docs/ARCHITECTURE.md:77--90,126--146`; `docs/REQUIREMENTS.md:143--149`;
  `docs/SOURCE_ADMISSION_REGISTER.md:3--12,33--59`.

## SYS-T2 integration and provenance

SYS-T2 is integrated immediately after Section 4.6 prose and before Section 4.7 using
`\input{exhibits/sys_t2_deterministic_adapter_capability_state_matrix.tex}`. Its embedded caption is
`Deterministic adapter and capability-state matrix` and its label is
`tab:sys-adapter-capability-state`. The table distinguishes registry admission, the two synthetic
offline replay adapters, held Companies House API mode and the separately conditioned public-web
boundary. It is an author synthesis and non-empirical control map, not a live-source, coverage,
quality, availability or production result.

The sealed artefact hashes are:

- TEX: `649f22dbf3ea77cbae10ce67d2a592ba9f35544292b5851cf169a1348469299b`;
- TXT alternative: `553bbf997b4a90b1b0984ef1ba7519bf8c3551ff63dd04aeb3171d1e62e98162`;
- provenance JSON: `4362a0988c0c6da5300c727f312a28ed6e6d41bedcb5f1fe065d619dcc263b9c`.

All 31 declared stable inputs and both declared outputs independently match the provenance file.
The provenance has no claim-ledger or Section 4.6 evidence-packet input, avoiding a circular seal.

## Current validation state

- Citation-stripped prose: exactly 350 words in five substantive paragraphs; paragraph word counts
  60/73/74/68/75; distinct citation counts 2/3/3/3/3.
- New academic sources or bibliography entries: none; all nine cited keys already resolve to
  locally admitted, hash-pinned PDFs and existing bibliography entries.
- Focused adapter/capability/time/quality tests: all 51 selected offline cases passed; no live
  source, public-web or external-model call was made.
- Strict bibliography/source gate: passed with 38 local PDFs and hashes, two immutable web
  captures, 99 substantive body paragraphs and 34 distinct cited sources.
- Tectonic build: passed, producing a 76-page A4 PDF. No overfull, underfull or package warning
  originates in Section 4.6 or SYS-T2; reported underfull warnings belong to earlier admitted
  exhibits, references and an appendix.
- Targeted order and render: physical page 58 contains the complete Section 4.6 prose, page 59 the
  complete one-page Table 4.2, and page 60 the still-heading-only Sections 4.7--4.9. The 150-dpi
  render shows no clipping, overlap, column collision, stray blank page or float-order regression.
- Live registry, public-web and model calls: prohibited for this section and not run.

## Prohibited overreach

- Do not describe synthetic replay as live registry verification or current company truth.
- Do not call a pre-invocation capability rejection a persisted source `blocked` state.
- Do not collapse no-record, unavailable, invalid, policy-blocked and failed outcomes into zero or
  one generic missing state.
- Do not allow retrieval time or a later correction to make evidence eligible at an earlier cutoff.
- Do not claim exact locators, hashes, deterministic replay or quality flags establish correctness,
  completeness, evaluated benefit or production readiness.
