from pathlib import Path
import os,numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score
B=Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'));O=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'))
f=pd.read_csv(B/'table_01_polygon_features_and_labels.csv',dtype={'identifier_2018':str});p=pd.read_csv(B/'table_04_out_of_city_predictions.csv',dtype={'identifier_2018':str});rng=np.random.default_rng(20261014)
rows=[]
for city in ['Kavala','Graz','Tirana']:
 d=f[f.city==city].copy()
 q=p[(p.city==city)&(p.model=='XGBoost')][['identifier_2018','predicted_probability']]
 d=d.merge(q,on='identifier_2018',validate='one_to_one')
 label=d.transition.to_numpy();score=d.predicted_probability.to_numpy()
 coords=d.block_5km.str.split('_',expand=True).astype(int)
 for bs in (5,10,20):
  key=(coords[0]//(bs//5)).astype(str)+'_'+(coords[1]//(bs//5)).astype(str)
  g=pd.DataFrame({'block':key,'pos':label});groups=list(g.groupby('block').indices.values())
  valid=[];rng=np.random.default_rng(20261014)
  for j in range(1000):
   ix=np.concatenate([groups[k] for k in rng.integers(0,len(groups),len(groups))]);yy=label[ix]
   if np.unique(yy).size<2:continue
   valid.append((roc_auc_score(yy,score[ix]),average_precision_score(yy,score[ix])))
  val=np.asarray(valid)
  row=dict(city=city,block_km=bs,n_groups=len(groups),positive_groups=key[label==1].nunique(),valid_reps=len(val),total_reps=1000,point_AUROC=roc_auc_score(label,score),point_AP=average_precision_score(label,score),AUROC_low=np.quantile(val[:,0],.025),AUROC_high=np.quantile(val[:,0],.975),AP_low=np.quantile(val[:,1],.025),AP_high=np.quantile(val[:,1],.975)) if len(val)>0 else None
  print(row,flush=True);rows.append(row)
pd.DataFrame(rows).to_csv(O/'r2_blocksize_sensitivity.csv',index=False)
