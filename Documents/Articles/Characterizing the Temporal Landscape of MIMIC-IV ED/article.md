# Characterizing the Temporal Landscape of MIMIC-IV ED: A Declarative Workflow for Assessing Vital Sign Data Quality and Modeling Potential

## Abstract

**Background:** The application of sequential deep learning models to Electronic Health Record (EHR) time-series data holds immense promise for predictive clinical analytics. The MIMIC-IV Emergency Department (ED) dataset offers a rich source of such data from the earliest stages of acute care. However, the effective application of these models is contingent upon a deep understanding of the data's underlying structural and temporal characteristics.

**Objective:** This study performs a comprehensive exploratory data analysis (EDA) of the MIMIC-IV ED vital signs data to assess its suitability for time-series forecasting and to characterize its broader modeling potential. We also demonstrate a modern, declarative workflow for conducting reproducible clinical data analysis. Additionally, we investigate whether strategic vital sign selection—specifically excluding body temperature—can improve temporal resolution and data quality.

**Methods:** We analyzed 10,996,821 vital sign measurements from 425,087 ED encounters in the MIMIC-IV database (v2.2). Using a reproducible, SQL-centric workflow, we quantified data completeness, patterns of missingness, temporal granularity, and observational sequence lengths. We conducted formal statistical testing (Chi-square, conditional distribution tests) to determine whether missingness patterns are random or systematic, and performed a comparative analysis evaluating the impact of excluding temperature from the vital sign set (5 vs 6 vitals).

**Results:** Our analysis revealed a dataset of contrasts. While individual measurement timestamps showed high completeness (93.3% contained ≥5 of 6 target vitals), we found a systematic pattern of missingness, with body temperature accounting for 90.1% of absent values in near-complete sets. Formal statistical testing (Chi-square = 97,562.66, p < 0.001) confirmed that temperature missingness is NOT Missing Completely at Random (MCAR), indicating systematic recording patterns. With all 6 vitals, the data shows severe temporal irregularity (median time delta: 162 minutes) and short sequences (mean: 3.3 per encounter). However, excluding temperature reduces the median time delta to 105 minutes (35% improvement) while increasing usable data points by 56% and complete timestamps by 37%.

**Conclusion:** The MIMIC-IV ED vital signs dataset, when requiring all 6 vitals, is not well-suited for standard recurrent neural network models. However, our analysis demonstrates that excluding temperature—justified by its systematic (not random) missingness pattern—substantially improves temporal resolution and data availability, making the dataset more amenable to sequential modeling. We recommend using 5 vital signs (HR, RR, SpO2, SBP, DBP) for initial LSTM exploratory analysis. The data should be conceptualized as a discrete sequence of states, and is highly valuable for alternative modeling paradigms such as Markov models or feature-based classifiers.

---

## 1. Introduction

### 1.1. The Promise of High-Resolution EHR Data

The digital transformation of healthcare has rendered modern Electronic Health Records (EHR) into vast repositories of high-resolution clinical data. This data offers an unprecedented opportunity to move from reactive to proactive medicine, leveraging machine learning (ML) and artificial intelligence (AI) to forecast patient trajectories, identify risks, and personalize interventions [1]. Within this landscape, time-series data—such as sequential vital signs, lab results, and medication logs—are of particular interest. Models capable of processing this temporal information, such as Recurrent Neural Networks (RNNs) and their variants like Long Short-Term Memory (LSTM) and Gated Recurrent Unit (GRU) networks, hold the promise of capturing complex physiological dynamics to predict clinical outcomes with greater accuracy and timeliness [2].

### 1.2. The MIMIC-IV ED Dataset

The Emergency Department (ED) represents a uniquely data-rich and high-stakes clinical environment. It is the nexus of unscheduled care, where rapid decisions based on limited information can have profound impacts on patient outcomes. The MIMIC-IV (Medical Information Mart for Intensive Care) database, a cornerstone of open-access clinical research, includes a comprehensive module containing data from over 400,000 ED patient encounters [3, 4]. This subset, containing time-stamped vital signs, triage information, and clinical notes, presents a valuable resource for studying the earliest phases of critical care and developing models to predict outcomes like ICU admission or in-hospital mortality.

### 1.3. Initial Hypothesis and Study Objective

The initial hypothesis for this work was that the temporal density of the MIMIC-IV ED vital signs data would be sufficient for the application of granular time-series forecasting models. The goal was to build a model capable of predicting a patient's subsequent vital signs based on their recent physiological history, a foundational step for more advanced event prediction.

