## 4.5. Recommendations for Modeling

The insights gained from this EDA lead to a set of concrete recommendations for researchers and practitioners seeking to model the MIMIC-IV ED dataset. The choice of model should be deliberately guided by the data's inherent structure rather than by the allure of a specific algorithm.

### 4.5.1. Study Design Recommendation: Use 5 Vital Signs

**For initial LSTM exploratory analysis, we recommend excluding body temperature and using 5 vital signs:**
*   Heart Rate (HR)
*   Respiratory Rate (RR)
*   Oxygen Saturation (SpO2)
*   Systolic Blood Pressure (SBP)
*   Diastolic Blood Pressure (DBP)

This is justified by:
1.  Statistical evidence (MCAR rejected, p < 0.001)
2.  Clinical rationale (different measurement modalities)
3.  Substantial data quality improvements (+56% more data, -35% time delta)

### 4.5.2. For Time-Series Forecasting with 5 Vitals

**OPTION 1: Variable-Length Sequences (RECOMMENDED)**
*   Use natural timestamps without resampling
*   Include **time-since-last-measurement** as an explicit input feature
*   Use padding/masking for batching
*   Best preserves actual clinical timing and data integrity

**OPTION 2: Fixed Timestep with 2-3 Hour Intervals**
*   With 5 vitals, a 120-180 minute timestep covers the majority of natural intervals
*   Use forward-fill or interpolation for gaps
*   Balances coverage vs. granularity
*   Trade-off: Loss of temporal precision

**OPTION 3: Time-Aware Architectures**
*   Time-Aware LSTMs (T-LSTMs) [5] explicitly incorporate time gaps as model parameters
*   Allows the network to learn how to weight past information based on temporal distance
*   Preserves original data granularity but adds model complexity

### 4.5.3. Timestep Coverage Analysis (5 Vitals)

| Timestep | Coverage |
|----------|----------|
| 60 min | ~35% |
| 90 min | ~45% |
| 120 min | ~55% |
| 180 min | ~70% |

With 5 vitals, coverage at each timestep is higher than with 6 vitals because the median delta is shorter (105 min vs. 162 min).

### 4.5.4. Recommended Alternatives: State-Based and Feature-Based Models

Given the data's characteristics, we strongly recommend practitioners first consider models that align with the "state-transition" nature:

**1. Markov Models:**
*   Excellent fit for this data structure
*   Model probability of transitioning from one physiological state to another
*   Robust to irregular temporal sampling
*   States can be defined by clustering or simple physiological thresholds

**2. Feature-Based Classification:**
*   For prediction tasks (e.g., ICU admission), abandon sequential modeling
*   Engineer features from the entire encounter:
    *   Mean, median, min, max, std for each vital
    *   Slope of each vital (linear regression)
    *   Number of observations, encounter duration
*   Use classifiers like XGBoost, LightGBM, or Logistic Regression
*   Resilient to temporal irregularities; often a strong baseline

### 4.5.5. Data Filtering Recommendations

*   Filter encounters with <2 complete timestamps (unusable for sequences)
*   Consider minimum sequence length of **3** for meaningful temporal patterns
*   With 5 vitals, **91%** of encounters meet the ≥2 threshold

## 4.6. Improving the Data Analysis Pipeline

Finally, this study highlights the critical role of a structured and declarative EDA. We recommend that such an analysis should be a mandatory first step in any clinical machine learning project.

The declarative workflow used here—separating data (Parquet), transformation (SQL), and orchestration (Python)—can be further formalized using open-source tools like `dbt` (data build tool). Doing so would allow research teams to build robust, testable, and production-ready data pipelines that transform raw EHR data into analysis-ready datasets.

## 4.7. Limitations and Future Work

### 4.7.1. Limitations

*   Analysis focused on ED vital signs; patterns may differ in ICU or ward settings
*   Temperature exclusion may not be appropriate for fever-specific prediction tasks
*   Statistical tests assume large-sample asymptotics (met given dataset size)

### 4.7.2. Future Work

*   Validate 5-vital approach with actual LSTM model training and performance comparison
*   Investigate time-aware architectures (T-LSTM, attention-based models)
*   Extend missingness mechanism analysis to lab values and other clinical data
*   Develop automated preprocessing pipelines with configurable vital sign selection

---
**References**

[5] Baytas, I., Xiao, C., Zhang, X., Wang, F., Jain, A. K., & Zhou, J. (2017). Patient Subtyping via Time-Aware LSTM Networks. *Proceedings of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*.
