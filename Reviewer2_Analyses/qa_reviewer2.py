from pathlib import Path
import os
import pandas as pd,numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss
base=Path(os.environ.get('URBAN_VERIFICATION_DIR','/mnt/data/r2_audit'));o=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'));s=Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'))
f=pd.read_csv(s/'table_01_polygon_features_and_labels.csv',dtype={'identifier_2018':str});p=pd.read_csv(s/'table_04_out_of_city_predictions.csv',dtype={'identifier_2018':str});m=pd.read_csv(base/'r2_complete_metrics.csv');print('records',len(f),'positives',f.transition.sum(),'predictions',len(p));assert(len(f),int(f.transition.sum()),len(p))==(18366,383,91830)
assert (p.predicted_probability.between(0,1)).all() and p.true_label.notna().all()
for (city,mod),d in p.groupby(['city','model']):
 y=d.true_label;pp=d.predicted_probability
 row=m[(m.city==city)&(m.model==mod)].iloc[0]
 for key,calc in [('auroc',roc_auc_score(y,pp)),('auprc',average_precision_score(y,pp)),('brier',brier_score_loss(y,pp)),('log_loss',log_loss(y,np.clip(pp,1e-8,1-1e-8),labels=[0,1]))]:
  assert abs(calc-row[key])<1e-11,(city,mod,key,calc,row[key])
lab=pd.read_csv(base/'r2_label_filter_comparison.csv');assert(lab.different_1pct.sum()==0 and lab.different_5pct.sum()==0)
mask=pd.read_csv(base/'r2_valid_mask_status_overlap.csv');assert (mask.outside_gt1sqm==0).all()
for c in ('Kavala','Graz','Tirana'):
 x=pd.read_csv(o/f'area_model_metrics_{c}_25m.csv');assert set(x.representation)=={'original','area_fractions','area_fractions_boundary_distance'}
 assert x[x.representation=='original'].max_abs_pred_diff_original.max()<1e-10
feat=pd.concat([pd.read_csv(o/f'area_features_{c}_25m.csv') for c in ('Kavala','Graz','Tirana')]);assert len(feat)==len(f)
print('ALL AUTOMATED REPLAY CHECKS PASSED')
