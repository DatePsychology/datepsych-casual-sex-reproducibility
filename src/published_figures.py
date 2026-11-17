#!/usr/bin/env python3
"""Rebuild article Figures 6–9 from explicitly transcribed published inputs.

These are *not* reanalyses of Malagón, RIVM, YouGov, or Chia/Lee original
respondent-level microdata. The source tables in inputs/ are attributed in
INPUT_SOURCES.md. Figure 7 has explicitly approximate 2018–21 test volumes.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NAVY='#255276'; TEAL='#2b948c'; GRAY='#515f6d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':13,
    'axes.titleweight':'semibold','axes.spines.top':False,'axes.spines.right':False,
    'figure.facecolor':'white','axes.labelcolor':'#374b5b','text.color':'#21333e'})

def plot_published(inputs: Path, figures: Path) -> None:
    figures.mkdir(parents=True,exist_ok=True)
    def save(fig,name):
        fig.savefig(figures/name,dpi=175,bbox_inches='tight',facecolor='white')
        plt.close(fig)

    # Article Figure 6: direct partnership-level assortativity estimates.
    a=pd.read_csv(inputs/'malagon_assortativity.csv')
    assert list(a.measure)==['Lifetime partner count','Partner acquisition rate','Concurrent partnerships']
    p=a.rho.to_numpy(); lo=a.ci_low.to_numpy(); hi=a.ci_high.to_numpy()
    y=np.arange(len(a))[::-1]
    fig,ax=plt.subplots(figsize=(9.7,4.3))
    ax.errorbar(p,y,xerr=[p-lo,hi-p],marker='o',ms=9,capsize=5,lw=0,elinewidth=2.2,color=NAVY)
    for rho,yy,c in zip(p,y,hi):
        ax.annotate(f'ρ = {rho:.2f}',(c,yy),xytext=(10,0),textcoords='offset points',va='center',fontsize=10)
    ax.set_yticks(y,a.measure);ax.set_xlim(0,.57);ax.set_ylim(-.6,2.7)
    ax.set_xlabel('Spearman correlation (ρ), 95% confidence interval')
    ax.set_title("How similar are dating partners' sexual histories?")
    ax.grid(axis='x',alpha=.16);fig.tight_layout()
    save(fig,'06_partner_assortativity.png')

    # Article Figure 7: RIVM series. The test counts before 2022 are approximate.
    annual=pd.read_csv(inputs/'rivm_chlamydia_series_2018_2022.csv')
    assert list(annual.Year)==[2018,2019,2020,2021,2022]
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(9.8,7.2),sharex=True,gridspec_kw={'height_ratios':[1.3,1]})
    x=np.arange(len(annual))
    ax1.plot(x,annual.Women_positivity_pct,marker='o',lw=2.3,ms=7,color=TEAL,label='Women')
    ax1.plot(x,annual.Heterosexual_men_positivity_pct,marker='s',lw=2.3,ms=6,color=NAVY,label='Heterosexual men')
    ax1.set_ylim(0,27);ax1.set_ylabel('Chlamydia positivity among tests (%)')
    ax1.set_title('Dutch sexual-health centres: positivity and testing volume, 2018–2022')
    ax1.legend(frameon=False,ncol=2,loc='upper left');ax1.grid(axis='y',alpha=.13)
    w=.36
    ax2.bar(x-w/2,annual.Women_tests/1000,w,color=TEAL,label='Women')
    ax2.bar(x+w/2,annual.Heterosexual_men_tests/1000,w,color=NAVY,label='Heterosexual men')
    ax2.set_xticks(x,annual.Year);ax2.set_ylim(0,92);ax2.set_ylabel('Chlamydia tests (thousands)')
    ax2.set_title('Number tested: 2018–2021 ≈ graph readings; 2022 exact',fontsize=10,pad=9)
    ax2.legend(frameon=False,loc='upper right',ncol=2,fontsize=9)
    ax2.grid(axis='y',alpha=.13);ax2.set_axisbelow(True)
    ax1.set_xticks(x);ax1.tick_params(labelbottom=False);fig.tight_layout(h_pad=3)
    save(fig,'07_netherlands_sti_positivity.png')

    # Article Figure 8: use official YouGov *table* wording, not conflicting prose.
    yo=pd.read_csv(inputs/'yougov_oral_sex_definitions.csv')
    fig,ax=plt.subplots(figsize=(9.6,4.6));x=np.arange(len(yo));w=.3
    for key,off,col,label in [('counts_as_sex_pct',-w/2,NAVY,'Counts as sex'),
                               ('does_not_count_pct',w/2,TEAL,'Does not count')]:
        bars=ax.bar(x+off,yo[key],w,color=col,label=label)
        for bar in bars:
            ax.annotate(f'{bar.get_height():.0f}%',(bar.get_x()+bar.get_width()/2,bar.get_height()),
                        xytext=(0,6),textcoords='offset points',ha='center',fontsize=10)
    ax.set_xticks(x,yo.group);ax.set_ylim(0,69);ax.set_ylabel('Survey response (%)')
    ax.set_title('Does oral stimulation of the penis alone count as “having sex”?')
    ax.legend(ncol=2,frameon=False,loc='upper center',bbox_to_anchor=(.5,1.02))
    ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True);fig.tight_layout()
    save(fig,'08_oral_sex_definitions.png')

    # Article Figure 9: attitudes and behavior deliberately in separate panels.
    chi=pd.read_csv(inputs/'chia_lee_peer_norms.csv')
    att=chi[chi.kind.eq('Attitude')];beh=chi[chi.kind.eq('Behavior')]
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12.2,4.8),gridspec_kw={'width_ratios':[1.7,1]})
    for ax,table,labels,title in [
       (ax1,att,['Comfortable with\nfirst-date sex','Comfortable with sex\nwhile casually dating'],'Attitudes: comfort with sex'),
       (ax2,beh,['Intercourse in\npast 6 months'],'Behavior: intercourse')]:
        x=np.arange(len(labels));w=.35
        for key,off,col,label in [('self_report_pct',-w/2,GRAY,'Respondents themselves'),
                                   ('perceived_peers_pct',w/2,TEAL,'Estimated for peers')]:
            bars=ax.bar(x+off,table[key],w,color=col,label=label)
            for bar in bars:
                ax.annotate(f'{bar.get_height():.0f}%',(bar.get_x()+bar.get_width()/2,bar.get_height()),
                            xytext=(0,5),textcoords='offset points',ha='center',fontsize=9)
        ax.set_xticks(x,labels);ax.set_ylim(0,62);ax.grid(axis='y',alpha=.13)
        ax.set_axisbelow(True);ax.set_title(title,fontsize=11);ax.tick_params(axis='x',labelsize=9)
    ax1.set_ylabel('Percentage (%)');h,l=ax1.get_legend_handles_labels()
    fig.legend(h,l,ncol=2,loc='upper center',bbox_to_anchor=(.5,1.01),frameon=False)
    fig.suptitle('Reported behaviors and attitudes versus perceived peer prevalence',fontsize=14,y=1.11)
    fig.tight_layout(w_pad=2)
    save(fig,'09_media_norms_singapore.png')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--inputs',type=Path,default=Path(__file__).resolve().parents[1]/'inputs')
    p.add_argument('--figures',type=Path,default=Path(__file__).resolve().parents[1]/'reproduced'/'figures')
    args=p.parse_args()
    plot_published(args.inputs,args.figures)
    print('Recreated published-summary figures 06–09 in',args.figures)