However, the application of complex models to raw clinical data without rigorous preliminary analysis is fraught with peril. The primary objective of this paper is therefore to conduct a comprehensive and reproducible Exploratory Data Analysis (EDA) to formally test this hypothesis. We aim to characterize the dataset's structural properties, focusing on the dimensions most critical to sequential modeling: data completeness, systematic missingness, temporal granularity, and sequence length. By doing so, we seek to provide a clear-eyed assessment of the dataset's true potential and limitations, moving beyond its apparent size to understand its functional utility.

A key secondary objective is to investigate whether strategic vital sign selection can improve data quality for temporal modeling. Specifically, we examine whether excluding body temperature—a vital sign with distinctly different recording patterns—can improve temporal resolution and data availability without sacrificing essential clinical information. This comparative analysis (5 vital signs vs. 6 vital signs) provides evidence-based guidance for preprocessing decisions in clinical ML pipelines.

### 1.4. A Modern Methodological Approach

A secondary contribution of this work is the demonstration of a modern analytical workflow. Rather than relying on monolithic, ad-hoc scripts, we adopted a declarative and portable pipeline for this EDA. By leveraging a database-first approach with modern tools capable of directly querying structured data files, our methodology ensures that the analysis is transparent, reproducible, and easily adaptable. This paper not only presents findings about the data but also serves as a case study in performing rigorous data characterization in a manner that aligns with modern principles of data engineering and scientific computing.

---

## 2. Methodology

### 2.1. Data Source and Cohort

This study utilizes the MIMIC-IV database (v2.2), a large, publicly available, de-identified dataset of patient data from the Beth Israel Deaconess Medical Center [3]. Our analysis focuses specifically on vital signs captured during patient stays in the Emergency Department, sourced from the `ed.vitalsign` table.

The primary cohort consists of all ED encounters containing at least two distinct timestamps with recorded vital sign observations. A minimum of two observations is required to enable temporal analysis, such as the calculation of time deltas between measurements. The vital signs selected for this study are six of the most frequently charted physiological parameters, identified by their LOINC (Logical Observation Identifiers Names and Codes) identifiers:

* **Body Temperature** (`8310-5`)
* **Heart Rate** (`8867-4`)
* **Respiratory Rate** (`9279-1`)
* **Oxygen Saturation** (`2708-6`)
* **Systolic Blood Pressure** (`8480-6`)
* **Diastolic Blood Pressure** (`8462-4`)

### 2.2. The Declarative Analysis Framework

To ensure the principles of transparency, reproducibility, and portability, we adopted a modern, declarative framework for this analysis. Instead of creating monolithic data-processing scripts that generate intermediate files, our approach interfaces directly with the source data in its Parquet file format.

The core of this framework is a "database-first" methodology utilizing DuckDB, an in-memory analytical database. Upon initiating an analysis session, a temporary in-memory database is created. The raw `vitalsign.parquet` data is not loaded or transformed in an imperative script; instead, it is registered as a SQL view within the database. All subsequent data cleaning, filtering, and aggregation steps are expressed as a series of layered SQL queries and views. This approach provides several key advantages:

* **Reproducibility:** SQL queries provide a transparent, unambiguous, and universally understood definition of every data transformation.
* **Portability:** The entire analysis depends only on the source data files and the analysis script, not on a complex environment of intermediate files or database servers.
* **Separation of Concerns:** The raw source data remains immutable, cleanly separated from the logic used to analyze it.

Python's data science libraries, primarily `pandas` and `matplotlib`, were used for orchestrating the execution of these queries and for visualizing the final, aggregated results.

### 2.3. Study Phases

Our exploratory data analysis was structured into five thematic phases, designed to build a comprehensive understanding of the dataset from foundational integrity to complex temporal dynamics.

1. **Phase 1: Data Integrity and Value Distribution:** Initial checks to validate the data's quality, consistency, and the plausibility of its physiological values.
2. **Phase 2a: Sparsity and Missingness Analysis:** A deep dive to quantify the extent and nature of missing data, a critical feature of all clinical datasets.
3. **Phase 2b: Missingness Mechanism Analysis:** Statistical testing to determine whether missingness is Missing Completely at Random (MCAR), Missing at Random (MAR), or Missing Not at Random (MNAR).
4. **Phase 3: Temporal and Sequential Characterization:** An analysis of the time dimension, focusing on the frequency of measurements and the length of patient encounters, performed comparatively for 6-vital and 5-vital configurations.
5. **Phase 4: Comparative Analysis (6 vs 5 Vitals):** Direct comparison of data quality metrics when including vs. excluding body temperature from the vital sign set.

### 2.4. Phase 1 Methods: Data Integrity and Value Distribution

