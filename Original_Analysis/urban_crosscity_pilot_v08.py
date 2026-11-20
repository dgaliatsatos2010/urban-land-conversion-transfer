#!/usr/bin/env python3
"""Retrospective, non-causal, polygon-level urban land conversion pilot.
Three genuine European Copernicus Urban Atlas 2018 and Change 2018-2021 FUAs.
Fixed models, no tune-on-test, no oversampling, no future predictors.
WARNING: UA2018 revised retrospectively; not a prospective forecast.
Usage: python urban_crosscity_pilot_v08.py --input /path/to/raw_zip_folder --output /path/to/results
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, shutil, tempfile, warnings, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from scipy.spatial import cKDTree
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss
from tan_bayesian_network_v03 import TreeAugmentedBayes,NUMERIC,CATEGORICAL,FEATURES
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CITY_SOURCES={
 'Kavala':{'annual':'118380.zip','change':'118386.zip','code':'EL008L1','country':'Greece'},
 'Graz':{'annual':'CLMS_UA_LCU_S2018_V025ha_AT002L3_GRAZ_03035_V01_R01_20250227.zip','change':'CLMS_UA_LCUC_C2018-2021_V010ha_AT002L3_GRAZ_03035_V01_R01_20250227.zip','code':'AT002L3','country':'Austria'},
 'Tirana':{'annual':'CLMS_UA_LCU_S2018_V025ha_AL001L1_TIRANA_03035_V01_R01_20250620.zip','change':'CLMS_UA_LCUC_C2018-2021_V010ha_AL001L1_TIRANA_03035_V01_R01_20250620.zip','code':'AL001L1','country':'Albania'}
}
SEED=20261014
BUILT_TARGET={'11100','11210','11220','11230','11240','11300','12100','12210','12220','12230','12300','12400'}
SOURCE_PREFIXES=('21','22','31','32','33')
STRICT_SOURCE_EXCLUDES=('23','24') # pasture, permanent crops? 22 allowed; 24 excluded.


def read_fgb_nested(zpath,tmp:Path):
    """Extract one nested or direct FGB without copying original ZIP into outputs."""
    with zipfile.ZipFile(zpath) as z:
        names=[n for n in z.namelist() if n.lower().endswith(('.fgb','.zip'))]
        if len(names)!=1: raise ValueError(f'{zpath}: expected one FGB or inner ZIP, got {names}')
        n=names[0]
        if n.lower().endswith('.zip'):
            with z.open(n) as f: raw=io.BytesIO(f.read())
            with zipfile.ZipFile(raw) as inner:
                members=[m for m in inner.namelist() if m.lower().endswith('.fgb')]
                if len(members)!=1: raise ValueError('Expected exactly one inner FGB')
                with inner.open(members[0]) as f,open(tmp/Path(members[0]).name,'wb') as dst:shutil.copyfileobj(f,dst)
                filename=tmp/Path(members[0]).name
        else:
            with z.open(n) as f,open(tmp/Path(n).name,'wb') as dst:shutil.copyfileobj(f,dst)
            filename=tmp/Path(n).name
    try: return gpd.read_file(filename)
    finally: filename.unlink(missing_ok=True)

def check_layer(df,code,cols,label):
    if not {'identifier','geometry','fua_code',*cols}.issubset(df.columns):
        raise ValueError(f'Column missing in {label}: {df.columns.tolist()}')
    if not df.crs or df.crs.to_epsg()!=3035: raise ValueError(f'{label}: CRS is not EPSG:3035')
    if df['fua_code'].nunique()!=1 or df['fua_code'].iloc[0]!=code: raise ValueError(f'{label}: inconsistent FUA')
    if df['identifier'].isna().any() or df['identifier'].duplicated().any():raise ValueError(f'{label}: identifier not unique')
    if df.geometry.is_empty.any() or df.geometry.isna().any() or not df.geometry.is_valid.all():raise ValueError(f'{label}: invalid geometry')
    if df[list(cols)].isna().any().any():raise ValueError(f'{label}: missing land class')

def build_city(city,paths,temp):
    spec=CITY_SOURCES[city]
    a=read_fgb_nested(paths/spec['annual'],temp);c=read_fgb_nested(paths/spec['change'],temp)
    check_layer(a,spec['code'],['code_2018'],f'{city} 2018')
    check_layer(c,spec['code'],['code_2018','code_2021'],f'{city} change')
    # Source-eligible polygon set in 2018. Full set needed to compute 2018-only context.
    a['code_2018']=a['code_2018'].astype(str);c['code_2018']=c['code_2018'].astype(str);c['code_2021']=c['code_2021'].astype(str)
    eligible=a['code_2018'].str.startswith(SOURCE_PREFIXES)
    cand=a.loc[eligible].copy().reset_index(drop=True)
    source_change=c['code_2018'].str.startswith(SOURCE_PREFIXES)
    strict_change=c.loc[source_change & c['code_2021'].isin(BUILT_TARGET)].copy().reset_index(drop=True)
    base_area=shapely.area(cand.geometry.array)
    # Area intersections are computed only for intersecting candidate/change pairs.
    ct=shapely.STRtree(cand.geometry.array)
    cidx, pidx=ct.query(strict_change.geometry.array,predicate='intersects')
    cross=shapely.intersection(strict_change.geometry.to_numpy()[cidx],cand.geometry.to_numpy()[pidx])
    areas=shapely.area(cross)
    matched_code=strict_change['code_2018'].to_numpy()[cidx]==cand['code_2018'].to_numpy()[pidx]
    valid=(areas>1)&matched_code
    pidx=pidx[valid];areas=areas[valid]
    overlapping=np.bincount(pidx,weights=areas,minlength=len(cand))
    # For uncertainty analysis, also store alternate thresholds. Changing geography not done post hoc.
    positive=((overlapping>=100)&(overlapping>=base_area*0.01))
    sensitivity=((overlapping>=100)&(overlapping>=base_area*0.05))
    # 2018-only point-based context using strictly defined developed categories, not all artificial land.
    # Urban green areas, mines, dumps and construction sites are excluded from built-context reference points.
    allpts=shapely.get_coordinates(shapely.point_on_surface(a.geometry.array))
    pts=shapely.get_coordinates(shapely.point_on_surface(cand.geometry.array))
    alltree=cKDTree(allpts)
    developed=a['code_2018'].isin(BUILT_TARGET).to_numpy()
    bpts=allpts[developed]
    if len(bpts)==0: raise ValueError('No built-up 2018 polygons')
    btree=cKDTree(bpts)
    distance=np.asarray(btree.query(pts,k=1,workers=1)[0])
    fractions={}
    for rad in (250,1000):
        allcounts=np.asarray(alltree.query_ball_point(pts,r=rad,return_length=True,workers=1))
        builtcounts=np.asarray(btree.query_ball_point(pts,r=rad,return_length=True,workers=1))
        fractions[rad]=builtcounts/np.maximum(allcounts,1)
    source_geom_area=base_area
    frame=pd.DataFrame({
        'city':city,'country':spec['country'],'fua_code':spec['code'],
        'identifier_2018':cand.identifier.to_numpy(),
        'code_2018':cand.code_2018.to_numpy(),
        'transition':positive.astype(int),'transition_5pct':sensitivity.astype(int),
        'overlap_m2':overlapping,'polygon_m2':source_geom_area,
        'built_fraction_250m':fractions[250],
        'built_fraction_1000m':fractions[1000],
        'distance_to_built_m':distance,
        'block_5km':(np.floor(pts[:,0]/5000).astype(int).astype(str)+'_'+np.floor(pts[:,1]/5000).astype(int).astype(str))
    })
    cnt=dict(city=city,year2018_polygons=int(len(a)),change_polygons=int(len(c)),
        eligible_2018_polygons=int(len(cand)),strict_conversion_change_polygons=int(len(strict_change)),
        strict_conversion_change_ha=float(shapely.area(strict_change.geometry.array).sum()/1e4),
        labeled_positive=int(positive.sum()),labeled_positive_5pct=int(sensitivity.sum()),
        positive_rate_polygon=float(positive.mean()),
        total_mapped2018_km2=float(shapely.area(a.geometry.array).sum()/1e6),
        cross_intersection_pairs=int(valid.sum()))
    print('CITY QA:',cnt,flush=True)
    if cnt['labeled_positive']<3: warnings.warn(f'{city}: very few positive polygons')
    return frame,cnt

def make_model(name):
    if name=='TAN_BN':return TreeAugmentedBayes(bins=4,alpha=1)
    pre=ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),NUMERIC),('cat',OneHotEncoder(handle_unknown='ignore'),CATEGORICAL)])
    if name=='LogisticRegression': m=LogisticRegression(max_iter=1500,C=1.0,random_state=SEED)
    elif name=='RandomForest': m=RandomForestClassifier(n_estimators=120,max_depth=10,min_samples_leaf=10,random_state=SEED,n_jobs=2)
    elif name=='XGBoost':
        from xgboost import XGBClassifier
        m=XGBClassifier(n_estimators=140,max_depth=3,learning_rate=0.05,subsample=0.9,colsample_bytree=0.9,objective='binary:logistic',eval_metric='logloss',random_state=SEED,n_jobs=2)
    else:raise ValueError(name)
    return Pipeline([('prepare',pre),('model',m)])

def evaluate(y,p):
    y=np.asarray(y,dtype=int);p=np.clip(np.asarray(p,dtype=float),1e-8,1-1e-8)
    return {'n':len(y),'events':int(sum(y)),'prevalence':float(y.mean()),
            'auroc':float(roc_auc_score(y,p)) if len(np.unique(y))==2 else np.nan,
            'auprc':float(average_precision_score(y,p)) if sum(y)>0 else np.nan,
            'brier':float(brier_score_loss(y,p)),
            'log_loss':float(log_loss(y,p,labels=[0,1]))}

def bootstrap_block_ci(dat,p,n_boot=0):
    # A descriptive within-FUA spatial-block bootstrap, NOT uncertainty over new cities.
    from sklearn.metrics import roc_auc_score,average_precision_score
    labels=dat.transition.to_numpy(); groups=list(dat.groupby('block_5km').indices.values())
    rng=np.random.default_rng(SEED)
    if len(groups)<4 or n_boot==0:return {'auroc_low':np.nan,'auroc_high':np.nan,'auprc_low':np.nan,'auprc_high':np.nan}
    rows=[]
    for _ in range(n_boot):
        take=rng.integers(0,len(groups),len(groups))
        idx=np.concatenate([groups[i] for i in take])
        if not (labels[idx].any() and (~labels[idx].astype(bool)).any()):continue
        rows.append((roc_auc_score(labels[idx],p[idx]),average_precision_score(labels[idx],p[idx])))
    if len(rows)<35:return {'auroc_low':np.nan,'auroc_high':np.nan,'auprc_low':np.nan,'auprc_high':np.nan}
    arr=np.array(rows)
    return dict(auroc_low=float(np.quantile(arr[:,0],.025)),auroc_high=float(np.quantile(arr[:,0],.975)),
                auprc_low=float(np.quantile(arr[:,1],.025)),auprc_high=float(np.quantile(arr[:,1],.975)))

def run(inputs,output,existing=False):
    output.mkdir(parents=True,exist_ok=True)
    frames=[]; audit=[]; hashed=[]
    if existing:
        d=pd.read_csv(output/'table_01_polygon_features_and_labels.csv',dtype={'code_2018':'str','identifier_2018':'str'})
    else:
      with tempfile.TemporaryDirectory() as work:
        temp=Path(work)
        for city,spec in CITY_SOURCES.items():
            for layer in ('annual','change'):
                filename=spec[layer];p=inputs/filename
                if not p.is_file():raise FileNotFoundError(p)
                h=hashlib.sha256()
                with p.open('rb') as f:
                    for block in iter(lambda:f.read(1<<20),b''):h.update(block)
                hashed.append({'city':city,'layer':layer,'filename':filename,'sha256':h.hexdigest()})
            f,c=build_city(city,inputs,temp);frames.append(f);audit.append(c)
    if not existing:
        d=pd.concat(frames,ignore_index=True)
        d.to_csv(output/'table_01_polygon_features_and_labels.csv',index=False)
        pd.DataFrame(audit).to_csv(output/'table_02_city_cohort_and_label_audit.csv',index=False)
        pd.DataFrame(hashed).to_csv(output/'source_sha256.csv',index=False)
    # Immutable predefined model configs; 3-city data insufficient for stable inner city tuning.
    records=[];predictions=[];edges=[]
    models=['TrainingPrevalence','LogisticRegression','RandomForest','XGBoost','TAN_BN']
    for hold in CITY_SOURCES:
        train=d.loc[d.city!=hold].copy();test=d.loc[d.city==hold].copy()
        ytr=train.transition.to_numpy();yte=test.transition.to_numpy()
        if len(np.unique(ytr))!=2:raise ValueError(f'Cannot fit held-out {hold}, training missing class')
        print(f'LOCO: hold {hold}, train {len(train)} / {int(ytr.sum())}, test {len(test)} / {int(yte.sum())}',flush=True)
        trainprev=float(ytr.mean())
        for name in models:
            if name=='TrainingPrevalence':p=np.full(len(test),trainprev)
            else:
                mdl=make_model(name)
                mdl.fit(train[FEATURES],ytr)
                p=mdl.predict_proba(test[FEATURES])[:,1]
                if name=='TAN_BN':
                    for row in mdl.edges_as_rows():edges.append({'heldout_city':hold,**row})
            met=evaluate(yte,p);ci=bootstrap_block_ci(test,p)
            records.append({'city':hold,'model':name,'train_n':len(train),'train_events':int(ytr.sum()),'train_prevalence':trainprev,**met,**ci})
            predictions.append(pd.DataFrame({'city':hold,'model':name,'identifier_2018':test.identifier_2018.values,'true_label':yte,'predicted_probability':p}))
            print('  ',name,'AUROC',round(met['auroc'],4),'AP',round(met['auprc'],4),'Brier',round(met['brier'],5),flush=True)
    result=pd.DataFrame(records)
    result.to_csv(output/'table_03_heldout_city_metrics.csv',index=False)
    pred=pd.concat(predictions,ignore_index=True)
    pred.to_csv(output/'table_04_out_of_city_predictions.csv',index=False)
    pd.DataFrame(edges).to_csv(output/'table_05_tan_dependencies.csv',index=False)
    # Paired descriptive score comparison by city (n=3; no inferential significance claims).
    baseline=result.loc[result.model=='TrainingPrevalence'].set_index('city')
    summary=[]
    for model in models[1:]:
        r=result.loc[result.model==model].copy()
        r['baseline_brier']=r.city.map(baseline.brier)
        r['delta_brier']=r.brier-r.baseline_brier
        summary.append({'model':model,'mean_AUROC_cities':r.auroc.mean(),'mean_AUPRC_cities':r.auprc.mean(),
                        'mean_Brier_cities':r.brier.mean(),'mean_delta_Brier_vs_baseline':r.delta_brier.mean(),
                        'cities_better_Brier':int((r.delta_brier<0).sum())})
    pd.DataFrame(summary).to_csv(output/'table_06_macro_descriptive_model_comparison.csv',index=False)
    for metric,title,fname in [('auprc','Area under precision–recall curve','figure_01_heldout_auprc.png'),('brier','Brier score (lower is better)','figure_02_heldout_brier.png')]:
        pivot=result.pivot(index='city',columns='model',values=metric).reindex(['Kavala','Graz','Tirana'])
        ax=pivot.plot.bar(figsize=(10.5,5),rot=0,width=0.78)
        ax.set(title=f'Pilot leave-one-city-out validation: {title}',ylabel=title,xlabel='Held-out city')
        ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),fontsize=8);ax.grid(axis='y',alpha=.25)
        ax.figure.tight_layout();ax.figure.savefig(output/fname,dpi=170,bbox_inches='tight');plt.close(ax.figure)
    with (output/'run_manifest.json').open('w') as f:
        json.dump({'data':'Real Copernicus UA 2018 revised and official change 2018-2021',
                   'design':'retrospective, polygon-level, held-out FUA',
                   'positive_label':'2018 eligible parcel intersects strict built conversion at >=100m² and >=1% of parcel area',
                   '2018_source_prefixes':SOURCE_PREFIXES,'2021_built_destination_codes':sorted(BUILT_TARGET),
                   'features':FEATURES,'neighbor_features':'fraction of 2018 developed-category polygon representative points within a fixed radius divided by count of all 2018 polygon representative points within radius; unweighted by polygon area','selection':'fixed parameter models; no tuning on test',
                   'cautions':['2018 revised retrospectively','polygon-level not area-level prevalence','labels may capture partial conversion',
                   'three geographic clusters only','BN associations do not imply causation','FUA mapping boundary differences','class imbalance']},f,indent=2)
    print('COMPLETE',len(d),'polygons in cohort',flush=True)
    return d,result

if __name__=='__main__':
    par=argparse.ArgumentParser()
    par.add_argument('--input',type=Path,default=Path('/mnt/data'))
    par.add_argument('--output',type=Path,default=Path(__file__).parent)
    par.add_argument('--existing',action='store_true',help='Reuse earlier validated cohort data for rerun')
    ar=par.parse_args()
    run(ar.input,ar.output,existing=ar.existing)
