import numpy as np,pandas as pd
from pathlib import Path
B=Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'));O=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'))
p=pd.read_csv(B/'table_04_out_of_city_predictions.csv',dtype={'identifier_2018':str})
rows=[]
for (city,model),g in p.groupby(['city','model'],sort=True):
 n=len(g);k=int(np.ceil(0.05*n));y=g.true_label.to_numpy(dtype=int);s=g.predicted_probability.to_numpy();ids=g.identifier_2018.to_numpy()
 cutoff=np.sort(s)[-k];high=np.flatnonzero(s>cutoff);ties=np.flatnonzero(s==cutoff);slots=k-len(high)
 stable=np.lexsort((ids,-s))[:k]
 npositives=int(y.sum());above_positive=int(y[high].sum());tie_positive=int(y[ties].sum());
 det_positive=int(y[stable].sum())
 min_possible=above_positive+max(0,slots-(len(ties)-tie_positive))
 max_possible=above_positive+min(slots,tie_positive)
 rng=np.random.default_rng(20261014)
 sampled=[above_positive+int(y[rng.choice(ties,size=slots,replace=False)].sum()) for _ in range(1000)] if len(ties)>1 and len(high)<k else [det_positive]
 row=dict(city=city,model=model,n=n,events=npositives,budget_n=k,cutoff_score=cutoff,tied_at_cutoff=len(ties),slots_among_ties=slots,positives_above=above_positive,positives_among_ties=tie_positive,deterministic_detected=det_positive,deterministic_recall=det_positive/npositives,minimum_recall=min_possible/npositives,maximum_recall=max_possible/npositives,random_tie_mean_recall=float(np.mean(sampled)/npositives),random_tie_p05_recall=float(np.quantile(sampled,.05)/npositives),random_tie_p95_recall=float(np.quantile(sampled,.95)/npositives))
 rows.append(row)
 print(row,flush=True)
pd.DataFrame(rows).to_csv(O/'r2_top5_tie_deterministic_and_random.csv',index=False)
