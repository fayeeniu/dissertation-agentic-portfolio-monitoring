# Section 2.3 verified evidence packet

Scope: `2.3 Data quality, entity identity, missingness, and time` only. Page numbers are PDF page
numbers in the hash-pinned local files. These claims were checked against locally extracted text on
27 August 2026.

## Paragraph 1: quality as fitness for a defined use

- `nikiforova2020quality`, PDF pp. 1--3 and 15--17: data quality is multi-dimensional and should be
  evaluated against a user's data object and task; accuracy, reliability, timeliness, completeness
  and consistency cannot be collapsed into one context-free notion of quality.
- `krasikov2020ready`, PDF pp. 5--9: corporate-register data fitness depends on the enterprise use
  case, including content, accessibility and interpretability; open availability is insufficient.

Safe synthesis: define quality through explicit task-specific dimensions and validation rules. Do
not infer that one aggregate score establishes fitness for every reporting purpose.

## Paragraph 2: source-scoped legal identity

- `thorne2026funding`, PDF pp. 5--6: sources without common identifiers require conservative exact
  and fuzzy linkage; incomplete coverage and matching errors remain.
- `surak2026gateways`, PDF p. 6: inconsistent country/entity information required fuzzy and manual
  matching, illustrating the ambiguity of uncontrolled labels.
- `galanakis2026chrt`, PDF pp. 1--3 and 6: Companies House records identify incorporated entities,
  while incorporation and economic activity remain different concepts.

Safe synthesis: use an exact source-scoped company number as the legal-identity anchor. Names may
order candidates but must not silently merge entities; unresolved or conflicting identity remains a
review state.

## Paragraph 3: semantically distinct missingness

- `gebru2021datasheets`, PDF pp. 4--6: dataset documentation should state whether information is
  missing, why it is missing, and what remains unknown; unavailable, redacted and unknown states can
  have different meanings.
- `bradley2024synfintabs`, PDF pp. 3--5: financial-table extraction depends on explicit row,
  cell/empty-cell positions and semantic roles; an empty cell is part of table structure rather than
  automatically a numeric value.
- `nikiforova2020quality`, PDF pp. 2--3 and 15--17: completeness and validity are separate quality
  dimensions that require use-case-specific checks.

Safe synthesis: preserve blank, zero, explicit none, not applicable, not reported, not found
publicly, invalid and observed as distinct typed states. Literature supports preserving meaning and
documenting absence; the exact taxonomy is the artefact's design choice, not a published universal.

## Paragraph 4: availability time, cutoff and correction

- `hardman2023small`, PDF pp. 3, 5--6 and 21--25: register analyses use dated snapshots; filing
  availability and recent-company filing lag affect what can be known at a given date.
- `galanakis2026chrt`, PDF pp. 1--3 and 6: incorporation records are timely, but legal registration,
  later economic activity and official statistics have different timings and meanings.
- `kapoor2023leakage`, PDF pp. 3 and 5: using future information when evaluating a past prediction
  creates temporal leakage and can inflate measured performance.

Safe synthesis: retain observation/value period, publication/effective time, retrieval time and the
reporting cutoff separately. Later corrections create a new version and must not support an earlier
report retrospectively.

## Paragraph 5: synthesis into an evaluable contract

- `nikiforova2020quality`, PDF pp. 15--17: executable checks should be attached to the data object and
  user task rather than remain abstract dimension labels.
- `gebru2021datasheets`, PDF pp. 4--10: documentation should expose unknowns, errors, external
  dependencies, uses and maintenance/corrections.
- `kapoor2023leakage`, PDF pp. 1--7: data leakage and under-specified reporting can invalidate ML
  comparisons despite apparently strong metrics.

Safe synthesis: an evaluable evidence contract should type identity, missingness, time, source and
version, expose invalid/held states, and test each distinction. This is a design rationale; system
implementation and results belong to later chapters.

## Proposed exhibit LIT-T3

Create a compact data-semantics failure-prevention matrix with five rows: legal identity; observed
value/missing state; publication/effective/retrieval/cutoff time; correction/version/snapshot; and
use-case data quality. Columns: required distinction; unsafe collapse; reporting/evaluation
consequence; key local literature. Label as author synthesis, non-empirical and not a result. Include
a complete text alternative and provenance. Do not claim that the exact missing-state taxonomy is a
published standard.

## Prohibited overreach

- Do not treat company name matching as legal-identity resolution.
- Do not convert blank, absent, not found, invalid or not applicable into zero.
- Do not allow later-published or corrected evidence to support an earlier cutoff.
- Do not claim one generic quality score is sufficient or that the design is already empirically
  validated.
- Do not present the artefact's exact semantic taxonomy as a universal literature standard.
