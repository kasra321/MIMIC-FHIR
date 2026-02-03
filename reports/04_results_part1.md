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
