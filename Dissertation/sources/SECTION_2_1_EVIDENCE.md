# Section 2.1 verified evidence packet

Scope: `2.1 Review method and evidence boundary` only. Page numbers are PDF page numbers in the
hash-pinned local files. These claims were checked against locally extracted text on 27 August 2026.

## Paragraph 1: review purpose and transparent corpus construction

- `pineau2021reproducibility`, PDF pp. 1--5: reproducibility depends on specifying hypotheses,
  experiments, data, code, metrics and reporting details; checklists and code/data availability can
  improve transparency but do not guarantee replication.
- `gebru2021datasheets`, PDF pp. 2--5: structured documentation should record motivation,
  composition, collection, preprocessing, uses, distribution and maintenance; the reflective process
  matters and cannot be reduced to automated form filling.

Safe synthesis: describe this as a purposive, problem-led review that builds a transparent local
evidence corpus for design and evaluation decisions. It is not a PRISMA systematic review,
meta-analysis or claim of exhaustive coverage.

## Paragraph 2: admission and claim-fit verification

- `gao2023alce`, PDF pp. 3--4 and 10: citation quality has distinct correctness and completeness
  components; automatic citation metrics and visible references have limitations.
- `gao2023rarr`, PDF pp. 1--2: attribution and answer correctness are distinct; an answer can be
  attributable to a source that is itself wrong.
- `pineau2021reproducibility`, PDF pp. 1--3: access to code/data, specified metrics and complete
  reporting are material to reproducing results.

Safe synthesis: require a stable local full-text file, manifest row, checksum, bibliography key and
page-level claim verification. Search snippets, inaccessible pages and unsupported model statements
are ineligible. The local controls demonstrate internal traceability, not source truth by themselves.

## Paragraph 3: source hierarchy and limitations

- `kapoor2023leakage`, PDF pp. 1--2 and 6--7: methodological leakage, incomplete reporting,
  unavailable code/data and metric choices can undermine ML claims; reporting templates help but do
  not eliminate these problems.
- `pineau2021reproducibility`, PDF pp. 1--4: reproducing the same analysis differs from replication,
  robustness and generalisability; successful reruns do not establish external validity.
- `gebru2021datasheets`, PDF pp. 4--9: documentation should state unknowns, errors, risks and
  non-applicable fields rather than omit them.

Safe synthesis: distinguish peer-reviewed empirical work, preprints, official guidance and official
technical documentation. Retain source-specific limitations and report gaps. The resulting synthesis
supports this artefact's design rationale but does not estimate a pooled effect or prove deployment
performance.

## Proposed exhibit LIT-T1

Create a compact review/source-admission protocol table showing: problem-led discovery; stable local
full-text requirement; manifest/checksum/bibliography binding; page-level claim verification;
contradiction/limitation retention; and strict freeze validation. Include a text alternative and
provenance. Do not present the process as systematic, exhaustive or PRISMA-compliant, and do not put
mutable corpus counts in the table.

## Prohibited overreach

- Do not claim database completeness, exhaustive search, formal systematic-review registration or
  risk-of-bias scoring that was not performed.
- Do not treat preprints, guidance or vendor documentation as equivalent to peer-reviewed causal
  evidence.
- Do not say local storage, hashing or citation presence proves that a source is true.
- Do not introduce empirical findings from later chapters.
