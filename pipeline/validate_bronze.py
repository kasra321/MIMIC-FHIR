# pipeline/validate_bronze.py
import duckdb
import os
import sys

db_path = os.environ["DUCKDB_PATH"]
con = duckdb.connect(db_path)

errors = []

# 1. Row count > 0
row_count = con.execute(
    "SELECT COUNT(*) FROM bronze.fhir_resources"
).fetchone()[0]
if row_count == 0:
    errors.append("bronze.fhir_resources is empty")

# 2. Required columns exist
expected_cols = {"resource_type", "resource_id", "resource", "source_file"}
actual_cols = {
    row[0]
    for row in con.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'bronze' AND table_name = 'fhir_resources'"
    ).fetchall()
}
missing = expected_cols - actual_cols
if missing:
    errors.append(f"Missing columns: {missing}")

# 3. Null rate on critical fields
for col in ("resource_id", "resource_type"):
    null_count = con.execute(
        f"SELECT COUNT(*) FROM bronze.fhir_resources WHERE {col} IS NULL"
    ).fetchone()[0]
    null_rate = null_count / row_count if row_count > 0 else 0
    if null_rate > 0.05:
        errors.append(f"{col} null rate = {null_rate:.1%} (threshold: 5%)")

con.close()

if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"Bronze validation passed ({row_count:,} rows).")
