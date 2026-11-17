"""Small arithmetic reconstructions from publicly printed summary statistics.

Does not reproduce original X votes, social-desirability experiments, STI
transmission, or Nuance Pill's datasets. Figures are sourced in inputs/.
"""
from pathlib import Path
import pandas as pd
import math

ROOT=Path(__file__).resolve().parents[1]

def compute():
    rows={v['check']:v for v in pd.read_csv(ROOT/'inputs'/'published_arithmetic_inputs.csv').to_dict('records')}
    oral=rows['oral_survey_category_total'];poll=rows['poll_association']
    total=int(oral['value_1']+oral['value_2']+oral['value_3'])
    mismatch=total-int(oral['reported_total'])
    women=poll['value_1']; men=poll['value_2']
    odds_ratio=(women/(1-women))/(men/(1-men))
    phi=math.sqrt(poll['value_3']/poll['reported_total'])
    return [{'check':'oral_survey_categories','derived':total,'reported':int(oral['reported_total']),'difference':mismatch,
             'interpretation':'Category counts sum to 640 versus stated N=628; categories assumed exhaustive as presented'},
            {'check':'poll_implied_odds_ratio','derived':odds_ratio,'reported':float('nan'),'difference':float('nan'),
             'interpretation':'Approximate odds ratio from rounded 50.0% vs 43.6%; not an independent poll replication'},
            {'check':'poll_phi_from_reported_chisquare','derived':phi,'reported':float('nan'),'difference':float('nan'),
             'interpretation':'Phi = sqrt(reported chi-square / reported N); X gender subgroup counts unavailable'}]

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'reproduced'/'tables'/'published_arithmetic_checks.csv');a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(compute()).to_csv(a.output,index=False)
    print(pd.DataFrame(compute()).to_string(index=False))
    # Mechanical evaluation of the *displayed, rounded* interval endpoints.
    # This is not a direct statistical test of cross-year quantile differences.
    v=pd.read_csv(ROOT/'inputs'/'harper_nuance_intervals.csv')
    v['strict_nonoverlap_as_displayed']=(v.first_ci_high < v.second_ci_low) | (v.second_ci_high < v.first_ci_low)
    v['touching_endpoint_as_displayed']=(v.first_ci_high == v.second_ci_low) | (v.second_ci_high == v.first_ci_low)
    v.to_csv(a.output.parent/'harper_nuance_interval_checks.csv',index=False)
    print('Harper/Nuance displayed-interval comparisons saved to',a.output.parent/'harper_nuance_interval_checks.csv')
