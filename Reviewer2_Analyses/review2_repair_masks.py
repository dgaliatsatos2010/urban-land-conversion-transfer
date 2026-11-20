from pathlib import Path
from tempfile import TemporaryDirectory
import sys,os,time,numpy as np,pandas as pd, shapely
sys.path.insert(0,str(Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'))))
from urban_crosscity_pilot_v08 import read_fgb_nested,CITY_SOURCES,SOURCE_PREFIXES
B=Path(os.environ.get('URBAN_SOURCE_DIR','/mnt/data'));O=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'));v={'Kavala':'118393.zip','Graz':'CLMS_UA_LCU_S2021_V025ha_AT002L3_GRAZ_03035_V01_R01_20250227.zip','Tirana':'CLMS_UA_LCU_S2021_V025ha_AL001L1_TIRANA_03035_V01_R01_20250620.zip'}
rows=[];errors=[]
for city in ['Kavala','Graz','Tirana']:
 t=time.time();print('Start',city,flush=True)
 with TemporaryDirectory() as td:
  a=read_fgb_nested(B/CITY_SOURCES[city]['annual'],Path(td));b=read_fgb_nested(B/v[city],Path(td))
 print('loaded',flush=True)
 ag=shapely.coverage_union_all(a.geometry.to_numpy());bg=shapely.coverage_union_all(b.geometry.to_numpy())
 print('merged',round(time.time()-t,1),'valid raw',shapely.is_valid(ag),shapely.is_valid(bg),'reason:',shapely.is_valid_reason(bg)[:150],flush=True)
 a_valid=shapely.buffer(ag,0);b_valid=shapely.buffer(bg,0)
 print('repaired',round(time.time()-t,1),'valid',shapely.is_valid(a_valid),shapely.is_valid(b_valid),'area changes',shapely.area(a_valid)-shapely.area(ag),shapely.area(b_valid)-shapely.area(bg),flush=True)
 cand=a.loc[a.code_2018.astype(str).str.startswith(SOURCE_PREFIXES)].reset_index(drop=True)
 candidates=cand.geometry.to_numpy();A=shapely.area(candidates)
 covered=shapely.covered_by(candidates,b_valid);bad=np.where(~covered)[0]; outside=[]
 for i in bad:
  d=shapely.area(shapely.difference(candidates[i],b_valid)); outside.append(d)
  errors.append(dict(city=city,id=str(cand.identifier[i]),code=str(cand.code_2018[i]),outside_m2=float(d),source_area_m2=float(A[i])))
 out=np.array(outside)
 row=dict(city=city,eligible=int(len(cand)),noncovered_by2021=int(len(bad)),outside_eligible_area_ha=float(sum(out)/1e4),outside_gt1sqm=int(sum(out>1)),outside_1pct=int(sum((out/A[bad])>0.01)) if len(bad) else 0,only_2018_area_km2=float(shapely.area(shapely.difference(a_valid,b_valid))/1e6),only_2021_area_km2=float(shapely.area(shapely.difference(b_valid,a_valid))/1e6),first_union_valid=bool(shapely.is_valid(a_valid)),second_union_valid=bool(shapely.is_valid(b_valid)),time_seconds=int(time.time()-t))
 print('DONE',row,flush=True);rows.append(row)
 pd.DataFrame(rows).to_csv(O/'r2_valid_mask_status_overlap.csv',index=False);pd.DataFrame(errors).to_csv(O/'r2_valid_mask_exceptions.csv',index=False)
