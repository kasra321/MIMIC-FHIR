# ingestion/load_bronze.py
#
# Unified FHIR bronze loader. Detects file format by extension:
#   *.ndjson  → one resource per line
#   *.json    → Bundle (entry[].resource) or individual resource
#
# Usage:
#   python ingestion/load_bronze.py --source mimic-iv
#   python ingestion/load_bronze.py --source synthea-sample
#
# Env vars: DUCKDB_PATH, RAW_DATA_PATH

import argparse
import duckdb
import glob
import json
import os
import re
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Load FHIR resources into bronze layer")
    parser.add_argument(
        "--source",
        required=True,
        help="Dataset source label (e.g. 'mimic-iv', 'synthea-sample'). "
             "Stored in dataset_source column for provenance.",
    )
    return parser.parse_args()


def build_ndjson_select(file_path, filename, dataset_source):
    """Build SELECT for an NDJSON file (one JSON resource per line)."""
    return f"""
    SELECT
        json_extract_string(raw, '$.resourceType') AS resource_type,
        json_extract_string(raw, '$.id') AS resource_id,
        raw AS resource,
        '{filename}' AS source_file,
        '{dataset_source}' AS dataset_source
    FROM (
        SELECT column0 AS raw
        FROM read_csv('{file_path}', delim=NULL, header=false,
                      auto_detect=false, columns={{'column0': 'VARCHAR'}})
    )
    """


def load_bundle_json(file_path, filename, dataset_source):
    """Parse a JSON file as a FHIR Bundle or individual resource.

    Returns list of (resource_type, resource_id, resource_json, source_file, dataset_source) tuples.
    """
    with open(file_path, "r") as f:
        data = json.load(f)

    rows = []
    if data.get("resourceType") == "Bundle" and "entry" in data:
        for entry in data["entry"]:
            resource = entry.get("resource", {})
            rows.append((
                resource.get("resourceType"),
                resource.get("id"),
                json.dumps(resource),
                filename,
                dataset_source,
            ))
    else:
        # Individual resource (not a Bundle)
        rows.append((
            data.get("resourceType"),
            data.get("id"),
            json.dumps(data),
            filename,
            dataset_source,
        ))
    return rows


def main():
    args = parse_args()
    dataset_source = args.source

    db_path = os.environ["DUCKDB_PATH"]
    raw_data_path = os.environ["RAW_DATA_PATH"]

    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze;")

    ndjson_files = sorted(glob.glob(os.path.join(raw_data_path, "*.ndjson")))
    json_files = sorted(glob.glob(os.path.join(raw_data_path, "*.json")))

    if not ndjson_files and not json_files:
        print("No NDJSON or JSON files found — skipping bronze ingestion.")
        con.close()
        sys.exit(0)

    # --- NDJSON files: use DuckDB's read_csv for speed ---
    ndjson_selects = []
    for file_path in ndjson_files:
        filename = os.path.basename(file_path)
        if not re.match(r"^[\w\-. ]+\.ndjson$", filename):
            print(f"  Skipping file with unexpected name: {filename}")
            continue
        ndjson_selects.append(build_ndjson_select(file_path, filename, dataset_source))
        print(f"  Queued NDJSON: {filename}")

    # --- JSON files: parse in Python (Bundles need entry extraction) ---
    json_rows = []
    for file_path in json_files:
        filename = os.path.basename(file_path)
        if not re.match(r"^[\w\-. ]+\.json$", filename):
            print(f"  Skipping file with unexpected name: {filename}")
            continue
        rows = load_bundle_json(file_path, filename, dataset_source)
        json_rows.extend(rows)
        bundle_label = f"Bundle ({len(rows)} entries)" if len(rows) > 1 else "resource"
        print(f"  Parsed JSON: {filename} — {bundle_label}")

    # --- Build the table ---
    parts = []

    if ndjson_selects:
        parts.append(" UNION ALL ".join(ndjson_selects))

    if json_rows:
        # Register Python rows as a DuckDB table, then SELECT into the union
        con.execute("""
            CREATE OR REPLACE TEMP TABLE _json_staging (
                resource_type VARCHAR,
                resource_id VARCHAR,
                resource VARCHAR,
                source_file VARCHAR,
                dataset_source VARCHAR
            )
        """)
        con.executemany(
            "INSERT INTO _json_staging VALUES (?, ?, ?, ?, ?)", json_rows
        )
        parts.append("SELECT * FROM _json_staging")

    if not parts:
        print("No valid files to ingest.")
        con.close()
        sys.exit(0)

    con.execute(f"""
        CREATE OR REPLACE TABLE bronze.fhir_resources AS
        {" UNION ALL ".join(parts)}
    """)

    row_count = con.execute(
        "SELECT COUNT(*) FROM bronze.fhir_resources"
    ).fetchone()[0]
    print(f"Bronze ingestion complete: {row_count:,} rows (source: {dataset_source}).")
    con.close()


if __name__ == "__main__":
    main()
