#!/bin/bash
set -e

case "${1:-}" in
  fhir-ingestion)
    echo "WARNING: This will rebuild the bronze layer from raw FHIR files."
    echo "         Any existing bronze data will be replaced."
    read -p "Continue? [y/N] " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
      echo "Aborted."
      exit 0
    fi
    echo "--- BRONZE INGESTION ---"
    python /app/ingestion/load_bronze.py --source "${2:-unknown}"
    echo "--- BRONZE VALIDATION ---"
    python /app/ingestion/validate_bronze.py
    ;;
  vitals-pipeline)
    echo "--- SILVER: FLATTEN VIEWS ---"
    python /app/pipeline/build_silver/apply_views.py
    echo "--- GOLD: SQLMESH MODELS ---"
    cd /app/models
    sqlmesh plan --auto-apply --no-prompts
    ;;
  *)
    echo "Usage: run_pipeline.sh <pipeline> [options]"
    echo ""
    echo "Available pipelines:"
    echo "  fhir-ingestion <source>  Load raw FHIR files into bronze layer"
    echo "  vitals-pipeline          Flatten vitals + build EDA models"
    exit 1
    ;;
esac

echo "--- PIPELINE COMPLETE ---"
