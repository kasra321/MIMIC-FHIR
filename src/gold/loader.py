"""Gold layer: pivot silver vitals for LSTM preparation."""

import argparse
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).parent.parent.parent
SILVER_DIR = PROJECT_ROOT / "output" / "silver"
OUTPUT_DIR = PROJECT_ROOT / "output" / "gold"


def pivot(silver_dir: Path, output_dir: Path) -> None:
    """Pivot silver_vitals from long to wide format."""
    output_dir.mkdir(parents=True, exist_ok=True)
    source = silver_dir / "silver_vitals.parquet"
    target = output_dir / "gold_vitals.parquet"

    conn = duckdb.connect(":memory:")
    conn.execute(f"""
        COPY (
            SELECT
                patient_id,
                encounter_id,
                effective_datetime,
                AVG(CASE WHEN loinc_code = '8310-5' THEN value END) AS body_temperature,
                AVG(CASE WHEN loinc_code = '8867-4' THEN value END) AS heart_rate,
                AVG(CASE WHEN loinc_code = '9279-1' THEN value END) AS respiratory_rate,
                AVG(CASE WHEN loinc_code = '2708-6' THEN value END) AS oxygen_saturation,
                AVG(CASE WHEN loinc_code = '8480-6' THEN value END) AS systolic_bp,
                AVG(CASE WHEN loinc_code = '8462-4' THEN value END) AS diastolic_bp
            FROM read_parquet('{source}')
            GROUP BY patient_id, encounter_id, effective_datetime
            ORDER BY patient_id, encounter_id, effective_datetime
        ) TO '{target}' (FORMAT PARQUET)
    """)
    conn.close()

    print(f"Pivoted to {target}")


def main():
    parser = argparse.ArgumentParser(
        description="Gold layer: pivot silver vitals for LSTM preparation",
    )
    parser.add_argument(
        "command",
        choices=["pivot", "run"],
        help="pivot/run: pivot silver vitals to wide format",
    )
    parser.add_argument(
        "--silver-dir",
        type=Path,
        default=SILVER_DIR,
        help="Path to silver parquet directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Path for gold output",
    )

    args = parser.parse_args()

    if args.command in ("pivot", "run"):
        pivot(args.silver_dir, args.output_dir)


if __name__ == "__main__":
    main()
