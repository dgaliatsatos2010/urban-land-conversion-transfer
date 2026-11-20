#!/usr/bin/env python3
"""Reproduce 30 held-out XGBoost permutations per feature and city.

Uses the published 18,366-record polygon panel, fixed original model
configuration and seed. Verifies refitted held-out probabilities against
the 91,830 archived prediction records before producing any results.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Original_Analysis"))
from urban_crosscity_pilot_v08 import make_model, FEATURES, SEED

panel = pd.read_csv(ROOT / "Original_Analysis/table_01_polygon_features_and_labels.csv",
                    dtype={"code_2018": str, "identifier_2018": str})
stored = pd.read_csv(ROOT / "Original_Analysis/table_04_out_of_city_predictions.csv",
                     dtype={"identifier_2018": str})
assert len(panel) == 18366 and len(stored) == 91830

rows, checks = [], []
for held in ["Kavala", "Graz", "Tirana"]:
    train = panel.loc[panel.city != held]
    test = panel.loc[panel.city == held]
    y = test.transition.to_numpy()
    model = make_model("XGBoost")
    model.fit(train[FEATURES], train.transition.to_numpy())
    scores = model.predict_proba(test[FEATURES])[:, 1]
    reference = stored.loc[(stored.city == held) & (stored.model == "XGBoost")]
    paired = test[["identifier_2018"]].assign(recomputed=scores).merge(
        reference[["identifier_2018", "predicted_probability"]],
        on="identifier_2018", validate="one_to_one")
    error = float(np.max(np.abs(paired.recomputed - paired.predicted_probability)))
    assert error < 1e-6, (held, error)
    baseline = float(roc_auc_score(y, scores))
    checks.append(dict(city=held, n_test=len(test), n_positives=int(y.sum()),
                       baseline_auroc=baseline, max_abs_probability_difference=error))
    rng = np.random.default_rng(SEED)
    for feature in FEATURES:
        for repetition in range(1, 31):
            X = test[FEATURES].copy()
            X[feature] = rng.permutation(X[feature].to_numpy())
            permuted = float(roc_auc_score(y, model.predict_proba(X)[:, 1]))
            rows.append(dict(city=held, feature=feature, repetition=repetition,
                             seed=SEED, baseline_auroc=baseline,
                             permuted_auroc=permuted, auroc_drop=baseline-permuted))
    print(held, "max_probability_difference", error, flush=True)

out = ROOT / "Reviewer2_Results"
out.mkdir(exist_ok=True)
full = pd.DataFrame(rows)
assert len(full) == 360
full.to_csv(out / "xgboost_permutation_30_full.csv", index=False, float_format="%.16g")
summary = (full.groupby(["city", "feature"], sort=False).auroc_drop
           .agg(["count", "mean", "std", "min", "max"]).reset_index()
           .rename(columns={"count": "n_repeats", "mean": "mean_auroc_drop",
                            "std": "sd_auroc_drop", "min": "min_auroc_drop",
                            "max": "max_auroc_drop"}))
summary.to_csv(out / "xgboost_permutation_30_summary.csv",
               index=False, float_format="%.16g")
pd.DataFrame(checks).to_csv(out / "xgboost_permutation_model_replay_checks.csv",
                            index=False, float_format="%.16g")
print("PASS: 360 permutations, 12 city-feature summaries, 3 replay checks")
