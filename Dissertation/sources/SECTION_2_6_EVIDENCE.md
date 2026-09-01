# Section 2.6 verified evidence packet

Scope: `2.6 Bounded multi-agent systems and human review` only. Page numbers are PDF page numbers
in the hash-pinned local files. These claims were checked against locally extracted text on
27 August 2026 and the added empirical failure study on 31 August 2026.

## Paragraph 1: decomposition requires programmed roles and interfaces

- `guo2024multiagent`, PDF pp. 3--5: multi-agent systems differ in environment interfaces, agent
  profiles, communication paradigms, communication structures and exchanged content; roles and
  coordination are design choices rather than evidence of collective intelligence by themselves.
- `wu2024autogen`, PDF pp. 1--5: agents may combine LLMs, humans and tools; developers specify roles,
  capabilities, messages, conversation control, human-input conditions, tool execution and
  termination conditions.
- `peffers2007dsrm`, PDF pp. 16--18: design-science evaluation should test whether an artefact meets
  its stated objectives rather than infer utility from its construction.

Safe synthesis: decompose the workflow only where a distinct responsibility, input/output contract
and failure boundary can be evaluated. A role name or conversation does not create independence,
competence or benefit.

## Paragraph 2: bounded orchestration and independent verification

- `guo2024multiagent`, PDF pp. 4--5 and 10--11: communication structures and orchestration govern
  information flow; hallucinations can cascade between agents, while more agents increase
  coordination, communication and resource complexity.
- `cemri2025masfailures`, PDF pp. 1--3: 1,642 traces from seven selected multi-agent systems were
  classified into fourteen failure modes across system design, inter-agent alignment and task
  verification. Reported failure rates varied substantially. The tasks were coding, mathematics and
  general-agent benchmarks, and much of the larger dataset used model-assisted annotation, so the
  results do not transfer directly to portfolio reporting.
- `wu2024autogen`, PDF pp. 2--5: multi-agent workflows require programmed control flow, role-specific
  computations, termination conditions, human-input modes and tool-execution rules.
- `nist2023airmf`, PDF pp. 33--35: rigorous testing should document uncertainty and evaluated
  conditions; independent review can mitigate internal bias and conflicts of interest, and limits
  beyond tested conditions should remain visible.

Safe synthesis: use a serial, budgeted task graph with typed handoffs, bounded retries, explicit
termination and separate verifier records. The verifier evaluates support and may reject or hold a
claim; it must not silently rewrite the producer's output. More agents are not assumed to be better.

## Paragraph 3: human authority is not automatic quality improvement

- `amershi2019guidelines`, PDF pp. 3--5 and 16--19: human--AI interaction should support invocation,
  dismissal, correction, uncertainty scoping, explanation, feedback and global controls; the
  guidelines are design aids rather than outcome evidence for this artefact.
- `bucinca2021forcing`, PDF pp. 1--4 and 16--18: explanations alone do not eliminate overreliance;
  cognitive forcing reduced overreliance in one controlled task but did not improve overall team
  performance, reduced perceived usability and benefited participant groups differently.
- `nist2023airmf`, PDF pp. 32--35: human oversight and independent assessment should be defined,
  documented and connected to the system's context and risk tolerance.

Safe synthesis: a named reviewer supplies decision authority, not new evidence. The interface should
show the claim, exact support, conflicts, uncertainty, limitations and content hash, and permit
approve, reject or return-for-correction. Do not infer review quality, user benefit or calibrated
trust without an authorised human study.

## Paragraph 4: limits, telemetry and evaluable failure

- `guo2024multiagent`, PDF pp. 10--11: multi-agent hallucination propagation, orchestration,
  scalability, coordination and incomplete benchmarks remain open challenges.
- `wu2024autogen`, PDF pp. 3--5 and 9--10: framework flexibility includes human/tool/LLM roles,
  configurable control and termination; reported pilot results are application-specific and do not
  establish universal superiority.
- `nist2023airmf`, PDF pp. 33--38: measurement, uncertainty, safe failure, documented limitations,
  risk tracking, response, recovery and change management support controlled operation.
- `pineau2021reproducibility`, PDF pp. 1--4: data, code, procedures, metrics and reporting boundaries
  are required for repeatable evaluation and claims proportionate to evidence.

Safe synthesis: persist role/task/attempt IDs, inputs/outputs, hashes, duration, tokens, errors,
stop reasons, cancellation and recovery state. Evaluate each role and the end-to-end workflow against
frozen cases, including disagreement and failure. Do not treat message count, agent count or a
completed conversation as task success.

## Proposed exhibit LIT-T4

Create a compact role-and-authority matrix with five rows: query planner/discovery; evidence
extractor; independent verifier; deterministic composer; named human reviewer. Columns: permitted
input/tools; required output; stop/failure condition; forbidden authority. Make clear that the model
roles propose or assess bounded records, the composer cannot introduce facts, and the reviewer may
approve/reject/return but cannot manufacture support. Label as author synthesis, non-empirical and
not a result. Include a LaTeX table, complete text alternative and provenance with exact source and
repository hashes.

## Prohibited overreach

- Do not anthropomorphise roles or imply that messages establish independent reasoning.
- Do not claim that more agents, debate or role separation is universally superior.
- Do not let a verifier silently revise the claim it is meant to assess.
- Do not claim that a human reviewer adds evidence or automatically improves accuracy, trust or
  utility.
- Do not transfer AutoGen pilot results or Bu\c{c}inca task results to this artefact.
- Do not report unrun human-review outcomes or live multi-agent performance.
