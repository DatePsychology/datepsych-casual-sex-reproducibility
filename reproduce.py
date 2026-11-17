#!/usr/bin/env python3
"""Reproduce DatePsych casual-sex critique (published summaries + optional GSS).

No private records, original study PDFs, or authors' proprietary survey data
are bundled. See README.md for exact scope and data acquisition instructions.

Examples:
  python reproduce.py
  python reproduce.py --gss ./2022_stata.zip
  python reproduce.py --gss ./GSS2022.dta --output ./my_results
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import csv

ROOT=Path(__file__).resolve().parent

def run(script,*args):
    cmd=[sys.executable,str(ROOT/'src'/script),*map(str,args)]
    print('Running:', ' '.join(cmd),flush=True)
    subprocess.run(cmd,check=True)

def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('--gss',type=Path,default=None,help='NORC 2022_stata.zip or extracted GSS2022.dta (not included)')
    p.add_argument('--output',type=Path,default=ROOT/'reproduced',help='Directory for newly created figures and aggregate tables')
    args=p.parse_args();dest=args.output.resolve()
    (dest/'figures').mkdir(parents=True,exist_ok=True)
    (dest/'tables').mkdir(parents=True,exist_ok=True)
    run('published_figures.py','--inputs',ROOT/'inputs','--figures',dest/'figures')
    run('published_arithmetic.py','--output',dest/'tables'/'published_arithmetic_checks.csv')
    if args.gss is None:
        print('\nReproduced Figures 6–9 from published summary data.')
        print('To independently recompute Figures 1–5 and all GSS tables, download the NORC 2022 survey and rerun with --gss PATH.')
        print('Checked-in aggregate GSS tables and the nine original figure PNGs remain in reference_results/ and figures/.')
        return
    inp=args.gss.expanduser().resolve()
    if not inp.is_file():
        p.error(f'GSS input file not found: {inp}')
    run('replicate_gss.py','--zip',inp,'--output',dest/'legacy_audit')
    for src in (dest/'legacy_audit'/'tables').glob('*.csv'):
        shutil.copy2(src,dest/'tables'/src.name)
    run('build_figures.py','--zip',inp,'--output',dest)
    run('additional_sensitivity.py','--zip',inp,'--output',dest/'tables')
    # Basic automated reproducibility assertions, not tests of the original studies.
    import pandas as pd
    df=pd.read_csv(dest/'tables'/'summary_weight_sensitivity.csv')
    base=df[df.version.eq('Historical baseline · WTSSPS')].set_index('sex')
    assert int(base.loc['Men','valid_n'])==189
    assert int(base.loc['Women','valid_n'])==230
    assert abs(float(base.loc['Men','two_plus_pct'])-22.7819)<0.03
    assert abs(float(base.loc['Women','two_plus_pct'])-21.0512)<0.03
    rel=pd.read_csv(dest/'tables'/'relatsex_age_sensitivity.csv')
    female=rel[(rel.sex=='Women')&(rel.age_from==30)&(rel.age_to==39)].iloc[0]
    assert abs(female.weighted_pct-10.26)<0.08
    con=pd.read_csv(dest/'tables'/'concentration_sensitivity.csv')
    m=con[(con.sex=='Men')&(con.method=='historical WTSSPS')].iloc[0]
    assert abs(m.concentration_lower_pct-45.34)<0.10
    files=list((dest/'figures').glob('*.png'))
    assert len(files)==9,('Expected 9 figure PNGs',sorted(x.name for x in files))
    print('\nPASS: GSS baseline counts, partner shares, RELATSEX benchmark, concentration estimate, 9 figures.')
    print('Aggregate output:',dest/'tables')
    print('Images:',dest/'figures')
    print('Do not interpret sensitivity deletions as corrected population estimates.')

if __name__=='__main__':main()
