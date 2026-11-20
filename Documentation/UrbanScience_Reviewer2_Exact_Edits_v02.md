# Urban Science — Reviewer 2: exact editing guide after real reanalysis

**Base file:** `Urban Science(1).docx` (not an older manuscript). **Manuscript policy:** main text only; no supplementary manuscript. The scripts/derived tables for reproducibility are a separate, versioned *code and data* package, not a supplementary scientific document. **Important restriction:** the available products establish status-map overlap but do not provide an independent producer-certified, FUA-specific change-survey mask. Do not claim complete negative-label validity without further provenance/confirmation.

## 1. Section 2.2 — resolve the inconsistent geometric filter (REPLACE)
**Delete the entire existing third paragraph**, beginning `To preserve the relationship between the official change inventory...` and containing `Fragments below the 100 m² absolute threshold are excluded prior to summing;`.

**Paste:**

For every eligible 2018 source polygon, intersections with qualifying official change polygons were calculated, and only intersections with matching 2018 source-class codes were retained. Individual intersection fragments of 1 m² or less were discarded; the remaining areas were then summed for each source polygon. A positive label required an accumulated overlap of at least 100 m² and at least 1% of the entire 2018 source-polygon area. The 100 m² criterion was therefore applied **after aggregation**, not to individual fragments. The 100 m² minimum was used as a pragmatic safeguard against small incidental overlaps, while the 1% relative threshold aimed to reduce the dependence of the binary label on source-polygon size; neither threshold is a producer-prescribed Urban Atlas change minimum mapping unit or a validated planning threshold. The 5% threshold represents an alternative outcome definition for sensitivity analysis. We recomputed labels after imposing the alternative rule of rejecting individual intersections smaller than 100 m² before summation. The two rules agreed for all 18,366 primary labels and all alternative 5% labels; consequently, no model predictions or performance metrics changed. The executable labelling and sensitivity-check scripts accompany the versioned analysis package [33,36].

**Keep** the existing first two paragraphs of Section 2.2, but check that the expression `Oᵢ` refers to the sum *after discarding ≤1 m² fragments*. The displayed threshold (100 m² and 1%) remains unchanged.

## 2. Section 2.1 — area-of-observation evidence (REPLACE)
**Delete** the portion of the second paragraph from `Moreover, the annual mapped FUA footprints differ in Kavala and Graz.` to `...for the labelled study outcome.` (keep the first two sentences and the final sentence about changed-polygon checks, but avoid duplicating the new text).

**Paste instead:**

The revised 2018 and 2021 status polygons were dissolved independently for each FUA after repairing invalid multipart-union geometry. Their spatial intersection was used as a *common status-map observation mask*. A full-area containment analysis showed that all 18,366 eligible 2018 source polygons lie within that common mapped extent, allowing a 1 m² numerical tolerance. No eligible polygon required exclusion or clipping for a material annual-coverage mismatch. The total 2021 mapped footprints nevertheless exceeded the corresponding revised 2018 footprints by 73.77 km² for Kavala and 255.97 km² for Graz; no material footprint difference was observed for Tirana. These non-overlapping areas were mapped only in the 2021 product and were not part of the 2018 source-polygon cohort. The comparison does **not** derive conversion events by subtracting yearly status maps, and these coverage differences must not be interpreted as urban growth. The official Urban Atlas 2021 documentation describes FUA-wide change mapping and the delivery of revised 2018 maps; however, the original archive bundle does not expose a separate FUA-specific change-survey mask. Common status-map coverage and documented production scope support, but do not independently prove, complete change-detection coverage of all negatives. We therefore treat observations without qualifying recorded changes as *not mapped as changed*, conditional on the producer's documented detection process, rather than as independently verified unchanged land.

**Source:** Copernicus Urban Atlas 2021 PUM, especially Sections 7.2.2, 8.3.4 and 8.3.5, and official product technical summary [4]. **Outstanding:** if required by the editor, request the FUA-level change-observation mask or written completeness confirmation from CLMS. A status-layer intersection is not equivalent to independent proof of detection coverage.

## 3. Section 2.1 — sample selection and source manifest (ADD)
**Where:** First paragraph immediately after `The analysis covers Kavala (FUA EL008L1), Graz (AT002L3), and Tirana (AL001L1).`

**Add:**

