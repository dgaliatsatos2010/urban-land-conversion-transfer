#!/usr/bin/env python3
"""Frozen 4-model leave-one-city-out evaluation with area-based spatial-proxy alternatives.
Reproduces original model before any alternative analysis; never accesses heldout labels for fitting.
"""
import sys, argparse, time, json
from pathlib import Path
import os
import numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss
ROOT=Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08')); O=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'))
sys.path.insert(0,str(ROOT))
from urban_crosscity_pilot_v08 import make_model, FEATURES
models=('LogisticRegression','RandomForest','XGBoost','TAN_BN')
def main(city,cell=25):
 d=pd.read_csv(ROOT/'table_01_polygon_features_and_labels.csv',dtype={'identifier_2018':str,'code_2018':str});orig=d.copy()
 extra=pd.concat([pd.read_csv(O/f'area_features_{city}_{cell}m.csv',dtype={'identifier_2018':str}) for city in ['Kavala','Graz','Tirana']],ignore_index=True)
 d=d.merge(extra.drop(columns='cell_m'),on=['city','identifier_2018'],how='left',validate='1:1')
 assert len(d)==18366 and not d[['area_built_fraction_250m','area_built_fraction_1000m','distance_to_built_area_approx_m']].isna().any().any()
 train=d[d.city!=city].copy();test=d[d.city==city].copy();ytr=train.transition.to_numpy();yte=test.transition.to_numpy()
 truth=pd.read_csv(ROOT/'table_04_out_of_city_predictions.csv',dtype={'identifier_2018':str});
 records=[]; predictions=[]
 for repr in ('original','area_fractions','area_fractions_boundary_distance'):
  a=train.copy();b=test.copy()
  if repr!='original':
   for r in ('250m','1000m'):
    a['built_fraction_'+r]=a['area_built_fraction_'+r];b['built_fraction_'+r]=b['area_built_fraction_'+r]
  if repr=='area_fractions_boundary_distance':
    a['distance_to_built_m']=a['distance_to_built_area_approx_m'];b['distance_to_built_m']=b['distance_to_built_area_approx_m']
  for model in models:
   t=time.time();m=make_model(model)
   m.fit(a[FEATURES],ytr)
   p=m.predict_proba(b[FEATURES])[:,1]
   rec=dict(city=city,representation=repr,model=model,n=len(b),positives=int(yte.sum()),AUROC=float(roc_auc_score(yte,p)),AP=float(average_precision_score(yte,p)),Brier=float(brier_score_loss(yte,p)),LogLoss=float(log_loss(yte,p,labels=[0,1])),elapsed_s=round(time.time()-t,2))
   if repr=='original':
    s=truth[(truth.city==city)&(truth.model==model)].set_index('identifier_2018').reindex(b.identifier_2018).predicted_probability.to_numpy()
    rec['max_abs_pred_diff_original']=float(np.abs(s-p).max());rec['mean_abs_pred_diff_original']=float(np.abs(s-p).mean())
   records.append(rec)
   predictions.append(pd.DataFrame({'city':city,'representation':repr,'model':model,'identifier_2018':b.identifier_2018.to_numpy(),'true_label':yte,'score':p}))
   print(rec,flush=True)
 pd.DataFrame(records).to_csv(O/f'area_model_metrics_{city}_{cell}m.csv',index=False)
 pd.concat(predictions,ignore_index=True).to_csv(O/f'area_model_predictions_{city}_{cell}m.csv',index=False)
 print('complete',city,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--hold',required=True);p.add_argument('--cell',type=int,default=25);args=p.parse_args();main(args.hold,args.cell)
