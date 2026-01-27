"""Bronze layer: Load FHIR NDJSON into DuckDB."""

import gzip
import shutil
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
NDJSON_DIR = PROJECT_ROOT / "ndjson"
DB_DIR = PROJECT_ROOT / "db"


def unzip_ndjson():
    """Decompress all NDJSON files."""
    NDJSON_DIR.mkdir(exist_ok=True)
    for src in DATA_DIR.glob("Mimic*.ndjson.gz"):
        name = src.name.replace("Mimic", "").replace(".gz", "")
        dst = NDJSON_DIR / name
        if not dst.exists():
            print(f"Unzipping {src.name}")
            try:
                with gzip.open(src, "rb") as f_in, open(dst, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            except EOFError:
                print(f"  Truncated: {src.name}")


def load_to_duckdb():
    """Load NDJSON files into DuckDB tables."""
    DB_DIR.mkdir(exist_ok=True)
    conn = duckdb.connect(str(DB_DIR / "bronze.duckdb"))

    for ndjson in NDJSON_DIR.glob("*.ndjson"):
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


def main():
    unzip_ndjson()
    load_to_duckdb()


if __name__ == "__main__":
    main()