The cities were used as a purposive exploratory set of three data-accessible FUAs from different national mapping contexts rather than as a random or statistically representative sample of European cities. Their different mapped extents, source-class compositions and documented change frequencies enable a descriptive comparison of geographic model behaviour, but not population-level estimates of performance in new FUAs.

**Source manifest:** in Section 2.1, after the existing paragraph describing the `input-product manifest`, add:

The versioned provenance manifest lists all nine exact original archive filenames (2018, 2021 and Change for each FUA), file sizes and SHA-256 hashes. The archived identifiers are EL008L1_KAVALA_R01_20250321, AT002L3_GRAZ_R01_20250227 and AL001L1_TIRANA_R01_20250620. The manifest accompanies the derived modelling cohort, held-out predictions, evaluation scripts and analysis outputs for independent checking.

## 4. Section 2.3 — area-based spatial alternative and boundary handling (ADD)
**Where:** After the final existing paragraph, immediately before `2.4. Models and external evaluation`.

**Add:**

To investigate sensitivity to polygon subdivision, we constructed alternative neighbourhood measures based on estimated developed *area* rather than counts of polygon representative points. The 2018 status maps were rasterized onto a common 25 m grid in EPSG:3035. For each candidate representative point and 250 m or 1,000 m circular neighbourhood, the number of raster cells classified as developed was divided by the number classified as covered by any mapped 2018 land-use polygon. Thus only mapped land contributed to the denominator, and neighbourhoods crossing the FUA edge were not silently treated as wholly non-developed. The resulting proportions are raster approximations, not exact vector intersection-area ratios. We also derived an approximate 25 m raster distance to the nearest developed cell as an additional alternative to representative-point distance. The same procedure was repeated at 50 m resolution to assess raster discretization sensitivity. Candidate boundaries were diagnosed using the proportion of each 1,000 m circle covered by mapped 2018 land. All alternative features were derived from the 2018 status layer without using changes or 2021 target labels.

## 5. Section 2.4 — preprocessing, seeds and score ties (ADD)
**Where:** After the last paragraph about the uniform logistic-regression top-5% reference, before Section 2.5.

**Add:**

The data-processing code used median imputation for numeric predictors in non-Bayesian classifiers, numerical standardization within the training folds, and one-hot encoding of source classes with `handle_unknown='ignore'` for unseen categories. The custom TAN classifier used training-derived quantile discretization and a dedicated unseen-category state. There were no unseen source-class codes in any of the three held-out FUAs in the reported dataset. All random-state-aware classifiers used seed 20261014. For capacity-constrained ranking, observations were sorted by descending predicted probability and ties were resolved by ascending 2018 polygon identifier, providing a deterministic, reproducible top-5% selection of ceil(0.05 × n) observations. This explicit tie-breaking convention was applied to the revised screening graphics and was compared with 1,000 random selections among cutoff-tied observations for sensitivity analysis. It is a reporting rule introduced during revision, not a preregistered policy.

## 6. Section 2.5 — block and mapped-edge sensitivity (ADD)
**Where:** At end of existing bootstrap description, before area-weighted AP paragraph.

**Add:**

The original 5 km block size was a pragmatic spatial grouping scale rather than an empirically optimized independence distance. To assess its influence, we repeated the fixed-score XGBoost bootstrap for all three FUAs with 5, 10 and 20 km square blocks (1,000 resamples per setting), reporting the number of total and positive-containing blocks, valid resamples, and 95% conditional AP percentile intervals. In a separate mapped-edge sensitivity experiment, we retained only candidate polygons for which at least 95% of the 1,000 m neighbourhood was covered by the 2018 status map; all four classifiers were then refitted using the unchanged original point-count predictors and leave-one-FUA-out protocol. This edge-screen analysis changes the study cohort and thus is not directly comparable to fixed-sample reweighting.

## 7. Section 2.6 — reproducibility language (REPLACE)
**Find existing sentence:** `the accompanying environment specification should be retained and published alongside the scripts before submission.`

**Replace when the versioned package has actually been deposited:**

The versioned reproducibility package provides the executable Python scripts, a pinned environment specification, full source-archive manifest with SHA-256 hashes, 18,366 derived records, the 91,830 original held-out predictions and all additional reviewer-driven evaluation outputs, available from [INSERT REAL REVIEW ACCESS URL OR PERMANENT DOI]. The original nine Copernicus source archives remain accessible from CLMS and are not redistributed.

