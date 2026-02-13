# adapters/mimic/load_bronze.py
import duckdb
import os
import re
import glob

db_path = os.environ["DUCKDB_PATH"]
raw_data_path = os.environ["RAW_DATA_PATH"]

con = duckdb.connect(db_path)

con.execute("CREATE SCHEMA IF NOT EXISTS bronze;")

# Full reload — no upsert needed for static data
ndjson_files = glob.glob(os.path.join(raw_data_path, "*.ndjson"))

if not ndjson_files:
    print("No NDJSON files found — skipping bronze ingestion.")
    con.close()
    exit(0)

# Build a UNION ALL across all source files
selects = []
for file_path in sorted(ndjson_files):
    filename = os.path.basename(file_path)

    # Sanitize filename before interpolation
    if not re.match(r"^[\w\-. ]+\.ndjson$", filename):
        print(f"Skipping file with unexpected name: {filename}")
        continue

    selects.append(f"""
    SELECT
        json_extract_string(raw, '$.resourceType') AS resource_type,
        json_extract_string(raw, '$.id') AS resource_id,
        raw AS resource,
        '{filename}' AS source_file
    FROM (
        SELECT column0 AS raw
        FROM read_csv('{file_path}', delim=NULL, header=false, auto_detect=false, columns={{'column0': 'VARCHAR'}})
    )
    """)
    print(f"  Queued {filename}")

con.execute(f"""
CREATE OR REPLACE TABLE bronze.fhir_resources AS
{" UNION ALL ".join(selects)}
""")

row_count = con.execute(
    "SELECT COUNT(*) FROM bronze.fhir_resources"
).fetchone()[0]
print(f"Bronze ingestion complete: {row_count:,} rows.")
con.close()
