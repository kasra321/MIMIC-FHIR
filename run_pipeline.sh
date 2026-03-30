#!/bin/bash
set -e

case "${1:-}" in
  ingest)
    echo "--- BRONZE INGESTION ---"
    # Load each source directory under /data/raw/
    # Expected layout: /data/raw/mimic/, /data/raw/synthea_42/, etc.
    found_source=false
    for source_dir in /data/raw/*/; do
      if [ -d "$source_dir" ]; then
        source_name=$(basename "$source_dir")
        echo "Loading source: $source_name from $source_dir"
        python /app/pipeline/load_bronze.py --source "$source_name" --path "$source_dir" --replace
        found_source=true
      fi
    done
    if [ "$found_source" = false ]; then
      echo "No source directories found under /data/raw/"
      echo "Expected layout: /data/raw/<source_name>/ (e.g. /data/raw/mimic/)"
      exit 1
    fi
    echo "--- BRONZE VALIDATION ---"
    python /app/pipeline/validate_bronze.py
    ;;
  ingest_synthea)
    echo "--- GENERATE SYNTHEA ---"
    java -jar synthea-with-dependencies.jar -p $2
    echo "--- SYNTHEA INGESTION ---"
    python /app/adapters/synthea/load_synthea.py
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
    echo "  ingest                Load FHIR files from /data/raw/<source>/ into bronze"
    echo "  ingest_synthea        Load generated patient data into bronze layer"
    echo "  transform_vitals_eda  Flatten vitals + build EDA models"
    exit 1
    ;;
esac

echo "--- PIPELINE COMPLETE ---"