To assess the integrity and distribution of the physiological measurements, each of the six vital signs was analyzed independently. We generated histograms and boxplots for the `value` column of each vital sign. This visual analysis aimed to:

1. Identify and understand the range and central tendency of each measurement.
2. Screen for significant outliers or physiologically implausible values (e.g., negative heart rates, extreme temperatures) that might indicate data entry errors.
3. Examine the shape of the distribution (e.g., normal, skewed) for each vital sign.

Additionally, we performed a consistency check on the `unit` column for each `loinc_code` to ensure that all measurements for a given vital were recorded in a standard unit, preventing erroneous comparisons.

### 2.5. Phase 2a Methods: Sparsity and Missingness Analysis

The extent and pattern of missing data were quantified using two primary analyses:

* **Timestamp Completeness:** We first determined the number of unique vitals recorded at every distinct `(encounter_id, effective_datetime)` pair. This was achieved by grouping the data by these two columns and counting the distinct `loinc_code`s. The resulting distribution reveals what percentage of timestamps represent a "complete" set of all six vitals, versus "near-complete" or "sparse" sets.

* **Systematic Missingness:** To understand if the missingness was random or systematic, we isolated the "near-complete" timestamps (those with exactly 5 of the 6 target vitals). For this cohort of timestamps, we identified which specific vital sign was absent by taking the set difference between the universal set of 6 required LOINC codes and the set of 5 present LOINC codes for each timestamp. The frequency of each missing vital was then aggregated to identify any systematic patterns.

### 2.6. Phase 2b Methods: Missingness Mechanism Analysis

Given the finding that body temperature accounts for 90% of missingness in near-complete timestamps, we conducted rigorous statistical testing to determine the underlying missingness mechanism. Understanding whether missingness is MCAR (Missing Completely at Random), MAR (Missing at Random), or MNAR (Missing Not at Random) is critical for determining appropriate handling strategies.

#### 2.6.1. Little's MCAR Test (Chi-Square Approach)

We performed a Chi-square test of independence using a contingency table comparing temperature presence/absence against the presence of other vitals. Under MCAR, temperature missingness should be independent of other vital sign presence.

#### 2.6.2. Missingness Correlation Matrix

We created a binary missingness indicator matrix (1 = present, 0 = absent) for each vital sign at each timestamp-encounter combination. Pearson correlation coefficients were computed between these indicators to assess whether vital signs tend to be missing together or independently.

#### 2.6.3. Conditional Distribution Tests

To test whether vital sign values differ systematically when temperature is present versus absent, we performed:

* **Two-sample T-tests:** Comparing mean values of each vital when temperature is present vs. absent
* **Kolmogorov-Smirnov tests:** Comparing full distributions to detect any systematic differences

If vital values differ significantly when temperature is present vs. absent, this provides evidence against MAR and suggests MNAR.

#### 2.6.4. Temporal Pattern Analysis

We analyzed temperature presence rates across day/night hours to identify whether missingness follows clinical workflow patterns (e.g., nursing shift schedules) rather than random occurrence.

### 2.7. Phase 3 Methods: Temporal and Sequential Characterization

The temporal nature of the data was investigated through two key metrics, computed separately for the 6-vital and 5-vital configurations:

* **Temporal Irregularity:** To quantify the time gaps between measurements, we first filtered for timestamps that were "complete" (containing all required vitals). Within each patient encounter, we used the `LAG()` SQL window function, partitioned by `encounter_id` and ordered by `effective_datetime`, to compute the minute-level difference between each complete measurement and the one preceding it. The statistical distribution of these time deltas was then analyzed.

* **Sequence Length Distribution:** The length of the observational sequence for each patient is a critical parameter for recurrent neural models. We calculated the sequence length by counting the number of distinct, complete timestamps for each unique `encounter_id`. The distribution of these lengths was then plotted and analyzed.

### 2.8. Phase 4 Methods: Comparative Analysis (6 vs 5 Vitals)

To quantify the impact of excluding temperature, we computed parallel analyses for both configurations:

| Metric | 6 Vitals (with Temp) | 5 Vitals (excl. Temp) |
|--------|----------------------|-----------------------|
| Complete timestamps | Requiring all 6 vitals | Requiring HR, RR, SpO2, SBP, DBP |
| Usable time deltas | Between 6-vital timestamps | Between 5-vital timestamps |
| Median time delta | Computed from 6-vital deltas | Computed from 5-vital deltas |
| Usable encounters | Encounters with ≥2 complete 6-vital timestamps | Encounters with ≥2 complete 5-vital timestamps |

This comparative framework enables direct quantification of the data quality improvement achievable by strategic vital sign selection.

---

## 3. Results

### 3.1. Cohort and Data Profile

