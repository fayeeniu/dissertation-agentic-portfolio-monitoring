# Section 1.3 verified evidence packet

> Historical evidence note, 29 August 2026: this packet describes the superseded combined
> aim-and-questions section. Current paragraph evidence is recorded in `CLAIM_LEDGER.md`.

Scope: `1.3 Aim and research questions` only. Page numbers are PDF page numbers in the
hash-pinned local files. These claims were checked against locally extracted text on
27 August 2026.

## Paragraph 1: applied design-science aim

- `hevner2004design`, PDF pp. 4, 9 and 11: design science builds and evaluates purposeful
  artefacts for relevant problems. Utility, quality and efficacy require well-executed evaluation,
  appropriate metrics and relevant data; building the artefact alone is insufficient.
- `peffers2007dsrm`, PDF pp. 4 and 16--18: the design-science process connects problem
  identification, solution objectives, design/development, demonstration, evaluation and
  communication. Evaluation observes and measures how well results meet the stated objectives.

Safe synthesis: the dissertation aim may combine construction of a bounded reporting artefact with
pre-specified evaluation. It must not infer utility or effectiveness from implementation alone.

## Paragraph 2: RQ1 and RQ2 require separate observable outcomes

- `gao2023alce`, PDF pp. 3--4 and 10: cited generation separates answer correctness from citation
  quality; citation recall asks whether cited passages jointly support statements, while citation
  precision penalises irrelevant citations. Automatic scores inherit benchmark and NLI limits.
- `gao2023rarr`, PDF p. 2: end-task performance and attribution are not always aligned, and
  attribution does not entail correctness because a cited source can itself be wrong.

Safe synthesis: RQ1 should measure accurate and reliable bounded transformation of heterogeneous
inputs through typed, temporal, provenance and repeat-consistency outcomes rather than fluency;
RQ2 should isolate the change caused by independent verification using support, contradiction,
abstention and repeatability measures. The questions define tests, not achieved results.

## Paragraph 3: RQ3 is a held human comparison

- `amershi2019guidelines`, PDF pp. 3--5: human--AI systems should expose capability and uncertainty,
  support dismissal and correction, explain behaviour and provide controls. These are general design
  guidelines, not evidence of this artefact's user benefit.
- `bucinca2021forcing`, PDF pp. 1 and 16--18: in one controlled task, cognitive-forcing interfaces
  reduced over-reliance on erroneous AI suggestions but introduced preference, trust and subgroup
  trade-offs; findings are task-dependent.

Safe synthesis: RQ3 may compare manual C0, automated C1/C2 and named-review C3 conditions using
correctness, completeness, time, edit burden, approval time and reviewer utility only under separate
authorisation. Until then, its C0/C3 human outcomes are null/held and the primary question can be
answered only partly.

## Prohibited overreach

- Do not describe the research questions as findings or claim that the artefact is already useful.
- Do not equate citation presence, attribution or deterministic replay with factual correctness.
- Do not claim manual-effort reduction, user benefit, trust calibration or improved decisions before
  the authorised C0/C3 study.
- Do not introduce the live-unrun public-web company-research case study as RQ4.
- Do not use the RQs to imply investment performance, production readiness or exhaustive coverage.
