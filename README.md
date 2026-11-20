# Cross-city transfer of urban land-use conversion rankings

Reproducibility repository for an Urban Science manuscript comparing land-use conversion rankings across Kavala (Greece), Graz (Austria), and Tirana (Albania).

## Research materials
The verified local Reviewer 2 analysis bundle (v0.2) contains:
- Original_Analysis: original modelling scripts, derived polygon cohort and predictions.
- Reviewer2_Analyses: intersection-filter, spatial-coverage, raster resolution, edge, tie, and block-size sensitivity analyses.
- Reviewer2_Results: machine-readable outputs, status-coverage masks, city summaries and source-archive provenance.
- Documentation: manuscript edit guide, environment versions and supplementary table drafts.
- SHA256SUMS.csv: checksums of the bundle.

**Repository population is in progress.** This README alone is not the reproducibility archive. Do not cite this repository as a complete release until the actual scripts and outputs are uploaded, verified, and tagged.

## Reproducibility and limitations
The study comprises 18,366 eligible source polygons across three cities; only six positive labels occur in Kavala. Zero labels indicate no qualifying recorded mapped change, not independently verified absence of all land development. The shared 2018/2021 status-map extent is not an independently certified change-observation mask. Area-based neighbourhood measures are raster approximations. Within-city spatial block bootstraps do not establish generalization to unseen cities.

The nine original Copernicus Land Monitoring Service archives are not redistributed; original official filenames and hashes are recorded in the analysis bundle.

## Citation
Please cite the associated Urban Science paper once bibliographic metadata are finalized. No DOI or permanent archival release has been assigned yet.
