# 1. Introduction

## 1.1. The Promise of High-Resolution EHR Data

The digital transformation of healthcare has rendered modern Electronic Health Records (EHR) into vast repositories of high-resolution clinical data. This data offers an unprecedented opportunity to move from reactive to proactive medicine, leveraging machine learning (ML) and artificial intelligence (AI) to forecast patient trajectories, identify risks, and personalize interventions [1]. Within this landscape, time-series data—such as sequential vital signs, lab results, and medication logs—are of particular interest. Models capable of processing this temporal information, such as Recurrent Neural Networks (RNNs) and their variants like Long Short-Term Memory (LSTM) and Gated Recurrent Unit (GRU) networks, hold the promise of capturing complex physiological dynamics to predict clinical outcomes with greater accuracy and timeliness [2].

## 1.2. The MIMIC-IV ED Dataset

The Emergency Department (ED) represents a uniquely data-rich and high-stakes clinical environment. It is the nexus of unscheduled care, where rapid decisions based on limited information can have profound impacts on patient outcomes. The MIMIC-IV (Medical Information Mart for Intensive Care) database, a cornerstone of open-access clinical research, includes a comprehensive module containing data from over 400,000 ED patient encounters [3, 4]. This subset, containing time-stamped vital signs, triage information, and clinical notes, presents a valuable resource for studying the earliest phases of critical care and developing models to predict outcomes like ICU admission or in-hospital mortality.

## 1.3. Initial Hypothesis and Study Objective

The initial hypothesis for this work was that the temporal density of the MIMIC-IV ED vital signs data would be sufficient for the application of granular time-series forecasting models. The goal was to build a model capable of predicting a patient's subsequent vital signs based on their recent physiological history, a foundational step for more advanced event prediction.

However, the application of complex models to raw clinical data without rigorous preliminary analysis is fraught with peril. The primary objective of this paper is therefore to conduct a comprehensive and reproducible Exploratory Data Analysis (EDA) to formally test this hypothesis. We aim to characterize the dataset's structural properties, focusing on the dimensions most critical to sequential modeling: data completeness, systematic missingness, temporal granularity, and sequence length. By doing so, we seek to provide a clear-eyed assessment of the dataset's true potential and limitations, moving beyond its apparent size to understand its functional utility.

A key secondary objective is to investigate whether strategic vital sign selection can improve data quality for temporal modeling. Specifically, we examine whether excluding body temperature—a vital sign with distinctly different recording patterns—can improve temporal resolution and data availability without sacrificing essential clinical information. This comparative analysis (5 vital signs vs. 6 vital signs) provides evidence-based guidance for preprocessing decisions in clinical ML pipelines.

## 1.4. A Modern Methodological Approach

A secondary contribution of this work is the demonstration of a modern analytical workflow. Rather than relying on monolithic, ad-hoc scripts, we adopted a declarative and portable pipeline for this EDA. By leveraging a database-first approach with modern tools capable of directly querying structured data files, our methodology ensures that the analysis is transparent, reproducible, and easily adaptable. This paper not only presents findings about the data but also serves as a case study in performing rigorous data characterization in a manner that aligns with modern principles of data engineering and scientific computing.

---
**References**

[1] Rajkomar, A., Dean, J., & Kohane, I. (2019). Machine Learning in Medicine. *The New England Journal of Medicine, 380*(14), 1347-1358.

[2] Choi, E., Bahadori, M. T., Schuetz, A., Stewart, W. F., & Sun, J. (2016). Doctor AI: Predicting Clinical Events via Recurrent Neural Networks. *JMLR Workshop and Conference Proceedings, 56*, 301-318.

[3] Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023). MIMIC-IV (version 2.2). *PhysioNet*. https://doi.org/10.13026/66pc-qs21.

[4] Johnson, A. E. W., et al. (2023). MIMIC-IV-ED: A comprehensive public EMR dataset for the emergency department. *Scientific Data*.
