# Section 1.2 verified evidence packet

Scope: `1.2 Problem definition` only. Page numbers below are PDF page numbers in the
hash-pinned files under `sources/papers`; printed page numbers are included where useful.
These claims were checked against locally extracted text on 27 August 2026.

## Paragraph 1: heterogeneous records create identity, missingness and time risks

- `surak2026gateways`, PDF p. 6 (printed p. 5): a three-register UK study could not rely on
  standardised entity names or countries. It removed company suffixes, mapped country aliases,
  used fuzzy and manual matching, and matched 83% of titles; unmatched cases included
  non-compliance and poor-quality data.
- `nikiforova2020quality`, PDF pp. 15--16 (printed pp. 121--122): the Companies House case
  detected empty mandatory fields, inconsistent country names and use-case-dependent defects;
  the authors caution that apparently minor defects can produce inaccurate results or false
  decisions depending on the intended use.
- `hardman2023small`, PDF pp. 22--25 (printed pp. 138--141): a whole-register study recorded
  large `no accounts filed` and empty-field groups and linked recent `no detail available` states
  to the time lag in preparing and filing accounts.

Safe synthesis: a company name, a blank value or a recent filing must not be treated as an
unambiguous analytical fact. Legal-number resolution, explicit missing states and time-aware
interpretation are necessary controls, while residual non-match and unavailable-data states must
remain visible.

## Paragraph 2: fluent, cited synthesis can still be unsupported or unsafe

- `gao2023alce`, PDF pp. 1 and 4, with limitations on PDF p. 10: cited generation is evaluated
  along separate dimensions of correctness, citation recall and citation precision. Citation
  recall asks whether cited passages jointly support a statement; the automatic metrics inherit
  NLI and benchmark-coverage limits.
- `gao2023rarr`, PDF pp. 1--2: language-model output can be unsupported or misleading; the
  proposed research-and-revision workflow improves attribution, but the authors explicitly state
  that attribution does not entail correctness because a cited source itself may be wrong.
- `greshake2023indirect`, PDF pp. 1 and 3--5: retrieval blurs the boundary between data and
  instructions. The paper demonstrates indirect prompt injection through public and retrieved
  content and describes manipulated summaries, source selection and tool/API actions as threats.

Safe synthesis: neither a search result nor a citation marker is sufficient evidence. Candidate
pages require admission, immutable capture where permitted, exact claim-to-passage checking and
separate treatment of retrieved text as untrusted input.

## Paragraph 3: human control is necessary but is not automatically effective

- `amershi2019guidelines`, PDF pp. 3--5: the validated human--AI guidance says systems should
  state what they can do and how well, support dismissal and correction, scope services under
  uncertainty, explain behaviour and provide global controls. The paper validates general
  guidelines across products rather than this dissertation artefact.
- `bucinca2021forcing`, PDF pp. 1 and 16--18: in a controlled task, participants sometimes
  over-relied on incorrect AI suggestions. Cognitive-forcing interfaces reduced over-reliance but
  introduced preference, trust and subgroup trade-offs; the findings are task-specific and do not
  establish this prototype's user benefit.

Safe synthesis: the local artefact may place named approval before export and expose conflicts,
limits and evidence locators as design safeguards. These features must not be described as proven
to improve decisions until the authorised human-in-the-loop study is run.

## Prohibited overreach

- Do not report measured manual time, cost or error reduction; no corresponding baseline has run.
- Do not treat fuzzy entity matching as proof of identity or collapse an unmatched record into a
  negative company fact.
- Do not treat a retrieved page, search snippet, citation marker or model assertion as an admitted
  claim.
- Do not claim that a named approval gate, explanation or visual evidence display improves user
  decisions before the authorised human study.
- Do not imply exhaustive open-web coverage, production readiness or investment performance.
