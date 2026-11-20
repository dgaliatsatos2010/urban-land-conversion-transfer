#!/usr/bin/env python3
"""Leakage-safe Tree-Augmented Naive Bayes (TAN) Bayesian Network.

TAN is NOT Naive Bayes: P(Y, X1,...,Xp) = P(Y) P(Xroot|Y)
  product P(Xchild|Y, Xparent). The non-root predictor dependencies form a
  maximum conditional-mutual-information spanning tree.

Discretization, vocabulary and Bayesian network topology are learned on the
training partition only. This is predictive and associative, NOT causal.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.special import logsumexp
from sklearn.metrics import mutual_info_score

NUMERIC=['built_fraction_250m','built_fraction_1000m','distance_to_built_m']
CATEGORICAL=['code_2018']
FEATURES=NUMERIC+CATEGORICAL


@dataclass
class ColumnEncoding:
    is_numeric: bool
    edges: np.ndarray|None = None
    lookup: dict|None = None
    size: int = 0


class TreeAugmentedBayes:
    def __init__(self, bins=4, alpha=1.0):
        self.bins=int(bins)
        self.alpha=float(alpha)
        if self.bins < 2 or self.alpha <= 0:
            raise ValueError('bins>=2 and alpha>0 required')

    def _fit_encoding(self, X):
        self.encoders_=[]
        for col in FEATURES:
            if col in NUMERIC:
                arr=pd.to_numeric(X[col],errors='coerce').to_numpy(dtype=float)
                nonmissing=arr[np.isfinite(arr)]
                if len(nonmissing):
                    edges=np.unique(np.quantile(nonmissing,np.linspace(0,1,self.bins+1)[1:-1]))
                else: edges=np.array([],dtype=float)
                # State 0 = missing, 1..bins = data bins
                self.encoders_.append(ColumnEncoding(True,edges=edges,size=len(edges)+2))
            else:
                values=X[col].fillna('<NA>').astype(str).to_numpy()
                lookup={value:i+1 for i,value in enumerate(sorted(set(values)))}
                self.encoders_.append(ColumnEncoding(False,lookup=lookup,size=len(lookup)+1))

    def _encode(self,X):
        if not all(col in X for col in FEATURES):
            raise ValueError('Missing TAN features')
        enc=np.zeros((len(X),len(FEATURES)),dtype=int)
        for j,col in enumerate(FEATURES):
            spec=self.encoders_[j]
            if spec.is_numeric:
                a=pd.to_numeric(X[col],errors='coerce').to_numpy(dtype=float)
                mask=np.isfinite(a)
                enc[mask,j]=np.searchsorted(spec.edges,a[mask],side='right')+1
            else:
                vals=X[col].fillna('<NA>').astype(str).to_numpy()
                enc[:,j]=[spec.lookup.get(v,0) for v in vals]
        return enc

    @staticmethod
    def _conditional_information(x, z, y):
        total=len(y); val=0.0
        for cls in [0,1]:
            mask=y==cls
            if mask.sum()>0:
                val+=mask.mean()*mutual_info_score(x[mask],z[mask])
        return float(val)

    def fit(self,X,y):
        X=pd.DataFrame(X).reset_index(drop=True)
        y=np.asarray(y,dtype=int)
        if len(y)!=len(X) or set(np.unique(y))!={0,1}:
            raise ValueError('TAN fit needs nonempty X and both binary classes')
        self._fit_encoding(X)
        z=self._encode(X)
        nfeat=z.shape[1]
        # Maximum spanning tree using Kruskal; fixed deterministic tie-breaking.
        weighted=[]
        for i in range(nfeat):
            for j in range(i+1,nfeat):
                weighted.append((self._conditional_information(z[:,i],z[:,j],y),i,j))
        weighted.sort(key=lambda t:(-t[0],t[1],t[2]))
        root=list(range(nfeat))
        def find(a):
            while root[a]!=a:
                root[a]=root[root[a]]; a=root[a]
            return a
        edges=[]
        for strength,i,j in weighted:
            ai,aj=find(i),find(j)
            if ai!=aj:
                root[ai]=aj
                edges.append((i,j,strength))
            if len(edges)==nfeat-1: break
        # Root at baseline land-use class, useful for reproducible interpretations.
        self.root_=FEATURES.index('code_2018')
        adjacency={i:[] for i in range(nfeat)}
        for i,j,_ in edges:
            adjacency[i].append(j);adjacency[j].append(i)
        self.parents_={self.root_:None}
        stack=[self.root_]
        for node in stack:
            for neighbor in sorted(adjacency[node]):
                if neighbor not in self.parents_:
                    self.parents_[neighbor]=node;stack.append(neighbor)
        self.structure_=[{'child':FEATURES[j], 'parent':FEATURES[parent],
                          'cmi_nats':next(e[2] for e in edges if set(e[:2])=={j,parent})}
                         for j,parent in self.parents_.items() if parent is not None]
        self.prior_=(np.bincount(y,minlength=2)+self.alpha)/(len(y)+2*self.alpha)
        self.cpts_={}
        for j in range(nfeat):
            categories=self.encoders_[j].size
            parent=self.parents_[j]
            parent_states=self.encoders_[parent].size if parent is not None else 1
            counts=np.full((2,parent_states,categories),self.alpha)
            pp=z[:,parent] if parent is not None else np.zeros(len(y),dtype=int)
            np.add.at(counts,(y,pp,z[:,j]),1)
            self.cpts_[j]=counts/counts.sum(axis=-1,keepdims=True)
        return self

    def predict_proba(self,X):
        if not hasattr(self,'prior_'): raise ValueError('Fit TAN before prediction')
        z=self._encode(pd.DataFrame(X).reset_index(drop=True))
        logp=np.tile(np.log(self.prior_),(len(z),1))
        for j in range(len(FEATURES)):
            parent=self.parents_[j]
            pp=z[:,parent] if parent is not None else np.zeros(len(z),dtype=int)
            for cls in [0,1]:
                logp[:,cls]+=np.log(self.cpts_[j][cls,pp,z[:,j]])
        return np.exp(logp-logsumexp(logp,axis=1,keepdims=True))

    def edges_as_rows(self):
        return self.structure_
