# adapters/synthea/load_synthea.py
import duckdb
import os
import glob

db_path = os.environ["DUCKDB_PATH"]
synthea_data_path = os.environ["SYNTHEA_DATA_PATH"]

con = duckdb.connect(db_path)

# Removes old table and creates new one
con.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
con.execute("DROP TABLE IF EXISTS bronze.synthea;")

json_files = os.listdir(f"{synthea_data_path}/fhir")
if not json_files:
  print("No JSON files found — skipping Synthea ingestion.")
  con.close()
  exit(0)

# Ingest each file where each item in entry is its own row
for json in json_files:
  # File details
  s = json.split("_")
  file_id = s[-1].split('.')[0]
  name = "_".join(s[:-1])

  # Filename validation on both file id and name
  if not "-" in file_id:
    continue
  if any([n.istitle() for n in s[:-1]]) == False:
    continue

  # Ingestion
  file_path = f"{synthea_data_path}/fhir/{json}"
  # Determines the schema
  con.execute(f"""
    CREATE TABLE IF NOT EXISTS bronze.synthea AS
    SELECT * FROM (
      SELECT   
        entry->>'fullUrl' AS full_url,
        entry->>'resource'->>'resourceType' AS resource_type,
        entry->'resource' AS resource,
        entry->'request' AS request,
        '{name}'      AS source_file,
        '{file_id}'   AS file_id
      FROM (
        SELECT unnest((data->'entry')::JSON[]) AS entry
        FROM read_json('{file_path}', format='auto') AS data
      )
    ) LIMIT 0;
  """)

  con.execute(f"""
  INSERT INTO bronze.synthea
  SELECT 
    entry->>'fullUrl' AS full_url,
    entry->>'resource'->>'resourceType' AS resource_type,
    entry->'resource' AS resource,
    entry->'request' AS request,
    '{name}'      AS source_file,
    '{file_id}'   AS file_id
  FROM (
    SELECT unnest((data->'entry')::JSON[]) AS entry
    FROM read_json('{file_path}', format='auto') AS data
  )
  """)

row_count = con.execute(
  "SELECT COUNT(*) FROM bronze.synthea"
).fetchone()[0]
print(f"Synthea ingestion complete: {row_count:,} rows from {len(json_files)} files.")
con.close()



