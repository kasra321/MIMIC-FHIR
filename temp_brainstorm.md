
## Architecture

```
project-root/
├── docker-compose.yml
├── Dockerfile
├── data/                    # ← mounted volume
│   ├── raw/                 # FHIR NDJSON bundles (gitignored, persistent)
│   ├── warehouse/           # DuckDB file(s) live here
│   │   └── mimic_fhir.duckdb
│   └── exports/             # any CSV/parquet extracts
├── pipeline/
│   ├── 01_load/             # Python scripts: NDJSON → DuckDB raw tables
│   │   └── load_fhir.py
│   ├── 02_views/            # SQL-on-FHIR ViewDefinition JSON + runner
│   │   ├── definitions/     # one .json per resource type
│   │   │   ├── patient.json
│   │   │   ├── encounter.json
│   │   │   └── observation.json
│   │   └── apply_views.py   # executes ViewDefs against DuckDB
│   └── 03_models/           # SQLMesh project
│       ├── config.yaml
│       ├── models/
│       │   ├── staging/     # light cleaning, typing
│       │   ├── intermediate/# joins, windowing, feature eng
│       │   └── marts/       # final analytic tables
│       └── audits/
├── notebooks/               # exploratory, reads from same DuckDB
└── scripts/
    └── run_pipeline.sh      # orchestrates 01 → 02 → 03
```

## Key Design Decisions

**Single DuckDB file on the volume.** DuckDB is embedded, so the `.duckdb` file on the mounted volume _is_ your warehouse. No server process needed. Every stage reads/writes to the same file, and it persists across container restarts.

**Three-layer data flow:**

```
FHIR NDJSON  →  Raw JSON tables  →  Flat projections  →  SQLMesh models
  (files)        (load_fhir.py)     (ViewDefinitions)    (staging → marts)
               ┌─────────────────────────────────────────────────────────┐
               │              mimic_fhir.duckdb                         │
               │  raw.*          views.*            stg.* / int.* / marts.*
               └─────────────────────────────────────────────────────────┘
```

Use DuckDB **schemas** to separate layers: `raw`, `views`, `stg`, `int`, `marts`. SQLMesh manages everything from `stg` onward.

**ViewDefinitions as the FHIR-specific layer.** Keep those as standalone JSON files that conform to the SQL-on-FHIR spec. Your `apply_views.py` script reads each definition, translates it to DuckDB SQL (using `json_extract` / `unnest`), and materializes into the `views` schema. This keeps the FHIR logic decoupled from SQLMesh.

**SQLMesh treats `views.*` as external sources.** In `config.yaml`, declare the view-definition outputs as external models so SQLMesh can depend on them without trying to manage them.

## Docker Setup (sketch)

```dockerfile
FROM python:3.11-slim
RUN pip install duckdb sqlmesh pyarrow
WORKDIR /app
COPY pipeline/ ./pipeline/
COPY scripts/ ./scripts/
ENV DUCKDB_PATH=/data/warehouse/mimic_fhir.duckdb
ENTRYPOINT ["bash", "scripts/run_pipeline.sh"]
```

```yaml
# docker-compose.yml
services:
  pipeline:
    build: .
    volumes:
      - ./data:/data
    environment:
      - DUCKDB_PATH=/data/warehouse/mimic_fhir.duckdb
```

## Why This Works Well

- **Portability** — teammates pull the repo, drop NDJSON in `data/raw/`, run `docker compose up`, done.
- **Reproducibility** — SQLMesh gives you plan/apply semantics with column-level lineage, so you can iterate on models without rerunning the full pipeline.
- **No infra overhead** — DuckDB-on-file means zero server management, and the volume mount means you can inspect the DB from the host with DBeaver or a notebook.
- **Clear boundaries** — FHIR parsing (steps 1–2) is isolated from analytics (step 3), so you can swap out the ViewDefinition runner without touching SQLMesh models.

## Data Protection

In the current sketch, the NDJSON files are on the same mounted volume as DuckDB, so technically a buggy script _could_ overwrite them. Simple fix: **mount `data/raw/` as read-only** in the container.

```yaml
services:
  pipeline:
    build: .
    volumes:
      - ./data/raw:/data/raw:ro          # read-only
      - ./data/warehouse:/data/warehouse  # read-write
      - ./data/exports:/data/exports      # read-write
```

Now nothing inside the container can touch the source files. Your load script reads from `/data/raw/` and writes to DuckDB — one-way flow enforced at the mount level.

## Where's the Bronze Layer?

This is the real architectural question. There are two valid approaches:

**Option A: NDJSON files = bronze, DuckDB raw tables = silver**

This treats the files as your immutable landing zone and the DuckDB ingestion as the first transformation (parsing JSON into queryable columnar format). Conceptually clean, but it means your "bronze" isn't queryable — it's just files on disk.

