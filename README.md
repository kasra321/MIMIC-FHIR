# MIMIC-FHIR Modern Data Stack

A medallion architecture pipeline that transforms MIMIC-IV FHIR NDJSON data into analysis-ready tables using DuckDB.

## Architecture

```
Data/*.ndjson  -->  Bronze (DuckDB)  -->  Silver (flat vitals)  -->  Gold (SQLMesh)  -->  Notebooks / BI
  15 GB              1.0 GB               obs_vitals                vitals_wide, vitals_eda
```

- **Bronze** — Ingests raw FHIR NDJSON resources into `bronze.fhir_resources` in DuckDB
- **Silver** — Flattens FHIR Observations into `silver.obs_vitals` via hand-written SQL (LOINC-filtered vital signs)
- **Gold** — SQLMesh models pivot vitals wide and add temporal features (delta times, encounter phases)

## Prerequisites

- Python 3.11+
- Docker (for containerized pipeline)
- Node.js (optional, for `npx flatquack` reference SQL generation)
- MIMIC-IV FHIR NDJSON files in `data/raw/`

## Quick Start

```bash
# Docker (recommended)
docker compose run ingest                     # Bronze ingestion + validation
docker compose run ingest_synthea
docker compose run transform_vitals_eda       # Silver + Gold pipeline
docker compose run recommendation_pipe        # Patient similarity pipeline

# Local
pip install -e .
python adapters/mimic/load_bronze.py          # Bronze: ingest NDJSON -> DuckDB
python pipeline/validate_bronze.py            # Validate bronze layer
python pipeline/build_silver/apply_views.py   # Silver: flatten vitals
cd models && sqlmesh plan --auto-apply        # Gold: run SQLMesh models
python src/similarity/build_store.py          # Builds the patient document store
```

Running the patient recommender requires you have created the vectorestore

```bash
python src/similarity/query_store.py -q {query} -n {num_results}
```

## Project Structure

```
adapters/mimic/load_bronze.py      Source-specific NDJSON -> DuckDB ingestion
pipeline/validate_bronze.py        Bronze validation gate
pipeline/build_silver/sql/         Silver SQL (source of truth)
pipeline/build_silver/apply_views.py  Executes silver SQL
specs/*.vd.json                    FHIR ViewDefinition specs (reference)
models/                            SQLMesh gold layer
src/                               Use case related scripts
notebooks/                         EDA and analysis notebooks
wiki/                              Documentation (git submodule)
local/                             Untracked scratch space
```

## Notebooks

- `data_profiling_harmonization`:
- `healthcare_utilization_demo`:
- `patient_recommender`: Workspace for the patient similarity pipeline. Sample code snippets that made it into the final scripts.
- `pipeline_test`:
- `table_exploration`: Explores the different structure and content of MIMIC and Synthea data

## Documentation

Full documentation lives in the [project wiki](https://github.com/kasra321/MIMIC-FHIR/wiki), also available locally at `wiki/` (git submodule, Obsidian-compatible).

## Environment Variables

- `DUCKDB_PATH` — Path to DuckDB warehouse file (default in Docker: `/data/warehouse/mimic_fhir.duckdb`)
- `RAW_DATA_PATH` — Directory containing raw NDJSON/JSON files

For Patient Recommender

- `EMBED_MODEL` — Embedding model used to vectorise patient documents
- `VECSTORE_PATH` — Path to create vectorestore
- `HF_API` — HuggingFace account API
