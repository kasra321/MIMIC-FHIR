# 2. Methodology

## 2.1. Data Source and Cohort

This study utilizes the MIMIC-IV database (v2.2), a large, publicly available, de-identified dataset of patient data from the Beth Israel Deaconess Medical Center [3]. Our analysis focuses specifically on vital signs captured during patient stays in the Emergency Department, sourced from the `ed.vitalsign` table.

The primary cohort consists of all ED encounters containing at least two distinct timestamps with recorded vital sign observations. A minimum of two observations is required to enable temporal analysis, such as the calculation of time deltas between measurements. The vital signs selected for this study are six of the most frequently charted physiological parameters, identified by their LOINC (Logical Observation Identifiers Names and Codes) identifiers:

*   **Body Temperature** (`8310-5`)
*   **Heart Rate** (`8867-4`)
*   **Respiratory Rate** (`9279-1`)
*   **Oxygen Saturation** (`2708-6`)
*   **Systolic Blood Pressure** (`8480-6`)
*   **Diastolic Blood Pressure** (`8462-4`)

## 2.2. The Declarative Analysis Framework

To ensure the principles of transparency, reproducibility, and portability, we adopted a modern, declarative framework for this analysis. Instead of creating monolithic data-processing scripts that generate intermediate files, our approach interfaces directly with the source data in its Parquet file format.

The core of this framework is a "database-first" methodology utilizing DuckDB, an in-memory analytical database. Upon initiating an analysis session, a temporary in-memory database is created. The raw `vitalsign.parquet` data is not loaded or transformed in an imperative script; instead, it is registered as a SQL view within the database. All subsequent data cleaning, filtering, and aggregation steps are expressed as a series of layered SQL queries and views. This approach provides several key advantages:

*   **Reproducibility:** SQL queries provide a transparent, unambiguous, and universally understood definition of every data transformation.
*   **Portability:** The entire analysis depends only on the source data files and the analysis script, not on a complex environment of intermediate files or database servers.
*   **Separation of Concerns:** The raw source data remains immutable, cleanly separated from the logic used to analyze it.

Python's data science libraries, primarily `pandas` and `matplotlib`, were used for orchestrating the execution of these queries and for visualizing the final, aggregated results.

## 2.3. Study Phases

Our exploratory data analysis was structured into four thematic phases, designed to build a comprehensive understanding of the dataset from foundational integrity to complex temporal dynamics.

1.  **Phase 1: Data Integrity and Value Distribution:** Initial checks to validate the data's quality, consistency, and the plausibility of its physiological values.
2.  **Phase 2: Sparsity and Missingness Analysis:** A deep dive to quantify the extent and nature of missing data, a critical feature of all clinical datasets.
3.  **Phase 3: Temporal and Sequential Characterization:** An analysis of the time dimension, focusing on the frequency of measurements and the length of patient encounters.
4.  **Phase 4: Multivariate and Relational Analysis:** An exploration of the relationships between different vital signs (this phase is proposed in our discussion for future work).

The subsequent sections will detail the specific methods employed within each of these phases.