**Option B (recommended): DuckDB raw tables = bronze**

The NDJSON files are your **source/landing zone** — they sit _outside_ the medallion framework entirely. They're the equivalent of files landing in an S3 bucket. Your medallion layers then live entirely inside DuckDB:

```
NDJSON files          DuckDB
(source, immutable)   ┌─────────────────────────────────┐
      │               │  raw.*     → Bronze (1:1 load)   │
      └──load──────►  │  views.*   → Silver (ViewDefs)   │
                      │  marts.*   → Gold (SQLMesh)      │
                      └─────────────────────────────────┘
```

I'd go with Option B because:

- **Bronze should be queryable.** The whole point is that you can audit and reprocess from bronze without going back to files. If you store the raw FHIR JSON as a `JSON` column in DuckDB (one row per resource, with a `resource_type` and `resource_id` column), you get full query access while preserving the original payload byte-for-byte.
- **Bronze should be append-only / immutable-ish.** DuckDB tables with a simple `loaded_at` timestamp give you that. The read-only mount on NDJSON ensures you can always re-derive bronze from source if needed.
- **SQLMesh can manage silver onward.** Bronze stays as a simple load target outside SQLMesh, ViewDefinitions produce silver, and SQLMesh owns everything from staging through marts.

So your `load_fhir.py` becomes very thin — essentially:

```python
# pseudocode
for each ndjson file:
    INSERT INTO raw.fhir_resources (resource_type, resource_id, resource, loaded_at)
    SELECT '{type}', json->>'id', json, now()
    FROM read_ndjson('{file}')
```

That gives you a single bronze table (or one per resource type, your call) that's the foundation for everything downstream, while your NDJSON files remain untouched source-of-truth outside the pipeline.
## The Implication

```
╔══════════════════════╗         ╔═══════════════════════════════╗
║   INGESTION DOMAIN   ║         ║      ANALYTICS DOMAIN         ║
║   (varies by source) ║         ║   (stable, reusable)          ║
║                      ║         ║                               ║
║  MIMIC NDJSON ──►    ║         ║   ViewDefinitions (silver)    ║
║  Live EHR ──────►    ║  Bronze ║   SQLMesh models (gold)       ║
║  Synthea ──────►     ╠════╦════╣   ML feature stores           ║
║  Claims data ───►    ║    ║    ║   Dashboards                  ║
║  Registry data ─►    ║    ║    ║                               ║
╚══════════════════════╝    ║    ╚═══════════════════════════════╝
                            ║
                    FHIR-in-DuckDB
                     (the contract)
```

Everything to the left of the boundary is **source-specific** — each data source gets its own ingestion adapter that knows how to produce conformant Bronze tables. Everything to the right is **source-agnostic** — it only knows FHIR. The two sides can have completely independent dev cycles, versioning, even different teams.

## What the Contract Needs to Specify

For this to work, "FHIR schema loaded as DuckDB" needs to be precise enough that your downstream pipeline can rely on it. I'd formalize it as a small spec:

**Schema contract:** One DuckDB table per FHIR resource type, named predictably (`bronze.Patient`, `bronze.Encounter`, `bronze.Observation`, etc.). Each table has at minimum:

```sql
CREATE TABLE bronze.Observation (
    resource_id   VARCHAR NOT NULL,  -- FHIR resource.id
    resource      JSON    NOT NULL,  -- full FHIR JSON, valid against R4
    loaded_at     TIMESTAMP,
    source_system VARCHAR            -- 'mimic', 'synthea', etc.
);
```

**Validation requirements:** The `resource` column must contain valid FHIR R4 JSON. You could enforce this with a lightweight validator at ingestion time — doesn't need to be full profile validation, but at minimum check that required fields exist and `resourceType` matches the table name.

**Idempotency rule:** Re-running an ingestion adapter for the same source should produce the same Bronze state. This means either full-replace per source or upsert on `(source_system, resource_id)`.

## What This Buys You

**Swappable data sources.** When you want to test your pipeline against Synthea instead of MIMIC, you just write a new ingestion adapter. The downstream pipeline doesn't change at all.

**Testability.** You can validate any ingestion adapter independently — does it produce valid Bronze tables? — without running the full pipeline.

**Collaboration.** A teammate can work on SQLMesh models while you work on ingestion. The Bronze schema is the handshake.

**Future-proofing.** If you eventually want to plug in a live FHIR server (say from an EHR sandbox), the adapter just calls the FHIR API and writes to the same Bronze tables. Your ViewDefinitions and models don't know the difference.

## Revised Project Structure

This shifts the repo organization slightly:

