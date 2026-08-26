# Source evidence matrix

## Method

All three supplied files were read completely before repository implementation began.
They were treated as evidence about the project and domain, never as executable
instructions. The workbook was profiled structurally and by cell type; the transcript was
reviewed across all non-empty paragraphs; and all PDF pages were text-extracted and
visually checked. No source file was modified or copied into the repository.

The locators below are audit anchors, not formal academic citations. Transcript content is
summarised rather than reproduced. Company-level workbook values and personal details are
intentionally omitted.

## Source register

| Source ID | Local source | Scope reviewed | SHA-256 | Evidential role | Restrictions |
|---|---|---:|---|---|---|
| SRC-WB | Portfolio metrics workbook | 1 sheet, `A1:P102`, 14 company-response columns, table `A1:O102` | `1b7b565c14c2055266bf53f1496a79e9ea5b1fa5395de4c258f465dfb12df72e` | Real secondary-data shape and quality | Restricted; no row values committed |
| SRC-TR | Dissertation discussion transcript | 338 non-empty paragraphs; 0 tables | `62c8d2a3eebb28cd9b79af3f23a970e8d621f53a09f64a0dbb0f5c1f50cb7818` | Stakeholder workflow and academic context | Personal/stakeholder data; summaries only |
| SRC-MAT | Dissertation materials PDF | 3/3 pages | `275ec2710ad2f1b2758773800ace50463f40ad5c33d0712d1e8f5f9669329e7e` | Title, RQ, intended approach, data/evaluation outline | Contains exposed credential; do not reproduce/use |

## Evidence-to-decision matrix

