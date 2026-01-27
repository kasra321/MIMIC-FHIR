"""Bronze layer: Load FHIR NDJSON into DuckDB."""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
OUTPUT_DIR = PROJECT_ROOT / "output" / "bronze"


def load_to_duckdb(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    """Load NDJSON files from data_dir into a DuckDB database."""
    output_dir.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(output_dir / "bronze.duckdb"))

    for ndjson in sorted(data_dir.glob("*.ndjson")):
        table = f"bronze_{ndjson.stem.lower()}"
        print(f"Loading {ndjson.name} -> {table}")
        try:
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table} AS
                SELECT * FROM read_json_auto('{ndjson}')
            """)
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {count:,} rows")
        except Exception as e:
            print(f"  Error: {e}")

    conn.close()


if __name__ == "__main__":
    load_to_duckdb()