The study cohort was derived from the MIMIC-IV ED database, encompassing all emergency department encounters with at least two distinct vital sign observations. The resulting dataset is substantial, comprising **10,996,821** individual vital sign measurements across **425,087** unique patient encounters. These encounters belong to a population of **205,504** unique patients. The six targeted vital signs were present across the dataset, forming the basis for the subsequent analyses. Initial value distribution analysis confirmed that the measurements for each vital sign were within physiologically plausible ranges, and all units were consistent, requiring no further conversion.

### 3.2. The Data Sparsity Landscape

A primary objective of the analysis was to move beyond the high-level observation count and characterize the functional completeness of the data at the point of collection.

#### 3.2.1. High Prevalence of Complete and Near-Complete Timestamps

Our analysis of timestamp completeness yielded an encouraging result. We found that a significant majority of observation events contain a rich set of the target vitals. Specifically:

* **65.9%** of all unique timestamps within the cohort represent a "complete" measurement set, containing all 6 of the specified vital signs.
* An additional **27.4%** of timestamps are "near-complete," containing 5 of the 6 vitals.

Cumulatively, **93.3%** of all recorded timestamps provide a nearly complete physiological snapshot of the patient at that moment in time. Timestamps with four or fewer vitals account for less than 7% of the data, suggesting that when data is captured, it is generally captured comprehensively.

![Figure 1: Distribution of vitals recorded per timestamp. The majority of timestamps (65.9%) contain all 6 vital signs, with an additional 27.4% containing 5 vitals.](fig01_vitals_per_timestamp_distribution.png)

*Figure 1: Distribution of vitals recorded per timestamp, showing the high prevalence of complete measurement sets.*

#### 3.2.2. A Systematic Pattern of Missingness

While the overall completeness is high, the analysis of the "near-complete" timestamps revealed a highly systematic, rather than random, pattern of missingness. For the cohort of timestamps where exactly one vital sign was missing, our investigation found a single dominant factor:

* **Body Temperature (`LOINC: 8310-5`) accounted for 90.1% of the missing values.**

The next most frequently missing vital, Oxygen Saturation, accounted for only 8.2% of instances, with all other vitals being absent less than 2% of the time. This finding indicates that the absence of a body temperature measurement is not a random event but a structural feature of the data collection process in the ED.

![Figure 2: Breakdown of which vital sign is missing when 5 of 6 vitals are recorded. Temperature dominates at 90.1%.](fig02_missing_vital_breakdown.png)

*Figure 2: Most commonly missing vital sign in near-complete timestamps (5/6 recorded). Body temperature accounts for 90.1% of the missing values.*

### 3.3. Missingness Mechanism Analysis

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

![Figure 3: Missingness correlation matrix showing weak correlation between temperature missingness and other vitals.](fig03_missingness_correlation_matrix.png)

*Figure 3: Correlation matrix of missingness indicators. Temperature shows weak correlation with other vitals, which are highly inter-correlated.*

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

* Day hours (8am-6pm): **70.2%** presence
* Night hours (10pm-6am): **66.0%** presence
* Difference: 4.1 percentage points

This suggests temperature recording follows clinical workflow patterns (nursing schedules, spot-check protocols) rather than continuous monitoring.

![Figure 4: Temporal patterns of vital sign presence across hours of the day.](fig09_temporal_patterns_hour_of_day.png)

*Figure 4: Vital sign presence rates by hour of day, showing temporal patterns in recording behavior.*

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

### 3.4. Comparative Analysis: 6 Vitals vs 5 Vitals

Based on the missingness mechanism analysis, we evaluated the impact of excluding temperature from the vital sign set.

#### 3.4.1. Data Availability Comparison

| Metric | 6 Vitals (with Temp) | 5 Vitals (excl. Temp) | Improvement |
|--------|----------------------|-----------------------|-------------|
| Complete timestamps | 1,260,313 | 1,731,513 | **+37%** |
| Completeness rate | 65.9% | 90.6% | **+24.7 pp** |
| Usable time deltas | 843,575 | 1,312,375 | **+56%** |
| Encounters with >50% complete | 314,514 | 395,980 | +26% |
| Encounters with >80% complete | 211,025 | 342,843 | +62% |

**Key Finding:** Excluding temperature provides **471,200 additional complete timestamps** and **468,800 additional usable time deltas** for temporal analysis. This represents a substantial improvement in data availability without requiring imputation.

![Figure 5: Comparison of completeness metrics between 6-vital and 5-vital configurations.](fig08_completeness_comparison_5v_6v.png)

*Figure 5: Comparison of data completeness between configurations requiring 6 vitals vs. 5 vitals (excluding temperature).*

