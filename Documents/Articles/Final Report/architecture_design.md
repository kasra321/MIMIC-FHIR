In # Architecture Design: A Modular Pipeline for FHIR-Based Clinical Data Analysis

## 1. Introduction

The analysis of clinical data at scale presents a unique set of engineering challenges that are distinct from those encountered in conventional data science workflows. Electronic Health Records (EHR) data, particularly when encoded in modern interoperability standards such as HL7 FHIR (Fast Healthcare Interoperability Resources), arrives as deeply nested, semi-structured documents rather than flat, analysis-ready tables. The MIMIC-IV Emergency Department dataset [1, 2], comprising approximately 19.5 million FHIR resources serialized as NDJSON (Newline-Delimited JSON), exemplifies this challenge: the raw data is voluminous, structurally complex, and requires substantial transformation before any analytical work can begin.

A naive approach—loading, transforming, and analyzing data in a single monolithic script—quickly encounters practical limitations. Re-ingesting 19.5 million rows on every iteration of an analytical query is both wasteful and error-prone, particularly in memory-constrained environments where such operations may trigger out-of-memory failures. This paper describes the architecture of a modular, containerized pipeline designed to support iterative clinical data science workflows on FHIR-formatted EHR data. The central design principle is the separation of *ingestion* (an expensive, run-once operation) from *transformation* (an iterative, evolve-often operation), mediated by a shared analytical database.

## 2. Architecture Overview

### 2.1. The Medallion Pattern

The pipeline adopts the medallion architecture [3], a layered data design pattern that organizes data into progressive stages of refinement:

- **Bronze layer** — Raw FHIR resources ingested verbatim from NDJSON files. Each row stores the complete JSON document alongside its resource type and identifier. This layer serves as a faithful, queryable mirror of the source data.
- **Silver layer** — Flattened, typed, and filtered tables derived from bronze. Nested FHIR structures (e.g., `Observation.code.coding[]`) are unnested into columnar form, with explicit data types applied. This layer is domain-scoped: each table represents a specific clinical concept (e.g., vital sign observations filtered to a known set of LOINC codes).
- **Gold layer** — Analytical models built atop silver tables. These implement the aggregations, pivots, window functions, and derived features required for specific analytical use cases (e.g., exploratory data analysis of vital sign temporal patterns).

This pattern is well-suited to clinical EHR pipelines for several reasons. First, the bronze layer preserves the full fidelity of the FHIR source, allowing reprocessing without re-ingestion. Second, the silver layer provides a natural boundary for FHIR-specific complexity: all JSON extraction and unnesting logic is confined here, presenting downstream consumers with clean relational tables. Third, the gold layer can evolve independently as analytical requirements change, without requiring any modification to upstream layers.

### 2.2. Separation of Ingestion and Transformation

The most consequential architectural decision is the decomposition of the pipeline into two independent workflows:

1. **Ingestion pipeline** (`ingest`) — Reads raw NDJSON files from disk, parses each line as a FHIR resource, and writes the results into the bronze layer of a persistent DuckDB database. This operation processes 19.5 million resources and is designed to run once (or infrequently, when source data is updated). It includes a validation step that verifies row counts, schema integrity, and resource type coverage.

2. **Transformation pipeline** (`transform_vitals_eda`) — Reads from the bronze layer, applies silver flatten views to produce typed analytical tables, then executes gold-layer SQLMesh models. This pipeline is lightweight and designed for rapid iteration: a researcher modifying an analytical model can re-run it in seconds without re-ingesting the source data.

The two pipelines share state exclusively through the DuckDB database file, which resides on a volume-mounted directory. This architectural boundary ensures that the expensive ingestion step is decoupled from the iterative transformation cycle. The naming convention `{workflow}_{output}` (e.g., `transform_vitals_eda`, and in future, `transform_labs_qc` or `transform_encounters_timeline`) provides a scalable pattern for registering additional analytical pipelines without modifying the ingestion infrastructure.

## 3. Technology Choices

### 3.1. FHIR and NDJSON

HL7 FHIR is the predominant interoperability standard for healthcare data exchange [4]. Clinical data systems increasingly expose data as FHIR resources—self-contained JSON documents representing discrete clinical concepts (Patient, Encounter, Observation, Condition, etc.). The MIMIC-IV dataset is distributed in NDJSON format, where each line is a complete, independent FHIR resource. This format is streaming-friendly and well-suited to bulk ingestion, as each line can be parsed and loaded without buffering the entire file.

The choice to ingest FHIR resources in their native JSON form into the bronze layer (rather than pre-flattening during ingestion) preserves maximum flexibility. New silver views can extract different fields from the same bronze data without re-ingestion—a critical capability when analytical requirements evolve.

### 3.2. DuckDB

DuckDB [5] serves as the analytical engine for the entire pipeline. Several properties make it particularly well-suited to this use case:

