from pathlib import Path
from tempfile import TemporaryDirectory
import os
import sys,numpy as np,pandas as pd,shapely
sys.path.insert(0,os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'))
from urban_crosscity_pilot_v08 import read_fgb_nested,CITY_SOURCES,BUILT_TARGET,SOURCE_PREFIXES
P=Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'));OUT=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup')); D=pd.read_csv(P/'table_01_polygon_features_and_labels.csv',dtype={'code_2018':str})
summary=[];category=[];dest=[]
for city,d in D.groupby('city'):
 for pre,v in d.groupby(d.code_2018.str[:2]):
  category.append(dict(city=city,source_prefix=pre,n=len(v),n_pct=100*len(v)/len(d),area_ha=v.polygon_m2.sum()/1e4,area_pct=100*v.polygon_m2.sum()/d.polygon_m2.sum(),positives=int(v.transition.sum())))
 with TemporaryDirectory() as t:
  sp=CITY_SOURCES[city]; C=read_fgb_nested(Path(os.environ.get('URBAN_SOURCE_DIR','/mnt/data'))/sp['change'],Path(t))
  C['code_2018']=C.code_2018.astype(str);C['code_2021']=C.code_2021.astype(str)
  S=C[C.code_2018.str.startswith(SOURCE_PREFIXES)&C.code_2021.isin(BUILT_TARGET)].copy()
  S['ha']=shapely.area(S.geometry.to_numpy())/1e4
  for code,g in S.groupby('code_2021'):dest.append(dict(city=city,code_2021=code,n=len(g),change_ha=g.ha.sum(),pct_change_ha=100*g.ha.sum()/S.ha.sum()))
 summary.append(dict(city=city,eligible=len(d),positives=int(d.transition.sum()),source_eligible_area_ha=d.polygon_m2.sum()/10000,median_source_polygon_ha=d.polygon_m2.median()/10000,median_250m_point_fraction=d.built_fraction_250m.median(),median_1000m_point_fraction=d.built_fraction_1000m.median(),median_point_distance_m=d.distance_to_built_m.median(),strict_change_polygons=len(S),strict_change_ha=S.ha.sum()))
 print(summary[-1],flush=True)
pd.DataFrame(summary).to_csv(OUT/'r2_city_comparison.csv',index=False)
pd.DataFrame(category).to_csv(OUT/'r2_source_prefix_composition.csv',index=False)
pd.DataFrame(dest).to_csv(OUT/'r2_destination_composition.csv',index=False)
print('SOURCE PREFIXES',pd.DataFrame(category).to_string(index=False))
print('DEST TOP',pd.DataFrame(dest).sort_values(['city','change_ha'],ascending=[True,False]).groupby('city').head(3).to_string(index=False))
