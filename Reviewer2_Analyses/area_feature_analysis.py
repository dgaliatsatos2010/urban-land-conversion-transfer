#!/usr/bin/env python3
"""Exploratory 25 m raster approximation of area-based neighborhoods in Urban Atlas 2018.
Inputs: exactly the nine source ZIPs from the 3-city project, without current/future predictors.
Outputs: reproducible source-level area-fraction features and boundary coverage indicators.
"""
import sys, argparse, time, json, os
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np, pandas as pd, shapely
from rasterio.features import rasterize
from rasterio.transform import from_origin
from scipy.signal import fftconvolve
sys.path.insert(0,os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'))
from urban_crosscity_pilot_v08 import read_fgb_nested, CITY_SOURCES, BUILT_TARGET, SOURCE_PREFIXES
SOURCE=Path(os.environ.get('URBAN_SOURCE_DIR','/mnt/data'))
OUT=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'))
SEED=20261118

def disk_kernel(rad,cell):
 r=int(np.ceil(rad/cell)); I,J=np.mgrid[-r:r+1,-r:r+1]
 k=np.asarray((I*cell)**2+(J*cell)**2 <= rad**2, dtype=np.float32)
 return k

def raster_mask(gs,h,w,trans):
 return rasterize(((g,1) for g in gs),out_shape=(h,w),transform=trans,dtype='uint8',fill=0,all_touched=False)

def main(city,cell):
 t=time.time(); spec=CITY_SOURCES[city]
 with TemporaryDirectory() as temp:
  a=read_fgb_nested(SOURCE/spec['annual'],Path(temp))
 print('loaded',city,len(a),round(time.time()-t,1),flush=True)
 a['code_2018']=a.code_2018.astype(str)
 cand=a.loc[a.code_2018.str.startswith(SOURCE_PREFIXES)].reset_index(drop=True)
 dg=a.loc[a.code_2018.isin(BUILT_TARGET)]
 x0,y0,x1,y1=a.total_bounds
 padding=1250; xmin=np.floor((x0-padding)/cell)*cell;ymax=np.ceil((y1+padding)/cell)*cell
 W=int(np.ceil((x1+padding-xmin)/cell));H=int(np.ceil((ymax-(y0-padding))/cell))
 trans=from_origin(xmin,ymax,cell,cell)
 print('grid',city,cell,H,W,round(W*H/1e6,2),'Mpx',round(time.time()-t,1),flush=True)
 cov=raster_mask(a.geometry.to_numpy(),H,W,trans)
 print('rasterized all',round(time.time()-t,1),flush=True)
 built=raster_mask(dg.geometry.to_numpy(),H,W,trans)
 print('rasterized built',round(time.time()-t,1),flush=True)
 pts=shapely.point_on_surface(cand.geometry.to_numpy())
 coords=shapely.get_coordinates(pts)
 cols=np.floor((coords[:,0]-xmin)/cell).astype(int);rows=np.floor((ymax-coords[:,1])/cell).astype(int)
 assert np.min(cols)>=0 and np.max(cols)<W and np.min(rows)>=0 and np.max(rows)<H
 src=pd.read_csv(Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'))/'table_01_polygon_features_and_labels.csv',dtype={'identifier_2018':str,'code_2018':str});src=src[src.city==city]
 result=pd.DataFrame({'city':city,'identifier_2018':cand.identifier.astype(str).to_numpy(),'cell_m':cell})
 for rad in (250,1000):
  k=disk_kernel(rad,cell);kn=float(k.sum())
  # finite grid, 25 m centre-in-polygon approximation in EPSG:3035
  covsum=fftconvolve(cov.astype(np.float32),k,mode='same')[rows,cols]
  devsum=fftconvolve(built.astype(np.float32),k,mode='same')[rows,cols]
  covsum=np.maximum(covsum,0);devsum=np.maximum(devsum,0)
  result[f'area_built_fraction_{rad}m']=np.clip(devsum/np.maximum(covsum,1e-6),0,1)
  result[f'circle_mapped_fraction_{rad}m']=np.clip(covsum/kn,0,1)
  result[f'near_boundary_{rad}m']=result[f'circle_mapped_fraction_{rad}m']<0.90
  print('r',rad,'area coverage',np.round(np.quantile(covsum/kn,[0,.05,.5,.95,1]),4),'built frac',np.round(np.quantile(result[f'area_built_fraction_{rad}m'],[0,.5,.95,1]),4),round(time.time()-t,1),flush=True)
 from scipy.ndimage import distance_transform_edt
 # Raster approximation to minimum distance to developed LAND AREA; not exact polygon-boundary distance.
 dmap=distance_transform_edt(built==0,sampling=cell)
 result['distance_to_built_area_approx_m']=dmap[rows,cols]
 del dmap,built,cov
 print('raster distance completed',round(time.time()-t,1),flush=True)
 m=src.merge(result,on=['city','identifier_2018'],validate='1:1',indicator=True)
 assert (m._merge=='both').all() and len(m)==len(cand)
 assert (m.transition==src.set_index('identifier_2018').loc[m.identifier_2018,'transition'].to_numpy()).all()
 result.to_csv(OUT/f'area_features_{city}_{cell}m.csv',index=False)
 d={"city":city,"cell_m":cell,"eligible":len(cand),"full_landuse_polygons":len(a),"developed_reference_polygons":len(dg),"near_boundary_250m":int(result.near_boundary_250m.sum()),"near_boundary_1000m":int(result.near_boundary_1000m.sum()),"coverage_1000m_median":float(result.circle_mapped_fraction_1000m.median()),"elapsed_sec":round(time.time()-t,2)}
 print('SUMMARY',json.dumps(d),flush=True)
 return d
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--city',required=True);p.add_argument('--cell',default=25,type=int);args=p.parse_args();main(args.city,args.cell)
