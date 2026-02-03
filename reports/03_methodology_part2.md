## 2.4. Phase 1 Methods: Data Integrity and Value Distribution

To assess the integrity and distribution of the physiological measurements, each of the six vital signs was analyzed independently. We generated histograms and boxplots for the `value` column of each vital sign. This visual analysis aimed to:
1.  Identify and understand the range and central tendency of each measurement.
2.  Screen for significant outliers or physiologically implausible values (e.g., negative heart rates, extreme temperatures) that might indicate data entry errors.
3.  Examine the shape of the distribution (e.g., normal, skewed) for each vital sign.

Additionally, we performed a consistency check on the `unit` column for each `loinc_code` to ensure that all measurements for a given vital were recorded in a standard unit, preventing erroneous comparisons.

## 2.5. Phase 2a Methods: Sparsity and Missingness Analysis

The extent and pattern of missing data were quantified using two primary analyses:

*   **Timestamp Completeness:** We first determined the number of unique vitals recorded at every distinct `(encounter_id, effective_datetime)` pair. This was achieved by grouping the data by these two columns and counting the distinct `loinc_code`s. The resulting distribution reveals what percentage of timestamps represent a "complete" set of all six vitals, versus "near-complete" or "sparse" sets.

*   **Systematic Missingness:** To understand if the missingness was random or systematic, we isolated the "near-complete" timestamps (those with exactly 5 of the 6 target vitals). For this cohort of timestamps, we identified which specific vital sign was absent by taking the set difference between the universal set of 6 required LOINC codes and the set of 5 present LOINC codes for each timestamp. The frequency of each missing vital was then aggregated to identify any systematic patterns.

## 2.6. Phase 2b Methods: Missingness Mechanism Analysis

Given the finding that body temperature accounts for 90% of missingness in near-complete timestamps, we conducted rigorous statistical testing to determine the underlying missingness mechanism. Understanding whether missingness is MCAR (Missing Completely at Random), MAR (Missing at Random), or MNAR (Missing Not at Random) is critical for determining appropriate handling strategies.

### 2.6.1. Little's MCAR Test (Chi-Square Approach)

We performed a Chi-square test of independence using a contingency table comparing temperature presence/absence against the presence of other vitals. Under MCAR, temperature missingness should be independent of other vital sign presence.

### 2.6.2. Missingness Correlation Matrix

We created a binary missingness indicator matrix (1 = present, 0 = absent) for each vital sign at each timestamp-encounter combination. Pearson correlation coefficients were computed between these indicators to assess whether vital signs tend to be missing together or independently.

### 2.6.3. Conditional Distribution Tests

To test whether vital sign values differ systematically when temperature is present versus absent, we performed:
*   **Two-sample T-tests:** Comparing mean values of each vital when temperature is present vs. absent
*   **Kolmogorov-Smirnov tests:** Comparing full distributions to detect any systematic differences

If vital values differ significantly when temperature is present vs. absent, this provides evidence against MAR and suggests MNAR.

### 2.6.4. Temporal Pattern Analysis

We analyzed temperature presence rates across day/night hours to identify whether missingness follows clinical workflow patterns (e.g., nursing shift schedules) rather than random occurrence.

## 2.7. Phase 3 Methods: Temporal and Sequential Characterization

The temporal nature of the data was investigated through two key metrics, computed separately for the 6-vital and 5-vital configurations:

*   **Temporal Irregularity:** To quantify the time gaps between measurements, we first filtered for timestamps that were "complete" (containing all required vitals). Within each patient encounter, we used the `LAG()` SQL window function, partitioned by `encounter_id` and ordered by `effective_datetime`, to compute the minute-level difference between each complete measurement and the one preceding it. The statistical distribution of these time deltas was then analyzed.

*   **Sequence Length Distribution:** The length of the observational sequence for each patient is a critical parameter for recurrent neural models. We calculated the sequence length by counting the number of distinct, complete timestamps for each unique `encounter_id`. The distribution of these lengths was then plotted and analyzed.

## 2.8. Phase 4 Methods: Comparative Analysis (6 vs 5 Vitals)

To quantify the impact of excluding temperature, we computed parallel analyses for both configurations:

| Metric | 6 Vitals (with Temp) | 5 Vitals (excl. Temp) |
|--------|----------------------|-----------------------|
| Complete timestamps | Requiring all 6 vitals | Requiring HR, RR, SpO2, SBP, DBP |
| Usable time deltas | Between 6-vital timestamps | Between 5-vital timestamps |
| Median time delta | Computed from 6-vital deltas | Computed from 5-vital deltas |
| Usable encounters | Encounters with ≥2 complete 6-vital timestamps | Encounters with ≥2 complete 5-vital timestamps |

This comparative framework enables direct quantification of the data quality improvement achievable by strategic vital sign selection.
