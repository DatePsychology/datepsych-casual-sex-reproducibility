from pathlib import Path
import argparse, sys
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parent))
from replicate_gss import load_data,survey_estimate
parser=argparse.ArgumentParser(description='Recreate GSS figures 01–03 and supporting aggregate tables')
parser.add_argument('--zip',required=True,help='NORC 2022_stata.zip or a GSS2022.dta file')
parser.add_argument('--output',default='reproduced',help='Destination folder for figures/ and tables/')
args=parser.parse_args()
root=Path(args.output);out=root/'figures';out.mkdir(parents=True,exist_ok=True)
(root/'tables').mkdir(exist_ok=True)
D=load_data(args.zip)
B=D[D.baselinestatus.eq(1)].copy()
NAVY='#255276';TEAL='#2b948c';LIGHT='#d2e3e6';GRAY='#515f6d';RED='#ae5946'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':13,'axes.titleweight':'semibold','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.labelcolor':'#374b5b','text.color':'#21333e'})
def write(fig,fn):
 fig.savefig(out/fn,dpi=175,bbox_inches='tight',facecolor='white');plt.close(fig)
# Fig1, faithful but raw counts shown for rare 3/4 categories directly
cats=[(0,'0'),(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5–10'),(6,'11–20')]
result={}
for name,code in [('Men',1),('Women',2)]:
 v=B[B.sex.eq(code)&B.age.between(18,35)&B.partners_8822.between(0,8)]
 den=v.wtssps.sum();result[name]=[(100*v.loc[v.partners_8822.eq(i),'wtssps'].sum()/den,int(v.partners_8822.eq(i).sum())) for i,_ in cats]
fig,ax=plt.subplots(figsize=(11.8,5.8));x=np.arange(len(cats));width=.36
for name,color,offset in [('Men',NAVY,-width/2),('Women',TEAL,width/2)]:
 vals=[a for a,b in result[name]];bars=ax.bar(x+offset,vals,width,label=f'{name} (n={189 if name=="Men" else 230})',color=color)
 for k,(bar,(_,n)) in enumerate(zip(bars,result[name])):
  pct=bar.get_height()
  if pct>.1:
   txt=f'{pct:.1f}%'+(f'\nn={n}' if k in [3,4] else '')
   ax.text(bar.get_x()+bar.get_width()/2,pct+.7,txt,ha='center',va='bottom',fontsize=7.8,color='#283b4b')
ax.set_xticks(x,[s for _,s in cats]);ax.set_ylim(0,78);ax.set_ylabel('% of age-18–35 respondents, weighted');ax.set_xlabel('Partners in preceding 12 months');ax.set_title('The GSS partner-count distribution is reproducible')
ax.legend(frameon=False,ncol=2,loc='upper right');ax.grid(axis='y',alpha=.12);ax.set_axisbelow(True)
fig.tight_layout();write(fig,'01_original_chart_replicated.png')
# Fig2 weighting comparison dot-and-interval (no trend lines)
versions=[('Historical baseline','wtssps',True),('Nonresponse-adjusted','wtssnrps',True),('Expanded sample','wtssnrps_as',False)]
records=[]
for i,(nm,w,base) in enumerate(versions):
 a=B if base else D
 for code,name in [(1,'Men'),(2,'Women')]:
  domain=a.age.between(18,35)&a.sex.eq(code)&a.partners_8822.between(0,8)&a[w].notna()&(a[w]>0)
  r=survey_estimate(a,domain,a.partners_8822.ge(2).astype(float),w)
  records.append(dict(method=nm,weight=w,sex=name,estimate=100*r['estimate'],lower=100*r['low'],upper=100*r['high'],n=r['n']))
pd.DataFrame(records).to_csv(root/'tables'/'revised_figure2_estimates.csv',index=False)
fig,ax=plt.subplots(figsize=(10.2,5.8)); xx=np.arange(len(versions))
for name,color,off in [('Men',NAVY,-.10),('Women',TEAL,.10)]:
 rec=[r for r in records if r['sex']==name]
 y=np.array([r['estimate'] for r in rec]);low=np.array([r['lower'] for r in rec]);high=np.array([r['upper'] for r in rec]);xs=xx+off
 ax.errorbar(xs,y,yerr=[y-low,high-y],marker='o',markersize=8,elinewidth=2,capsize=4,lw=0,color=color,label=name)
 for xp, yp in zip(xs,y):ax.annotate(f'{yp:.1f}%',(xp,yp),xytext=(11,0),textcoords='offset points',fontsize=9,va='center',color=color)
ax.set_xticks(xx,['Historical\nWTSSPS','Baseline nonresponse-adjusted\nWTSSNRPS','Expanded + AmeriSpeak\nWTSSNRPS_AS']);ax.set_xlim(-.5,2.65);ax.set_ylim(0,45)
ax.set_ylabel('Reporting ≥2 partners (%)');ax.set_title('Weighting choices: similar point estimates, wide intervals');ax.grid(axis='y',alpha=.16);ax.legend(frameon=False,loc='upper right');fig.tight_layout();write(fig,'02_weight_sensitivity.png')
# Fig3: Highlight male and female influential bins
fig,ax=plt.subplots(figsize=(9.9,5.3));cases=[('Men: exactly 3',1,3),('Women: exactly 4',2,4)]
xx=np.arange(2);w=.32
raw=[];weighted=[];totaln=[]
for nm,code,k in cases:
 v=B[B.sex.eq(code)&B.age.between(18,35)&B.partners_8822.between(0,8)]
 raw.append(100*v.partners_8822.eq(k).mean());weighted.append(100*v.loc[v.partners_8822.eq(k),'wtssps'].sum()/v.wtssps.sum());totaln.append(int(v.partners_8822.eq(k).sum()))
for vals,off,col,lab in [(raw,-w/2,GRAY,'Raw share'),(weighted,w/2,TEAL,'Survey-weighted share')]:
 bars=ax.bar(xx+off,vals,w,color=col,label=lab)
 for bar, val in zip(bars,vals):ax.annotate(f'{val:.1f}%',(bar.get_x()+bar.get_width()/2,val),xytext=(0,5),textcoords='offset points',ha='center',fontsize=10)
ax.set_xticks(xx,[f'{nm}\n(n={n})' for (nm,_,_),n in zip(cases,totaln)]);ax.set_ylim(0,16);ax.set_ylabel('Share of valid respondents (%)');ax.set_title('Few high-weight responses make some bars unstable');ax.legend(frameon=False);ax.grid(axis='y',alpha=.14);ax.set_axisbelow(True);fig.tight_layout();write(fig,'03_rare_bins_weight_leverage.png')
# Figures 6–9 are created by published_figures.py from disclosed transcribed inputs.
print('Generated GSS figures 01–03 and GSS aggregate tables in',root)

# Additional reproducible sensitivity diagnostics (not corrected probability estimates)
rows=[]
for sex,code in [('Men',1),('Women',2)]:
    v=B[B.sex.eq(code)&B.age.between(18,35)&B.partners_8822.between(0,8)].copy()
    w=v.wtssps.astype(float);y=v.partners_8822.ge(2)
    threshold=float(np.quantile(w,.95));wc=w.clip(upper=threshold)
    rare=3 if code==1 else 4
    excluded=v[v.partners_8822.eq(rare)].sort_values('wtssps',ascending=False).head(2 if code==1 else 1).index
    kept=v.drop(index=excluded)
    rows.append(dict(sex=sex,n=len(v),unweighted_pct=100*y.mean(),original_pct=100*w[y].sum()/w.sum(),capped_p95_pct=100*wc[y].sum()/wc.sum(),cap_threshold=threshold,excluded_n=len(excluded),excluded_pct=100*kept.loc[kept.partners_8822.ge(2),'wtssps'].sum()/kept.wtssps.sum(),rare_bin=rare))
pd.DataFrame(rows).to_csv(root/'tables'/'influence_checks.csv',index=False)
rr=[]
for lo,hi in [(18,29),(18,35),(30,35),(30,39)]:
 for name,code in [('Men',1),('Women',2)]:
    r=B[B.age.between(lo,hi)&B.sex.eq(code)&B.relatsex.isin([1,2])]
    rr.append(dict(age_min=lo,age_max=hi,sex=name,n=len(r),pct_last_sex_not_ongoing=100*r.loc[r.relatsex.eq(2),'wtssps'].sum()/r.wtssps.sum()))
pd.DataFrame(rr).to_csv(root/'tables'/'relatsex_by_age_sex.csv',index=False)
print('Additional sensitivity and RELATSEX tables written to:',root/'tables')
