## 3.4. Comparative Analysis: 6 Vitals vs 5 Vitals

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

## 3.5. The Temporal Irregularity Problem: Comparative Analysis

While the data is often complete at any given timestamp, the time *between* these timestamps is highly inconsistent. We analyzed this separately for 6-vital and 5-vital configurations.

#### 3.5.1. Time Delta Distribution Comparison

| Percentile | 6 Vitals (min) | 5 Vitals (min) | Improvement |
|------------|----------------|----------------|-------------|
| 25th | 70 | 37 | **-47%** |
| 50th (Median) | **162** | **105** | **-35%** |
| 75th | 261 | 189 | -28% |
| 90th | 382 | 299 | -22% |

**Key Finding:** Excluding temperature reduces the median time gap from **162 minutes (2.7 hours) to 105 minutes (1.75 hours)**—a 35% improvement in temporal resolution.

#### 3.5.2. Temporal Dynamics Within Encounters

The pattern of time deltas within encounters differs between configurations:

**6 Vitals:** Measurements tend to **spread out** over time:
*   Early positions average: 206 min
*   Later positions average: 244 min
*   Trend: Increasing deltas (sparser measurements later in encounter)

**5 Vitals:** Measurements tend to **compress** over time:
*   Early positions average: 133 min
*   Later positions average: 34 min
*   Trend: Decreasing deltas (denser measurements later in encounter)

This reversal suggests that temperature's infrequent recording introduces artificial gaps early in encounters when continuous monitor vitals are already available.

## 3.6. The Short Sequence Problem: Comparative Analysis

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

#### 3.6.3. Impact of Excluding Temperature

Using 5 vitals increases:
*   Usable encounters (≥2 timestamps): from 367,432 to **386,789** (+5%)
*   Overall encounter usability: from 86.4% to **91.0%**

## 3.7. Summary: Impact of Excluding Temperature

| Metric | 6 Vitals | 5 Vitals | Impact |
|--------|----------|----------|--------|
| Complete timestamps | 1,260,313 | 1,731,513 | **+37%** |
| Usable time deltas | 843,575 | 1,312,375 | **+56%** |
| Median time delta | 162 min | 105 min | **-35%** |
| Usable encounters | 86.4% | 91.0% | **+5 pp** |

**Conclusion from Results:** Excluding temperature provides substantially more data with denser temporal coverage, without requiring imputation or introducing bias. This is justified by the MCAR test rejection and the systematic (non-random) nature of temperature missingness.