**Important:** do not insert a fictitious URL/DOI or say the package is publicly available merely because a ZIP exists locally. Until uploaded, retain a clear editorial placeholder. In the final Data Availability Statement, replace the current `[Before submission: provide verified URL/DOI ...]` placeholder with the same real access address.

## 8. Section 3.5 — correct AP terminology (REPLACE phrase)
**Replace** `AUROC, AUPRC, Brier score and log loss were independently reproduced` with `AUROC, average precision (AP; computed using scikit-learn's average_precision_score), Brier score and log loss were independently reproduced`.

**Review text/table titles:** use `average precision (AP)` for the original score, not trapezoidally integrated PR-AUC. In Table 3 caption, Table 5 caption and Figure 1 y-axis, use **average precision (AP)**. Figure 1 already shows four models and no training-prevalence bar; the older reviewer remark about the legend is addressed by this figure replacement, not by adding a fictitious baseline model.

## 9. Section 3.3 — replace Figure 4, revise caption (REPLACE)
**Remove** the previous Figure 4 PNG, which depicts an implicit tie-ordering for TAN.
**Insert** `Figure_4_REVISED_Deterministic_Ties.png` from the verification package.

**Replace figure caption with:**

Figure 4. Recall among historical positive source polygons in the top 5% of eligible 2018 polygons, for four frozen classifiers evaluated in Graz and Tirana. Candidate scores were ordered in descending probability with ascending polygon identifier used to resolve ties. Large TAN ties occur at the capacity cutoff (875 tied polygons in Graz and 174 in Tirana); therefore, TAN bars are sensitive to tie-breaking, as reported in Section 3.6. Kavala is omitted from the comparative chart owing to only six positive polygons. This retrospective selection is not a validated operational planning policy.

**No change to Table 4:** it uses logistic regression in all cities and its cutoff has no boundary-crossing ties.

## 10. Add new Section 3.6 after existing Table 10 in Section 3.5
**Insert heading:** `3.6. City composition, observation coverage and representation sensitivity`.

**Insert text:**

Table 11 summarizes the three source cohorts and their differing land-use contexts. Although eligible source polygon areas have broadly similar medians, source-class composition and proximity descriptors differ markedly. Class-family 21 accounted for 61.9% of the eligible polygons in Graz and 43.9% in Kavala, whereas class-family 32 was most frequent in Tirana (38.3%). The main recorded developed destination was class 12100, accounting for 49.6%, 82.3% and 86.2% of the strict change-layer area in Graz, Kavala and Tirana, respectively. These percentages describe the gross area of qualifying *official change polygons*, not the amount of complete eligible source polygons labelled positive. The pronounced differences provide a plausible descriptive explanation for heterogeneity in model transport, without establishing causal mechanisms.

**Table 11 caption:** City-level comparison of mapped coverage, eligible 2018 source polygons, dominant source-class prefix and strict developed destination, and source-polygon median area.

**Figure 6 placement:** after Table 11. Insert `Figure_R2_FUA_Footprint_Comparison.png` with caption: `Figure 6. Difference between revised Urban Atlas 2018 and Urban Atlas 2021 mapped footprints for Kavala, Graz and Tirana. The 2021-only areas are outside the 2018 eligible cohort and are not interpreted as land-use change. Status-map overlap does not independently prove full change-detection coverage.`

**Then add:**

The raster-based alternative neighbourhood measures produced a different distribution of geographic context than the original representative-point counts. For example, the median Graz 1,000 m developed-point fraction was 0.556, compared with a 25 m raster-approximated developed-area fraction of 0.114. Across the three FUAs, the two measures were positively but imperfectly associated. Table 12 compares average precision obtained by refitting the four fixed classifiers on their original features and on area-based neighbourhood alternatives, using the same city-exclusive folds. No alternative representation consistently improved AP across cities and models. In particular, TAN AP in Graz increased from 0.053 to 0.070 after replacing the two point-count proportions with developed-area fractions, whereas random-forest AP in Tirana decreased from 0.088 to 0.071. Area-based distance was additionally evaluated as a 25 m raster approximation, not an exact polygon-boundary distance. Repeating the area-fraction experiment at 50 m changed AP by up to 0.029 (most prominently in the small Kavala cohort), demonstrating discretization sensitivity.

