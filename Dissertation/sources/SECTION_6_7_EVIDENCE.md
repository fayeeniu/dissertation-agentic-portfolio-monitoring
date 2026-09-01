# Section 6.7 verified evidence packet

Scope: `6.7 Practical implications and recommendations` only. Checked 31 August 2026 against the
current manuscript, local sources, Chapter 5, the governance record and ADR-0005.

## Evidence-bounded recommendations

- `pineau2021reproducibility`, PDF pp. 1--5 and 9--13, and `nist2023airmf`, PDF pp. 31 and 33--37:
  a local pilot should have fixed scope, documented conditions, versioned evidence and risk-aware
  review. The manuscript withholds time, cost, decision and satisfaction effects.
- `kaplan2016vcdata`, PDF pp. 3--7, and `britishbusinessbank2025equity`, PDF pp. 55--57: early-stage
  and angel evidence can be private, incomplete and definition-sensitive. Supported coverage and
  abstention must therefore be reported together.
- `nikiforova2020quality`, PDF pp. 1--3 and 15--17, and `peffers2007dsrm`, PDF pp. 4 and 16--18:
  quality measures must fit the reporting task, and artefact construction requires evaluation.

## Integration choice

- `buneman2001provenance`, PDF pp. 1--3, and `pineau2021reproducibility`, PDF pp. 1--5 and 9--13:
  typed origin/transformation records and repeatable versions support a canonical machine-readable
  contract.
- ADR-0005 records JSON as the canonical machine-readable output and Markdown/HTML as review formats.
  The discussion adds the PDF-first, JSON-only, schema-coupling, version-mismatch and misuse trade-offs
  without claiming observed re-entry savings.

## Human and engineering boundary

- `amershi2019guidelines`, PDF pp. 2--8, and `bucinca2021forcing`, PDF pp. 1--4 and 16--18: human
  review effects require observation and cannot be inferred from interface construction.
- The governance record does not verify ethics approval, consent, recruitment authority or a frozen
  participant protocol. Participant work therefore remained inadmissible/unrun; this is not evidence
  that interviews were unnecessary.
- Chapter 5 retains 286 passing tests, a formatting-gate failure and 22 warnings. The discussion
  presents this as mixed engineering evidence rather than production readiness.

## Prohibited overreach

- Do not name an external organisation or claim it authorised field use without evidence.
- Do not claim time, cost, accuracy, usefulness, satisfaction or decision benefit from the pilot.
- Do not treat a large public-company engineering case as early-stage field validation.
- Do not call participant evidence unnecessary or RQ3 answered.
