#!/usr/bin/env python3
"""Independent checks, alternative-label sensitivity, feature ablation, and held-out permutation.
Consumes derived validated polygon panel. No training on held-out city and no future predictors.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from urban_crosscity_pilot_v08 import make_model, FEATURES, SEED

_parser=argparse.ArgumentParser()
_parser.add_argument('--output',type=Path,default=Path(__file__).parent)
ROOT=_parser.parse_args().output
panel=pd.read_csv(ROOT/'table_01_polygon_features_and_labels.csv',dtype={'code_2018':'str','identifier_2018':'str'})
assert len(panel)==18366 and set(panel.city)=={'Kavala','Graz','Tirana'}
assert (panel.transition_5pct<=panel.transition).all()
assert not panel.duplicated(['city','identifier_2018']).any()
assert not panel[FEATURES].isna().any().any()
assert (panel.overlap_m2>=0).all()
assert (panel.overlap_m2<=panel.polygon_m2+1e-3).all()
assert ((panel.transition==1)==((panel.overlap_m2>=100)&(panel.overlap_m2>=panel.polygon_m2*.01))).all()
assert ((panel.transition_5pct==1)==((panel.overlap_m2>=100)&(panel.overlap_m2>=panel.polygon_m2*.05))).all()
assert all(np.isfinite(panel[x]).all() for x in ['built_fraction_250m','built_fraction_1000m','distance_to_built_m'])
assert all(panel[x].between(0,1).all() for x in ['built_fraction_250m','built_fraction_1000m'])

# Model-only, class-only baseline. Kept same core hyperparameter settings as full models.
def class_only_model(name):
    t=ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore'),['code_2018'])])
    if name=='LogisticRegression':model=LogisticRegression(max_iter=1500,C=1,random_state=SEED)
    elif name=='RandomForest':model=RandomForestClassifier(n_estimators=120,max_depth=10,min_samples_leaf=10,n_jobs=2,random_state=SEED)
    elif name=='XGBoost':model=XGBClassifier(n_estimators=140,max_depth=3,learning_rate=.05,subsample=.9,colsample_bytree=.9,objective='binary:logistic',eval_metric='logloss',n_jobs=2,random_state=SEED)
    else:raise ValueError(name)
    return Pipeline([('prep',t),('clf',model)])

records=[]; permutation=[]
for held in ['Kavala','Graz','Tirana']:
  train=panel.loc[panel.city!=held];test=panel.loc[panel.city==held]
  for label in ['transition','transition_5pct']:
    y_train=train[label].to_numpy();y_test=test[label].to_numpy()
    for model_name in ['LogisticRegression','RandomForest','XGBoost','TAN_BN']:
      mdl=make_model(model_name)
      mdl.fit(train[FEATURES],y_train)
      p=mdl.predict_proba(test[FEATURES])[:,1]
      records.append(dict(heldout=held,label=label,model=model_name,feature_set='full_2018',train_events=int(y_train.sum()),test_events=int(y_test.sum()),test_n=len(y_test),
        auroc=float(roc_auc_score(y_test,p)),auprc=float(average_precision_score(y_test,p)),brier=float(brier_score_loss(y_test,p))))
      if label=='transition' and model_name=='XGBoost':
        base=float(roc_auc_score(y_test,p));rng=np.random.default_rng(SEED)
        for feature in FEATURES:
          shuffled=[]
          for rep in range(5):
            X=test[FEATURES].copy()
            X[feature]=rng.permutation(X[feature].to_numpy())
            r=mdl.predict_proba(X)[:,1]
            shuffled.append(base-float(roc_auc_score(y_test,r)))
          permutation.append(dict(city=held,feature=feature,n_repeats=5,mean_auroc_drop=float(np.mean(shuffled)),min_auroc_drop=float(np.min(shuffled)),max_auroc_drop=float(np.max(shuffled))))
    if label=='transition':
      for model_name in ['LogisticRegression','RandomForest','XGBoost']:
        mdl=class_only_model(model_name)
        mdl.fit(train[['code_2018']],y_train)
        p=mdl.predict_proba(test[['code_2018']])[:,1]
        records.append(dict(heldout=held,label=label,model=model_name,feature_set='class_only_2018',train_events=int(y_train.sum()),test_events=int(y_test.sum()),test_n=len(y_test),
          auroc=float(roc_auc_score(y_test,p)),auprc=float(average_precision_score(y_test,p)),brier=float(brier_score_loss(y_test,p))))
  print('Finished',held,flush=True)
comparison=pd.DataFrame(records)
comparison.to_csv(ROOT/'table_07_sensitivity_and_ablation.csv',index=False)
pd.DataFrame(permutation).to_csv(ROOT/'table_08_xgboost_heldout_permutation.csv',index=False)
print('\nSensitivity AUROC and AP (full):')
print(comparison.loc[comparison.feature_set=='full_2018'].pivot_table(index=['heldout','model'],columns='label',values='auprc').round(4).to_string())
print('\nAblation AP:')
print(comparison.loc[comparison.label=='transition'].pivot_table(index=['heldout','model'],columns='feature_set',values='auprc').round(4).to_string())
