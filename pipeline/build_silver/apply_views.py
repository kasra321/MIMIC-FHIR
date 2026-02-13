# pipeline/build_silver/apply_views.py
import duckdb
import os
import glob

db_path = os.environ["DUCKDB_PATH"]
con = duckdb.connect(db_path)

con.execute("CREATE SCHEMA IF NOT EXISTS silver;")

sql_files = glob.glob(
    os.path.join(os.path.dirname(__file__), "sql", "*.sql")
)
for sql_file in sorted(sql_files):
    print(f"Applying {os.path.basename(sql_file)}...")
    with open(sql_file, "r") as f:
        con.execute(f.read())

print("Silver transformation complete.")
con.close()
