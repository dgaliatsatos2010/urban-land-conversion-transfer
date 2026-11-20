from pathlib import Path
import os,numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score
P=Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08')); O=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'));seed=20261014
feat=pd.read_csv(P/'table_01_polygon_features_and_labels.csv',dtype={'code_2018':str,'identifier_2018':str}); pred=pd.read_csv(P/'table_04_out_of_city_predictions.csv',dtype={'identifier_2018':str});metric=pd.read_csv(P/'table_03_heldout_city_metrics.csv')
metric[['city','model','n','events','auroc','auprc','brier','log_loss']].to_csv(O/'r2_complete_metrics.csv',index=False)
feats=['built_fraction_250m','built_fraction_1000m','distance_to_built_m','polygon_m2','overlap_m2']
rows=[];summ=[];blocks=[];ties=[];pcounts=[]
for city,d in feat.groupby('city'):
  p=d.transition.to_numpy();train=feat[feat.city!=city]
  train_code=set(train.code_2018);test_code=set(d.code_2018)
  unfamiliar=test_code-train_code
  for cls,sub in d.groupby('code_2018'):
    rows.append(dict(city=city,class_code=cls,n=len(sub),area_ha=sub.polygon_m2.sum()/1e4,positives=int(sub.transition.sum())))
  for nm in feats:
    x=d[nm].dropna().to_numpy()
    summ.append(dict(city=city,variable=nm,n=len(x),missing=int(d[nm].isna().sum()),min=float(x.min()),median=float(np.median(x)),q25=float(np.quantile(x,.25)),q75=float(np.quantile(x,.75)),q95=float(np.quantile(x,.95)),max=float(x.max())))
  pcounts.append(dict(city=city,unseen_classes_n=len(unfamiliar),unseen_classes=';'.join(sorted(unfamiliar)),unseen_test_polygons=int(d.code_2018.isin(unfamiliar).sum()),unseen_test_positives=int(d.loc[d.code_2018.isin(unfamiliar),'transition'].sum())))
  xyz=d.block_5km.str.split('_',expand=True).astype(int)
  for size,mult in [(5,1),(10,2),(20,4)]:
    grp=(xyz[0]//mult).astype(str)+'_'+(xyz[1]//mult).astype(str)
    nblock=grp.nunique();posblocks=grp[p>0].nunique();
    blocks.append(dict(city=city,block_km=size,total_blocks=int(nblock),positive_blocks=int(posblocks),min_positives_per_positive_block=int(pd.Series(p).groupby(grp.reset_index(drop=True)).sum().loc[lambda x:x>0].min()),max_positives_per_positive_block=int(pd.Series(p).groupby(grp.reset_index(drop=True)).sum().max())))
  for model,g in pred[pred.city==city].groupby('model'):
    g=g.copy();g['rank']=g.predicted_probability.rank(ascending=False,method='min')
    n=int(np.ceil(.05*len(g)));sort=np.sort(g.predicted_probability.to_numpy())[::-1];cut=sort[n-1];ties_at=int((g.predicted_probability==cut).sum());above=int((g.predicted_probability>cut).sum())
    ties.append(dict(city=city,model=model,top5_n=n,cutoff_score=cut,tied_at_cutoff=ties_at,strictly_above_cutoff=above,boundary_tie_crossing=bool(above<n and above+ties_at>n),number_unique_score=int(g.predicted_probability.nunique())))
  print('Done quick',city,flush=True)
for data,name in [(rows,'r2_city_class_composition.csv'),(summ,'r2_feature_distribution.csv'),(blocks,'r2_positive_spatial_blocks.csv'),(ties,'r2_ties_in_review_budget.csv'),(pcounts,'r2_unseen_source_classes.csv')]:pd.DataFrame(data).to_csv(O/name,index=False)
print('All quick checks done',flush=True)
