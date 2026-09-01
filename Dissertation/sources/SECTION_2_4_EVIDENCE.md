# Section 2.4 verified evidence packet

Scope: `2.4 Provenance, source admission, contradiction, and auditable synthesis` only. Page
numbers are PDF page numbers in the hash-pinned local files. These claims were checked against
locally extracted text on 27 August 2026 and the foundational provenance source on 31 August 2026.

## Paragraph 1: provenance as traceability, not truth

- `buneman2001provenance`, PDF pp. 1--3: for database-query results, why-provenance concerns source
  data influencing a result's existence and where-provenance concerns source locations from which
  values were extracted. The paper does not address free-form report truth.
- `gebru2021datasheets`, PDF pp. 2--6 and 9--10: useful documentation records motivation,
  composition, collection, processing, missing information, known errors, external dependencies,
  distribution, maintenance and correction practices.
- `pineau2021reproducibility`, PDF pp. 1--4: reliable ML reporting depends on repeatable
  experimental processes, access to data and code, specified metrics and procedures, and claims that
  do not extend beyond the evidence.

Safe synthesis: provenance should bind a report statement to its source record, capture, locator,
transformation and decision history. This establishes internal traceability and repeatability, not
the truth, authority or completeness of the underlying source.

## Paragraph 2: source admission and claim-fit are separate gates

- `gao2023alce`, PDF pp. 3--4 and 10: answer correctness and citation quality are separate
  evaluation dimensions; citation quality includes both entailment/correctness and completeness, and
  visible citations can still provide incomplete or irrelevant support.
- `gao2023rarr`, PDF pp. 1--2: retrieved material may be ignored or contradicted, and attribution
  does not entail correctness because an attributed source may itself be wrong.
- `pineau2021reproducibility`, PDF pp. 1--3: incomplete reporting, unavailable artefacts,
  under-specified metrics and over-claiming weaken reliability.

Safe synthesis: first admit a source under explicit policy, then test whether an exact passage
supports the bounded claim. Search snippets, URL presence and fluent synthesis do not pass either
gate by themselves.

## Paragraph 3: immutable capture, exact locator and version

- `gebru2021datasheets`, PDF pp. 6 and 9--10: documentation should identify external resources,
  distribution, errata, updates, validation of contributions, retention and whether older versions
  remain available.
- `pineau2021reproducibility`, PDF pp. 1--5: reproducibility depends on retaining sufficient data,
  code, procedures, metrics and reporting information to repeat the work.
- `mitchell2019modelcards`, PDF pp. 1--4 and 7--8: structured reporting should state model version,
  intended uses, evaluation data and procedures, quantitative results, limitations, caveats and
  recommendations.

Safe synthesis: capture an admitted artefact immutably where permitted, record its checksum,
retrieval time and exact page/passage locator, and preserve later corrections as new versions. The
project-specific record fields are design choices informed by reporting and reproducibility work.

## Paragraph 4: contradiction and unverifiable states

- `huang2023hallucination`, PDF pp. 5--7 and 11--13: factual outputs may contradict available
  evidence, be unverifiable or overclaim; inability to reject or express uncertainty can increase
  fabrication, while verification should compare extracted factual statements with trusted
  knowledge.
- `gao2023rarr`, PDF p. 2: retrieved evidence can conflict with generated text, and attribution does
  not establish source correctness.
- `gao2023alce`, PDF pp. 3--4 and 10: correctness, citation entailment and citation completeness are
  distinct, so a citation marker cannot resolve substantive disagreement.

Safe synthesis: retain mutually inconsistent supported claims as an explicit conflict set, and hold
unverifiable material rather than silently selecting the majority, newest or most fluent version.
Resolution requires a stated policy or named review; the literature does not establish the
artefact's exact conflict-state taxonomy as universal.

## Paragraph 5: auditable synthesis and independent verification

- `nist2023airmf`, PDF pp. 33--35: measurement should use rigorous testing, uncertainty,
  benchmarks, formal reporting and documentation; independent review can mitigate internal bias and
  conflicts of interest, and limitations beyond evaluated conditions should be documented.
- `gao2023alce`, PDF pp. 3--4 and 10: correctness, citation correctness and citation completeness
  require separate evaluation.
- `gao2023rarr`, PDF pp. 1--2: an attribution report aligns claims with evidence, while attribution
  remains distinct from correctness.
- `amershi2019guidelines`, PDF pp. 3--5: human--AI systems should communicate uncertainty, support
  correction and dismissal, and make consequential actions clear.

Safe synthesis: auditable synthesis records candidate, admission, capture, claim, verification,
conflict and approval decisions; an independent verifier checks support without silently rewriting
the primary output. Only approved, supported claims may reach export. This is a literature-based
design rationale, not evidence that the current artefact has achieved user benefit or deployment
safety.

## Proposed exhibit LIT-F1

Create an evidence-to-claim admission and audit chain: candidate discovery; source-policy admission;
immutable capture; exact passage/span; typed claim; independent verification; contradiction state;
and approved report/export. Show rejected and held branches. Visually separate traceability from
source truth. Label it as author synthesis, non-empirical and not a result. Include a complete text
alternative, deterministic renderer and provenance record.

## Prohibited overreach

- Do not equate provenance, a checksum, a citation or source prestige with truth.
- Do not treat search snippets, generated summaries or bare URLs as admitted evidence.
- Do not silently discard, average or resolve contradictory evidence.
- Do not claim immutable capture is always legally or technically permitted.
- Do not claim that independent or human review automatically improves outcomes.
- Do not report current implementation or evaluation results in this literature-review section.
