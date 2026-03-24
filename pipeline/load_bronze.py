# pipeline/load_bronze.py — Unified FHIR Bronze Loader
# Loads FHIR resources from NDJSON and JSON Bundle files into bronze.fhir_resources.
# Injects meta.source into each resource for lineage tracking.

import argparse
import duckdb
import glob
import os
import re
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Load FHIR resources into bronze layer")
    parser.add_argument("--source", required=True, help="Source name (e.g. mimic, synthea_42)")
    parser.add_argument("--path", required=True, help="Directory containing FHIR data files")
    parser.add_argument("--db", default=os.environ.get("DUCKDB_PATH"), help="Path to DuckDB file")
    parser.add_argument("--replace", action="store_true",
                        help="Delete existing rows for this source before inserting")
    return parser.parse_args()


def find_fhir_files(directory):
    """Find all .ndjson and .json files in the given directory."""
    ndjson = glob.glob(os.path.join(directory, "*.ndjson"))
    json_files = glob.glob(os.path.join(directory, "*.json"))
    return sorted(ndjson), sorted(json_files)


SAFE_FILENAME = re.compile(r"^[\w\-. ]+\.(ndjson|json)$")


def build_ndjson_select(file_path, source):
    """Build SQL to read an NDJSON file: one resource per line."""
    filename = os.path.basename(file_path)
    return f"""
    SELECT
        json_extract_string(patched, '$.resourceType') AS resource_type,
        json_extract_string(patched, '$.id')           AS resource_id,
        patched                                         AS resource,
        '{filename}'                                    AS source_file
    FROM (
        SELECT json_merge_patch(
            column0::JSON,
            '{{"meta": {{"source": "{source}"}}}}'
        )::VARCHAR AS patched
        FROM read_csv('{file_path}',
             delim=NULL, header=false, auto_detect=false,
             columns={{'column0': 'VARCHAR'}})
    )
    """


def build_bundle_select(file_path, source):
    """Build SQL to read a JSON Bundle file: unnest entry[].resource."""
    filename = os.path.basename(file_path)
    return f"""
    SELECT
        json_extract_string(patched, '$.resourceType') AS resource_type,
        json_extract_string(patched, '$.id')           AS resource_id,
        patched                                         AS resource,
        '{filename}'                                    AS source_file
    FROM (
        SELECT json_merge_patch(
            entry_resource::JSON,
            '{{"meta": {{"source": "{source}"}}}}'
        )::VARCHAR AS patched
        FROM (
            SELECT unnest(
                json_extract(content, '$.entry[*].resource')::VARCHAR[]
            ) AS entry_resource
            FROM read_json('{file_path}',
                 format='unstructured', columns={{'content': 'JSON'}})
        )
    )
    """


def main():
    args = parse_args()

    if not args.db:
        print("Error: --db or DUCKDB_PATH environment variable required")
        sys.exit(1)

    if not os.path.isdir(args.path):
        print(f"Error: {args.path} is not a directory")
        sys.exit(1)

    # Sanitize source name to prevent SQL injection
    if not re.match(r"^[\w\-]+$", args.source):
        print(f"Error: source name must be alphanumeric/underscore/hyphen, got '{args.source}'")
        sys.exit(1)

    ndjson_files, json_files = find_fhir_files(args.path)
    if not ndjson_files and not json_files:
        print(f"No .ndjson or .json files found in {args.path}")
        sys.exit(0)

    # Build SELECT statements for each file
    selects = []
    for f in ndjson_files:
        if not SAFE_FILENAME.match(os.path.basename(f)):
            print(f"  Skipping file with unexpected name: {os.path.basename(f)}")
            continue
        selects.append(build_ndjson_select(f, args.source))
        print(f"  Queued NDJSON: {os.path.basename(f)}")

    for f in json_files:
        if not SAFE_FILENAME.match(os.path.basename(f)):
            print(f"  Skipping file with unexpected name: {os.path.basename(f)}")
            continue
        selects.append(build_bundle_select(f, args.source))
        print(f"  Queued Bundle: {os.path.basename(f)}")

    if not selects:
        print("No valid files to load.")
        sys.exit(0)

    con = duckdb.connect(args.db)
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
    con.execute("""
        CREATE TABLE IF NOT EXISTS bronze.fhir_resources (
            resource_type VARCHAR,
            resource_id   VARCHAR,
            resource      VARCHAR,
            source_file   VARCHAR
        )
    """)

    if args.replace:
        deleted = con.execute(f"""
            DELETE FROM bronze.fhir_resources
            WHERE json_extract_string(resource, '$.meta.source') = '{args.source}'
        """).fetchone()
        print(f"  Deleted existing rows for source '{args.source}'")

    union_sql = " UNION ALL ".join(selects)
    con.execute(f"INSERT INTO bronze.fhir_resources {union_sql}")

    row_count = con.execute(
        "SELECT COUNT(*) FROM bronze.fhir_resources"
    ).fetchone()[0]

    source_count = con.execute(f"""
        SELECT COUNT(*) FROM bronze.fhir_resources
        WHERE json_extract_string(resource, '$.meta.source') = '{args.source}'
    """).fetchone()[0]

    print(f"Bronze ingestion complete: {source_count:,} rows from '{args.source}' "
          f"({row_count:,} total rows).")
    con.close()


if __name__ == "__main__":
    main()
