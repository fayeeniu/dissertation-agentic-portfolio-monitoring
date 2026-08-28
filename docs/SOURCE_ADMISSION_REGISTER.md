# Source admission register

This register separates implemented connector mechanics from permission to perform live retrieval.
It does not assert current licence/terms text that has not been independently captured and approved.
Gate G2 is the hard stop for every live public-source action except the two explicitly approved,
conditioned capabilities below. Direct registry connectors and all other source packs remain held.

| Source key | Publisher/interface | Implemented mode | Identity key | Capability/version | Licence/terms evidence | Live status | Permitted dissertation use now |
|---|---|---|---|---|---|---|---|
| `portfolio_submission` | Supplied CBIT workbook | Immutable local restricted snapshot | reviewed portfolio identity | CBIT profile v1; catalogue hash pinned | Data authority/ethics scope still requires external confirmation | Local restricted import only | Structural counts and authorised local processing; never Git/external model |
| `companies_house` | Companies House | Immutable synthetic replay; gated GET-only API adapter | exact Companies House number | manifest `1.4.0` | **EVIDENCE_REQUIRED:** capture current authoritative access, licence/terms, credential, retention, and attribution requirements before G2 closes | **HELD** | Connector/temporal/provenance/document-extraction mechanism tests only |
| `ukri_gtr` | UKRI Gateway to Research | Immutable synthetic replay | exact UKRI organisation ID | manifest `1.3.0` | **EVIDENCE_REQUIRED:** capture current authoritative interface, licence/terms, redistribution, time semantics, and attribution before any live/data release use | **HELD** | Lifecycle/correction/missing/non-GBP amount mechanism tests only |
| `fixture_connector` | Repository fictional evidence | Local JSON fixture | fictional legacy ID | `1.0.0` | Repository-owned fictional test asset | Enabled only by explicit fixture flag | Offline workflow and D0 engineering proof |
| `ons_context` | Office for National Statistics | Not implemented | aggregate cohort dimensions | no manifest | **EVIDENCE_REQUIRED** before admission | **NOT ADMITTED** | Method discussion only; no numeric context claim |
| `ukipo` | UK Intellectual Property Office | Not implemented | exact official identifier/linkage | no manifest | **EVIDENCE_REQUIRED** before feasibility/design | **NOT ADMITTED** | Conditional future-work discussion only |
| `openai_web_search` | OpenAI Responses API web-search tool | Implemented, explicit opt-in, URL discovery only | reviewed Companies House number plus pinned company/cutoff query | `public-web-research-v1`; prompt `company-research-web-v9` | Official tool/data-control documentation reviewed 2026-08-27; provider retention setting must be checked per project | **CONDITIONALLY ADMITTED** for public company-level local research | Discover bounded HTTPS source candidates across official, first-party, regional, trade, public-notice, customer, partnership, financing, technical, and adverse-evidence lanes; snippets/model prose are not evidence; public/mixed CBIT metrics require a canonical metric key and exact captured span |
| `public_web_capture` | Publisher pages discovered by the admitted search task | Implemented guarded HTTPS GET, local immutable bytes and deterministic text | exact discovered URL; company association remains claim-level | `public-web-research-v1` | Robots/access checks are executable; each publisher's redistribution/licence remains source-specific and is not inferred | **CONDITIONALLY ADMITTED** for local review only | Capture accessible company-level pages; no forms/login/paywall/CAPTCHA/commercial-platform scraping or public redistribution claim |

## G2 admission checklist

A source/version may transition to live only when a named reviewer records:

1. authoritative interface and publisher;
2. access method, authentication, current licence/terms URL plus captured review date;
3. permitted retrieval, storage, redistribution, attribution, and retention;
4. exact identifier mapping and company authority;
5. publication, availability, effective, correction, and retrieval time semantics;
6. bounded rate, attempts, response size/media type, timeout, and failure treatment;
7. local snapshot location/classification/access/deletion controls;
8. allowed fact/event keys and prohibited inferences; and
9. a counts/hash/locator-only live smoke protocol that does not enter CI.

Changing a source interface, licence, schema, or manifest semantics requires a new reviewed version.
An implementation or public website does not by itself grant admission.

The persisted connector capability manifest records the licence and terms evidence state, dated
admission review (when one exists), and `live_retrieval_admitted`. Both implemented registry
connectors remain inactive for live use: non-offline requests are rejected before connector
invocation, and public-classified connector snapshot content is rejected before database or file
persistence. Within the connector registry, only repository-owned synthetic replays are executable.
The separately conditioned web-research path uses revision-`0009` research records rather than
silently opening those registry connectors. Synthetic replays require an exact reviewed identifier
bound to the requested company, source, validity interval, and cutoff before connector invocation.
A cumulative metric also requires the persisted programme
start, and every returned cumulative fact must exactly cover programme start through cutoff.
Returned media and event types are checked, and every fact key must match its manifest's exact
metric binding(s), unit, currency, extraction method/schema, timestamps, and structured locator
before immutable bytes or metadata are
persisted; the resulting snapshot is then explicitly associated with the initiating workflow run.
The versioned `source-derivation-v2` SHA-256 covers terminal source metadata, the programme window,
facts, fact provenance, events, locators, and temporal fields. Legacy v1 hashes remain verifiable;
new or lazily backfilled hashes use v2. Forced refreshes and concurrent winners must match both raw
bytes and the applicable derivation contract or fail closed.

UKRI's GBP cumulative total becomes `grant_funding` evidence only when every award in the exact
programme window has a finite explicit GBP amount. Missing amounts or non-GBP awards leave the
explicit subtotal descriptive, add diagnostic counts plus a typed missing state, and produce no
complete-total claim. Event locators use stable public project/outcome identifiers rather than
array positions, so longitudinal insertion cannot invalidate an otherwise immutable replay.

## Local research-corpus redistribution boundary

The pre-existing `research/literature/` corpus is design evidence, not an operational source. Its
manifest records source URLs and hashes but does not yet establish artifact-by-artifact
redistribution permission for every publisher PDF and supporting dataset. No paper or dataset bytes
were added by this upgrade. Until a named reviewer captures each applicable licence and repository
distribution right, exclude the literature PDFs and released data files from any public repository
bundle; cite the papers and authoritative release pages instead. This is a packaging hold, not a
claim that local scholarly use or redistribution is permitted or prohibited.
