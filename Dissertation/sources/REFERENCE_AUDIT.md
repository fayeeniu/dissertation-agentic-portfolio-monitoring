# Reference audit

Audit date: 31 August 2026

Every source cited in the dissertation has a local PDF. The title, author or corporate author, year,
publication details and identifier were checked against the local copy. The claim pages used in the
dissertation are listed separately in `CLAIM_LEDGER.md`. `check_sources.py --strict-bibliography`
checks that every cited key has a bibliography entry, manifest row, local PDF, matching checksum and
correct page count. `check_claim_ledger.py` checks that each substantive paragraph has the same
citation set as its page-level evidence row.

The bibliography follows Harvard (Warwick WMS): round author-date citations, `&` before the final
author, entries in A-Z order, and `Available from` with an access date for web pages. Undated official
pages use an `n.d.` suffix in the display label. Internal citation keys may retain `2026` to keep the
source and claim ledgers stable; the bibliography does not imply a publication year for those pages.

| Citation key | Local PDF | Pages | Result |
|---|---|---:|---|
| `affinity2026portfolio` | `html/affinity_portfolio_management.pdf` | 4 | Verified official vendor capture; capability description only |
| `amershi2019guidelines` | `papers/13_amershi_human_ai_guidelines.pdf` | 19 | Verified |
| `artstein2008agreement` | `papers/35_artstein_poesio_intercoder_agreement.pdf` | 42 | Verified |
| `bradley2024synfintabs` | `papers/06_bradley_et_al_2024_synfintabs.pdf` | 12 | Verified |
| `britishbusinessbank2025equity` | `papers/39_british_business_bank_equity_tracker_2025.pdf` | 78 | Verified; descriptive market context, not system-effect evidence |
| `bucinca2021forcing` | `papers/31_bucinca_cognitive_forcing.pdf` | 21 | Verified |
| `buneman2001provenance` | `papers/42_buneman_et_al_data_provenance.pdf` | 16 | Verified; database-query provenance scope retained |
| `cddo2023genai` | `papers/26_hmg_generative_ai_framework.pdf` | 76 | Verified |
| `cemri2025masfailures` | `papers/43_cemri_et_al_multi_agent_failures.pdf` | 47 | Verified; selected task/system and model-assisted annotation limits retained |
| `demsar2006comparisons` | `papers/36_demsar_statistical_comparisons.pdf` | 30 | Verified |
| `diciccio1996bootstrap` | `papers/38_diciccio_efron_bootstrap_confidence_intervals.pdf` | 40 | Verified |
| `estrin2024digital` | `papers/01_estrin_et_al_2024_access_to_digital_finance.pdf` | 17 | Verified |
| `fca2024promotions` | `papers/27_fca_financial_promotions_guidance.pdf` | 47 | Verified |
| `galanakis2026chrt` | `papers/03_savagar_galanakis_2026_tracking_firm_creation.pdf` | 33 | Verified |
| `gale2013framework` | `papers/37_gale_framework_method_qualitative_analysis.pdf` | 8 | Verified |
| `gao2023alce` | `papers/28_gao_alce_citations.pdf` | 24 | Verified |
| `gao2023rarr` | `papers/16_lewis_rarr_attribution.pdf` | 32 | Verified |
| `gao2023ragsurvey` | `papers/17_gao_rag_survey.pdf` | 21 | Verified |
| `gebru2021datasheets` | `papers/20_gebru_datasheets_for_datasets.pdf` | 18 | Verified |
| `gompers2016vcdecisions` | `papers/40_gompers_et_al_venture_capital_decisions.pdf` | 64 | Verified NBER working paper; descriptive self-report, not causal tool evidence |
| `greshake2023indirect` | `papers/29_greshake_indirect_prompt_injection.pdf` | 33 | Verified |
| `guo2024multiagent` | `papers/19_guo_llm_multi_agent_survey.pdf` | 15 | Verified |
| `hardman2023small` | `papers/04_hardman_ramirez_santos_2023_think_small_first.pdf` | 49 | Verified |
| `hevner2004design` | `papers/14_hevner_design_science.pdf` | 32 | Verified |
| `huang2023hallucination` | `papers/18_huang_llm_hallucination_survey.pdf` | 58 | Verified |
| `kaplan2016vcdata` | `papers/41_lerner_et_al_venture_capital_data.pdf` | 26 | Verified NBER working paper; historical data-provider and disclosure caveats retained |
| `kapoor2023leakage` | `papers/32_kapoor_data_leakage.pdf` | 29 | Verified |
| `krasikov2020ready` | `papers/10_krasikov_et_al_2020_open_data_ready_enterprises.pdf` | 12 | Verified |
| `mitchell2019modelcards` | `papers/21_mitchell_model_cards.pdf` | 10 | Verified |
| `mondal2025state` | `papers/07_mondal_mellor_2025_state_support_innovation_pathways.pdf` | 12 | Verified |
| `nist2023airmf` | `papers/11_nist_ai_rmf_1_0.pdf` | 48 | Verified |
| `autio2024genai` | `papers/12_nist_genai_profile.pdf` | 64 | Verified |
| `nikiforova2020quality` | `papers/05_nikiforova_et_al_2020_user_oriented_data_quality.pdf` | 20 | Verified |
| `openai2026datacontrols` | `html/openai_data_controls.pdf` | 19 | Verified, no publication date shown |
| `openai2026websearch` | `html/openai_web_search.pdf` | 12 | Verified, no publication date shown |
| `peffers2007dsrm` | `papers/15_peffers_design_science_methodology.pdf` | 53 | Verified; published page range is 45-77 |
| `pineau2021reproducibility` | `papers/33_pineau_reproducibility.pdf` | 20 | Verified |
| `ribeiro2020checklist` | `papers/34_ribeiro_checklist.pdf` | 11 | Verified; supplies the behavioural-testing warrant for D0. Diagnostic scope retained: a targeted suite shows a behaviour is present, not a rate on unseen data |
| `sculley2015debt` | `papers/22_sculley_ml_technical_debt.pdf` | 9 | Verified; ML-system debt patterns transferred conceptually to fixed-rule maintenance cost, not as a measurement of this prototype |
| `surak2026gateways` | `papers/08_surak_inkley_2026_gateways_funnels_stackers.pdf` | 15 | Verified |
| `thorne2026funding` | `papers/09_thorne_et_al_2026_uk_funding_lifecycle.pdf` | 9 | Verified |
| `visible2026investors` | `html/visible_investors.pdf` | 14 | Verified official vendor capture; capability description only |
| `wasti2024successive` | `papers/02_wasti_et_al_2024_successive_round_signal.pdf` | 16 | Verified |
| `wu2024autogen` | `papers/30_wu_autogen_multi_agent.pdf` | 46 | Verified |
| `zapflow2026portfolio` | `html/zapflow_portfolio_management.pdf` | 6 | Verified official vendor capture; capability description only |

`ribeiro2020checklist` and `sculley2015debt` were previously admitted but uncited. Both are now cited
and carry bibliography entries: the first as the methodological warrant for the D0 behavioural suite
(Sections 2.7 and 3.3), the second on the maintenance cost of fixed rules and the risk added by extra
roles (Sections 1.5 and 7.5).

One additional PDF is kept in the source library for possible later use. It is not in the
bibliography because the dissertation does not cite it.
