# Proposed new tables for the Urban Science main manuscript (Reviewer 2)

All values originate from the supplied FUA source products or from actual refitting on their derived records. Numbers below are rounded for publication; calculations use full precision.

## Table 11. FUA mapped area and source composition

|FUA|Mapped 2018 / 2021 (km²)|Eligible n / positive n|Eligible median area (ha)|Dominant source code prefix (% of eligible polygons)|Leading developed destination (% of qualifying change area)|
|---|---:|---:|---:|---|---|
|Kavala|281.70 / 355.47|645 / 6|3.78|21 (43.9%)|12100 (82.3%)|
|Graz|2,832.55 / 3,088.51|11,412 / 280|3.35|21 (61.9%)|12100 (49.6%)|
|Tirana|1,670.19 / 1,670.19|6,309 / 97|3.56|32 (38.3%)|12100 (86.2%)|

*Note:* Source prefixes are the first two digits of Urban Atlas codes. Destination shares are based on the full official qualifying change geometries, NOT the area of complete positively labelled source polygons. Full class breakdown is available in `r2_source_prefix_composition.csv` and `r2_destination_composition.csv`. Additional 2021-only mapped coverage is 73.77 km² in Kavala, 255.97 km² in Graz and 0 in Tirana.

## Table 12. Comparison of held-out average precision (AP) under alternative spatial proxies (25 m raster)

|FUA|Model|Original point-count AP|Area-fraction AP|Area fraction + raster-distance AP|
|---|---|---:|---:|---:|
|Kavala|LogisticRegression|0.100|0.041|0.040|
|Kavala|RandomForest|0.171|0.054|0.069|
|Kavala|XGBoost|0.323|0.096|0.093|
|Kavala|TAN_BN|0.090|0.051|0.083|
|Graz|LogisticRegression|0.084|0.088|0.090|
|Graz|RandomForest|0.076|0.074|0.087|
|Graz|XGBoost|0.073|0.071|0.089|
|Graz|TAN_BN|0.053|0.070|0.061|
|Tirana|LogisticRegression|0.061|0.049|0.042|
|Tirana|RandomForest|0.088|0.071|0.072|
|Tirana|XGBoost|0.076|0.068|0.077|
|Tirana|TAN_BN|0.057|0.059|0.059|

*Note:* The area-fraction version substitutes the 250 m and 1,000 m point-count fractions with fractions of developed raster cells over mapped raster cells within the respective circles (EPSG:3035, 25 m cell size); the original point-distance variable remains. The final column also replaces that distance by the approximate distance to the nearest developed cell. All models were refitted with the same folds, binary labels and unchanged hyperparameter specifications. The 50 m-resolution results and scores are available as separate audit files; conclusions are exploratory.

## Table 13. Complete probability error scores on the original held-out predictions

|FUA|Model|Brier score|Log loss|
|---|---|---:|---:|
|Kavala|TrainingPrevalence|0.00936|0.05712|
|Kavala|LogisticRegression|0.00993|0.04901|
|Kavala|RandomForest|0.00925|0.04759|
|Kavala|XGBoost|0.00889|0.04513|
|Kavala|TAN_BN|0.00923|0.04650|
|Graz|TrainingPrevalence|0.02403|0.11791|
|Graz|LogisticRegression|0.02329|0.10482|
|Graz|RandomForest|0.02349|0.10726|
|Graz|XGBoost|0.02373|0.10795|
|Graz|TAN_BN|0.02390|0.10893|
|Tirana|TrainingPrevalence|0.01521|0.08116|
|Tirana|LogisticRegression|0.01484|0.07541|
|Tirana|RandomForest|0.01467|0.07166|
|Tirana|XGBoost|0.01473|0.07045|
|Tirana|TAN_BN|0.01485|0.07329|

*Note:* Lower is better; the training-prevalence reference is the constant model equal to the event prevalence in the two training FUAs. Numerical values are reproduced from frozen original test-city scores.

## Table 14. XGBoost 1,000-replicate spatial-block bootstrap size sensitivity

|FUA|Block width (km)|Total blocks|Blocks with positives|Valid / 1,000|AP 95% conditional percentile interval|
|---|---:|---:|---:|---:|---|
|Kavala|5|21|3|967 / 1,000|0.026–0.664|
|Kavala|10|8|2|917 / 1,000|0.020–0.473|
|Kavala|20|4|2|948 / 1,000|0.029–0.474|
|Graz|5|152|81|1000 / 1,000|0.054–0.097|
|Graz|10|47|34|1000 / 1,000|0.050–0.104|
|Graz|20|17|11|1000 / 1,000|0.045–0.099|
|Tirana|5|94|27|1000 / 1,000|0.037–0.148|
|Tirana|10|33|12|1000 / 1,000|0.021–0.167|
|Tirana|20|13|6|1000 / 1,000|0.021–0.150|

*Note:* These are conditional, fixed-prediction, within-FUA intervals. They are NOT confidence intervals over new FUAs; the 5/10/20-km grid origins are fixed to EPSG:3035 coordinates.

## Table 15 (optional). TAN top-5% cutoff ties and tie-resolution diagnostics

|FUA|Tied at cutoff|Deterministic detected / total|Deterministic recall|Theoretical possible recall range|Random-tie 5th–95th percentile recall|
|---|---:|---:|---:|---|---|
|Kavala|39|3 / 6|0.500|0.500–0.667|0.500–0.667|
|Graz|875|49 / 280|0.175|0.000–0.225|0.125–0.168|
|Tirana|174|24 / 97|0.247|0.175–0.247|0.227–0.247|

*Note:* Deterministic ordering: predicted score descending, 2018 polygon ID ascending. Random-tie percentile ranges use 1,000 random cutoff selections and are NOT inferential confidence intervals. The original five-percent Logistic Regression reference table is unaffected by ambiguous cutoff ties.