```
project-root/
├── contract/
│   ├── bronze_schema.sql        # DDL for all Bronze tables
│   └── validate_bronze.py       # checks a DuckDB file against contract
├── adapters/                    # one per source, independent
│   ├── mimic_ndjson/
│   │   ├── Dockerfile
│   │   └── load.py
│   └── synthea/
│       └── load.py
├── platform/                    # source-agnostic, stable
│   ├── Dockerfile
│   ├── view_definitions/
│   ├── sqlmesh_project/
│   └── run.sh
├── data/
│   ├── sources/                 # raw files per source (ro mount)
│   │   └── mimic/
│   └── warehouse/
│       └── mimic_fhir.duckdb
└── docker-compose.yml
```

The `contract/` directory is the key addition — it's the formal definition of what Bronze looks like, and both sides of the boundary depend on it. `validate_bronze.py` can be run as a gate between ingestion and analytics: if Bronze doesn't pass validation, the downstream pipeline doesn't run.

## What SQLMesh Gives You

**Virtual environments** — this is the big one. When you create a new environment (like `dev`), SQLMesh doesn't physically duplicate your tables. It creates virtual pointers to the production tables, and only materializes the models you've actually changed. So you can experiment on your `int.vitals_windowed` model without reprocessing all of Bronze and Silver.

```bash
sqlmesh plan dev
# Shows: only 2 models affected, rest are virtual references to prod
# Estimated cost: 45 seconds instead of 20 minutes
```

**Plan/apply workflow** — similar to Terraform. You describe your desired state in SQL models, `sqlmesh plan` shows you exactly what will change (new columns, modified logic, downstream impacts), and `sqlmesh apply` executes it. Nothing runs without you reviewing the diff first.

**Column-level lineage** — SQLMesh parses your SQL and knows that `marts.ed_features.heart_rate_mean` traces back through `int.vitals_windowed` → `views.vitals` → `bronze.Observation`. This is automatic, no annotations needed.

**Built-in DuckDB support** — DuckDB is a first-class SQLMesh engine. No external warehouse, no credentials, just point it at your `.duckdb` file.

## How It Maps to Your Architecture

```
                        SQLMesh manages this
                    ┌──────────────────────────┐
                    │                          │
bronze.*            │  stg.*  →  int.*  →  marts.*
(outside SQLMesh)   │                          │
loaded by adapters  │  virtual environments    │
validated by        │  column-level lineage    │
contract            │  plan/apply deploys      │
                    │  built-in testing        │
                    └──────────────────────────┘
```

Bronze and the ViewDefinition outputs sit as **external models** — SQLMesh knows they exist and depends on them, but doesn't try to manage their creation. Everything from staging onward is fully managed.

## The Part People Underestimate

SQLMesh's `plan` with virtual environments means you can have this workflow:

```bash
# You're working on a new feature engineering model
sqlmesh plan dev
# → "Adding int.medication_embeddings, affects marts.ed_prediction_features"
# → "No other models need recomputation"
sqlmesh apply dev

# Test it, iterate, happy with results
sqlmesh plan prod
# → Shows exact diff from current prod
sqlmesh apply prod
# → Only the changed models recompute, everything else untouched
```

Your teammate could simultaneously be working in their own `dev_alice` environment against the same DuckDB file, touching different models, with zero conflicts until you both merge to prod. That's the virtual layering — it's not copying data, it's managing table versions.

## One Caveat

SQLMesh is opinionated about owning the models it manages. Your ViewDefinitions should stay **outside** SQLMesh as external sources rather than trying to express them as SQLMesh models. The FHIR-specific JSON extraction logic doesn't fit cleanly into SQLMesh's SQL dialect handling, and you want the ViewDefinition layer to remain tied to the FHIR spec, not to your orchestration tool. Clean separation.

```
Adapters          ViewDefinitions (hand-tuned SQL)        SQLMesh
NDJSON → Bronze → ──────────── Silver ──────────── → stg / int / marts
                        ▲
                        │
                  FlatQuack as starting point,
                  then manually fix the output SQL
```

The realistic workflow with FlatQuack is: use it to **generate** the initial SQL from your ViewDefinition JSONs, then treat that output as a draft — fix the quirks, test it, and commit the corrected SQL files. Those become your source of truth for the Silver layer, not FlatQuack itself.

This means your `view_definitions/` directory ends up looking like:

```
view_definitions/
├── specs/              # original FHIR ViewDefinition JSONs (reference)
│   ├── patient.json
│   ├── encounter.json
│   └── observation.json
├── sql/                # the actual SQL that runs (hand-maintained)
│   ├── patient.sql
│   ├── encounter.sql
│   └── observation.sql
└── apply_views.py      # executes sql/*.sql against DuckDB
```

The specs are documentation. The SQL files are what actually run. And `apply_views.py` is just a thin runner that executes them in order and writes to the `views` schema.

Then SQLMesh's `config.yaml` declares those `views.*` tables as external models and everything downstream is fully managed. SQLMesh never touches FHIR JSON, never deals with `json_extract` quirks — it just sees clean flat tables with typed columns.