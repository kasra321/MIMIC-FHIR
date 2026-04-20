import os
import duckdb

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/warehouse/mimic_fhir.duckdb")

def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DUCKDB_PATH, read_only=True)
