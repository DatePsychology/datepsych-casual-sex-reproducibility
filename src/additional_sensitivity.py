#!/usr/bin/env python3
"""Reproduce GSS concentration bounds and RELATSEX age/window/CI sensitivity.

Requires: numpy, pandas, scipy; original NORC 2022_stata.zip. Outputs only
aggregate tables. No respondent-level data are distributed.

python additional_sensitivity.py --zip /path/to/2022_stata.zip --output output
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from replicate_gss import load_data, survey_estimate

p=argparse.ArgumentParser();p.add_argument('--zip',required=True);p.add_argument('--output',default='sensitivity_tables');args=p.parse_args()
root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
D=load_data(args.zip); B=D[D.baselinestatus.eq(1)].copy()
lo={0:0,1:1,2:2,3:3,4:4,5:5,6:11,7:21,8:101}
hi={0:0,1:1,2:2,3:3,4:4,5:10,6:20,7:100,8:101}
con=[]
for sex,sex_code in [('Men',1),('Women',2)]:
 v=B[B.sex.eq(sex_code)&B.age.between(18,35)&B.partners_8822.between(0,8)&(B.wtssps>0)].copy()
 wcap=v.wtssps.clip(upper=v.wtssps.quantile(0.95))
 rare=3 if sex_code==1 else 4
 omit=v[v.partners_8822.eq(rare)].sort_values('wtssps',ascending=False).head(2 if sex_code==1 else 1).index
 for method,a,w in [('historical WTSSPS',v,v.wtssps),('95th-percentile weight cap',v,wcap),('drop influential cases',v.drop(index=omit),v.drop(index=omit).wtssps),('unweighted',v,pd.Series(1.,index=v.index))]:
  count=a.partners_8822.astype(int);ww=w.to_numpy(float);minor=count.map(lo).to_numpy(float);major=count.map(hi).to_numpy(float)
  high=count.ge(3).to_numpy(bool)
  # group 3+ has numerator and is also part of denominator; only non-group values vary to get extreme fraction
  group_low=(ww[high]*minor[high]).sum();group_high=(ww[high]*major[high]).sum()
  others_low=(ww[~high]*minor[~high]).sum();others_high=(ww[~high]*major[~high]).sum()
  result_low=100*group_low/(group_low+others_high)
  result_high=100*group_high/(group_high+others_low)
  con.append(dict(sex=sex,method=method,unweighted_n=len(a),concentration_lower_pct=result_low,concentration_upper_pct=result_high,
                  population_share_three_plus_pct=100*np.sum(ww[high])/np.sum(ww),
                  removed_respondents=len(omit) if method=='drop influential cases' else 0))
pd.DataFrame(con).to_csv(root/'concentration_sensitivity.csv',index=False,float_format='%.4f')
rel=[]
for left,right in [(18,24),(18,29),(18,35),(25,34),(28,32),(30,35),(30,39),(35,44)]:
 for sex,code in [('Men',1),('Women',2)]:
  domain=B.age.between(left,right)&B.sex.eq(code)&B.relatsex.isin([1,2])&(B.wtssps>0)
  v=B[domain].copy(); y=v.relatsex.eq(2);w=v.wtssps
  estimate=100*w[y].sum()/w.sum(); cap=w.clip(upper=w.quantile(.95))
  capped=100*cap[y].sum()/cap.sum()
  err=survey_estimate(B,domain,B.relatsex.eq(2).astype(float),'wtssps')
  rel.append(dict(age_from=left,age_to=right,sex=sex,unweighted_n=len(v),weighted_pct=estimate,
                  approximate_ci_low_pct=100*err['low'],approximate_ci_high_pct=100*err['high'],
                  capped_95th_pct=capped,kish_effective_n=err['kish_n']))
pd.DataFrame(rel).to_csv(root/'relatsex_age_sensitivity.csv',index=False,float_format='%.4f')
print('Created',root/'concentration_sensitivity.csv','and',root/'relatsex_age_sensitivity.csv')

# Publication figures, using only aggregate values computed above.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
outfig = root.parent/'figures'
outfig.mkdir(exist_ok=True,parents=True)
NAVY='#255276'; TEAL='#2b948c'; GRAY='#526674'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.titleweight':'semibold','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','text.color':'#223440','axes.labelcolor':'#304b5a'})
cr=pd.DataFrame(con)
methods=['historical WTSSPS','95th-percentile weight cap','drop influential cases','unweighted']
labels=['Original survey weights','95th-percentile weight cap','Influential cases excluded','Unweighted respondents']
fig,ax=plt.subplots(figsize=(11,5.4));y=np.arange(4)[::-1]
for sx,color,off in [('Men',NAVY,.15),('Women',TEAL,-.15)]:
 sub=cr[cr.sex.eq(sx)].set_index('method').loc[methods]
 lo=np.array(sub.concentration_lower_pct);hi=np.array(sub.concentration_upper_pct);midd=(lo+hi)/2
 ax.hlines(y+off,lo,hi,colors=color,linewidth=5,alpha=.85)
 ax.scatter(midd,y+off,color=color,s=42,zorder=3)
 for x1,x2,z in zip(lo,hi,y+off):ax.text(x2+1,z,f'{x1:.0f}–{x2:.0f}%',va='center',fontsize=9,color=color)
ax.set_yticks(y,labels);ax.set_xlim(0,65);ax.set_ylim(-.6,3.65);ax.set_xlabel('Share of summed annual partner-count totals (%)');ax.set_title('How sensitive are the GSS concentration bounds?');ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
ax.legend(handles=[Line2D([0],[0],color=NAVY,lw=5,label='Men'),Line2D([0],[0],color=TEAL,lw=5,label='Women')],frameon=False,loc='lower right')
fig.tight_layout();fig.savefig(outfig/'05_concentration_sensitivity.png',dpi=190,bbox_inches='tight');plt.close(fig)

r=pd.DataFrame(rel)
windows=['18–24','18–29','18–35','25–34','28–32','30–35','30–39','35–44']
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,7.1),gridspec_kw={'width_ratios':[1,1]},sharey=False)
y=np.arange(len(windows))[::-1]
for sex,color,off in [('Men',NAVY,.14),('Women',TEAL,-.14)]:
 sr=r[r.sex.eq(sex)].copy();sr['age']=sr.age_from.astype(str)+'–'+sr.age_to.astype(str)
 sr=sr.set_index('age').loc[windows]
 val=sr.weighted_pct.to_numpy()
 ax1.scatter(val,y+off,color=color,s=42,label=sex,zorder=3)
 for pct,yy in zip(val,y+off): ax1.text(pct+.8,yy,f'{pct:.1f}',va='center',fontsize=8,color=color)
ax1.set_yticks(y,windows);ax1.set_xlabel('Last encounter not with ongoing partner (%)');ax1.set_xlim(0,78);ax1.set_title('Different age windows, different estimates');ax1.grid(axis='x',alpha=.15);ax1.legend(frameon=False,loc='lower right')
labels=['Men, 18–35','Women, 18–35','Men, 30–39','Women, 30–39']
values=[]
for age_lo,age_hi,sx in [(18,35,'Men'),(18,35,'Women'),(30,39,'Men'),(30,39,'Women')]:
 values.append(r[(r.age_from==age_lo)&(r.age_to==age_hi)&r.sex.eq(sx)].iloc[0])
y2=np.arange(4)[::-1]
for yy,rr,lab in zip(y2,values,labels):
 color=NAVY if lab.startswith('Men') else TEAL
 val=rr.weighted_pct
 ax2.errorbar(val,yy,xerr=[[val-rr.approximate_ci_low_pct],[rr.approximate_ci_high_pct-val]],fmt='o',capsize=4,color=color,ms=7,lw=2)
 ax2.scatter(rr.capped_95th_pct,yy,marker='D',s=42,facecolors='white',edgecolors=color,linewidths=1.7,zorder=5)
ax2.set_yticks(y2,labels);ax2.set_xlim(0,66);ax2.set_ylim(-.7,3.65)
ax2.set_xlabel('Percentage (%)');ax2.set_title('Selected windows: approximate 95% CIs')
ax2.grid(axis='x',alpha=.15)
ax2.legend(handles=[Line2D([0],[0],color=GRAY,marker='o',lw=2,label='Original estimate ± approx. 95% CI'),Line2D([0],[0],color=GRAY,marker='D',markerfacecolor='white',lw=0,label='95th-percentile weight-cap diagnostic')],loc='lower right',frameon=False,fontsize=8)
fig.suptitle('GSS RELATSEX: a last-encounter question, not past-year casual sex',y=1.02,fontsize=14)
fig.tight_layout(w_pad=2.5);fig.savefig(outfig/'04_relatsex_age_sensitivity.png',dpi=190,bbox_inches='tight');plt.close(fig)
