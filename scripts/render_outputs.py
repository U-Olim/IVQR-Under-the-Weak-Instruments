#!/usr/bin/env python3
"""New descriptive views of archived results; no estimator, simulator, or cutoff recalibration."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile
from verify_evidence import ROOT, ESTIMATORS, KAPPAS, TAUS, records, require, cell, number, verify


def generate(root, output):
    require(not output.exists(), "Refusing to overwrite a reporting directory")
    require(not output.resolve().is_relative_to(root.resolve()), "Write reporting outputs outside the frozen repository")
    output.mkdir(parents=True)
    saved, power = {}, {}
    for n in (500, 1000):
        for r in records(root, f"results/main/n{n}/summary.csv"): saved[cell(r)] = r
        for r in records(root, f"results/main/n{n}/power_summary.csv"):
            power[cell(r) + (number(r['Delta']),)] = number(r['power'])
    main_columns = ['n','tau','kappa','estimator','Bias','MAE','RMSE','Coverage','median_grid_accepted_set_measure']
    with (output/'main_performance.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=main_columns); w.writeheader()
        for t in (.1,.5,.9):
            for k in KAPPAS:
                for e in ESTIMATORS:
                    r = saved[(1000,t,k,e)]; w.writerow({c:r[c] for c in main_columns})
    calibrated = list(records(root,'data/kappa_strength_summary.csv'))
    with (output/'strength_calibration.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=calibrated[0]); w.writeheader(); w.writerows(calibrated)
    # Explicitly new plotting environment, separate from historical R/solver dependencies.
    with tempfile.TemporaryDirectory(prefix='ivqr-plot-cache-') as cache:
        os.environ['MPLCONFIGDIR'] = cache
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        with matplotlib.rc_context({'font.family':'DejaVu Sans', 'svg.hashsalt':'ivqr-archived-views-v1'}):
            def save(fig, name):
                fig.savefig(output/name, format='svg', metadata={'Date':None,'Creator':'IVQR archived-output reporting'})
                plt.close(fig)
            for field, title, name, vmax in (
                ('Coverage','Direct truth acceptance (nominal reference rule)','truth_acceptance.svg',1),
                ('all_41_acceptance_rate','All 41 grid points accepted','full_grid_acceptance.svg',1),
                ('median_grid_accepted_set_measure','Median grid quadrature within [-1,3]','accepted_measure.svg',4),
                ('RMSE','Grid point-estimator RMSE','rmse.svg',None)):
                fig, axes = plt.subplots(2,3,figsize=(12,6.4),layout='constrained')
                maximum = vmax if vmax is not None else max(number(r[field]) for r in saved.values())
                for i,n in enumerate((500,1000)):
                    for j,e in enumerate(ESTIMATORS):
                        a=axes[i,j]; matrix=[[number(saved[(n,t,k,e)][field]) for k in KAPPAS] for t in TAUS]
                        im=a.imshow(matrix, vmin=0, vmax=maximum, aspect='auto', cmap='viridis')
                        a.set_xticks(range(4),[str(k) for k in KAPPAS]); a.set_yticks(range(5),[str(t) for t in TAUS])
                        a.set_xlabel('Designed relevance kappa'); a.set_ylabel('Quantile tau'); a.set_title(f'{e}, n={n}')
                fig.colorbar(im,ax=axes.ravel().tolist(),shrink=.8); fig.suptitle(title); save(fig,name)
            fig, axes=plt.subplots(2,4,figsize=(14,6.4),layout='constrained')
            deltas=(-1.,-.5,-.25,0.,.25,.5,1.)
            for i,n in enumerate((500,1000)):
                for j,k in enumerate(KAPPAS):
                    a=axes[i,j]
                    for e in ESTIMATORS:
                        y=[number(saved[(n,.5,k,e)]['Size']) if d==0 else power[(n,.5,k,e,d)] for d in deltas]
                        a.plot(deltas,y,marker='o',label=e)
                    a.set_ylim(0,1); a.set_title(f'n={n}, kappa={k}'); a.set_xlabel('Candidate minus true effect')
                    a.set_ylabel('Raw rejection frequency'); a.grid(alpha=.25)
            axes[0,0].legend(fontsize=7); fig.suptitle('Median quantile: truth and false-candidate rejection, not size-adjusted power')
            save(fig,'median_rejection.svg')
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--compare-bundled',action='store_true')
    args=p.parse_args()
    validation=verify(ROOT)
    require(validation['archived_verification']=='PASS','Sealed archived-evidence verification did not pass')
    hashes=generate(ROOT,args.output)
    if args.compare_bundled:
        for name,digest in hashes.items():
            bundled=ROOT/('figures' if name.endswith('.svg') else 'results/views')/name
            require(bundled.is_file() and hashlib.sha256(bundled.read_bytes()).hexdigest()==digest,
                    f'Rendered view differs: {name}; verify the documented plotting environment')
    print(json.dumps({'scope':'Reconstructed views, not pixel-identical original manuscript graphics',
                      'files':hashes,'bundled_match':args.compare_bundled},indent=2))


if __name__=='__main__': main()