### 3.5. The Temporal Irregularity Problem: Comparative Analysis

While the data is often complete at any given timestamp, the time *between* these timestamps is highly inconsistent. We analyzed this separately for 6-vital and 5-vital configurations.

#### 3.5.1. Time Delta Distribution Comparison

| Percentile | 6 Vitals (min) | 5 Vitals (min) | Improvement |
|------------|----------------|----------------|-------------|
| 25th | 70 | 37 | **-47%** |
| 50th (Median) | **162** | **105** | **-35%** |
| 75th | 261 | 189 | -28% |
| 90th | 382 | 299 | -22% |

**Key Finding:** Excluding temperature reduces the median time gap from **162 minutes (2.7 hours) to 105 minutes (1.75 hours)**—a 35% improvement in temporal resolution.

![Figure 6: Distribution of time deltas between complete timestamps using 5 vitals (excluding temperature).](fig11_time_delta_distribution_5v.png)

*Figure 6: Distribution of time deltas between complete 5-vital timestamps. The median delta of 105 minutes represents a 35% improvement over the 6-vital configuration.*

#### 3.5.2. Temporal Dynamics Within Encounters

The pattern of time deltas within encounters differs between configurations:

**6 Vitals:** Measurements tend to **spread out** over time:
* Early positions average: 206 min
* Later positions average: 244 min
* Trend: Increasing deltas (sparser measurements later in encounter)

**5 Vitals:** Measurements tend to **compress** over time:
* Early positions average: 133 min
* Later positions average: 34 min
* Trend: Decreasing deltas (denser measurements later in encounter)

This reversal suggests that temperature's infrequent recording introduces artificial gaps early in encounters when continuous monitor vitals are already available.

![Figure 7: Average time delta by position within encounters.](fig12_avg_delta_by_position.png)

*Figure 7: Average time delta by observation position within encounters, showing how temporal patterns differ between configurations.*

### 3.6. The Short Sequence Problem: Comparative Analysis

#### 3.6.1. Sequence Length Metrics

| Metric | 6 Vitals | 5 Vitals | Improvement |
|--------|----------|----------|-------------|
| Unusable (0-1 timestamps) | 13.6% | **9.0%** | -4.6 pp |
| Usable (≥2 timestamps) | 86.4% | **91.0%** | +4.6 pp |
| Mean sequence length | 3.3 | ~4.5 | ~+36% |

#### 3.6.2. Sequence Length Distribution (6 Vitals)

| Sequence Length | Percentage of Encounters |
|-----------------|-------------------------|
| 0-1 (Unusable) | 13.6% |
| 2 | 31.8% |
| 3 | 27.2% |
| 4-5 | 20.5% |
| 6-10 | 6.5% |
| >10 | 0.5% |

With 6 vitals, the mean number of complete timestamps per encounter is only **3.3**, and nearly 60% of encounters have ≤3 observations. This limits the ability of sequential models to learn complex temporal patterns.

![Figure 8: Sequence length distribution using 5 vitals.](fig16_sequence_length_distribution_5v.png)

*Figure 8: Distribution of sequence lengths (complete timestamps per encounter) using 5 vitals. The 5-vital configuration provides longer sequences suitable for sequential modeling.*

#### 3.6.3. Impact of Excluding Temperature

Using 5 vitals increases:
* Usable encounters (≥2 timestamps): from 367,432 to **386,789** (+5%)
* Overall encounter usability: from 86.4% to **91.0%**

### 3.7. Summary: Impact of Excluding Temperature

| Metric | 6 Vitals | 5 Vitals | Impact |
|--------|----------|----------|--------|
| Complete timestamps | 1,260,313 | 1,731,513 | **+37%** |
| Usable time deltas | 843,575 | 1,312,375 | **+56%** |
| Median time delta | 162 min | 105 min | **-35%** |
| Usable encounters | 86.4% | 91.0% | **+5 pp** |

**Conclusion from Results:** Excluding temperature provides substantially more data with denser temporal coverage, without requiring imputation or introducing bias. This is justified by the MCAR test rejection and the systematic (non-random) nature of temperature missingness.

![Figure 9: Timestep coverage comparison between 6-vital and 5-vital configurations.](fig17_timestep_coverage_comparison.png)

*Figure 9: Comparison of timestep coverage at various fixed intervals, showing improved coverage with the 5-vital configuration.*

---

## 4. Discussion

The results of our exploratory analysis provide a multifaceted view of the MIMIC-IV ED vital signs dataset. While the data volume is impressive and individual measurements are often comprehensive, its structural and temporal characteristics present significant, nuanced challenges. This section interprets these findings, revisits our initial hypothesis, and reframes the dataset's potential for clinical machine learning.

