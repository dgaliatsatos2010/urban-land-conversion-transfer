from pathlib import Path
from tempfile import TemporaryDirectory
import sys,time,numpy as np,pandas as pd,shapely,geopandas as gpd
sys.path.insert(0,'/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08')
from urban_crosscity_pilot_v08 import read_fgb_nested,CITY_SOURCES
B=Path('/mnt/data');OUT=Path('/mnt/data/r2_followup');v={'Kavala':'118393.zip','Graz':'CLMS_UA_LCU_S2021_V025ha_AT002L3_GRAZ_03035_V01_R01_20250227.zip','Tirana':'CLMS_UA_LCU_S2021_V025ha_AL001L1_TIRANA_03035_V01_R01_20250620.zip'}
rows=[]
for city in ('Kavala','Graz','Tirana'):
 t=time.time()
 with TemporaryDirectory() as tmp:
  a=read_fgb_nested(B/CITY_SOURCES[city]['annual'],Path(tmp));b=read_fgb_nested(B/v[city],Path(tmp))
 ga=shapely.buffer(shapely.coverage_union_all(a.geometry.to_numpy()),0)
 gb=shapely.buffer(shapely.coverage_union_all(b.geometry.to_numpy()),0)
 # Valid geometries, no simplification or reference-grid rasterization.
 x=shapely.intersection(ga,gb)
 y=shapely.difference(gb,ga)
 z=shapely.difference(ga,gb)
 for typ,geom in [('common_status_2018_2021',x),('mapped_only_2021',y),('mapped_only_2018',z)]:
  assert shapely.is_valid(geom)
  rows.append({'city':city,'mask_type':typ,'area_km2':shapely.area(geom)/1e6,'geometry':geom})
 print('geo status masks',city,[(r['mask_type'],round(r['area_km2'],4)) for r in rows[-3:]],'time',round(time.time()-t,1),flush=True)
G=gpd.GeoDataFrame(rows,geometry='geometry',crs='EPSG:3035')
fname=OUT/'r2_status_coverage_masks_epsg3035.gpkg'
G.to_file(fname,driver='GPKG',layer='status_coverage_masks')
print('wrote',fname,round(fname.stat().st_size/1e6,2),'MB')
print('reloaded shapes',len(gpd.read_file(fname)),flush=True)
