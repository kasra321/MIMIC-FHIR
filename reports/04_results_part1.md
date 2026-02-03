# 3. Results

## 3.1. Cohort and Data Profile

The study cohort was derived from the MIMIC-IV ED database, encompassing all emergency department encounters with at least two distinct vital sign observations. The resulting dataset is substantial, comprising **10,996,821** individual vital sign measurements across **425,087** unique patient encounters. These encounters belong to a population of **205,504** unique patients. The six targeted vital signs were present across the dataset, forming the basis for the subsequent analyses. Initial value distribution analysis confirmed that the measurements for each vital sign were within physiologically plausible ranges, and all units were consistent, requiring no further conversion.

## 3.2. The Data Sparsity Landscape

A primary objective of the analysis was to move beyond the high-level observation count and characterize the functional completeness of the data at the point of collection.

#### 3.2.1. High Prevalence of Complete and Near-Complete Timestamps

Our analysis of timestamp completeness yielded an encouraging result. We found that a significant majority of observation events contain a rich set of the target vitals. Specifically:

*   **65.9%** of all unique timestamps within the cohort represent a "complete" measurement set, containing all 6 of the specified vital signs.
*   An additional **27.4%** of timestamps are "near-complete," containing 5 of the 6 vitals.

Cumulatively, **93.3%** of all recorded timestamps provide a nearly complete physiological snapshot of the patient at that moment in time. Timestamps with four or fewer vitals account for less than 7% of the data, suggesting that when data is captured, it is generally captured comprehensively.

#### 3.2.2. A Systematic Pattern of Missingness

While the overall completeness is high, the analysis of the "near-complete" timestamps revealed a highly systematic, rather than random, pattern of missingness. For the cohort of timestamps where exactly one vital sign was missing, our investigation found a single dominant factor:

*   **Body Temperature (`LOINC: 8310-5`) accounted for 90.1% of the missing values.**

The next most frequently missing vital, Oxygen Saturation, accounted for only 8.2% of instances, with all other vitals being absent less than 2% of the time. This finding indicates that the absence of a body temperature measurement is not a random event but a structural feature of the data collection process in the ED.

## 3.3. Missingness Mechanism Analysis

Given the finding that body temperature dominates missingness, we conducted formal statistical testing to characterize the mechanism.

#### 3.3.1. Individual Vital Sign Missingness Rates

| Vital Sign | Missingness Rate |
|------------|------------------|
| Body Temperature | 30.6% |
| Oxygen Saturation | 8.0% |
| Respiratory Rate | 5.6% |
| Heart Rate | 4.4% |
| Systolic BP | 0.0% |
| Diastolic BP | 0.0% |

Temperature's 30.6% missingness rate is dramatically higher than other vitals, with blood pressure showing perfect recording consistency.

#### 3.3.2. MCAR Test Results (Chi-Square)

| Metric | Value |
|--------|-------|
| Chi-square statistic | **97,562.66** |
| Degrees of freedom | 1 |
| P-value | **< 0.001** |
| **Conclusion** | **REJECT MCAR** |

**Interpretation:** The extremely low p-value (effectively zero) provides overwhelming statistical evidence that temperature missingness is NOT Missing Completely at Random. Systematic factors determine when temperature is recorded.

#### 3.3.3. Missingness Correlation Analysis

The correlation between temperature missingness and other vitals' missingness indicators was notably **weak (average correlation: 0.232)**. In contrast, other vitals (HR, RR, SpO2) showed **high inter-correlation**, indicating they are typically recorded together as part of the same measurement event. Temperature follows a different recording schedule.

#### 3.3.4. Conditional Distribution Tests

We compared vital value distributions when temperature was present vs. absent:

| Vital Sign | T-test Result | Interpretation |
|------------|---------------|----------------|
| Heart Rate | p < 0.05 | **Significant difference** |
| Respiratory Rate | p < 0.05 | **Significant difference** |
| Oxygen Saturation | p < 0.05 | **Significant difference** |
| Systolic BP | p < 0.05 | **Significant difference** |
| Diastolic BP | p < 0.05 | **Significant difference** |

**All 5 vitals showed statistically significant distribution differences** when temperature was present vs. absent. This provides strong evidence that temperature missingness is NOT Missing at Random (MAR)—the missing mechanism likely depends on unobserved factors (e.g., clinical indication, patient acuity).

#### 3.3.5. Temporal Patterns

Temperature presence rates showed modest but consistent patterns:
*   Day hours (8am-6pm): **70.2%** presence
*   Night hours (10pm-6am): **66.0%** presence
*   Difference: 4.1 percentage points

This suggests temperature recording follows clinical workflow patterns (nursing schedules, spot-check protocols) rather than continuous monitoring.

#### 3.3.6. Median Time Delta Per Vital Sign

| Vital Sign | Median Time Delta |
|------------|-------------------|
| Body Temperature | **145 min** |
| Heart Rate | 94 min |
| Respiratory Rate | 96 min |
| Oxygen Saturation | 95 min |
| Systolic BP | 88 min |
| Diastolic BP | 88 min |

Temperature has the longest median time delta (145 min vs. 88-96 min for other vitals), confirming it is measured less frequently—consistent with spot-check protocols vs. continuous bedside monitors.