### 4.1. The Initial Hypothesis Revisited: A Nuanced Conclusion

Our initial hypothesis was that the dataset's temporal density would be adequate for granular time-series forecasting using standard recurrent neural network architectures. The results of this EDA compel us to **partially revise** this hypothesis, with the outcome depending critically on vital sign selection.

#### 4.1.1. With 6 Vitals (Including Temperature): Unsuitability Confirmed

When requiring all 6 vital signs, two key findings violate the implicit assumptions of models like LSTMs and GRUs:

1. **Severe Temporal Irregularity:** Standard RNNs are designed for sequences where the data arrives at regular, discrete time steps. Our finding of a **162-minute median time delta**, with a wide and inconsistent distribution, fundamentally breaks this assumption. When fed such data directly, an RNN would treat the gap between a measurement taken 5 minutes ago and one taken 5 hours ago as equivalent, leading it to learn distorted and clinically meaningless temporal dependencies.

2. **Prevalence of Short Sequences:** The power of RNNs lies in their ability to capture long-term dependencies from sequential data. The finding that the mean sequence length is only **3.3 observations** suggests that the vast majority of encounters do not provide enough data for these models to learn meaningful patterns.

#### 4.1.2. With 5 Vitals (Excluding Temperature): Improved Feasibility

Excluding temperature substantially improves the data characteristics:

| Metric | 6 Vitals | 5 Vitals | Improvement |
|--------|----------|----------|-------------|
| Median time delta | 162 min | 105 min | -35% |
| Usable time deltas | 843,575 | 1,312,375 | +56% |
| Encounter usability | 86.4% | 91.0% | +4.6 pp |

While the data still has limitations for standard RNNs, the 5-vital configuration is **substantially more amenable to sequential modeling**, particularly with time-aware architectures or variable-length sequence approaches.

### 4.2. The Case for Excluding Temperature: Evidence Summary

The decision to exclude temperature is not arbitrary but is justified by rigorous statistical evidence:

#### 4.2.1. Statistical Evidence

1. **MCAR Test REJECTED (χ² = 97,562.66, p < 0.001):** Temperature missingness is NOT random—systematic factors determine when it is recorded.

2. **Weak Missingness Correlation (0.232):** Temperature missingness is only weakly correlated with other vitals' missingness. Other vitals are recorded together (high inter-correlation), but temperature follows a different schedule.

3. **Conditional Distribution Differences:** All 5 other vitals show statistically significant value differences when temperature is present vs. absent. This indicates the recording context affects both temperature and other vital values.

4. **Longer Median Time Delta for Temperature (145 min vs. 88-96 min):** Temperature is measured less frequently than vitals from continuous monitors.

#### 4.2.2. Clinical Rationale

* Temperature is typically measured **intermittently** (spot-check with thermometer)
* Other vitals often come from **continuous bedside monitors** (HR, SpO2, BP)
* Temperature is more stable; measured more frequently only when **clinically indicated** (e.g., suspected fever)
* Excluding temperature does NOT lose clinical signal—fever dynamics can be studied separately when temperature data is available

#### 4.2.3. Data Quality Impact

Excluding temperature provides:
* **+37%** more complete timestamps
* **+56%** more usable time deltas
* **-35%** reduction in median time gap
* **+4.6 pp** increase in usable encounters

### 4.3. Reframing the Dataset's Potential: State Transitions vs. Time-Series

This conclusion should not be mistaken for a declaration that the dataset lacks value. Instead, our findings guide us toward a more appropriate conceptualization of the data.

Rather than viewing it as a *continuous-time signal* that has been irregularly sampled, it is more productively viewed as a **discrete sequence of multi-dimensional states**.

In this paradigm, the object of interest is not the precise time between measurements, but the evolution of the patient's physiological state from one observation to the next. Each "state" is a rich vector of vital signs. The value of the dataset, then, lies in its ability to model the probability of transitioning from one state to another (e.g., from a stable state to a tachycardic, hypotensive state).

### 4.4. Implications of Systematic Missingness

The discovery that body temperature is systematically absent (MCAR rejected) has direct modeling implications:

1. **Naive imputation is dangerous.** Simply filling missing temperature values with the mean or the last observed value would ignore the clinical context and could introduce significant bias.

2. **Missingness itself is informative.** The absence of a temperature reading could be a powerful predictive feature, signifying a likely non-febrile, lower-acuity patient.

3. **Excluding is preferable to imputing.** Given the systematic (not random) missingness pattern, excluding temperature for initial LSTM analysis is statistically more defensible than imputation.

### 4.5. Recommendations for Modeling