- **Embedded, serverless architecture** — No database server to provision, configure, or maintain. The entire database is a single file on disk, simplifying deployment and reproducibility.
- **Columnar storage with OLAP optimization** — Analytical queries over millions of rows execute efficiently, with automatic vectorized execution and predicate pushdown.
- **Native JSON extraction** — DuckDB's `json_extract`, `json_extract_string`, and `unnest` functions operate directly on JSON columns, enabling FHIR resource flattening within SQL without external preprocessing.
- **Configurable resource management** — Memory limits, thread counts, and insertion ordering can be tuned via pragmas (`SET memory_limit`, `SET threads`, `SET preserve_insertion_order`), enabling execution in constrained environments such as Docker containers with limited memory allocations.

The single-file database also serves as the natural integration point between the ingestion and transformation pipelines: both connect to the same `.duckdb` file, with DuckDB's file-level locking ensuring that only one writer operates at a time.

Critically, DuckDB's role extends beyond query execution: it functions as a unified storage layer in which bronze, silver, intermediate, and gold tables all coexist within a single file. This eliminates the need for separate storage systems or file-format negotiations between pipeline stages. Raw FHIR JSON, flattened relational tables, pivoted analytical views, and enriched mart models all reside in one portable artifact. The result is an all-in-one analytical warehouse that can be copied, versioned, or shared as a single file—a property that dramatically simplifies reproducibility in research contexts.

This unified storage model also unlocks a powerful capability: **multi-source ingestion with downstream source awareness**. Because the bronze layer records the data source alongside each FHIR resource, multiple clinical data sources—institutional EHRs, registry exports, or federated FHIR endpoints—can be ingested into the same bronze schema. Downstream transformation pipelines can then operate across all sources simultaneously or be dynamically filtered to a specific source, enabling comparative analyses without maintaining separate databases. The data is *source-aware but source-agnostic*: each record knows its provenance, but the analytical models need not be rewritten for each new data source.

Furthermore, the FHIR standard's use of established clinical terminologies creates natural extension points for knowledge graph integration. Terminology services such as SNOMED-CT (for clinical findings, procedures, and diagnoses) and RxNorm (for medication concepts) define hierarchical concept relationships that can be materialized as reference tables within the same DuckDB instance. Silver-layer transformations can then join FHIR-coded observations against these terminology graphs—mapping local codes to canonical concepts, traversing hierarchies for roll-up aggregations, or linking across vocabularies (e.g., mapping a LOINC observation to its associated SNOMED finding). Because these reference tables are lightweight, portable, and expressed in the same relational format as the clinical data, they integrate seamlessly into the existing flatten-and-transform workflow. The result is a silver layer capable of merging clinical observations with multiple knowledge graphs in a single SQL join, producing transformations that are robust to institutional coding variation, portable across FHIR-compliant data sources, and interoperable by construction.

### 3.3. Flatten Views (Silver Layer)

The silver layer uses plain SQL scripts that execute `CREATE OR REPLACE TABLE` statements against the bronze layer. Each script follows the naming convention `flatten_{resource}_{domain}.sql` (e.g., `flatten_obs_vitals.sql`), producing a table in the `silver` schema (e.g., `silver.obs_vitals`). The `flatten_` prefix groups all silver scripts together when listed alphabetically, while the resource abbreviation (`obs` for Observation, full name for others) and domain suffix provide immediate clarity about both the FHIR source and the analytical context.

These scripts use `LATERAL unnest` joins to expand nested FHIR arrays (such as `Observation.code.coding[]`) into flat rows. The lateral join pattern is preferred over correlated subqueries for its more predictable memory profile when operating over large datasets, as it allows the query engine to process the unnesting in a streaming fashion rather than materializing intermediate results.

### 3.4. SQLMesh

SQLMesh [6] orchestrates the gold-layer transformations. It provides several capabilities that plain SQL scripts do not:

- **DAG-based dependency resolution** — Models declare their upstream dependencies, and SQLMesh automatically determines execution order. When a silver table changes, only its downstream dependents are recomputed.
- **Schema contracts via external models** — The `external_models.yaml` file declares the expected schema of silver tables (column names and types). SQLMesh validates these contracts before executing transformations, catching schema drift early.
- **Incremental build support** — While the current models use `FULL` refresh (appropriate for the dataset size), SQLMesh's incremental modes provide a migration path as data volumes grow.

The intermediate layer (`intermediate.vitals_wide`) pivots long-format vital sign observations into wide-format rows (one row per encounter-timestamp, with columns for each vital sign). The mart layer (`marts.vitals_eda`) enriches this with derived features for exploratory analysis: observation counts, temporal deltas, encounter phases, and duration metrics.

### 3.5. Docker

Docker containerization serves three purposes in this architecture:

1. **Reproducibility** — The Dockerfile captures the exact Python version, package versions, and system dependencies required to execute the pipeline. Any collaborator can reproduce results by running a single command.
2. **Isolation** — The container provides a controlled execution environment with predictable resource constraints, preventing host-system variability from affecting results.
3. **Separation of compute from storage** — Docker volumes mount the data directories from the host filesystem into the container. The container is ephemeral (created and destroyed per pipeline run via `docker compose run --rm`), while the data persists on the host. This pattern ensures that the DuckDB database survives across pipeline runs without being embedded in the container image.

The `docker-compose.yml` defines two services corresponding to the two pipelines. The `ingest` service mounts both the raw data directory (read-only) and the warehouse directory. The `transform_vitals_eda` service mounts only the warehouse—it has no access to raw NDJSON files, enforcing the architectural boundary at the filesystem level.

## 4. Design Decisions

### 4.1. Run-Once vs. Iterate-Often

The separation of ingestion from transformation directly addresses the practical workflow of clinical data analysis. During the exploratory phase, a researcher may modify a SQL view or analytical model dozens of times before arriving at the correct transformation. If each iteration requires re-ingesting 19.5 million FHIR resources, the feedback loop extends from seconds to minutes—a significant impediment to productive analysis.

The run-once ingestion model also improves reliability. The bronze ingestion step is the most memory-intensive operation in the pipeline (parsing and loading millions of JSON documents). By isolating it, an out-of-memory failure during ingestion does not invalidate or corrupt an in-progress analytical transformation, and vice versa.

### 4.2. Naming Conventions

The naming conventions are designed to scale with project growth without requiring retroactive renaming:

- **Silver scripts**: `flatten_{resource}_{domain}.sql` — The verb prefix groups all flattening scripts together, the resource abbreviation identifies the FHIR source, and the domain narrows the scope. Future additions (`flatten_obs_labs.sql`, `flatten_encounters.sql`) follow the same pattern without ambiguity.
- **Silver tables**: `silver.{resource}_{domain}` — The schema name already implies the flattening operation, so the table name drops the verb.
- **Intermediate models**: `{domain}_{shape}.sql` — Describes what the data looks like (e.g., `vitals_wide`).
- **Mart models**: `{domain}_{purpose}.sql` — Describes the analytical intent (e.g., `vitals_eda`), with the domain placed first for alphabetical grouping by subject area.

### 4.3. Memory Management in Constrained Environments

Docker containers frequently operate with memory limits below those of the host system. The pipeline configures DuckDB pragmas at the start of each connection:

```sql
SET memory_limit = '4GB';
SET threads = 2;
SET preserve_insertion_order = false;
```

Limiting threads reduces peak memory consumption by constraining parallel hash table construction during joins and aggregations. Disabling insertion order preservation allows DuckDB to write results in the order they are computed rather than the order they appear in the source, eliminating a potentially large sorting buffer. These pragmas were introduced after observing an out-of-memory failure during the lateral unnest operation on 19.5 million bronze rows—a direct example of how constrained-environment deployment surfaces issues that do not manifest in local development.

## 5. Conclusion

The architecture described in this paper—a medallion-pattern pipeline with separated ingestion and transformation workflows, orchestrated within Docker containers and mediated by an embedded analytical database—addresses the practical demands of iterative clinical data science on FHIR-formatted EHR data. By treating ingestion as a run-once operation and transformation as an iterate-often operation, the architecture reduces feedback loop latency from minutes to seconds, enabling the rapid exploratory analysis cycles that characterize early-stage clinical research.

The technology choices—DuckDB for embedded analytics, SQL-based flatten views for FHIR unnesting, SQLMesh for DAG-based orchestration, and Docker for reproducible execution—were selected to minimize operational complexity while providing the structural guarantees (schema contracts, dependency resolution, resource management) required for reliable analytical workflows. The naming conventions and pipeline registration pattern (`{workflow}_{output}`) provide a scalable foundation for extending the infrastructure to additional clinical domains (laboratory results, encounters, conditions) without architectural modification.

This modular approach reflects a broader principle in clinical data engineering: the cost of re-processing raw data should be paid once, not on every analytical iteration. By making this separation explicit in the architecture, the pipeline supports the kind of sustained, exploratory engagement with clinical data that leads to meaningful analytical insights.

---

**References**

[1] Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023). MIMIC-IV (version 2.2). *PhysioNet*. https://doi.org/10.13026/66pc-qs21.

[2] Johnson, A. E. W., et al. (2023). MIMIC-IV-ED: A comprehensive public EMR dataset for the emergency department. *Scientific Data*.

[3] Databricks. (2022). Medallion Architecture. https://www.databricks.com/glossary/medallion-architecture.

[4] HL7 International. (2019). HL7 FHIR Release 4. https://hl7.org/fhir/R4/.

[5] Raasveldt, M., & Muhleisen, H. (2019). DuckDB: An embeddable analytical database. *Proceedings of the 2019 International Conference on Management of Data (SIGMOD)*, 1981-1984.

[6] Tobiko Data. (2023). SQLMesh: A next-generation data transformation framework. https://sqlmesh.com.
