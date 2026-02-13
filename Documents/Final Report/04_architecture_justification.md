# Architectural Justification: A Local-First FHIR Analytics Platform for Clinical Research

**Author:** Kasra  
**Program:** MS Applied Data Science, University of Michigan  
**Project:** MIMIC-FHIR Analytics Platform
**Date**: 02/12/2026

---

## Abstract

This document provides technical and methodological justification for the architectural decisions underlying the MIMIC-FHIR analytics platform. The platform implements a medallion architecture (Bronze-Silver-Gold) using DuckDB as the execution engine and SQLMesh as the transformation orchestrator, with FHIR resource structures serving as the bronze layer contract. We argue that this design optimally balances research reproducibility, data governance requirements, computational efficiency, and extensibility for observational health research conducted within academic medical centers. The architecture prioritizes local-first execution while maintaining clear migration paths to distributed systems if scale requirements change.

---

## 1. Introduction

Clinical informatics research increasingly relies on secondary analysis of electronic health record (EHR) data to generate insights for precision medicine, predictive modeling, and health services research. However, the heterogeneity of EHR systems, the complexity of healthcare data models, and stringent data governance requirements create significant technical barriers to reproducible research. This project addresses these challenges through deliberate architectural choices that optimize for the realistic constraints of academic health research environments.

The core design question animating this architecture is: **How can we build a reusable, reproducible analytical pipeline that works across diverse health datasets while respecting institutional data governance boundaries?** The answer lies in three key architectural decisions: (1) adopting FHIR as a standardized bronze layer contract, (2) selecting DuckDB for local-first analytical execution, and (3) using SQLMesh for declarative transformation orchestration. Each decision is justified below.

---

## 2. FHIR as the Bronze Layer Contract

### 2.1. The Interoperability Challenge

Healthcare data exists in myriad formats: proprietary vendor schemas (Epic Clarity, Cerner Millennium), research-specific exports (OMOP CDM, i2b2), and raw HL7v2 messages. Each format requires bespoke extraction logic, creating brittle pipelines where the bronze ingestion adapter becomes tightly coupled to downstream transformations. Changing data sources—a common requirement in multi-site studies or longitudinal research programs—necessitates rewriting not just the adapter but often the entire analytical codebase.

### 2.2. FHIR as a Canonical Intermediate Representation

Fast Healthcare Interoperability Resources (FHIR) provides a standardized, resource-oriented data model with well-defined semantics. By establishing `bronze.fhir_resources` as the pipeline's contract table—where each row contains a complete FHIR resource as JSON alongside extracted metadata (`resource_type`, `resource_id`, `source_file`)—we create a **source-agnostic boundary**. Downstream transformations (Silver and Gold layers) query this contract table without knowledge of whether the source was MIMIC-IV on FHIR, Synthea synthetic data, or a hospital's Epic FHIR endpoint.

```
Adapter Boundary:
MIMIC NDJSON → adapters/mimic/load_bronze.py → bronze.fhir_resources
Synthea NDJSON → adapters/synthea/load_bronze.py → bronze.fhir_resources
Epic FHIR API → adapters/epic/load_bronze.py → bronze.fhir_resources
                                                        ↓
                                    [Identical Silver/Gold pipeline]
```

This design follows the **adapter pattern** from software engineering, isolating variability (data source specifics) from invariants (analytical logic).

### 2.3. Acknowledging FHIR Conformance Requirements

A critical limitation must be acknowledged: **FHIR conformance is not automatic**. Not all health datasets arrive in FHIR format. MIMIC-IV and Synthea provide native FHIR exports, but datasets like eICU, CPRD, or institutional EHR extracts often use proprietary schemas. Integrating such sources requires an upfront **conformance mapping** step—translating source-specific data structures into valid FHIR resources according to appropriate Implementation Guides (e.g., US Core).

This is a **deliberate trade-off**. The initial cost of FHIR conformance is offset by:
1. **Reusability**: The same Silver/Gold SQL runs across all conformant datasets
2. **Semantic clarity**: FHIR's standardized vocabularies (LOINC, SNOMED, RxNorm) reduce ambiguity
3. **Tooling ecosystem**: Libraries like HAPI FHIR, FlatQuack, and SQL-on-FHIR enable validation and transformation

We accept manual conformance verification as a **one-time upfront cost** that yields long-term analytical leverage. For datasets requiring extensive transformation (e.g., eICU), this may involve writing custom ETL scripts using tools like HAPI FHIR or Bunsen to produce conformant NDJSON files before ingestion.

---

## 3. DuckDB: The Case for Local-First Analytical Execution

### 3.1. The Cloud-Native Orthodoxy and Its Limitations

Contemporary data engineering discourse often assumes cloud data warehouses (Snowflake, BigQuery, Redshift) are the default choice for analytical workloads. While appropriate for enterprise SaaS applications with petabyte-scale data and high concurrency requirements, this paradigm introduces friction for academic health research:

