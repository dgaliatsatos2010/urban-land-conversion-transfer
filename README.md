# Urban Science — Reviewer 2 reproducibility materials, v0.2

Independent reanalysis of actual Copernicus three-city source files and the 18,366-source-polygon/91,830-prediction original held-out pilot.

## Contents
- `Original_Analysis/`: exact prior model scripts and original derived cohort/predictions; original metrics reproduced to numerical precision <1e-14 by model refitting in the audited environment.
- `Reviewer2_Analyses/`: scripts for area-based neighbourhood rasterization, alternative model refitting, cutoff-tie analysis, mapped-edge and city-composition sensitivity, label-filter and mask checks.
- `Reviewer2_Results/`: all machine-readable derived tables; no invented model results.
- `Reviewer2_Results/r2_status_coverage_masks_epsg3035.gpkg`: vector polygon mask representing only the shared 2018/2021 status coverage and their differences (not the producer change-survey area).
- `Figures/`: corrected Figure 4 and the status-map footprint comparison for inclusion in the main manuscript.
- `Documentation/`: exact Greek-language edit guide with ready-to-paste English manuscript text, new Tables 11–15, environment versions and SHA-256s.

## Data provenance
Use the official nine CLMS ZIP archives in `Reviewer2_Results/r2_exact_9_source_archives.csv` (three per city, with exact original filename and SHA-256). Original raw Copernicus source ZIPs are deliberately not redistributed in this package. They must be downloaded from CLMS or sourced from the authors' original downloads. Note Kavala's original local `118380.zip`/`118393.zip`/`118386.zip` convenience filenames, whose embedded official filename and SHA-256 are documented.

## Re-running on another system
Recommended Python 3.13 with package versions in `ENVIRONMENT_VERSIONS.json`. Install runtime dependencies: `pip install numpy pandas scipy scikit-learn geopandas shapely rasterio xgboost matplotlib pyogrio`. The analysis scripts in this bundle accept the environment variables below for their input and output paths. The exact original v0.8 core pilot script is unchanged.

Set the following environment variables when using the adapted area-feature and model scripts:

```
export URBAN_SOURCE_DIR=/path/to/nine/original/zips
export URBAN_CODE_DIR=/path/to/Original_Analysis
export URBAN_ANALYSIS_OUT=/path/to/reviewer2/output
```

Then:
```
python Original_Analysis/urban_crosscity_pilot_v08.py --input "$URBAN_SOURCE_DIR" --output "$URBAN_CODE_DIR" --existing
for city in Kavala Graz Tirana; do
  python Reviewer2_Analyses/area_feature_analysis.py --city "$city" --cell 25
  python Reviewer2_Analyses/area_feature_analysis.py --city "$city" --cell 50
  python Reviewer2_Analyses/fit_area_sensitivity.py --hold "$city" --cell 25
  python Reviewer2_Analyses/fit_area_sensitivity.py --hold "$city" --cell 50
done
python Reviewer2_Analyses/tie_sensitivity.py
python Reviewer2_Analyses/interior_only_sensitivity.py
```

For the original source-mask and label-filter checks, the same environment variables apply. Specify `URBAN_VERIFICATION_DIR` to point at the folder containing earlier audit tables when invoking the table assembly or QA scripts.

## Critical interpretation limitations
1. `0` labels mean no qualifying recorded mapped change. Interannual status-map coverage was verified, but an independent producer-certified FUA-specific change-observation mask was not supplied. A complete negative-label validity claim remains conditional on CLMS change-survey scope.
2. Area-based neighbourhood features are raster-cell approximations, not exact vector circle-area integrations. The alternative approximate distance is to the nearest developed raster cell, not a boundary-to-boundary distance.
3. All model comparisons are within a three-city retrospective study, with only six primary positives in Kavala.
4. 5/10/20-km bootstraps are conditional within FUA, not confidence intervals over new cities.
5. Deterministic top-5% TAN tie resolution changes chart values relative to implicit ordering; the original Table 4 Logistic Regression is unaffected.
6. This package is a *local reproducibility bundle*, not yet a published repository, permanent DOI, or evidence of complete external independent re-execution. A real reviewer-accessible link is required before manuscript resubmission.

## Public release verification
This archive is the full reproducibility bundle. After publishing, verify the public commit, file list and checksums before citing a release. Original CLMS raw archives are not included.
