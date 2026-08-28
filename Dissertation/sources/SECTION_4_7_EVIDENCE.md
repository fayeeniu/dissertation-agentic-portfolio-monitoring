# Section 4.7 evidence packet: Bounded public-web company-research case study

Checked: 28 August 2026  
Draft state: SYS-F5 integrated; author source/build/render checks complete; round-one assessor gate
FAIL because the concurrently changing implementation is currently syntactically invalid  
Target: exactly 400 citation-stripped words in five substantive paragraphs

## Claim boundary

Section 4.7 describes the current working-tree implementation of a bounded public-company research
path. It treats Responses web search as URL discovery only, requires application-controlled guarded
capture, accepts only literal spans from stored redacted text, persists serial research tasks and
produces a deterministic pending-review profile with visible coverage gaps. The implementation and
tests are currently uncommitted. No live company, OpenAI, publisher, participant or production run
is claimed; no coverage, correctness, usefulness, investment-performance or superiority result is
inferred. This is implementation evidence within the dissertation's stated evaluation design, not
an additional empirical research question.

## Local-source admission

Every cited item resolves to a readable, hash-pinned local PDF in
`Dissertation/sources/MANIFEST.csv` and an existing bibliography entry:

- `openai2026websearch`: local PDF pp. 1--3 and 6 document Responses web search, URL annotations,
  source lists and domain filtering; the documentation does not prove this runtime called the API.
- `gao2023alce`: local PDF pp. 1--3 and 8--9 motivates evaluating factual correctness and citation
  quality separately; its benchmark scores do not transfer to this artefact.
- `gao2023rarr`: local PDF pp. 1--5 motivates attribution through retrieved evidence and warns that
  retrieval-augmented output can add, ignore or contradict evidence; it does not validate exact-span
  admission here.
- `greshake2023indirect`: local PDF pp. 1--5 and 25 demonstrates indirect prompt injection and
  source-manipulation risk in LLM-integrated applications; attack coverage is system-specific.
- `autio2024genai`: local PDF pp. 15--16, 44, 48 and 55--56 supports treating indirect prompt
  injection, component provenance, monitoring and human moderation as design risks and controls;
  this voluntary profile does not certify the implementation.
- `nist2023airmf`: local PDF pp. 33--35 supports documented measurement, monitoring, uncertainty
  and risk response; it does not establish operational effectiveness.

## Paragraph evidence map

### 4.7-P1 - gated discovery and URL-only authority

Claim purpose: describe public-case and reviewed-identity preconditions, `store=False` Responses web
discovery, strict returned-source URL admission, and the candidate-not-fact boundary.

- Academic evidence: `openai2026websearch`, PDF pp. 1--3 and 6; `gao2023alce`, PDF pp. 1--3 and
  8--9.
- Repository evidence: `src/portfolio_agent/company_research.py:361--400,1111--1211,2870--2990`;
  `docs/SOURCE_ADMISSION_REGISTER.md:20--35`.
- Test evidence: `tests/integration/test_company_research.py:1313--1366`;
  `tests/unit/test_company_research_fixtures.py:35--104`.

### 4.7-P2 - guarded capture and connection pinning

Claim purpose: describe scheme, credential, port, DNS, robots, redirect, MIME and byte checks, plus
the distinction between connecting to a validated public IP and preserving hostname-based TLS
verification.

- Academic evidence: `greshake2023indirect`, PDF pp. 1--5 and 25; `autio2024genai`, PDF pp. 15--16.
- Repository evidence: `src/portfolio_agent/company_research.py:361--400,824--897,1267--1402`.
  `_PinnedNetworkBackend` supplies the validated IP to the TCP backend, while the HTTP connection
  pool keeps a default SSL context and the original URL hostname for TLS processing.
- Test evidence: `tests/integration/test_company_research.py:1212--1310`. These are mock/resolver
  boundary tests, not evidence of a live publisher connection.

### 4.7-P3 - immutable redacted snapshots and literal-span admission

Claim purpose: describe public-text redaction, owner-scoped content-addressed snapshots, bounded
model input, literal containment/equality validation, cutoff checks and exact grounding of dates and
amounts.

- Academic evidence: `gao2023alce`, PDF pp. 1--3 and 8--9; `gao2023rarr`, PDF pp. 1--5;
  `autio2024genai`, PDF pp. 44, 55--56.
- Repository evidence: `src/portfolio_agent/company_research.py:734--820,1002--1055,2140--2212,
  2225--2540,3123--3171`.
- Test evidence: `tests/integration/test_company_research.py:337--478,892--1002,1177--1211`;
  `tests/unit/test_company_research_fixtures.py:105--167`.