- **Data governance barriers**: IRB protocols and HIPAA compliance often prohibit uploading identified patient data to third-party cloud infrastructure
- **Economic inefficiency**: Exploratory research workloads incur compute costs ($50-500 per pipeline run) without guaranteed ROI
- **Reproducibility challenges**: External reviewers cannot easily replicate analyses requiring cloud accounts and data egress fees
- **Institutional IT approval delays**: VPC peering, PrivateLink configuration, and security audits extend timelines by months

### 3.2. DuckDB's Performance Envelope

DuckDB is an embedded, columnar analytical database optimized for OLAP workloads on single-node systems. Its vectorized execution engine achieves performance competitive with distributed systems for datasets under ~10TB. Critically, **most observational health research operates well below this threshold**:

| Dataset | Approximate Size | Typical Research Cohort |
|---------|-----------------|------------------------|
| MIMIC-IV (complete) | 100-150 GB compressed | 50,000-80,000 patients |
| UK Biobank | 200-300 GB | 500,000 participants |
| All of Us (wave 1) | 500 GB - 1 TB | 250,000 participants |
| Synthea (100K patients) | 5-10 GB | 100,000 synthetic patients |

DuckDB can perform full-table scans across MIMIC-IV's ~500 million observations in under 5 minutes on a consumer-grade M1 MacBook Air (8GB RAM). Aggregation queries with complex window functions execute in seconds. **The vertical scaling ceiling of commodity hardware exceeds the data volume of the vast majority of clinical research projects.**

### 3.3. The Local-First Advantage

Local execution provides several non-obvious benefits:

**Data Locality and Governance**: Processing occurs entirely within institutional secure enclaves. No patient data leaves the hospital network, simplifying IRB approvals and HIPAA attestations.

**Reproducibility**: The entire analytical environment—data, code, and execution engine—packages into a single Docker container and DuckDB file (~100GB). Collaborators execute `docker run` to reproduce results bitwise-identically without cloud account provisioning.

**Cost Structure**: Zero marginal compute costs for exploratory analysis. Researchers iterate freely without budget anxiety. A single high-memory EC2 instance ($200/month) can support dozens of concurrent users querying shared DuckDB databases.

**Development Velocity**: No network latency, no authentication tokens expiring mid-query, no quota limits. The tight feedback loop (edit SQL → re-run → examine results in <30 seconds) accelerates iterative analysis.

### 3.4. Migration Path to Distributed Systems

Importantly, **local-first does not preclude cloud deployment**. DuckDB's SQL dialect is PostgreSQL-compatible, and SQLMesh abstracts the execution backend. Should scale requirements grow—e.g., expanding to multi-site federated analyses with billions of records—the transformation logic in `models/` transfers to Snowflake, BigQuery, or Databricks with minimal modification (primarily changing `config.yaml` and addressing vendor-specific SQL dialect differences like window function syntax or JSON extraction functions). The adapter pattern ensures data ingestion logic remains modular.

The architecture optimizes for **the common case** (institutional-scale research) while preserving **optionality** for the exceptional case (population-scale deployment).

---

## 4. SQLMesh: Declarative Transformation Orchestration

### 4.1. The Problem with Imperative Pipelines

Traditional data pipelines in health research often consist of ad hoc Python scripts or Jupyter notebooks containing SQL strings, pandas operations, and file I/O. This approach creates several maintainability pathologies:

- **Implicit dependencies**: No declared lineage between datasets; failures cascade unpredictably
- **No versioning**: Changing a transformation breaks downstream analyses with no rollback mechanism
- **Testing debt**: Validating correctness requires manual re-execution of entire notebooks
- **No incremental computation**: Full recomputation even when only a small subset of data changed

### 4.2. SQLMesh's Declarative Model

SQLMesh addresses these issues through **declarative transformation definitions**. Each model specifies:

```sql
MODEL (
  name marts.eda_vitals,
  kind FULL,
  grain [encounter_id, patient_id, effective_datetime]
);

SELECT ...
FROM intermediate.vitals_wide
```

The `MODEL` block explicitly declares dependencies (`FROM intermediate.vitals_wide`), granularity guarantees (`grain`), and materialization strategy (`kind FULL`). SQLMesh constructs a directed acyclic graph (DAG) of transformations, enabling:

- **Automated lineage tracking**: `sqlmesh dag` visualizes data flow
- **Impact analysis**: Changes to upstream models automatically trigger downstream rebuilds
- **Testing framework**: `sqlmesh test` validates transformations against fixture data
- **Environment isolation**: `sqlmesh plan` previews changes before applying to production tables

### 4.3. Separation of Staging and Modeling

A key architectural decision is the explicit split between **Silver (staging)** and **Gold (modeling)** layers, implemented through different technologies:

**Silver Layer** (pipeline/build_silver/):
- Hand-written SQL files executed via `apply_views.py`
- Performs FHIR resource extraction and flattening
- Example: Parsing nested JSON in `Observation.valueQuantity` into columnar `value` and `unit`

