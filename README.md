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
docker compose run transform_vitals_eda       # Silver + Gold pipeline

# Local
pip install -e .
python adapters/mimic/load_bronze.py          # Bronze: ingest NDJSON -> DuckDB
python pipeline/validate_bronze.py            # Validate bronze layer
python pipeline/build_silver/apply_views.py   # Silver: flatten vitals
cd models && sqlmesh plan --auto-apply        # Gold: run SQLMesh models
```

## Project Structure

```
adapters/mimic/load_bronze.py      Source-specific NDJSON -> DuckDB ingestion
pipeline/validate_bronze.py        Bronze validation gate
pipeline/build_silver/sql/         Silver SQL (source of truth)
pipeline/build_silver/apply_views.py  Executes silver SQL
specs/*.vd.json                    FHIR ViewDefinition specs (reference)
models/                            SQLMesh gold layer
notebooks/                         EDA and analysis notebooks
wiki/                              Documentation (git submodule)
local/                             Untracked scratch space
```

## Documentation

Full documentation lives in the [project wiki](https://github.com/kasra321/MIMIC-FHIR/wiki), also available locally at `wiki/` (git submodule, Obsidian-compatible).

## Environment Variables

- `DUCKDB_PATH` — Path to DuckDB warehouse file (default in Docker: `/data/warehouse/mimic_fhir.duckdb`)
- `RAW_DATA_PATH` — Directory containing raw NDJSON/JSON files
