# Section 1.5 verified evidence packet

Scope: `1.5 Scope, contribution, and exclusions` only. Page numbers are PDF page numbers in the
hash-pinned local files. These claims were checked against locally extracted text on 27 August 2026.

## Paragraph 1: research-prototype and data boundary

- `nist2023airmf`, PDF pp. 15, 31 and 37: AI risk management should document intended purpose,
  users, context and operational boundaries, then make an explicit decision about whether deployment
  should proceed. The framework does not certify a particular system.
- `cddo2023genai`, PDF pp. 9--10 and 72: generative-AI use requires privacy/security controls and
  meaningful human control; official or sensitive information should not be entered into public
  generative-AI applications or APIs unless already public or cleared for publication.

Safe synthesis: describe the artefact as a local, loopback-only, single-user research prototype.
Restricted/internal material remains local and cannot cross the external-model boundary; only
public company-level material may be eligible under explicit controls. Do not imply that these
choices establish production security, legal compliance or provider-side zero retention.

## Paragraph 2: bounded research contribution

- `hevner2004design`, PDF pp. 4, 9 and 11, and `peffers2007dsrm`, PDF pp. 16--18: a design-science
  contribution combines a relevant artefact with explicit, rigorous evaluation against stated
  objectives; implementation alone does not demonstrate utility.
- `gao2023alce`, PDF pp. 3--4 and 10, and `gao2023rarr`, PDF p. 2: citation support, attribution and
  answer correctness are different properties; sourced text can still require verification.

Safe synthesis: state the contribution as a reproducible evidence-first artefact, evaluation
protocol and traceable reporting method. It may include the implemented but live-unrun public-web
case study. Do not claim operational benefit, exhaustive web coverage, investment performance or
general superiority.

## Paragraph 3: exclusions and human authority

- `fca2024promotions`, PDF pp. 5, 9, 13 and 30--31: financial communications can affect investment
  decisions; applicable promotions must be balanced, fair, clear and not misleading, while
  investment-strategy recommendations and unauthorised promotion create additional duties/risks.
  This guidance supports a conservative communication boundary but is not a legal opinion about
  this dissertation.
- `greshake2023indirect`, PDF pp. 2--5 and 13: retrieved public content can indirectly control an
  LLM-integrated application and cross security boundaries, especially where systems act through
  tools with little oversight.
- `cddo2023genai`, PDF pp. 10, 46 and 50: quality assurance, accountable human responsibility and
  meaningful human oversight are needed for generative-AI outputs and decisions.

Safe synthesis: exclude buy/sell recommendations, speculative valuation, person profiling,
autonomous publication, remote/multi-tenant deployment and claims of production readiness. Named
approval remains required before export. These are project boundaries, not proof that every possible
wording or attack is prevented.

## Prohibited overreach

- Do not state or imply that the artefact is production-ready, legally compliant or safe in every
  deployment context.
- Do not say that `store=False` creates Zero Data Retention; provider retention is discussed later.
- Do not claim that the public-web path has been run live or evaluated on a frozen company set.
- Do not state that human review improves decisions; C0/C3 evidence remains held.
- Do not turn a design contribution into a demonstrated operational, financial or social outcome.
