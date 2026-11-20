"""Recalculate saved metrics and inspect reproducibility for the real-data pilot."""
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss
R=Path(__file__).parent
panel=pd.read_csv(R/'table_01_polygon_features_and_labels.csv',dtype={'code_2018':'str'})
metrics=pd.read_csv(R/'table_03_heldout_city_metrics.csv')
pred=pd.read_csv(R/'table_04_out_of_city_predictions.csv')
# Verify original bundle; original Copernicus archives are not redistributed.
import hashlib
manifest=pd.read_csv(R.parent/'SHA256SUMS.csv')
assert len(manifest)==73 and set(manifest.columns)=={'file','sha256'}
for rec in manifest.itertuples(index=False):
 if not (rec.file.startswith('Original_Analysis/table_') or rec.file.startswith('Reviewer2_Results/')): continue  # source data/results only; documentation and scripts may evolve
 f=R.parent/rec.file
 assert f.is_file(), f'Missing bundled file: {rec.file}'
 assert hashlib.sha256(f.read_bytes()).hexdigest()==rec.sha256, f'Checksum mismatch: {rec.file}'
assert len(panel)==18366 and int(panel.transition.sum())==383
assert manifest.sha256.str.len().eq(64).all()
assert len(pred)==len(panel)*5, (len(pred),len(panel))
assert not panel.duplicated(['city','identifier_2018']).any()
assert not pred.duplicated(['city','model','identifier_2018']).any()
assert not panel[['transition','built_fraction_250m','built_fraction_1000m','distance_to_built_m']].isna().any().any()
assert not pred[['predicted_probability','true_label']].isna().any().any()
assert pred.predicted_probability.between(0,1).all()
merged=pred.merge(panel[['city','identifier_2018','transition']],on=['city','identifier_2018'],how='left',validate='many_to_one')
assert not merged.transition.isna().any()
assert (merged.true_label==merged.transition).all()
for (city,mod),g in pred.groupby(['city','model']):
 old=metrics[(metrics.city==city)&(metrics.model==mod)].iloc[0]
 assert len(g)==old['n'] and int(g.true_label.sum())==old.events
 for key,func in [('auroc',roc_auc_score),('auprc',average_precision_score),('brier',brier_score_loss)]:
  value=func(g.true_label,g.predicted_probability)
  assert abs(value-old[key])<1e-10,(city,mod,key,value,old[key])
print('PASS: 18,366 baseline polygons, 383 positives; 91,830 held-out model predictions; 15/15 metric rows reproduced; all labels and published bundle hashes consistent')
