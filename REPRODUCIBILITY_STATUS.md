# Reproducibility status — 20 November 2026

## Verified in local analysis archive
The original reviewer analysis ZIP was inspected locally and contains original modelling scripts, derived polygon-level features and predictions, reviewer sensitivity scripts, output tables, provenance and GIS status coverage masks. The SHA-256 manifest was previously checked against the local package (73/73 manifest entries).

## Already published to this GitHub repository
- `README.md`
- `requirements.txt`
- `CITATION.cff`
- `.gitignore`
- `Reviewer2_Results/r2_city_comparison.csv`
- `Reviewer2_Results/r2_label_filter_comparison.csv`

## Not yet published or independently re-run from GitHub
The complete original modelling scripts, the rest of the sensitivity analysis scripts, derived polygon/prediction tables, GIS mask, remaining figures/results, source manifests, and full SHA-256 manifest have not yet been uploaded. Therefore this is not yet a complete reproducibility release; no release tag or DOI has been issued.

## Reviewer 2: intersection filter comparison
The source ZIP table `r2_label_filter_comparison.csv` reports 0 changed labels in all three cities under the compared 1 m² and 100 m² intersection-fragment treatments. The primary positive counts remain Kavala 6, Graz 280, Tirana 97. This is a dataset-specific sensitivity finding, not proof that the two filters are generally equivalent.

## Source data and legal considerations
Original Copernicus source ZIP archives are excluded from redistribution. Before posting derived spatial data or prediction tables, confirm the underlying dataset terms and check for inadvertent confidential content. The exact original archive hashes and filenames are in the local bundle pending publication.

## Manuscript data availability
Do not state that a complete public code-and-data release exists until all intended research materials are available and the repository has been independently verified. Cite the exact release tag and commit SHA only after publication.
