#!/usr/bin/env python3
"""2022 GSS audit for Date Psychology's March 2024 sexual-partner histogram.

Usage: python replicate_gss.py --zip /path/to/2022_stata.zip --output audit_output
Dependencies: pandas, numpy, scipy, matplotlib
The source zip is not redistributed; obtained from NORC GSS single-year Stata download.
"""
import argparse
import tempfile
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import t

CATEGORIES = [(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5–10'), (6, '11–20'), (7, '21–100'), (8, '>100')]
CATS = [v for v, _ in CATEGORIES]


def load_data(path):
    path = Path(path)
    if path.suffix.lower() == '.dta':
        return pd.read_stata(path, convert_categoricals=False)
    with zipfile.ZipFile(path) as z, tempfile.TemporaryDirectory() as tmp:
        matches = [v for v in z.namelist() if v.lower().endswith('gss2022.dta')]
        if len(matches) != 1:
            raise ValueError(f'Expected one GSS2022.dta, got {matches}')
        z.extract(matches[0], tmp)
        return pd.read_stata(Path(tmp) / matches[0], convert_categoricals=False)


def survey_estimate(df, domain, y, wtcol='wtssps'):
    """Approx Taylor-linearized domain ratio with 2022 public-use vstrat/vpsu design.

    The complex-sample variance estimate is approximate; the codebook's
    'svyset [pweight=WTSSNRPS], strata(vstrat) psu(vpsu)' inspired it.
    Use full survey rows in the variance calculation, zero outside domain.
    """
    weights = df[wtcol].fillna(0).to_numpy(dtype=float)
    domain = domain.to_numpy(dtype=bool) & np.isfinite(weights) & (weights > 0)
    y = np.asarray(y, dtype=float)
    denom = weights[domain].sum()
    est = np.dot(weights[domain], y[domain]) / denom
    linear = np.zeros(len(df))
    linear[domain] = weights[domain] * (y[domain] - est) / denom
    d = df[['vstrat', 'vpsu']].copy()
    d['linear'] = linear
    variance = 0.
    for _, st in d.groupby('vstrat'):
        psu_totals = st.groupby('vpsu')['linear'].sum().to_numpy()
        m = len(psu_totals)
        if m > 1:
            variance += m / (m - 1) * np.sum((psu_totals - psu_totals.mean()) ** 2)
    se = np.sqrt(variance)
    dfree = df['vstrat'].nunique()
    critical = t.ppf(0.975, dfree)
    return dict(estimate=float(est), se=float(se), low=float(est-critical*se), high=float(est+critical*se), n=int(domain.sum()),
                kish_n=float(denom**2 / np.sum(weights[domain]**2)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', required=True, help='Official NORC 2022_stata.zip or GSS2022.dta')
    parser.add_argument('--output', default='gss2022_audit_output')
    args = parser.parse_args()
    out = Path(args.output); (out/'figures').mkdir(parents=True, exist_ok=True); (out/'tables').mkdir(exist_ok=True)
    d = load_data(args.zip)
    assert d.shape[0] == 4149, 'Expected 2022 GSS combined release with 4,149 rows'
    assert int(d.baselinestatus.eq(1).sum()) == 3544

    versions = [
        ('Historical baseline · WTSSPS', 'wtssps', True),
        ('Baseline · WTSSNRPS', 'wtssnrps', True),
        ('Combined · WTSSNRPS_AS', 'wtssnrps_as', False)
    ]
    bins = []; summary = []
    for version, weight, baseline in versions:
        use = d[d.baselinestatus.eq(1)].copy() if baseline else d.copy()
        for code, sex in [(1, 'Men'), (2, 'Women')]:
            all_age = use[use.age.between(18,35) & use.sex.eq(code)].copy()
            valid = all_age[all_age.partners_8822.between(0,8) & all_age[weight].notna() & (all_age[weight] > 0)].copy()
            sumwt = valid[weight].sum()
            kish = sumwt**2 / (valid[weight]**2).sum()
            def percent(mask): return float(100*valid.loc[mask,weight].sum()/sumwt)
            for value,label in CATEGORIES:
                subset = valid[valid.partners_8822.eq(value)]
                bins.append(dict(version=version, sex=sex, category=label, category_code=value, unweighted_count=len(subset),
                                 unweighted_pct=100*len(subset)/len(valid), weighted_pct=100*subset[weight].sum()/sumwt))
            dom = use.age.between(18,35) & use.sex.eq(code) & use.partners_8822.between(0,8)
            pr=survey_estimate(use,dom,use.partners_8822.ge(2).astype(float),weight)
            summary.append(dict(version=version, sex=sex, age_18_35_respondents=len(all_age), valid_n=len(valid), unspecified_n=int(all_age.partners_8822.eq(9).sum()),
                                kish_effective_n=round(kish,2), zero_pct=percent(valid.partners_8822.eq(0)), one_pct=percent(valid.partners_8822.eq(1)),
                                two_plus_pct=percent(valid.partners_8822.ge(2)), three_plus_pct=percent(valid.partners_8822.ge(3)), five_plus_pct=percent(valid.partners_8822.ge(5)),
                                two_plus_se_pp=100*pr['se'], two_plus_ci_low=100*pr['low'], two_plus_ci_high=100*pr['high']))
    tb=pd.DataFrame(bins); smry=pd.DataFrame(summary)
    tb.to_csv(out/'tables'/'partner_bins_by_weight.csv', index=False, float_format='%.4f')
    smry.to_csv(out/'tables'/'summary_weight_sensitivity.csv', index=False, float_format='%.4f')

    # Plot 1: faithful percentage reconstruction, not an exact rendering copy of the original artwork.
    hist=tb[tb.version == versions[0][0]]
    labels=[label for val,label in CATEGORIES if val <= 6]
    men=[float(hist[(hist.sex=='Men')&(hist.category==c)].weighted_pct.iloc[0]) for c in labels]
    women=[float(hist[(hist.sex=='Women')&(hist.category==c)].weighted_pct.iloc[0]) for c in labels]
    x=np.arange(len(labels)); w=.38
    fig,ax=plt.subplots(figsize=(11,5.6))
    b1=ax.bar(x-w/2,men,w,label='Men (n=189)'); b2=ax.bar(x+w/2,women,w,label='Women (n=230)')
    ax.set(xlabel='Partners reported in previous 12 months',ylabel='Weighted percentage of valid responses',title='Reproducing Date Psychology’s GSS 2022 chart (ages 18–35)')
    ax.set_xticks(x,labels);ax.legend();ax.set_ylim(0,76);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    for rect in list(b1)+list(b2):
        v=rect.get_height()
        if v>0.15: ax.annotate(f'{v:.1f}%',(rect.get_x()+rect.get_width()/2,v),xytext=(0,4),textcoords='offset points',ha='center',fontsize=8)
    fig.text(.1,.02,'Source: GSS 2022 baseline, PARTNERS_8822; weight WTSSPS; 419 valid age-18–35 respondents. Figure newly produced from public microdata.',fontsize=9)
    fig.subplots_adjust(bottom=.17)
    fig.savefig(out/'figures'/'01_original_chart_replicated.png',dpi=180,bbox_inches='tight');plt.close(fig)

    # Plot 2: compare old and newer recommended weights.
    f=smry.copy()
    fig,ax=plt.subplots(figsize=(10.8,5.3))
    for sex in ['Men','Women']:
        rows=f[f.sex==sex]
        ax.plot(range(3), rows.two_plus_pct,marker='o',label=f'{sex} reporting 2+ partners')
        for j,yval in enumerate(rows.two_plus_pct):ax.annotate(f'{yval:.1f}%',(j,yval),xytext=(0,9 if sex=='Men' else -15),textcoords='offset points',ha='center',fontsize=9)
    ax.set_xticks(range(3),['Historical\nWTSSPS','Baseline nonresponse-adjusted\nWTSSNRPS','Baseline + AmeriSpeak\nWTSSNRPS_AS'])
    ax.set_ylim(15,27);ax.set_ylabel('Weighted percentage, ages 18–35');ax.set_title('How sensitive is the “roughly 20%” result to GSS weighting?');ax.grid(axis='y',alpha=.2);ax.legend(loc='upper right')
    fig.text(.12,.02,'Same 2022 GSS data; final group adds 605 AmeriSpeak respondents to the 3,544 baseline sample. Source: NORC.',fontsize=9)
    fig.subplots_adjust(bottom=.22)
    fig.savefig(out/'figures'/'02_weight_sensitivity.png',dpi=180,bbox_inches='tight');plt.close(fig)

    # Plot 3: female 3-vs-4 partner reversal under weights.
    f=hist[(hist.sex=='Women') & (hist.category.isin(['3','4']))]
    x=np.arange(2); w=.34
    fig,ax=plt.subplots(figsize=(8.3,5.2))
    a=ax.bar(x-w/2,f.unweighted_pct.to_numpy(),w,label='Unweighted');b=ax.bar(x+w/2,f.weighted_pct.to_numpy(),w,label='WTSSPS-weighted')
    ax.set_xticks(x,['Exactly 3 partners\n(12 respondents)','Exactly 4 partners\n(9 respondents)']);ax.set_ylabel('Percentage among 230 valid female respondents');ax.set_title('Why the original female distribution looks unusual');ax.legend();ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    for rect in list(a)+list(b):ax.annotate(f'{rect.get_height():.1f}%',(rect.get_x()+rect.get_width()/2,rect.get_height()),xytext=(0,4),textcoords='offset points',ha='center')
    ax.set_ylim(0,9)
    fig.text(.08,.02,'One respondent supplies 51% of the weighted total in the four-partner category. This does not itself show a data error.',fontsize=9)
    fig.subplots_adjust(bottom=.23)
    fig.savefig(out/'figures'/'03_rare_bins_weight_leverage.png',dpi=180,bbox_inches='tight');plt.close(fig)

    # Public-sample leverage and time-window cross-checks.
    orig=d[d.baselinestatus.eq(1) & d.age.between(18,35)].copy()
    findings=[]
    for code,sex in [(1,'Men'),(2,'Women')]:
        dd=orig[orig.sex.eq(code)]
        valid=dd[dd.partners_8822.between(0,8)]
        rel=dd[dd.relatsex.isin([1,2])]
        rel_pct=100*rel.loc[rel.relatsex.eq(2),'wtssps'].sum()/rel.wtssps.sum()
        rare_value=3 if code==1 else 4
        rare=valid[valid.partners_8822.eq(rare_value)].wtssps.sort_values(ascending=False)
        top_n=2 if code==1 else 1
        findings.append(dict(sex=sex, rare_category=rare_value, rare_raw_n=len(rare), most_weighted_count=top_n,
                             share_of_rare_weight_by_top_cases=100*rare.head(top_n).sum()/rare.sum(),
                             last_sex_no_ongoing_pct=rel_pct, last_sex_valid_n=len(rel),
                             zero_partners_but_last_sex_answer_n=int((dd.partners_8822.eq(0)&dd.relatsex.isin([1,2])).sum()),
                             reported_pickup_yes_n=int((valid.pikupsex==1).sum()),
                             pickup_yes_with_one_partner_n=int((valid.partners_8822.eq(1)&valid.pikupsex.eq(1)).sum())))
    pd.DataFrame(findings).to_csv(out/'tables'/'interpretation_checks.csv',index=False,float_format='%.4f')
    print('Reproduced the original age-18–35 WTSSPS chart. Detailed tables and figures written to:',out)
    print(smry[['version','sex','valid_n','two_plus_pct','two_plus_ci_low','two_plus_ci_high']].round(2).to_string(index=False))
    print(pd.DataFrame(findings).round(2).to_string(index=False))

if __name__=='__main__':main()