**Table 12 caption:** Original and 25 m area-based spatial-context representations: held-out city average precision, with unchanged labels and predefined model settings. The third column of alternative results also replaces point-to-point distance with approximate raster distance to the nearest developed cell.

**Then add:**

All 18,366 eligible source polygons were covered by both annual status layers within 1 m² numerical tolerance, but local neighbourhoods frequently intersected the outer mapped boundary. At the 25 m grid resolution, 1,000 m neighbourhoods had less than 90% mapped coverage for 120 Kavala candidates, 1,321 Graz candidates and 638 Tirana candidates. A stricter mapped-edge screen requiring at least 95% neighbourhood coverage retained 497/645 Kavala polygons (5 positive), 9,884/11,412 Graz polygons (259 positive) and 5,554/6,309 Tirana polygons (91 positive). Models were refitted on the respective interior-only training and test cohorts. Ranking results changed under this altered sample, confirming boundary sensitivity; the diagnostic does not prove complete change-survey coverage.

**Then add:**

Table 13 supplies the complete model-specific Brier scores and log losses, alongside the training-prevalence benchmark, using the same frozen held-out predictions as the existing AUROC/AP tables. Probability error cannot be inferred reliably from AUROC/AP alone. For example, logistic regression had a higher Brier error than the training-prevalence benchmark in Kavala but lower errors in Graz and Tirana.

**Table 13 caption:** Complete held-out Brier score and log loss by FUA and classifier, including the constant training-prevalence baseline (lower is better).

**Then add:**

The within-city XGBoost bootstrap was sensitive to block size (Table 14). Positive polygons occurred in 3 of 21 five-kilometre blocks in Kavala, compared with 81/152 in Graz and 27/94 in Tirana. Under 5, 10 and 20 km blocks, the conditional 95% AP intervals for Kavala were 0.026–0.664, 0.020–0.473 and 0.029–0.474, respectively. Thus, uncertainty summaries for the six positive Kavala polygons are highly sensitive to block grouping and must remain secondary diagnostics rather than cross-city confidence intervals.

**Table 14 caption:** XGBoost spatial-block bootstrap sensitivity (1,000 resamples per setting), with total/positive blocks, valid resamples and within-city conditional 95% AP intervals.

**Then add:**

In the original fixed top-5% rankings, TAN exhibited substantial score ties at the inspection cutoff: 39 tied candidates in Kavala, 875 in Graz and 174 in Tirana. Under the deterministic score-plus-identifier rule, TAN detected 3/6, 49/280 and 24/97 events, respectively. For Graz, random tie resolution over 1,000 simulations produced a fifth-to-95th-percentile recall range of 0.125–0.168; deterministic identifier ordering yielded 0.175. These are tie-resolution diagnostics, not statistical confidence intervals. The common logistic-regression reference in Table 4 is unaffected by ambiguous boundary-crossing ties.

**Optional Table 15:** TAN cutoff ties and ranges (see verification CSV). The Figure 4 caption and the above paragraph are sufficient if the manuscript is too long.

## 11. Section 4.2 — direct land-change literature and quantified planning meaning (ADD)
**After the current paragraph beginning `Excluding an entire Functional Urban Area...`, add:**

Urban-expansion studies have already investigated the transferability of growth models across regions. Yu et al. [50] used multi-area and multi-period urban growth simulations to characterize transfer uncertainty across European functional urban areas, while Wang et al. [51] proposed similarity-based transfer of urban expansion rules among Chinese cities. Unlike their simulation and rule-transfer approaches, the present study evaluates fixed polygon-level *rankings of historically mapped conversion* under full-city holdouts, explicitly contrasting polygon-count and area-based neighbourhood proxies and reporting rare-event average precision. This is a narrower retrospective diagnostic rather than a competing urban growth simulation system. At the illustrative 5% review budget, logistic regression selected 571 Graz polygons to retrieve 69 historical positives (502 non-positive selected polygons; precision 12.1%) and 316 Tirana polygons to retrieve 23 (293 non-positive; precision 7.3%). These outcomes limit any practical interpretation as a resource-efficient screening rule without independent prospective and cost-sensitive validation.

**Append references in this order to the end of the existing 49** (references [50]–[51], first cited here, after the earlier 49 have already appeared):

