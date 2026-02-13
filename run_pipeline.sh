#!/bin/bash
set -e

echo "--- STAGE 1: BRONZE INGESTION ---"
python /app/adapters/mimic/load_bronze.py

echo "--- STAGE 1.5: BRONZE VALIDATION ---"
python /app/pipeline/validate_bronze.py

echo "--- STAGE 2: SILVER TRANSFORMATION ---"
python /app/pipeline/build_silver/apply_views.py

echo "--- STAGE 3: GOLD MODELING (SQLMESH) ---"
cd /app/models
sqlmesh run

echo "--- PIPELINE COMPLETE ---"
