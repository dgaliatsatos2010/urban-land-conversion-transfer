import sys, numpy as np, pandas as pd,shapely
from tempfile import TemporaryDirectory
from pathlib import Path
sys.path.insert(0,str(Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'))))
from urban_crosscity_pilot_v08 import read_fgb_nested, CITY_SOURCES, SOURCE_PREFIXES, BUILT_TARGET
OUT=[];SUB=[];base=Path(os.environ.get('URBAN_SOURCE_DIR','/mnt/data'))
for city,sp in CITY_SOURCES.items():
 with TemporaryDirectory() as td:
  a=read_fgb_nested(base/sp['annual'],Path(td));c=read_fgb_nested(base/sp['change'],Path(td))
 a['code_2018']=a.code_2018.astype(str);c['code_2018']=c.code_2018.astype(str);c['code_2021']=c.code_2021.astype(str)
 cand=a[a.code_2018.str.startswith(SOURCE_PREFIXES)].reset_index(drop=True)
 change=c[c.code_2018.str.startswith(SOURCE_PREFIXES)&c.code_2021.isin(BUILT_TARGET)].reset_index(drop=True)
 cidx,pidx=shapely.STRtree(cand.geometry.to_numpy()).query(change.geometry.to_numpy(),predicate='intersects')
 inter=shapely.intersection(change.geometry.to_numpy()[cidx],cand.geometry.to_numpy()[pidx]);area=shapely.area(inter)
 matched=(change.code_2018.to_numpy()[cidx]==cand.code_2018.to_numpy()[pidx]);ac=shapely.area(cand.geometry.to_numpy())
 res=[]
 for thresh in (1.0,99.999999999,100.0):
  valid=matched &(area>thresh if thresh<=1 else area>=thresh)
  overlap=np.bincount(pidx[valid],weights=area[valid],minlength=len(cand))
  p1=(overlap>=100)&(overlap/ac>=0.01);p5=(overlap>=100)&(overlap/ac>=0.05)
  res.append((p1,p5,valid,overlap))
 dif=(res[0][0]!=res[1][0]);dif5=(res[0][1]!=res[1][1])
 OUT.append(dict(city=city,eligible=len(cand),change=len(change),intersections_total=int(len(area)),intersections_matched=int(matched.sum()),matched_over1=int(res[0][2].sum()),matched_between1_100=int((matched&(area>1)&(area<100)).sum()),labels_1m2=int(res[0][0].sum()),labels_100m2=int(res[1][0].sum()),different_1pct=int(dif.sum()),labels_5pct_1m2=int(res[0][1].sum()),labels_5pct_100m2=int(res[1][1].sum()),different_5pct=int(dif5.sum())))
 for i in np.where(dif |dif5)[0]:SUB.append(dict(city=city,identifier=str(cand.identifier[i]),old_label=int(res[0][0][i]),new_label=int(res[1][0][i]),old_5pct=int(res[0][1][i]),new_5pct=int(res[1][1][i])))
 print(OUT[-1],flush=True)
pd.DataFrame(OUT).to_csv(Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'))/'r2_label_filter_comparison.csv',index=False);pd.DataFrame(SUB).to_csv(Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'))/'r2_label_changes_if_any.csv',index=False)
