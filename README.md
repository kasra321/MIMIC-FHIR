# MIMIC-FHIR Modern Data Stack

A source-agnostic medallion architecture that transforms clinical FHIR data into analysis-ready tables using DuckDB and SQLMesh. Supports MIMIC-IV and Synthea out of the box.

## Architecture

```
FHIR sources          Bronze            Silver               Gold (SQLMesh)         Consumers
─────────────       ──────────       ──────────────       ───────────────────      ────────────
MIMIC-IV NDJSON ┐   fhir_resources   patients             encounter_index     ┌─> FastAPI
Synthea Bundles ┘                    encounters            utilization_history │   Notebooks
                                     conditions            condition_burden    │   BI tools
                                     obs_vitals      ───>  utilization_eda  ──┘
                                     procedures            recommend (10 models)
                                     medications
```

- **Bronze** — Ingests raw FHIR NDJSON and JSON Bundle resources into `bronze.fhir_resources`, tagging each with `meta.source` for lineage
- **Silver** — Flattens FHIR resources into relational tables (patients, encounters, conditions, vitals, procedures, medications, locations, organizations)
- **Gold** — SQLMesh models compute utilization analytics (encounter index, lookback history, condition burden) and patient-recommendation feature tables

## Prerequisites

- Python 3.11+
- Docker (for containerized pipeline)
- MIMIC-IV FHIR NDJSON files in `data/raw/mimic/` (and/or Synthea bundles in `data/raw/synthea/`)

## Quick Start

```bash
# Docker (recommended)
docker compose run ingest                  # Bronze: load all sources + validate
docker compose run ingest_synthea          # Generate and load Synthea patients
docker compose run transform_vitals_eda    # Silver flattening + Gold SQLMesh models
docker compose run recommendation_pipe     # Build recommend tables

# Local
pip install -e .
python pipeline/load_bronze.py --source mimic --path data/raw/mimic/
python pipeline/validate_bronze.py
python pipeline/build_silver/apply_views.py
sqlmesh plan --auto-apply                  # Gold models

# API
uvicorn api.main:app                       # Starts on http://localhost:8000
```

## Project Structure

```
pipeline/
  load_bronze.py                   FHIR NDJSON/Bundle -> DuckDB ingestion
  validate_bronze.py               Bronze validation gate
  build_silver/sql/                Silver SQL (8 flattening scripts)
  build_silver/apply_views.py      Executes silver SQL

adapters/synthea/                  Synthea-specific ingestion

models/models/
  intermediate/                    encounter_index, utilization_history, condition_burden
  marts/                           utilization_eda (denormalized analytics fact table)
  recommend/                       10 feature tables for patient similarity

api/                               FastAPI read-only API over the gold layer
  routers/utilization.py           4 endpoints: list, stats, patient, encounter

src/
  utilization/analytics.py         Visualization module (charts, summaries)
  similarity/build_store.py        ChromaDB vector store for patient search
  pubmed/clustering.py             PubMed redundancy analysis via embeddings

notebooks/
  table_exploration                Exploration of raw data formats
  healthcare_utilization_demo      Dashboard over the API (zero SQL)
  data_profiling_harmonization     MIMIC vs Synthea harmonization analysis
  pubmed_redundancy_analysis       Literature redundancy clustering
  patient_recommender              Drafts of patient similarity system

wiki/                              Documentation (git submodule)
run_pipeline.sh                    Docker entrypoint (ingest, transform, recommend)
docker-compose.yml                 Multi-service orchestration
```

## API

The FastAPI server exposes the gold layer at `http://localhost:8000`:

| Endpoint                          | Description                                                            |
| --------------------------------- | ---------------------------------------------------------------------- |
| `GET /utilization`                | List records with filters (source, gender, encounter_class, age range) |
| `GET /utilization/stats`          | Aggregate statistics grouped by source and encounter class             |
| `GET /utilization/patient/{id}`   | All encounters for a patient                                           |
| `GET /utilization/{encounter_id}` | Single encounter detail                                                |

Interactive docs at `/docs` (Swagger UI).

## Documentation

Full documentation lives in the [project wiki](https://github.com/kasra321/MIMIC-FHIR/wiki), also available locally at `wiki/` (git submodule, Obsidian-compatible).

## Environment Variables

- `DUCKDB_PATH` — Path to DuckDB warehouse file (default: `data/warehouse/mimic_fhir.duckdb`)
- `RAW_DATA_PATH` — Directory containing raw NDJSON/JSON files
- `EMBED_MODEL` — Hugging Face embedding model (default: `kamalkraj/BioSimCSE-BioLinkBERT-BASE`)
- `VECSTORE_PATH` — Path to vectorstore
- `HF_API` — Hugging Face personal key
