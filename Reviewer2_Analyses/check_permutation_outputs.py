#!/usr/bin/env python3
"""Compare freshly regenerated permutation outputs against committed CSVs.

Uses the checkout's HEAD as immutable baseline. Allows only floating-point
roundoff (absolute tolerance 1e-9), never differences in row identity or count.
"""
from io import StringIO
from pathlib import Path
import subprocess
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
names = [
    "xgboost_permutation_30_full.csv",
    "xgboost_permutation_30_summary.csv",
    "xgboost_permutation_model_replay_checks.csv",
]
for name in names:
    rel = f"Reviewer2_Results/{name}"
    original = subprocess.check_output(
        ["git", "show", f"HEAD:{rel}"], cwd=root, text=True
    )
    expected = pd.read_csv(StringIO(original))
    observed = pd.read_csv(root / rel)
    assert expected.shape == observed.shape, (name, expected.shape, observed.shape)
    assert list(expected.columns) == list(observed.columns), name
    for col in expected.columns:
        if pd.api.types.is_numeric_dtype(expected[col]):
            a = expected[col].to_numpy(dtype=float)
            b = observed[col].to_numpy(dtype=float)
            assert np.allclose(a, b, rtol=0, atol=1e-9, equal_nan=True), (name, col, np.max(np.abs(a-b)))
        else:
            assert expected[col].fillna("<NA>").astype(str).equals(
                observed[col].fillna("<NA>").astype(str)
            ), (name, col)
    print(f"PASS: {name} ({len(observed)} rows)")
