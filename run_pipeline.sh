#!/bin/bash
set -e

case "${1:-}" in
  ingest)
    echo "WARNING: This will rebuild the bronze layer from raw NDJSON files."
    echo "         Any existing bronze data will be replaced."
    read -p "Continue? [y/N] " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
      echo "Aborted."
      exit 0
    fi
    echo "--- BRONZE INGESTION ---"
    python /app/adapters/mimic/load_bronze.py
    echo "--- BRONZE VALIDATION ---"
    python /app/pipeline/validate_bronze.py
    ;;
  transform_vitals_eda)
    echo "--- SILVER: FLATTEN VIEWS ---"
    python /app/pipeline/build_silver/apply_views.py
    echo "--- GOLD: SQLMESH MODELS ---"
    cd /app/models
    sqlmesh plan --auto-apply --no-prompts
    ;;
  *)
    echo "Usage: run_pipeline.sh <pipeline>"
    echo ""
    echo "Available pipelines:"
    echo "  ingest                Load raw NDJSON files into bronze layer"
    echo "  transform_vitals_eda  Flatten vitals + build EDA models"
    exit 1
    ;;
esac

echo "--- PIPELINE COMPLETE ---"
