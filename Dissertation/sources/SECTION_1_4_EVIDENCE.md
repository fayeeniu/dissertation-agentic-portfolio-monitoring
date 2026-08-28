# Section 1.4 verified evidence packet

Scope: `1.4 Research objectives` only. Page numbers are PDF page numbers in the hash-pinned local
files. These claims were checked against locally extracted text on 27 August 2026.

## Paragraph 1: build, implement and evaluate objectives

- `hevner2004design`, PDF pp. 4, 9 and 11: design-science research builds a viable artefact for a
  relevant problem and must demonstrate utility, quality and efficacy through rigorous evaluation,
  defined metrics and appropriate data.
- `peffers2007dsrm`, PDF pp. 16--18: objectives are inferred from the problem and what is feasible;
  design/development is followed by demonstration and evaluation against those objectives, with
  iteration where warranted.

Safe synthesis: O1--O3 may specify the bounded data/evidence design, its fail-closed implementation
and a frozen C1/C2 comparison. They are planned activities and acceptance criteria, not proof of
utility or successful evaluation.

## Paragraph 2: human-control and evidence-calibrated reporting objectives

- `amershi2019guidelines`, PDF pp. 3--5: human--AI design should expose system capability and
  uncertainty and support correction, dismissal, explanation and controls.
- `bucinca2021forcing`, PDF pp. 1 and 16--18: interventions intended to reduce AI over-reliance can
  introduce preference, trust and subgroup trade-offs, so task-specific human evaluation matters.
- `gao2023alce`, PDF pp. 3--4 and 10, and `gao2023rarr`, PDF p. 2: answer correctness, citation
  support and attribution are distinct; automatic citation evaluation has limitations, and an
  attributed source can still be wrong.

Safe synthesis: O4 may evaluate C0--C3 human/manual outcomes only where separately authorised. O5
may require transparent reporting of supported, unsupported, contradictory, unavailable, null and
held evidence. Neither objective licenses a current benefit claim.

## Prohibited overreach

- Do not describe any objective as completed merely because corresponding code or tests exist.
- Do not replace the frozen C0--C3 evaluation with the D0 synthetic mechanism check.
- Do not imply that named review, explanations or evidence displays have improved decisions.
- Do not turn the public-web company-research case study into an additional objective that changes
  the frozen research questions.
- Do not introduce investment, production-readiness or exhaustive-coverage outcomes.