**Gold Layer** (models/):
- SQLMesh-managed transformations
- Builds analytical denormalizations, feature engineering, and aggregations
- Example: Pivoting long-format vitals into wide format with temporal features

This separation enables **modular development**:
- Data engineers focus on Silver (optimizing FHIR extraction)
- Analysts focus on Gold (domain-specific feature engineering)
- Changes to Silver views trigger automatic Gold rebuilds via SQLMesh's dependency graph

Different development teams or "pods" can work in parallel—one pod improving vital sign extraction logic in `create_silver_observation_vitals.sql`, another pod developing medication exposure features in `models/marts/medication_timeline.sql`—without coordination overhead.

### 4.4. External Models and Source-Agnostic Pipelines

SQLMesh's `external_models.yaml` declares Silver tables as **external dependencies**:

```yaml
- name: silver.observation_vitals
  columns:
    resource_id: varchar
    patient_id: varchar
    effective_datetime: timestamp
    loinc_code: varchar
    value: double
```

This contract ensures Gold models can reference Silver tables without managing their creation. As long as an adapter produces conformant `bronze.fhir_resources` and the Silver SQL correctly extracts fields, Gold models execute unchanged. This is how a single Gold layer can consume MIMIC-IV, Synthea, or Epic data interchangeably.

---

## 5. Architectural Trade-offs and Design Constraints

### 5.1. Accepted Limitations

This architecture is optimized for **offline batch analytics**, not real-time stream processing. It assumes:
- Data arrives in bulk exports (daily/weekly FHIR bundles), not live event streams
- Query latency measured in seconds/minutes is acceptable (not milliseconds)
- Single-node vertical scaling suffices (datasets < 10TB)

These assumptions hold for >90% of observational health research but exclude use cases like:
- Real-time clinical decision support systems
- Continuous patient monitoring dashboards
- Population-health surveillance with sub-hourly updates

For such applications, alternative architectures (e.g., Kafka + Flink + Cassandra) are more appropriate.

### 5.2. When to Migrate Beyond This Architecture

Clear signals that scale requirements exceed DuckDB's capacity:
- Dataset size approaching 10TB
- Query execution times exceeding 10 minutes for routine aggregations
- Need for horizontal scaling across multiple compute nodes
- Requirement for sub-second query latency (BI tool responsiveness)
- Multi-tenant SaaS deployment with strict tenant isolation

At this inflection point, the migration path is:
1. Replace DuckDB connection in `models/config.yaml` with Snowflake/BigQuery
2. Adapt SQL dialect (e.g., `json_extract_string()` → `JSON_EXTRACT()`)
3. Implement schema-per-tenant strategy for multi-tenancy
4. Add API layer (FastAPI) with OAuth2 for authentication

Estimated effort: 4-6 weeks for an experienced data engineer, leveraging the existing SQLMesh models as-is.

---

## 6. Conclusion

The MIMIC-FHIR analytics platform architecture represents a **pragmatic synthesis** of modern data engineering patterns and the specific constraints of clinical informatics research. By standardizing on FHIR as the bronze layer contract, we enable source-agnostic pipelines that adapt to diverse health datasets with minimal rework. By selecting DuckDB for local-first execution, we optimize for data governance compliance, cost efficiency, and research reproducibility—priorities that outweigh absolute scalability for the vast majority of academic health research. By orchestrating transformations through SQLMesh, we achieve declarative, testable, and modular pipelines that support parallel development across staging and modeling phases.

This is not a production SaaS architecture. It is a **research-grade analytical framework** designed for the realistic operating environment of academic medical centers: constrained budgets, institutional data governance policies, and datasets in the hundreds of gigabytes rather than petabytes. It succeeds by optimizing for the common case while preserving clear migration paths for the exceptional case.

The proof of architectural fitness is not theoretical scaling limits but empirical utility: Can a researcher reproduce published results on their laptop in under an hour? Can a hospital analytics team deploy this on a secure VM to analyze their FHIR exports without cloud vendor lock-in? Can collaborators extend the pipeline to new data sources by writing a single adapter file? If the answer to these questions is yes—and for this architecture, it is—then the design has achieved its purpose.

---

## References

1. HL7 FHIR Specification R4: https://hl7.org/fhir/R4/
2. MIMIC-IV on FHIR: https://physionet.org/content/mimic-iv-fhir/
3. DuckDB Documentation: https://duckdb.org/docs/
4. SQLMesh Documentation: https://sqlmesh.readthedocs.io/
5. Wilkinson, M. D., et al. (2016). "The FAIR Guiding Principles for scientific data management and stewardship." *Scientific Data*, 3, 160018.
6. Mandel, J. C., et al. (2016). "SMART on FHIR: a standards-based, interoperable apps platform for electronic health records." *Journal of the American Medical Informatics Association*, 23(5), 899-908.
