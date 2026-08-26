# Rejected literature candidates

**Screening date:** 26 August 2026

These papers may be academically useful, but they were excluded from the implementation corpus because they failed at least one hard gate: accessible research data, isolatable UK-company scope, academic-paper status, or direct/supporting relevance. Rejection here is not a judgement of general scholarly quality.

| Candidate | Why it was relevant | Rejection reason |
|---|---|---|
| Woodruff, Enshaei, and Hasan (2021), *Fully-Automatic Pipeline for Document Signature Analysis to Detect Money Laundering Activities*, arXiv:2107.14091 | Companies House document extraction and entity investigation | The decisive Companies House signature crops, author labels, manually cleaned examples and pair labels used to train/evaluate the pipeline are custom and not released. The public source documents alone do not reconstruct the labelled task. |
| Risk Control Limited (2020), *Predicting Default for UK SMEs Using Companies House Data* | UK iXBRL/Gazette default features | This is a vendor technical note rather than a peer-reviewed academic paper, and the demonstrated Rating Engine plus frozen labelled company/default panel are not released. |
| Hafner, Peifer, and Hafner (2024), *Equal accuracy for Andrew and Abubakar—detecting and mitigating bias in name-ethnicity classification algorithms* | Shows bias risks when transforming public company/director names | The paper's code/source references are accessible, so it did not fail the data gate. It was rejected because inferring protected ethnicity from names is neither necessary nor proportionate for portfolio reporting. Its general fairness warning is retained as a governance constraint, not an implementation feature. |
| Banal-Estañol, Macho-Stadler, Nieto-Postigo, and Pérez-Castrillo (2023), *Early individual stakeholders, first venture capital investment, and exit in the UK startup ecosystem* | Direct UK start-up, ownership, VC and exit evidence | The study's comprehensive analytical data depend on commercial databases including VentureXpert/FAME/Orbis and are not released as an accessible firm-level replication dataset. |
| Coakley, Lazos, and Liñares-Zegarra (2022), *Equity Crowdfunding Founder Teams: Campaign Success and Venture Failure* | UK platform campaigns, founders and later failure | Campaign data were compiled through TAB on Thomson Reuters Eikon and are not provided as an open replication dataset. |
| Lazos and Shneor (2026), *Is having immigrants in entrepreneurial teams good for equity crowdfunding success and long-term venture survival?* | UK ECF team composition and survival | The sample is sourced from TAB through Thomson Reuters Eikon. It also requires sensitive demographic inference that is outside the portfolio-reporting purpose. |
| Kleinert and Volkmann (2019), *Forecasting success in equity crowdfunding* | UK Crowdcube/Seedrs success prediction | The campaign sample is sourced from TAB through Thomson Reuters Eikon; no accessible frozen replication panel was identified. |
| Ashouri et al. (2022), *Indicators on firm level innovation activities from web scraped data* | UK/EU company-web evidence and innovation indicators | Sampling starts from Bureau van Dijk Orbis and Google Search. The released derived data do not expose a sufficiently attributable UK-company identity/jurisdiction slice for evidence-linked portfolio reporting. |
| Bahaj, Piton, and Savagar (2024), *Business Creation during COVID-19* | UK firm creation and early-stage dynamics | The analysis combines sources that include commercial Bureau van Dijk data and platform-derived measures; the full frozen firm-level analytical panel is not openly downloadable. |
| Vanino, Roper, and Becker (2019), *Knowledge to money: Assessing the business performance effects of publicly-funded R&D grants* | UKRI grants and company performance | The impact evaluation depends on restricted-access ONS firm microdata. Public GtR inputs alone cannot reproduce the company-performance outcome panel. |
| Ashraf, Coyle, and Debnath (2026), *Code, Capital, and Clusters: Understanding Firm Performance in the UK AI Economy* | UK AI start-ups, finance and regional clusters | Core company classification/measurement uses glass.ai. Without that commercial dataset the paper's UK AI entity universe and features cannot be recreated. |
| *Fast Record Linkage for Company Entities* | Entity matching across noisy company records | The evaluated company corpus is commercial and the labelled match task is not released in an accessible UK-only form. |
| Studies using FAME/Orbis/Beauhurst/PitchBook/Crunchbase as the defining company universe | Often highly relevant to UK venture finance and growth | Rejected whenever the commercial universe, labels or outcomes were essential and no public UK replication dataset was released. An open PDF does not satisfy the data-access gate. |
| Bespoke Crowdcube/Seedrs web-scrape studies without a released snapshot | Direct ECF relevance | Historical failed campaigns and removed pages cannot be reliably reconstructed from current sites; papers were rejected when the frozen crawl, labels and campaign identifiers were not released. |

## Boundary decisions

- A paper was not rescued by replacing its unavailable outcome data with invented or approximate values.
- “Available from the authors on reasonable request” was treated as unavailable for this corpus because access is not assured or reproducible.
- A public PDF did not compensate for proprietary study data.
- An accessible mixed-country dataset was accepted only when a UK slice could be isolated deterministically; otherwise it was rejected.
- Supporting-method papers were admitted only when the UK component itself used public data and the transferred method was necessary for the implementation.