[50] Yu, J.; Hagen-Zanker, A.; Santitissadeekorn, N.; Hughes, S. A Data-Driven Framework to Manage Uncertainty Due to Limited Transferability in Urban Growth Models. *Comput. Environ. Urban Syst.* **2022**, *98*, 101892. https://doi.org/10.1016/j.compenvurbsys.2022.101892.

[51] Wang, H.; Liang, Y.; Xu, S.; He, S.; Zhang, B. A Similarity Law-Based Approach for the Transferability of the Urban Expansion Model. *Int. J. Geogr. Inf. Sci.* **2025**, *39*, 1801–1822. https://doi.org/10.1080/13658816.2025.2475329.

## 12. Section 4.3 — discuss coverage without overstating certainty (ADD)
**After** the current first paragraph about 2018 retrospective revision, add:

The spatial intersection of the two annual status-map coverages did not leave any materially uncovered eligible 2018 source polygons. However, no separate source-level change-survey coverage mask was delivered with the downloaded archive bundle, so the absence of a mapped change cannot be independently checked as an observed unchanged outcome at every location. This residual provenance uncertainty is distinct from the successful whole-change-polygon containment checks and must be addressed by the producer's technical documentation or a FUA-specific confirmation of survey completeness before broader interpretations of negative-label performance are made.

## 13. Section 4.4 — shorten repetitive limitations (DELETE / REPLACE)
**Delete paragraph** beginning `Kavala is retained as an illustrative low-event case rather than an equivalent unit...` if its contents are already fully covered in Section 3.2 and the preceding 4.4 paragraph. Keep the Olofsson/Foody paragraph containing references [33,34].

**Replace paragraph** beginning `The neighbourhood predictors introduce additional methodological limitations.` with:

The new area-based and mapped-edge sensitivity experiments demonstrate that the definition of neighbourhood context affects city-held-out rankings. Point-count fractions depend on land-use polygon subdivision, whereas raster area proportions introduce their own spatial-resolution and boundary-normalization assumptions. Neither representation can be treated as universally preferable from only three FUAs. The observed differences in source-class composition and destination transitions further suggest that performance variation is linked to the sampled cartographic contexts; this association requires verification in additional independent cities.

**Retain** the paragraph supporting the distinction between map thematic accuracy and model performance [33,34], but remove duplicated wording elsewhere rather than deleting the only citation supporting that distinction.

## 14. Section 5 — amend conclusions (REPLACE final paragraph)
**Delete** the current final paragraph of Conclusions starting `The principal contribution is a transparent and reproducible methodological framework...`.

**Paste:**

The primary contribution is an auditable, three-FUA, city-held-out evaluation of historical polygon-level urban conversion rankings. Independent checks showed that the alternative fragment-area filtering rule produced identical binary labels, whereas spatial-context representation, boundary-neighbourhood coverage, and TAN tie resolution materially influenced selected diagnostics. The alternative developed-area features did not improve average precision consistently, and the conditional block-bootstrap intervals varied with spatial-block size. The status-map coverage audit placed all eligible 2018 source polygons within the intersection of the two mapped status extents, but completeness of the producer's change-observation survey remains a separate provenance requirement. Further assessment should use a larger and prespecified sample of cities, producer-confirmed observation masks and temporally available baseline maps before prospective planning decisions are considered.

## 15. Data Availability Statement — REQUIRED ACTION BEFORE RESUBMISSION
**Current text has a publication placeholder.** Replace that placeholder **only once the versioned bundle is actually uploaded** to a reviewer-accessible repository or an immutable release with a real URL/DOI. Required files: exact source-product manifest (nine archived filenames + SHA-256), original 18,366 features and labels, 91,830 held-out scores, scripts and environment, label-filter alternatives, common status-mask checks, new area-proxy features and predictions, cutoff ties, full metrics, city composition, spatial-block and boundary sensitivity. Original CLMS ZIPs remain available from the producer; no redistribution is necessary.

## Explicit boundary of what was proven
**Proven from downloaded files:** all 18,366 2018 candidate polygons lie within the status-map intersection at a 1 m² tolerance; 0 label changes under fragment filtering; fully reproduced old model scores; all new model sensitivity outputs generated; source-version hashes. **Not yet independently proven:** a FUA-specific survey mask showing the producer examined all eligible negative locations for change, or prospectively valid prediction/transportability. The latter is a substantive outstanding Reviewer 2 issue and should not be masked by a strong-sounding Data Availability sentence.
