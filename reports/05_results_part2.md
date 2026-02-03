## 3.3. The Temporal Irregularity Problem

While the data is often complete at any given timestamp, the time *between* these timestamps is highly inconsistent. The analysis of time deltas between consecutive, complete sets of vital signs within each encounter revealed a significant challenge for standard time-series modeling.

The median time gap between valid observations was found to be **162 minutes (2.7 hours)**.

The distribution around this median is exceptionally wide, indicating a lack of any consistent measurement interval. The percentile distribution underscores this variability:
*   The 25th percentile of time deltas was **70 minutes**.
*   The 75th percentile was **261 minutes (4.35 hours)**.
*   The 90th percentile extended to **382 minutes (6.37 hours)**.

This confirms that the data is not sampled at or near a regular frequency. Instead, the timing of measurements appears to be driven by clinical need or workflow rather than a fixed monitoring schedule, posing a direct challenge to models that implicitly assume regular time steps. Further analysis into intra-encounter dynamics (Study 5a from the notebook) also revealed that this time delta tends to increase as the encounter progresses, meaning measurements are often more frequent at the beginning of a patient's stay and become sparser over time.

## 3.4. The Short Sequence Problem

In addition to the irregular sampling, the overall length of the observational sequences per encounter is typically short. For a model like an LSTM to learn complex temporal dependencies, it generally requires sequences of sufficient length.

Our analysis found that the mean number of complete vital sign observations per ED encounter is only **3.3**.

The distribution is heavily skewed towards very short sequences. A majority of encounters contain just two or three observation sets. While a long tail of encounters with many observations exists, they represent the exception rather than the norm. This finding suggests that for most encounters, there is insufficient sequential data to train a deep, recurrent model to learn long-term temporal patterns effectively.
