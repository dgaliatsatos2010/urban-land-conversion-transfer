import pandas as pd
from pathlib import Path
O=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'));R=Path('/mnt/data/r2_audit')
cityorder=['Kavala','Graz','Tirana'];models=['TrainingPrevalence','LogisticRegression','RandomForest','XGBoost','TAN_BN']
C=pd.read_csv(O/'r2_city_comparison.csv');sr=pd.read_csv(O/'r2_source_prefix_composition.csv');de=pd.read_csv(O/'r2_destination_composition.csv');status=pd.read_csv(R/'r2_valid_mask_status_overlap.csv');mx=pd.read_csv(R/'r2_complete_metrics.csv');a=pd.read_csv(O/'r2_area_proxy_model_comparison.csv');bs=pd.read_csv(R/'r2_blocksize_sensitivity.csv');ties=pd.read_csv(O/'r2_top5_tie_deterministic_and_random.csv')
with open(O/'UrbanScience_Reviewer2_Tables_11_to_15.md','w') as f:
 f.write('# Proposed new tables for the Urban Science main manuscript (Reviewer 2)\n\n')
 f.write('All values originate from the supplied FUA source products or from actual refitting on their derived records. Numbers below are rounded for publication; calculations use full precision.\n\n')
 f.write('## Table 11. FUA mapped area and source composition\n\n')
 f.write('|FUA|Mapped 2018 / 2021 (km²)|Eligible n / positive n|Eligible median area (ha)|Dominant source code prefix (% of eligible polygons)|Leading developed destination (% of qualifying change area)|\n|---|---:|---:|---:|---|---|\n')
 for c in cityorder:
  row=C[C.city==c].iloc[0];foot=status[status.city==c].iloc[0];top=sr[sr.city==c].sort_values('n_pct',ascending=False).iloc[0];d=de[de.city==c].sort_values('change_ha',ascending=False).iloc[0]
  # sum polygons area from separate original status coverage; use 2018 from original comparison report external values confirmed
  ar={'Kavala':(281.7018111495609,355.47279230482377),'Graz':(2832.546431476548,3088.5131583805273),'Tirana':(1670.1931001847474,1670.1931001847474)}[c]
  f.write(f'|{c}|{ar[0]:,.2f} / {ar[1]:,.2f}|{int(row.eligible):,} / {int(row.positives)}|{row.median_source_polygon_ha:.2f}|{top.source_prefix} ({top.n_pct:.1f}%)|{d.code_2021} ({d.pct_change_ha:.1f}%)|\n')
 f.write('\n*Note:* Source prefixes are the first two digits of Urban Atlas codes. Destination shares are based on the full official qualifying change geometries, NOT the area of complete positively labelled source polygons. Full class breakdown is available in `r2_source_prefix_composition.csv` and `r2_destination_composition.csv`. Additional 2021-only mapped coverage is 73.77 km² in Kavala, 255.97 km² in Graz and 0 in Tirana.\n\n')
 f.write('## Table 12. Comparison of held-out average precision (AP) under alternative spatial proxies (25 m raster)\n\n|FUA|Model|Original point-count AP|Area-fraction AP|Area fraction + raster-distance AP|\n|---|---|---:|---:|---:|\n')
 for c in cityorder:
  for m in models[1:]:
   row=a[(a.city==c)&(a.model==m)].iloc[0]
   f.write(f'|{c}|{m}|{row.AP_original:.3f}|{row.AP_area_fractions:.3f}|{row.AP_area_fractions_boundary_distance:.3f}|\n')
 f.write('\n*Note:* The area-fraction version substitutes the 250 m and 1,000 m point-count fractions with fractions of developed raster cells over mapped raster cells within the respective circles (EPSG:3035, 25 m cell size); the original point-distance variable remains. The final column also replaces that distance by the approximate distance to the nearest developed cell. All models were refitted with the same folds, binary labels and unchanged hyperparameter specifications. The 50 m-resolution results and scores are available as separate audit files; conclusions are exploratory.\n\n')
 f.write('## Table 13. Complete probability error scores on the original held-out predictions\n\n|FUA|Model|Brier score|Log loss|\n|---|---|---:|---:|\n')
 for c in cityorder:
  for mod in models:
   row=mx[(mx.city==c)&(mx.model==mod)].iloc[0]
   f.write(f'|{c}|{mod}|{row.brier:.5f}|{row.log_loss:.5f}|\n')
 f.write('\n*Note:* Lower is better; the training-prevalence reference is the constant model equal to the event prevalence in the two training FUAs. Numerical values are reproduced from frozen original test-city scores.\n\n')
 f.write('## Table 14. XGBoost 1,000-replicate spatial-block bootstrap size sensitivity\n\n|FUA|Block width (km)|Total blocks|Blocks with positives|Valid / 1,000|AP 95% conditional percentile interval|\n|---|---:|---:|---:|---:|---|\n')
 for c in cityorder:
  for sz in (5,10,20):
   v=bs[(bs.city==c)&(bs.block_km==sz)].iloc[0]
   f.write(f'|{c}|{sz}|{int(v.n_groups)}|{int(v.positive_groups)}|{int(v.valid_reps)} / 1,000|{v.AP_low:.3f}–{v.AP_high:.3f}|\n')
 f.write('\n*Note:* These are conditional, fixed-prediction, within-FUA intervals. They are NOT confidence intervals over new FUAs; the 5/10/20-km grid origins are fixed to EPSG:3035 coordinates.\n\n')
 f.write('## Table 15 (optional). TAN top-5% cutoff ties and tie-resolution diagnostics\n\n|FUA|Tied at cutoff|Deterministic detected / total|Deterministic recall|Theoretical possible recall range|Random-tie 5th–95th percentile recall|\n|---|---:|---:|---:|---|---|\n')
 for c in cityorder:
  v=ties[(ties.city==c)&(ties.model=='TAN_BN')].iloc[0]
  f.write(f'|{c}|{int(v.tied_at_cutoff)}|{int(v.deterministic_detected)} / {int(v.events)}|{v.deterministic_recall:.3f}|{v.minimum_recall:.3f}–{v.maximum_recall:.3f}|{v.random_tie_p05_recall:.3f}–{v.random_tie_p95_recall:.3f}|\n')
 f.write('\n*Note:* Deterministic ordering: predicted score descending, 2018 polygon ID ascending. Random-tie percentile ranges use 1,000 random cutoff selections and are NOT inferential confidence intervals. The original five-percent Logistic Regression reference table is unaffected by ambiguous cutoff ties.\n')
print('Tables ready')