The insights gained from this EDA lead to a set of concrete recommendations for researchers and practitioners seeking to model the MIMIC-IV ED dataset. The choice of model should be deliberately guided by the data's inherent structure rather than by the allure of a specific algorithm.

#### 4.5.1. Study Design Recommendation: Use 5 Vital Signs

**For initial LSTM exploratory analysis, we recommend excluding body temperature and using 5 vital signs:**
* Heart Rate (HR)
* Respiratory Rate (RR)
* Oxygen Saturation (SpO2)
* Systolic Blood Pressure (SBP)
* Diastolic Blood Pressure (DBP)

This is justified by:
1. Statistical evidence (MCAR rejected, p < 0.001)
2. Clinical rationale (different measurement modalities)
3. Substantial data quality improvements (+56% more data, -35% time delta)

#### 4.5.2. For Time-Series Forecasting with 5 Vitals

**OPTION 1: Variable-Length Sequences (RECOMMENDED)**
* Use natural timestamps without resampling
* Include **time-since-last-measurement** as an explicit input feature
* Use padding/masking for batching
* Best preserves actual clinical timing and data integrity

**OPTION 2: Fixed Timestep with 2-3 Hour Intervals**
* With 5 vitals, a 120-180 minute timestep covers the majority of natural intervals
* Use forward-fill or interpolation for gaps
* Balances coverage vs. granularity
* Trade-off: Loss of temporal precision

**OPTION 3: Time-Aware Architectures**
* Time-Aware LSTMs (T-LSTMs) [5] explicitly incorporate time gaps as model parameters
* Allows the network to learn how to weight past information based on temporal distance
* Preserves original data granularity but adds model complexity

#### 4.5.3. Timestep Coverage Analysis (5 Vitals)

| Timestep | Coverage |
|----------|----------|
| 60 min | ~35% |
| 90 min | ~45% |
| 120 min | ~55% |
| 180 min | ~70% |

With 5 vitals, coverage at each timestep is higher than with 6 vitals because the median delta is shorter (105 min vs. 162 min).

#### 4.5.4. Recommended Alternatives: State-Based and Feature-Based Models

Given the data's characteristics, we strongly recommend practitioners first consider models that align with the "state-transition" nature:

**1. Markov Models:**
* Excellent fit for this data structure
* Model probability of transitioning from one physiological state to another
* Robust to irregular temporal sampling
* States can be defined by clustering or simple physiological thresholds

**2. Feature-Based Classification:**
* For prediction tasks (e.g., ICU admission), abandon sequential modeling
* Engineer features from the entire encounter:
  * Mean, median, min, max, std for each vital
  * Slope of each vital (linear regression)
  * Number of observations, encounter duration
* Use classifiers like XGBoost, LightGBM, or Logistic Regression
* Resilient to temporal irregularities; often a strong baseline

#### 4.5.5. Data Filtering Recommendations

* Filter encounters with <2 complete timestamps (unusable for sequences)
* Consider minimum sequence length of **3** for meaningful temporal patterns
* With 5 vitals, **91%** of encounters meet the ≥2 threshold

### 4.6. Improving the Data Analysis Pipeline

Finally, this study highlights the critical role of a structured and declarative EDA. We recommend that such an analysis should be a mandatory first step in any clinical machine learning project.

The declarative workflow used here—separating data (Parquet), transformation (SQL), and orchestration (Python)—can be further formalized using open-source tools like `dbt` (data build tool). Doing so would allow research teams to build robust, testable, and production-ready data pipelines that transform raw EHR data into analysis-ready datasets.

### 4.7. Limitations and Future Work

#### 4.7.1. Limitations

* Analysis focused on ED vital signs; patterns may differ in ICU or ward settings
* Temperature exclusion may not be appropriate for fever-specific prediction tasks
* Statistical tests assume large-sample asymptotics (met given dataset size)

#### 4.7.2. Future Work

* Validate 5-vital approach with actual LSTM model training and performance comparison
* Investigate time-aware architectures (T-LSTM, attention-based models)
* Extend missingness mechanism analysis to lab values and other clinical data
* Develop automated preprocessing pipelines with configurable vital sign selection

---

## 5. Conclusion

### 5.1. Summary of Contributions

This paper presented a comprehensive exploratory data analysis of the vital signs data from the MIMIC-IV Emergency Department module. Our contributions are threefold:

#### 5.1.1. Primary Contribution: Data Quality Characterization

We rigorously characterized this dataset's fitness for machine learning applications, demonstrating that:
* Individual timestamps are often rich with complete physiological measurements
* Severe temporal irregularity exists (median interval: 162 min with 6 vitals, 105 min with 5 vitals)
* Short observational sequences predominate (mean: 3.3 events per encounter with 6 vitals)
* Body temperature exhibits systematic (not random) missingness patterns

