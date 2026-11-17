# Sources and classifications for the transcribed inputs

This repository distinguishes **(A) reanalysis from respondent-level GSS data obtained separately**, **(B) recomputation from published summary statistics**, and **(C) graphical approximations**. The CSVs here contain no respondent-level records.

| CSV | Source | Classification | Important caveat |
|---|---|---|---|
| `malagon_assortativity.csv` | Malagón et al. (2017), Table 2, https://pubmed.ncbi.nlm.nih.gov/28499281/ | B: published correlation estimates and 95% CIs | Selected young Montreal couples; approximately 92% of initial relationships described as steady. Not population mixing matrix. |
| `yougov_oral_sex_definitions.csv` | YouGov (2023), https://d3nkl3psvxxpe9.cloudfront.net/documents/YouGov_-_What_counts_as_sex.pdf, **p. 1** | B: labeled official table | The companion YouGov article reverses 45% yes and 41% no for all adults. Follow the PDF's labeled rows. |
| `chia_lee_peer_norms.csv` | Chia & Lee (2008), Table 1, https://doi.org/10.1093/ijpor/edn005 | B: published frequencies and average peer estimates | Sample at one Singapore university, 13.4% response rate. Self-reports are not objective verification. |
| `rivm_chlamydia_series_2018_2022.csv` | RIVM annual reports, particularly https://www.rivm.nl/bibliotheek/rapporten/2023-0161.pdf, Table 3.1/Figure 3.2 | B for positivity and 2022 counts; C for 2018–2021 counts | `Earlier_test_counts_approximate=True` marks approximate graph readings, not exact records. Clinic attendees are selected. |
| `harper_nuance_intervals.csv` | Harper et al. (2017), Tables 1–2, https://stacks.cdc.gov/view/cdc/151663/cdc_151663_DS1.pdf; and Nuance Pill (2023), https://web.archive.org/web/20231213174745/https://nuancepill.com/are-the-male-elite-enjoying-a-sexual-boomtime/ | B: displayed published intervals and C: rough readings from the later NSFG plot | The automated nonoverlap indicator is **only a comparison of rounded displayed endpoints**. No direct quantile-difference test or replication of either author’s code. |
| `published_arithmetic_inputs.csv` | Alexander's original essays | B: author's published numbers | These checks do not validate the underlying original surveys. |
| `reference_results/*.csv` | Independent calculations from NORC's 2022 GSS public dataset | A: aggregate outputs only | Produced by the bundled GSS code using an official dataset downloaded separately. Source release includes 2026 R3a updates; sample/weights documented in README. |

**Other conclusions are conceptual/source-interpretation checks, not reproducible estimates**: `RELATSEX` measures last sexual encounter, not annual casual sex; individual partner totals do not identify which people partnered; parallel STI curves cannot identify sexual mixing. The original X-poll data, Alexander's oral-sex individual responses, and Nuance Pill's original NSFG/GSS/NHANES analysis code are not part of this package.
