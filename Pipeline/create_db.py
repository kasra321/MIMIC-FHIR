#!/usr/bin/env python3
"""Create DuckDB database from MIMIC FHIR NDJSON files."""

import duckdb
from pathlib import Path

DATA_DIR = Path(__file__).parent / "Data"
DB_PATH = Path(__file__).parent / "mimic_fhir.duckdb"

TABLES = [
    ("organization", "MimicOrganization.ndjson"),
    ("location", "MimicLocation.ndjson"),
    ("patient", "MimicPatient.ndjson"),
    ("encounter", "MimicEncounterED.ndjson"),
    ("condition", "MimicConditionED.ndjson"),
    ("procedure", "MimicProcedureED.ndjson"),
    ("observation", "MimicObservationED.ndjson"),
    ("observation_vital_signs", "MimicObservationVitalSignsED.ndjson"),
    ("medication_dispense", "MimicMedicationDispenseED.ndjson"),
    ("medication_statement", "MimicMedicationStatementED.ndjson"),
]


def main():
    # Remove existing database to start fresh
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = duckdb.connect(str(DB_PATH))

    for table_name, filename in TABLES:
        filepath = DATA_DIR / filename
        print(f"Loading {table_name} from {filename}...")

        conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_json_auto('{filepath}', format='newline_delimited')
        """)

        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  -> {count:,} records loaded")

    # Show summary
    print("\nDatabase created successfully!")
    print(f"Location: {DB_PATH}")
    print("\nTables:")
    for row in conn.execute("SHOW TABLES").fetchall():
        table = row[0]
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  - {table}: {count:,} records")

    conn.close()


if __name__ == "__main__":
    main()
