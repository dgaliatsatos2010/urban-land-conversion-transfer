from pathlib import Path
import os
import pandas as pd,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(os.environ.get('URBAN_ANALYSIS_OUT','/mnt/data/r2_followup'))
T=pd.read_csv(D/'r2_top5_tie_deterministic_and_random.csv')
models=['LogisticRegression','RandomForest','XGBoost','TAN_BN']
colors=['#1f77b4','#ff7f0e','#2ca02c','#d62728']
cities=['Graz','Tirana']
fig,ax=plt.subplots(figsize=(9.5,5.7))
x=np.arange(len(cities));width=.18
for j,m in enumerate(models):
 v=T[(T.city.isin(cities))&(T.model==m)].set_index('city').loc[cities]
 vals=v.deterministic_recall.to_numpy();pos=x+(j-1.5)*width
 bars=ax.bar(pos,vals,width,label={'LogisticRegression':'Logistic regression','RandomForest':'Random forest','XGBoost':'XGBoost','TAN_BN':'TAN Bayesian network'}[m],color=colors[j])
 for b,vv in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,b.get_height()+.007,f'{vv:.3f}',ha='center',va='bottom',fontsize=9)
ax.set_xticks(x,cities);ax.set_ylabel('Recall among historical positives',labelpad=12);ax.set_xlabel('Held-out Functional Urban Area');ax.set_ylim(0,.36)
ax.set_title('Historical top-5% polygon review — deterministic cutoff ties',pad=15)
ax.yaxis.grid(True,linestyle=':',alpha=.3);ax.set_axisbelow(True)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.16),ncol=2,frameon=False,fontsize=9)
fig.subplots_adjust(left=.14,right=.98,top=.86,bottom=.29)
fig.savefig(D/'Figure_4_REVISED_Deterministic_Ties.png',dpi=300);plt.close(fig)
# Tables minimal publication-oriented
m=pd.concat([pd.read_csv(D/f'area_model_metrics_{c}_25m.csv') for c in ['Kavala','Graz','Tirana']],ignore_index=True)
comp=m.pivot_table(index=['city','model'],columns='representation',values=['AP','AUROC'])
comp.columns=['_'.join(c) for c in comp.columns];comp=comp.reset_index();comp.to_csv(D/'r2_area_proxy_model_comparison.csv',index=False)
# Concise proxy distribution by geography
f=pd.concat([pd.read_csv(D/f'area_features_{c}_25m.csv') for c in ['Kavala','Graz','Tirana']],ignore_index=True)
base=pd.read_csv(Path(os.environ.get('URBAN_CODE_DIR','/mnt/data/r2_audit/UrbanScience_ThreeCity_ML_Pilot_v08'))/'table_01_polygon_features_and_labels.csv',dtype={'identifier_2018':str})
f=f.merge(base[['city','identifier_2018','built_fraction_250m','built_fraction_1000m','transition']],on=['city','identifier_2018'],validate='1:1')
rows=[]
for city,g in f.groupby('city'):
 row={'city':city,'eligible':len(g),'events':int(g.transition.sum()),'point_count250_median':g.built_fraction_250m.median(),'point_count1000_median':g.built_fraction_1000m.median(),'area_250_median':g.area_built_fraction_250m.median(),'area_1000_median':g.area_built_fraction_1000m.median(),'fraction_below90pct_250':(g.circle_mapped_fraction_250m<.9).mean(),'fraction_below90pct_1000':(g.circle_mapped_fraction_1000m<.9).mean(),'n_below90pct_250':int((g.circle_mapped_fraction_250m<.9).sum()),'n_below90pct_1000':int((g.circle_mapped_fraction_1000m<.9).sum()),'spearman_count_vs_area250':float(g.built_fraction_250m.corr(g.area_built_fraction_250m,method='spearman')),'spearman_count_vs_area1000':float(g.built_fraction_1000m.corr(g.area_built_fraction_1000m,method='spearman'))}
 rows.append(row)
pd.DataFrame(rows).to_csv(D/'r2_proxy_distribution_and_edge_coverage.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
print(comp[['city','model','AP_original','AP_area_fractions','AP_area_fractions_boundary_distance']].to_string(index=False))