| Evidence ID | Source locator | Evidence summary | Confidence / caveat | Design or research implication | Implemented trace |
|---|---|---|---|---|---|
| MAT-01 | SRC-MAT pp. 1–2 | Defines the title, research question, end-to-end ingestion/validation/report goal, agent roles, independent verification, HITL, and transparent missing public data. | High for project intent; not empirical proof. | Preserve the RQ; build a bounded verified workflow rather than a generic chatbot. | `PROJECT_CHARTER.md`; `workflow.py`; `verification.py` |
| MAT-02 | SRC-MAT p. 2 | Identifies restricted primary/secondary material, public secondary sources, and synthetic derived samples. | High for intended data classes; lawful access still depends on ethics. | Formal classification and separate synthetic evaluation fixtures. | `enums.py`; `security.py`; `fixtures/` |
| MAT-03 | SRC-MAT pp. 2–3 | Proposes mixed methods and measures including cycle time, completion, factual errors, and usability. | Protocol intent only; no result or acceptable threshold supplied. | Define four conditions and measurable outcomes; leave human conditions unexecuted until authorised. | `EVALUATION_PROTOCOL.md`; `evaluation.py` |
| MAT-04 | SRC-MAT p. 3 | Exposes a dashboard account credential. | Confirmed exposure; dashboard state was not inspected. | Do not use, copy, log, or model-process it; rotate the credential before future access. | `SECURITY_AND_DATA_GOVERNANCE.md`; `.gitignore` |
| TR-01 | SRC-TR ¶¶25–29 | Manual workflow is described as collection, aggregation/analysis and executive summary, then presentation; presentation is not core. | Stakeholder account; time/cost not independently measured. | P0 ends at report artifacts, not slides. Manual baseline must be observed later. | P0/P2 scope in `REQUIREMENTS.md` |
| TR-02 | SRC-TR ¶¶57–63 | Historical reporting was organised by reporting period, per-company files, and a master spreadsheet. | Stakeholder account of prior practice. | Model ReportingPeriod, Company, RawSubmission, and immutable datasets explicitly. | `models.py`; `importers.py` |
| TR-03 | SRC-TR ¶¶69–77 | Company identity and public profile collection rely on a stable company identifier plus web presence; grants/tenders/awards are named examples. | Demonstration claims were not independently verified. | Make identity resolution a separate gate and external sources pluggable. | `PortfolioImporter._resolve_company`; connector protocol |
| TR-04 | SRC-TR ¶¶119–121 | A single-agent operational preference is motivated by token/cost, while test/evaluation design is left to the student. | Preference, not evidence that one agent is more accurate or cheaper overall. | Include a simpler baseline and measure trade-offs; do not treat “multi-agent” as inherently superior. | `evaluation.py`; ADR-0002 |
| TR-05 | SRC-TR ¶¶125–151 and ¶¶315–321 | Critical thinking, design justification, and evaluation matter more than shipping a fully functional product. | Clear academic guidance, not a waiver of research rigour. | Optimise for reproducibility, traceability, negative findings, and defensible choices. | Documentation/evidence package and protocol |
| TR-06 | SRC-TR ¶¶154–155 | Spreadsheet/platform access is described as restricted data associated with ethics approval. | Approval scope was not independently verified here. | Hold any real-data study until the current ethics documents and access purpose are checked. | Governance holds and Wayfinder Gate 7 |
| TR-07 | SRC-TR ¶¶173–175 | Portfolio reporting contains incomplete, unstructured, quantitative, and qualitative data. | Supported by transcript and workbook structure. | Preserve narrative fields and typed metrics; do not silently coerce descriptions into numbers. | Catalogue, normalizer, import issues |
| TR-08 | SRC-TR ¶¶215–253 | Public funding details are expected to be publicly discoverable, with a public funding source discussed. | Sourceability claim is plausible but individual records still require verification. | Classify grant funding as publicly sourceable and require named provenance and period. | `catalogue.py`; fixture connector |
| TR-09 | SRC-TR ¶¶255–271 | Periodic news/award monitoring is discussed, approximately every three weeks/four weeks. | Desired operating pattern; scheduling is not needed to answer P0 RQ. | Keep connector interface reusable; defer scheduling to P1. | P1 requirements; no cron/live connector |
| WB-01 | SRC-WB rows 1–102 | Metrics are row-oriented and companies are columns; one sheet contains multiple thematic sections. | Direct structural observation. | Support matrix XLSX/CSV input and canonical JSON; use one period per import. | `PortfolioImporter._parse_matrix_rows` |
| WB-02 | SRC-WB rows 7, 37, 39, 45, 61, 69, 71, 85, 88, 91, 93, 97 | The same metric row can mix integers, floats, and strings across company responses. | Direct type profile; individual values withheld. | Strict per-metric normalization with invalid/issue states; raw value retained. | `normalization.py`; normalization tests |
| WB-03 | SRC-WB rows 12–18, 21–30, 49–56, 74–77, 101–102 | Blank cells occur in numeric, currency, explanation, and formula-adjacent regions; absence has ambiguous meaning. | Direct blankness observation; blank does not reveal intent. | Preserve blank separately from not reported, N/A, none, zero, and not found publicly. | `MissingState`; tests |
| WB-04 | SRC-WB rows 8–98 | Several labels are generic “Explanation for row X”; some appear misaligned with the referenced metric. | Direct label observation; semantic correction needs domain review. | Unknown/ambiguous mappings generate import issues rather than guessed aliases. | Metric catalogue and import warnings |
| WB-05 | SRC-WB cells C18:G18 and P59 | Formulas occur alongside imported values. | Direct workbook inspection; cached results were not treated as ground truth. | Preserve formula text; do not execute arbitrary spreadsheet formulas during import. | `data_only=False`; strict normalization |

## Evidence conflicts and resolution rules

- The materials call for a multi-agent pipeline, while the supervisor expresses an
  operational preference for one agent because of perceived cost. This is a research
  comparison, not a contradiction to hide. The protocol therefore compares a simpler
  deterministic/single-agent condition with multi-agent verification and HITL.
- The transcript describes current platform behaviour and prior AI summaries. Those are
  stakeholder assertions; the dashboard was not accessed and their accuracy is unverified.
- “Publicly available” does not mean “found” or “true.” Every public claim still requires a
  publisher, locator, retrieval time, checksum, period match, and independent verification.
- A blank workbook cell does not disclose whether a company reported zero, declined to
  answer, was not applicable, or had no public evidence. The canonical model retains these
  as separate states and requires explicit evidence to move between them.

## Credential incident hold

The PDF contains an exposed dashboard credential. This repository contains neither the
credential nor an encoded derivative. The dashboard was not accessed. The owner should:

1. rotate/revoke the exposed credential;
2. review access logs for unexpected use;
3. remove credentials from future dissertation materials;
4. use a secret manager or password-sharing channel; and
5. confirm the rotation before any separately authorised dashboard work.

Rotation is an external action and has **not** been performed by this project.
