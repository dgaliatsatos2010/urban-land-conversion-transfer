# Reproducibility status — 20 November 2026

## Public materials
The repository includes the original derived 18,366-polygon analysis panel, 91,830 held-out prediction records, original model implementations, Reviewer 2 sensitivity scripts, machine-readable outputs, input provenance and SHA-256 manifest for the original analysis bundle. The original bundle was uploaded at commit `aa94dee4514abaf3370cd5328a54a669ce03ae75`.

## Independently rerun 30-repeat permutation evidence
The following new files have been **published** under `Reviewer2_Results/`:
- `xgboost_permutation_30_full.csv` — 360 individual held-out permutations (3 FUAs × 4 predictors × 30 repetitions)
- `xgboost_permutation_30_summary.csv` — 12 city/predictor means, sample standard deviations, minima and maxima
- `xgboost_permutation_model_replay_checks.csv` — held-out model prediction replay checks

Reproduction script: `Reviewer2_Analyses/reproduce_permutation_30.py`. The script refits the original XGBoost configuration using only the two training FUAs per fold, compares unpermuted probabilities with the original archived scores (absolute differences <1e-16 in local execution), and uses a fixed NumPy seed 20261014, reset once per city and advanced sequentially across the four predictors. A GitHub Actions workflow independently executes the script in a fresh runner and publishes the outputs.

**Important:** This reproducible permutation protocol produces slightly different values from an earlier manuscript Table 11. The revised manuscript must use the published CSV values (e.g. Graz class 0.1209 ± 0.0110, Tirana class 0.0552 ± 0.0127), not the superseded values.

## Caveats
The original nine Copernicus ZIP archives are not redistributed. The original `SHA256SUMS.csv` applies to the initial research bundle, not subsequent generated permutation files. The project has no archival DOI or versioned release tag yet. Reproduction in an automated runner does not constitute independent third-party scientific replication.
