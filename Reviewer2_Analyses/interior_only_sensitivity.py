"""Boundary-aware diagnostic: train and test only source polygons whose 1km neighborhood contains >=95% mapped pixels. Geometry from 2018 only; no heldout tuning."""
from pathlib import Path
import os
import sys
import numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss
SRC=Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'));OUT=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'))
sys.path.insert(0,str(SRC))
from urban_crosscity_pilot_v08 import make_model,FEATURES
D=pd.read_csv(SRC/'table_01_polygon_features_and_labels.csv',dtype={'identifier_2018':str,'code_2018':str})
A=pd.concat([pd.read_csv(OUT/f'area_features_{c}_25m.csv',dtype={'identifier_2018':str}) for c in ('Kavala','Graz','Tirana')],ignore_index=True)
D=D.merge(A[['city','identifier_2018','circle_mapped_fraction_1000m','near_boundary_1000m']],on=['city','identifier_2018'],validate='1:1')
counts=[];metrics=[]
for city,d in D.groupby('city'):
 inner=d[d.circle_mapped_fraction_1000m>=.95]
 counts.append({'city':city,'n_total':len(d),'positives_total':int(d.transition.sum()),'n_interior':len(inner),'positives_interior':int(inner.transition.sum()),'n_excluded_boundary':len(d)-len(inner),'positives_excluded_boundary':int(d.transition.sum()-inner.transition.sum()),'interior_area_ha':float(inner.polygon_m2.sum()/10000)})
for city in ('Kavala','Graz','Tirana'):
 train=D[(D.city!=city)&(D.circle_mapped_fraction_1000m>=.95)]; test=D[(D.city==city)&(D.circle_mapped_fraction_1000m>=.95)]
 for model in ('LogisticRegression','RandomForest','XGBoost','TAN_BN'):
  m=make_model(model);m.fit(train[FEATURES],train.transition);p=m.predict_proba(test[FEATURES])[:,1];y=test.transition.to_numpy()
  met={'city':city,'model':model,'n_test':len(test),'events_test':int(y.sum()),'AUROC':float(roc_auc_score(y,p)) if np.unique(y).size>1 else None,'AP':float(average_precision_score(y,p)) if y.sum()>0 else None,'Brier':float(brier_score_loss(y,p))};print(met,flush=True);metrics.append(met)
pd.DataFrame(counts).to_csv(OUT/'r2_interior_only_cohort.csv',index=False)
pd.DataFrame(metrics).to_csv(OUT/'r2_interior_only_refit_metrics.csv',index=False)
print('COUNT',pd.DataFrame(counts).to_string(index=False),flush=True)