#### 5.1.2. Key Contribution: Evidence-Based Vital Sign Selection

We demonstrated that **strategic vital sign selection—specifically excluding body temperature—substantially improves data quality** for sequential modeling:

| Metric | 6 Vitals | 5 Vitals | Impact |
|--------|----------|----------|--------|
| Complete timestamps | 1,260,313 | 1,731,513 | **+37%** |
| Usable time deltas | 843,575 | 1,312,375 | **+56%** |
| Median time delta | 162 min | 105 min | **-35%** |
| Usable encounters | 86.4% | 91.0% | **+5 pp** |

This decision is justified by formal statistical testing:
* **MCAR Test REJECTED** (χ² = 97,562.66, p < 0.001)
* Temperature missingness is systematic, not random
* Excluding is statistically more defensible than imputation

#### 5.1.3. Secondary Contribution: Methodological Framework

This work serves as a case study for a modern, declarative approach to clinical data analysis. By prioritizing a database-first, SQL-centric workflow, we produced an analysis that is transparent, reproducible, and portable.

### 5.2. Study Design Recommendation

**For initial LSTM exploratory analysis on MIMIC-IV ED vital signs, use 5 vital signs:**
* Heart Rate (HR)
* Respiratory Rate (RR)
* Oxygen Saturation (SpO2)
* Systolic Blood Pressure (SBP)
* Diastolic Blood Pressure (DBP)

**Exclude body temperature** based on:
1. MCAR hypothesis rejected (p < 0.001)
2. Clinical rationale (different measurement modalities)
3. Substantial data quality improvements

### 5.3. Final Takeaway

The central thesis of this paper is that **rigorous, context-aware EDA is an indispensable prerequisite to successful clinical modeling**.

The MIMIC-IV ED vital signs dataset is not a "plug-and-play" resource for time-series forecasting with standard RNNs—but this framing misses the point. Our analysis transforms what appeared to be a data quality problem (temperature missingness) into a principled study design decision. By demonstrating that temperature missingness is systematic rather than random, we provide evidence-based justification for a preprocessing choice that dramatically improves data availability.

### 5.4. Broader Perspective

In the current era of data-centric AI, there is a temptation to apply ever-more-complex models to ever-larger datasets. Yet, as this study demonstrates, the true value of clinical data lies not in its sheer volume but in its nuanced structure and the context of its collection.

The "digital exhaust" from our healthcare systems is not a clean, continuous signal but a messy, event-driven, and human-mediated record. Understanding why data looks the way it does—why temperature is measured less frequently than heart rate, why some encounters have dense monitoring while others have sparse—is essential for making principled modeling decisions.

The ultimate lesson from this analysis is a reinforcement of a foundational principle: **know thy data**. Before complex models are built, before computational resources are expended, a deep and honest appraisal of the data's character must be conducted. Only then can we build tools that are not just technically sophisticated but are also robust, reliable, and truly aligned with the clinical reality they seek to model.

### 5.5. Executive Summary Table

| Question | Finding |
|----------|---------|
| Is temperature missingness random? | **No** (MCAR rejected, p < 0.001) |
| Should we exclude temperature? | **Yes** for initial LSTM analysis |
| How much data do we gain? | **+37%** complete timestamps, **+56%** time deltas |
| How much does temporal resolution improve? | **35%** (162 min → 105 min median) |
| What approach should we use? | Variable-length sequences with time-since-last-measurement feature |

---

**The path forward is clear: use 5 vital signs, embrace the data's event-driven nature, and let rigorous EDA guide model selection.**

---

## References

[1] Rajkomar, A., Dean, J., & Kohane, I. (2019). Machine Learning in Medicine. *The New England Journal of Medicine, 380*(14), 1347-1358.

[2] Choi, E., Bahadori, M. T., Schuetz, A., Stewart, W. F., & Sun, J. (2016). Doctor AI: Predicting Clinical Events via Recurrent Neural Networks. *JMLR Workshop and Conference Proceedings, 56*, 301-318.

[3] Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023). MIMIC-IV (version 2.2). *PhysioNet*. https://doi.org/10.13026/66pc-qs21.

[4] Johnson, A. E. W., et al. (2023). MIMIC-IV-ED: A comprehensive public EMR dataset for the emergency department. *Scientific Data*.

[5] Baytas, I., Xiao, C., Zhang, X., Wang, F., Jain, A. K., & Zhou, J. (2017). Patient Subtyping via Time-Aware LSTM Networks. *Proceedings of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*.
