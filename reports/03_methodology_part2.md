## 2.4. Phase 1 Methods: Data Integrity and Value Distribution

To assess the integrity and distribution of the physiological measurements, each of the six vital signs was analyzed independently. We generated histograms and boxplots for the `value` column of each vital sign. This visual analysis aimed to:
1.  Identify and understand the range and central tendency of each measurement.
2.  Screen for significant outliers or physiologically implausible values (e.g., negative heart rates, extreme temperatures) that might indicate data entry errors.
3.  Examine the shape of the distribution (e.g., normal, skewed) for each vital sign.

Additionally, we performed a consistency check on the `unit` column for each `loinc_code` to ensure that all measurements for a given vital were recorded in a standard unit, preventing erroneous comparisons.

## 2.5. Phase 2 Methods: Sparsity and Missingness Analysis

The extent and pattern of missing data were quantified using two primary analyses:

*   **Timestamp Completeness:** We first determined the number of unique vitals recorded at every distinct `(encounter_id, effective_datetime)` pair. This was achieved by grouping the data by these two columns and counting the distinct `loinc_code`s. The resulting distribution reveals what percentage of timestamps represent a "complete" set of all six vitals, versus "near-complete" or "sparse" sets.

*   **Systematic Missingness:** To understand if the missingness was random or systematic, we isolated the "near-complete" timestamps (those with exactly 5 of the 6 target vitals). For this cohort of timestamps, we identified which specific vital sign was absent by taking the set difference between the universal set of 6 required LOINC codes and the set of 5 present LOINC codes for each timestamp. The frequency of each missing vital was then aggregated to identify any systematic patterns.

## 2.6. Phase 3 Methods: Temporal and Sequential Characterization

The temporal nature of the data was investigated through two key metrics:

*   **Temporal Irregularity:** To quantify the time gaps between measurements, we first filtered for timestamps that were "complete" (containing all 6 vitals), representing the best-case scenario for data capture. Within each patient encounter, we used the `LAG()` SQL window function, partitioned by `encounter_id` and ordered by `effective_datetime`, to compute the minute-level difference between each complete measurement and the one preceding it. The statistical distribution of these time deltas was then analyzed to characterize the regularity of data collection.

*   **Sequence Length Distribution:** The length of the observational sequence for each patient is a critical parameter for recurrent neural models. We calculated the sequence length by counting the number of distinct, complete timestamps for each unique `encounter_id`. The distribution of these lengths was then plotted and analyzed to determine the prevalence of short versus long observational windows in the dataset.
