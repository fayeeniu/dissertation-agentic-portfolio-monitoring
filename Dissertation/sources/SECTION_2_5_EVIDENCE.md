# Section 2.5 verified evidence packet

Scope: `2.5 LLM-assisted discovery and grounded extraction` only. Page numbers are PDF page
numbers in the hash-pinned local files. These claims were checked against locally extracted text on
27 August 2026.

## Paragraph 1: retrieval assistance and its boundary

- `gao2023ragsurvey`, PDF pp. 1 and 3: retrieval-augmented generation separates indexing,
  retrieval and generation, but may retrieve irrelevant chunks, omit important material or generate
  content unsupported by the retrieved context.
- `huang2023hallucination`, PDF pp. 20--22 and 26: external retrieval can reduce knowledge-gap
  hallucination, yet irrelevant or incorrect retrieval can introduce noise and retrieval-augmented
  systems can still produce inaccurate or misleading output.
- `gao2023rarr`, PDF pp. 1--2: post-generation research and revision can add attribution, while
  retrieval does not guarantee that generated text follows or correctly represents evidence.

Safe synthesis: use an LLM to widen and adapt candidate discovery, but keep retrieval, admission,
extraction and verification as separate stages. RAG is a useful design pattern, not a guarantee of
grounded output.

## Paragraph 2: Responses API web-search capability

- `openai2026websearch`, PDF pp. 1--3 and 5--7: the Responses API supports the `web_search` tool,
  optional model-managed search, inline URL citations, citation annotations, domain filtering and a
  complete consulted-source list; context size does not guarantee a particular number of sources or
  citations.
- `gao2023alce`, PDF pp. 1 and 3--4: cited generation requires evaluation of correctness and citation
  quality; visible citations can still be incomplete or unsupported.
- `gao2023ragsurvey`, PDF pp. 3--4: retrieval and generation are distinct components, and modular
  designs may search different data sources.

Safe synthesis: the documented API capabilities fit query planning and discovery, including source
inventory and domain controls. Treat returned URLs, snippets, annotations and model prose as
candidates until the local evidence-admission process succeeds. Documentation establishes API
features as captured on the access date, not this artefact's live performance.

## Paragraph 3: grounded extraction at claim and passage level

- `gao2023alce`, PDF pp. 3--4 and 10: correctness, citation entailment/correctness and citation
  completeness are distinct; passage-scale citations make human checking more tractable.
- `gao2023rarr`, PDF pp. 1--2: an attribution report aligns evidence snippets to relevant content,
  while attribution remains separate from correctness and revision may be needed when evidence
  disagrees.
- `gao2023ragsurvey`, PDF pp. 3, 8 and 14: retrieval depends on chosen chunks or atomic units, and
  evaluation should separate context relevance, faithfulness, answer relevance, rejection and
  robustness.

Safe synthesis: structured evidence should take a deterministic-first route. Admitted unstructured
public or synthetic evidence may use bounded model-assisted extraction, but its output remains a
typed proposal linked to an exact passage. Strict schema/span validation, deterministic
normalisation and independent verification remain mandatory; unsupported parts are rejected or held
rather than repaired from model memory. The ordered routing is the artefact's design choice.

## Paragraph 4: retrieved content is untrusted data

- `greshake2023indirect`, PDF pp. 1 and 3--5: indirect prompt injection places adversarial
  instructions in material likely to be retrieved; LLM-integrated search and document systems can
  blur data and instructions, manipulate summaries, queries, sources and downstream actions.
- `gao2023ragsurvey`, PDF pp. 3 and 14--15: RAG output is vulnerable to irrelevant, noisy,
  contradictory or adversarial context, and robustness and data security remain open engineering
  concerns.
- `nist2023airmf`, PDF pp. 32--35: third-party data risks, testing, uncertainty, independent review,
  safe failure and documented limits belong in AI risk management.

Safe synthesis: public pages must remain untrusted data, never higher-priority instructions. Search
and extraction require fixed tool permissions, validation, isolation, bounded redirects/requests and
fail-closed handling; the cited work establishes the threat and risk rationale, not the effectiveness
of this artefact's controls.

## Paragraph 5: bounded coverage and evaluable discovery

- `openai2026websearch`, PDF pp. 5--7 and 10--12: search context, returned-token budget, live-access
  control, domain filters and source lists are configurable, while source/citation counts are not
  guaranteed and search may remain optional unless required.
- `gao2023alce`, PDF pp. 1 and 3--4, 10: citation-supported generation needs separate correctness,
  entailment and completeness measures; benchmark systems still leave incomplete support.
- `gao2023ragsurvey`, PDF pp. 14--17: RAG evaluation spans relevance, faithfulness, rejection,
  integration and robustness, but metrics are not yet mature or standardised.
- `pineau2021reproducibility`, PDF pp. 1--4: procedures, data, metrics, code and reporting limits must
  be specified for repeatable and evidence-proportionate conclusions.

Safe synthesis: define comprehensive research as attempting every applicable admitted capability
under a recorded query, source, time, token and cost budget, and report inaccessible, missing,
contradictory and unverified areas. Do not claim exhaustive web coverage or infer recall against an
unknown open-web universe.

## Proposed exhibit LIT-F2

Create a discovery-and-evidence-processing diagram. The LLM-assisted discovery lane contains topic
planning, adaptive queries, Responses API web-search candidates and source inventory, and may meet
the evidence path only at a candidate queue. After source admission and controlled capture, show two
truthful extraction routes: deterministic structured extraction first, and a bounded optional
model-assisted route for admitted unstructured public/synthetic evidence. Both must converge on
deterministic exact-span/schema validation, normalisation and independent verification before any
supported claim. Show untrusted web content and prompt-injection containment, plus explicit
missing/held/conflict outputs. Label as author synthesis, non-empirical and not a result. Include
vector PDF/SVG, complete text alternative, deterministic renderer and provenance.

## Prohibited overreach

- Do not equate web-search citations, annotations, snippets or a source list with admitted evidence.
- Do not claim RAG or retrieval eliminates hallucination or establishes truth.
- Do not allow retrieved page text to act as system instructions or authorise new tools/actions.
- Do not describe every post-discovery extraction step as deterministic or conceal the bounded
  external-model extraction route.
- Do not report live search coverage, latency, cost, token use or comparative performance in this
  literature-review section.
- Do not call a bounded search exhaustive or infer open-web recall.
- Do not present documented API features as executed behaviour in this artefact.
