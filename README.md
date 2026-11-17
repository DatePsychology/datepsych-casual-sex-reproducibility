# Is Casual Sex Really Overestimated? — Reproducibility Materials

Code, checked aggregate results, documented published-statistic inputs, and nine figures accompanying a [methodological review](https://datepsych.substack.com/p/is-casual-sex-really-overestimated) of Date Psychology's [“Casual sex” is often mismeasured and overestimated](https://datepsychology.com/casual-sex-is-often-mismeasured-and-overestimated/) (2024).

**Scope:** The GSS portion is a reanalysis of publicly downloadable 2022 survey microdata. Other graphics reconstruct **published summary statistics**, not raw participant-level datasets. The original X-poll votes/subgroups, Alexander's oral-sex survey responses, and Nuance Pill's raw analysis scripts were unavailable. The package cannot reproduce those original analyses or prove the disputed sexual-network model. See [Input sources and evidentiary limits](INPUT_SOURCES.md).

## Contents

| File or folder | Purpose |
|---|---|
| [`reproduce.py`](reproduce.py) | One command to regenerate figures and audit tables. Works in a limited *published-data-only* mode without GSS; `--gss` enables full GSS reanalysis. |
| [`src/replicate_gss.py`](src/replicate_gss.py) | Independent baseline GSS reconstruction, detailed partner bins, weighting comparisons, and interpretive checks. |
| [`src/build_figures.py`](src/build_figures.py) | Publication GSS Figures 1–3, weighted proportions, and approximate survey intervals. |
| [`src/additional_sensitivity.py`](src/additional_sensitivity.py) | GSS Figures 4–5: `RELATSEX` age-window checks, weight caps, leave-out tests, and concentration bounds. |
| [`src/published_figures.py`](src/published_figures.py) | Figures 6–9, based exclusively on explicitly transcribed primary-source summary values. |
| [`src/published_arithmetic.py`](src/published_arithmetic.py) | Reconstructs the oral-sex category-total mismatch and approximate poll association statistics from published numbers. |
| [`inputs/`](inputs/) | Source-attributed CSVs of published summary statistics: Malagón correlations, RIVM chlamydia trends, YouGov responses, Chia–Lee survey comparisons, and two arithmetic checks and displayed Harper/Nuance confidence-interval comparisons. |
| [`reference_results/`](reference_results/) | **Aggregate GSS outputs** from the verified run, useful for checking an independent rerun. Contains no individual respondent records. |
| [`figures/`](figures/) | All nine PNGs used in the companion Substack article. |
| [`INPUT_SOURCES.md`](INPUT_SOURCES.md) | Exact source location, status of source verification, and limitations of each input. |
| [`requirements.txt`](requirements.txt) | Python dependencies. |
| [`.gitignore`](.gitignore) | Helps prevent accidental upload of the public GSS ZIP, extracted microdata, or regenerated working files. |

## Reproduce the figures and calculations

Requires Python **3.10 or newer**. Tested with Python **3.13** and the dependencies in `requirements.txt`.

```bash
python -m pip install -r requirements.txt
```

**A. Without downloading the GSS** (Figures **6–9** and the supplementary arithmetic and displayed-interval checks):

```bash
python reproduce.py
```

This regenerates the four figures derived from published tables in `reproduced/figures/`, and the published-number calculations and rounded Harper/Nuance interval comparisons in `reproduced/tables/`. The *checked-in* images for Figures 1–5 and their reference tables remain viewable on GitHub, but these five GSS figures **cannot be freshly recomputed from microdata** until you supply the GSS.

**B. Full GSS microdata reproduction** (all **nine figures**, aggregate tables and diagnostics):

1. Visit [NORC GSS — Stata Data](https://gss.norc.org/get-the-data/stata.html). Under **Individual Year Data Sets**, download **2022** (official `2022_stata.zip`). No special custom extract or CSV conversion is necessary.
2. Keep the ZIP on your own computer. **Do not add it to this repository.**
3. Run:

```bash
python reproduce.py --gss /path/to/2022_stata.zip
```

Windows example (replace the path with your own):

```powershell
python reproduce.py --gss "C:\Users\YourName\Downloads\2022_stata.zip"
```

The scripts accept either the official ZIP or the extracted `GSS2022.dta` file. Output is created under `reproduced/figures/` and `reproduced/tables/`; the command prints verification assertions. By default, **nothing overwrites the checked-in `figures/` or `reference_results/`**.

The run checks 2022 baseline respondents, sex-specific valid sample sizes, two-plus-partner percentages, the age-30–39 female `RELATSEX` benchmark, concentration bounds, and the presence of nine figures. **A successful run verifies these arithmetic outputs, not the truth of the original authors' broader causal or network claims.**

## Data source and sample specification

The checked results use NORC's public-use single-year **2022 GSS** Stata download, including its **Release 3a** updates. The ZIP supplied for the audit contains `2022/GSS2022.dta`, with **4,149 total** records: **3,544 baseline** respondents (`BASELINESTATUS = 1`) and **605 AmeriSpeak** additions.

For the reproduction of Alexander's original histogram:

- Age **18–35** inclusive; `SEX = 1` (men), `SEX = 2` (women).
- Baseline sample only: `BASELINESTATUS = 1`.
- Valid specified partner-count categories: `PARTNERS_8822` in **0–8**, excluding unspecified and missing codes. Codes **5–8 are ranges**, not literal integer counts: 5–10, 11–20, 21–100, >100.
- Historical `WTSSPS` weights. This yields **189 men and 230 women** with valid specified partner counts.
- Alternative weights are compared separately: baseline `WTSSNRPS` and expanded sample `WTSSNRPS_AS`.
- `RELATSEX` is a **last-encounter** item, **not** a question about any casual sex in the previous 12 months.

The expected underlying file (`GSS2022.dta`) has SHA-256 digest:

```
334ac5a7d7623e779800dedf5b1b39e3b6883c5d2bac6a26302b3b3f26773148
```

The ZIP used for this checked run had SHA-256 `ba0bc3255ce59d5351b8e5382c81d9d29ad6275d61cf24f6f027b69ef2e97fd0`. Future NORC releases can change numbers, labels, or sample definitions; if you obtain a different version, disclose it instead of silently treating mismatches as proof of errors in the original analysis.

## Main GSS benchmark results

| Weighted estimate, baseline WTSSPS, ages 18–35 | Men | Women |
|---|---:|---:|
| Valid specified partner counts, unweighted *n* | 189 | 230 |
| At least two partners in last year | **22.78%** | **21.05%** |
| Approximate 95% interval for preceding estimate | **8.4–37.2%** | **11.8–30.3%** |
| Reporting three or more partners | **16.49%** | **12.57%** |
| Share of summed partner-count totals by 3+ group (grouped-count lower–upper bounds) | **45.3–50.8%** | **37.9–42.8%** |
| Same concentration share after diagnostic removal of high-weight respondents | **28.9–37.8%** | **30.2–36.3%** |

The sensitivity exclusions remove **two high-weight men in the three-partner cell** and **one high-weight woman in the four-partner cell**. These are **diagnostics, not corrected estimates**. The approximate confidence intervals use the public-use `VSTRAT` / `VPSU` fields and Taylor linearization; they are **not official NORC interval estimates**, and may depend on design and small-sample conventions. The lower/upper *concentration* ranges are not confidence intervals: they arise from using category endpoints for grouped partner counts.

The 2022 baseline also permits a female `RELATSEX` result near **10.3%** when the **30–39** age interval is selected, but that age interval was found **exploratorily**. It is not evidence that Alexander selected precisely this age band. Nearby windows differ (see `reference_results/relatsex_age_sensitivity.csv`).

## Figure-to-code and evidence map

| Article figure | Content | Provenance | Reproduction script |
|---|---|---|---|
| 1 | Original GSS partner-count histogram faithfully reconstructed | **Microdata** | `src/build_figures.py` |
| 2 | Different weighting choices, with approximate intervals | **Microdata** | `src/build_figures.py` |
| 3 | Influence of small high-weight bins | **Microdata** | `src/build_figures.py` |
| 4 | `RELATSEX` age windows, approximate intervals, weight-cap checks | **Microdata** | `src/additional_sensitivity.py` |
| 5 | Bounds for share of reported partner-count totals and sensitivity | **Microdata** | `src/additional_sensitivity.py` |
| 6 | Correlations between dating partners' sexual histories | **Transcribed published values** | `src/published_figures.py` |
| 7 | Dutch chlamydia positivity/testing, 2018–2022 | **Published values; 2018–21 testing volumes approximate** | `src/published_figures.py` |
| 8 | YouGov opinions on whether oral-only activity counts as sex | **Official published table** | `src/published_figures.py` |
| 9 | Singapore students' self-reported and estimated peer behavior/attitudes | **Published Table 1** | `src/published_figures.py` |

## Interpretation, non-replications, and limits

- **Validated:** The historical-weight GSS histogram can be reconstructed. The distributions show concentration in **individuals' reported counts**. The fine categories are sensitive to relatively few large weights.
- **Not identified:** These marginal counts do *not* reveal whom respondents partnered with, the proportion of unique partners accounted for by the 3+ group, the true prevalence of casual sex, or a distinct 10% sexual network. STI case and clinic data do not solve that identification problem.
- **Published-summary charts:** The Malagón, YouGov, Chia–Lee, and RIVM charts are reproductions of **published numbers**. The underlying investigators' respondent-level data were not independently replicated here.
- **No fabricated X-poll reconstruction:** The original poll’s sex-specific raw counts and votes are unavailable. `published_arithmetic.py` calculates an approximate odds ratio from **rounded published percentages** and phi from the **reported** chi-square and *N*; it cannot verify the chi-square itself.
- **Alexander's oral-sex survey:** Its published category counts sum to 640 despite a stated total of 628. The script checks that arithmetic only; it does not infer the true unobserved breakdown or allege intentional misconduct.
- **Nuance Pill/Harper:** `inputs/harper_nuance_intervals.csv` documents their *displayed* rounded intervals, including the touching-endpoint cases; the derived overlap flags are not direct significance tests. The companion article describes a disputed confidence-interval replication and source-interpretation errors. No claim is made to have rerun Nuance Pill's NSFG, GSS, or NHANES analyses. The relevant original Harper article is available at [CDC Stacks](https://stacks.cdc.gov/view/cdc/151663/cdc_151663_DS1.pdf).
- **No definitive causal claims:** Cross-sectional survey associations or STI trends should not be interpreted as demonstrations of media-caused misperceptions or sexual-network structure.

## Main sources

- [Alexander (2024), “Casual sex” is often mismeasured and overestimated](https://datepsychology.com/casual-sex-is-often-mismeasured-and-overestimated/)
- [NORC, GSS public-use Stata downloads](https://gss.norc.org/get-the-data/stata.html) and [2022 codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202022%20Codebook.pdf)
- [Malagón et al. (2017), assortativity in newly formed dating partnerships](https://pubmed.ncbi.nlm.nih.gov/28499281/)
- [RIVM (2023), *Sexually transmitted infections in the Netherlands in 2022*](https://www.rivm.nl/bibliotheek/rapporten/2023-0161.pdf)
- [YouGov (2023), original table PDF](https://d3nkl3psvxxpe9.cloudfront.net/documents/YouGov_-_What_counts_as_sex.pdf)
- [Chia & Lee (2008), peer sexual-norm misperceptions](https://doi.org/10.1093/ijpor/edn005)
- [Harper et al. (2017), Changes in the distribution of sex partners](https://stacks.cdc.gov/view/cdc/151663/cdc_151663_DS1.pdf)

The companion critique contains a fuller bibliography. **This repository contains no copyrighted article/PDF copies, cloned third-party webpages, original poll votes, or respondent-level GSS data.** Research code and publication figures may be reused subject to whatever license the repository owner chooses to apply; no license is asserted for third-party materials.
