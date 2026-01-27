# MIMIC-FHIR Modern Data Stack

A medallion architecture pipeline that transforms MIMIC-IV FHIR data into analysis-ready Parquet files using DuckDB and FHIR ViewDefinitions.

## Architecture

```
Data/*.ndjson  -->  Bronze (DuckDB)  -->  Silver (Parquet)
  15 GB              1.0 GB               129 MB
```

- **Bronze** — Ingests raw FHIR NDJSON files into DuckDB tables.
- **Silver** — Compiles FHIR ViewDefinitions into SQL via [FlatQuack](https://github.com/nicktobey/flatquack), executes them with DuckDB, and outputs `silver_vitals.parquet`.

## Prerequisites

- Python 3.11+
- Node.js (for `npx flatquack`)
- MIMIC-IV FHIR NDJSON files in `Data/`

## Setup

```bash
pip install -e .
```

## Usage

### Bronze layer

```bash
python -m src.bronze.loader
```

Loads all `.ndjson` files from `Data/` into `output/bronze/bronze.duckdb`.

### Silver layer

```bash
# Compile ViewDefinitions to SQL, then materialize
python -m src.silver.loader run

# Or run steps individually
python -m src.silver.loader compile
python -m src.silver.loader materialize
```

Outputs `output/silver/silver_vitals.parquet` containing vital signs observations (heart rate, temperature, respiratory rate, O2 saturation, blood pressure) with standardized LOINC coding.

## Project Structure

```
src/
  bronze/loader.py          # NDJSON -> DuckDB ingestion
  silver/
    loader.py               # Compile & materialize pipeline
    views/*.vd.json         # FHIR ViewDefinition sources
sql/silver/                 # Generated SQL (git-ignored)
output/                     # Pipeline outputs (git-ignored)
Data/                       # Source NDJSON files (git-ignored)
```