### 4.7-P4 - serial persistence, budgets, telemetry and recovery

Claim purpose: explain the four-stage fingerprinted task sequence, prerequisite fencing, bounded
retries and elapsed/model/tool/token/source/byte/redirect budgets, together with named cancellation
and recorded interrupted-task recovery.

- Academic evidence: `nist2023airmf`, PDF pp. 33--35; `autio2024genai`, PDF pp. 44 and 48.
- Repository evidence: `src/portfolio_agent/company_research.py:91--101,1421--1508,1537--1774,
  1843--1941,2865--3106`.
- Test evidence: `tests/integration/test_company_research.py:508--803,1003--1176`.

### 4.7-P5 - deterministic gap-visible profile and live-unrun limit

Claim purpose: describe deterministic grouping, contradiction candidates, explicit source and
category coverage states, hash-bound pending-review output and the non-empirical interpretation of
SYS-F5.

- Academic evidence: `gao2023alce`, PDF pp. 1--3 and 8--9; `gao2023rarr`, PDF pp. 1--5;
  `nist2023airmf`, PDF pp. 33--35.
- Repository evidence: `src/portfolio_agent/company_research.py:2542--2698,2810--2852,3108--3151,
  3190--3305`; `docs/SOURCE_ADMISSION_REGISTER.md:20--35`.
- Test evidence: `tests/integration/test_company_research.py:337--478,1038--1176`. All named cases
  use fake model clients, mock transports or controlled local persistence.

## SYS-F5 integration and interpretation

SYS-F5 is integrated immediately after Section 4.7 prose and before Section 4.8 using
`\input{exhibits/sys_f5_company_research_evidence_funnel.tex}`. It maps candidate discovery to
guarded capture, strict extraction and deterministic composition, then overlays persistence,
budget, cancellation, recovery, telemetry and named-review controls. The figure is an author
synthesis of code and synthetic tests, not an observation of live web behaviour or company
coverage. Its text alternative is
`Dissertation/exhibits/sys_f5_company_research_evidence_funnel.txt`.

The sealed artefact hashes are:

- TeX: `90d8fd5b301a794f0192a8b7c9b96931870f5c1bd8761dc33378ca951c808624`;
- text alternative: `85c4028f5e6cc7695387bf2d706d166f80363882f3e37412377b97a01936bdcd`;
- provenance JSON: `e60345d72dec4beed8e0ba8d1f55f63332f0706d87e53017a03e6d67c87ed864`.

All 11 inputs and both outputs matched the initial assessor snapshot. During review,
`company_research.py` changed from sealed SHA `6b4b1ea8...` to `13e65088...`; current closure is
therefore 10/11 inputs and 2/2 outputs. The provenance file is retained as a disclosed earlier
snapshot, not misreported as a current working-tree seal.

## Author validation state

- Citation-stripped prose: exactly 400 words in five paragraphs; word counts 79/78/76/78/89;
  distinct citation counts 2/2/3/2/3.
- New academic downloads or bibliography entries: none. Only six existing manifest-admitted local
  PDFs are cited.
- Live source/model/company action: not run and not required for Section 4.7 author validation.
- Initial focused company-research run: 34 passed and 1 failed. The failure followed the tested flow
  and was a deck-schema contract mismatch: implementation v3 versus test expectation v2
  (`SYS47-001`). After a concurrent implementation edit, the module fails Python parsing at line
  3300 and the suite cannot collect (`SYS47-002`). The report edit changed neither file.
- Strict source gate: passed with 38 local PDFs and hashes, two immutable web captures, 104
  substantive body paragraphs and 35 distinct cited sources.
- Tectonic build: passed, producing a 78-page A4 PDF. No warning originates in Section 4.7 or SYS-F5.
- Render inspection: physical page 60 contains the complete prose, page 61 the complete figure and
  page 62 only the untouched Section 4.8--4.9 headings; no clipping, overlap, stray blank page or
  unreadable element was found.
- Round-one assessor review: FAIL. `SYS47-002` is MAJOR and `SYS47-001` remains open. Section 4.8 is
  not drafted or reviewed.

## Prohibited overreach

- Do not call search snippets, annotations, titles or model prose evidence.
- Do not describe URL discovery as exhaustive crawling, or a missing candidate as an official
  no-record finding.
- Do not state that connection pinning, TLS, robots or prompt checks eliminate SSRF, rebinding,
  publisher-policy or prompt-injection risk.
- Do not state that exact spans, citations, hashes or deterministic composition establish truth,
  completeness, independence or investment quality.
- Do not state that synthetic tests prove live API behaviour, publisher availability, user benefit,
  production readiness or empirical research outcomes.
