"""Silver layer: compile FHIR ViewDefinitions to SQL and materialize to parquet/csv."""

import argparse
import shutil
import subprocess
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).parent.parent.parent
VIEWS_DIR = PROJECT_ROOT / "src" / "silver" / "views"
SQL_DIR = PROJECT_ROOT / "sql" / "silver"
OUTPUT_DIR = PROJECT_ROOT / "output" / "silver"


def compile_views(views_dir: Path, sql_dir: Path, output_dir: Path, fmt: str) -> list[Path]:
    """Run flatquack to compile .vd.json files into .sql files.

    FlatQuack writes .sql files next to the .vd.json sources,
    so after the call we move them into sql_dir.

    Returns list of generated .sql paths in sql_dir.
    """
    sql_dir.mkdir(parents=True, exist_ok=True)

    print(f"Compiling ViewDefinitions in {views_dir}")
    subprocess.run(
        [
            "npx", "flatquack",
            "-m", "build",
            "-v", str(views_dir),
            "-p", "**/*.vd.json",
            "-t", f"@{fmt}",
            "--param", f"fq_output_dir={output_dir.resolve()}",
        ],
        check=True,
    )

    generated: list[Path] = []
    for sql_file in views_dir.glob("*.vd.sql"):
        dest = sql_dir / sql_file.name
        shutil.move(str(sql_file), str(dest))
        print(f"  {sql_file.name} -> {dest}")
        generated.append(dest)

    print(f"Compiled {len(generated)} view(s)")
    return generated


def materialize(sql_dir: Path, output_dir: Path) -> None:
    """Execute every .sql file in sql_dir using DuckDB."""
    output_dir.mkdir(parents=True, exist_ok=True)

    sql_files = sorted(sql_dir.glob("*.vd.sql"))
    if not sql_files:
        print(f"No .sql files found in {sql_dir}")
        return

    conn = duckdb.connect(":memory:")
    for sql_file in sql_files:
        print(f"Executing {sql_file.name}")
        sql_text = sql_file.read_text()
        try:
            conn.execute(sql_text)
            print(f"  Done")
        except Exception as e:
            print(f"  Error: {e}")
    conn.close()

    print(f"Materialized {len(sql_files)} view(s) to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Silver layer: compile and materialize FHIR ViewDefinitions",
    )
    parser.add_argument(
        "command",
        choices=["compile", "materialize", "run"],
        help="compile: generate SQL; materialize: execute SQL; run: both",
    )
    parser.add_argument(
        "--views-dir",
        type=Path,
        default=VIEWS_DIR,
        help="Path to ViewDefinition JSON files",
    )
    parser.add_argument(
        "--sql-dir",
        type=Path,
        default=SQL_DIR,
        help="Path for generated SQL output",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Path for materialized data output",
    )
    parser.add_argument(
        "--format",
        choices=["parquet", "csv"],
        default="parquet",
        help="Output format (default: parquet)",
    )

    args = parser.parse_args()

    if args.command in ("compile", "run"):
        compile_views(args.views_dir, args.sql_dir, args.output_dir, args.format)

    if args.command in ("materialize", "run"):
        materialize(args.sql_dir, args.output_dir)


if __name__ == "__main__":
    main()
