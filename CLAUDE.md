# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MIMIC-FHIR-MDS is a medallion-architecture data pipeline that transforms MIMIC-IV FHIR NDJSON data into analysis-ready tables using DuckDB. It processes ~15GB of raw FHIR resources through Bronze (raw ingestion) → Silver (flattened vitals) → Gold (SQLMesh analytical models).

## Structure

- `local/` — untracked scratch space for local-only files
- `wiki/` — GitHub Wiki (git submodule), editable via Obsidian or any markdown editor

## Wiki Conventions

Wiki pages live in `wiki/` (submodule linked to the GitHub Wiki at https://github.com/kasra321/MIMIC-FHIR.wiki.git).

The wiki serves as the project's version-controlled knowledge base. The `Home.md` page is the public-facing documentation visible on the GitHub wiki tab. Other branches and pages are used for implementation notes, reports, changelogs, and contextual content that can feed into websites, reports, RAGs, etc.

### Frontmatter

All markdown files in `wiki/` must include YAML frontmatter:

```yaml
---
title: Page Title
description: One-liner summary of the page
tags: []
created: "YYYY-MM-DD"
---
```

- **description**: A single sentence summarizing the page
- **tags**: Use existing tags from Obsidian's tag pane before creating new ones
- **created**: Date the page was first created
- Use the template at `wiki/.obsidian/templates/Default Note.md` for new pages (if available)

### Wikilinks and Assets

- Use `[[wikilinks]]` for internal links between wiki pages
- Store images and attachments in `wiki/assets/`
- Embed images with `![[assets/filename.png]]`

### Obsidian

The `wiki/.obsidian/` folder contains shared vault settings:
- `app.json` — wikilink format, attachment folder (`assets/`)
- `core-plugins.json` — enabled core plugins
- `community-plugins.json` — required community plugins
- `templates/` — note templates

Do not commit `.obsidian/workspace.json` or user-specific settings.

### Pushing Wiki Changes

```bash
git -C wiki add . && git -C wiki commit -m "update wiki" && git -C wiki push
```

### Tag Policy

Tags are for narrowing searches across wiki pages. Current tags:
- `architecture` — pipeline design, technology choices, system structure
- `article` — research writing, EDA findings, academic sections
- `report` — project management, changelogs, reviews, report structure

Rules:
- Only add a new tag if no combination of existing tags can narrow selection to 20 or fewer documents
- Every tag must have 3+ pages assigned — a tag with one page is not a tag
- Prefer `[[wikilinks]]` over tags for connecting related pages
- Use hierarchical tags (e.g., `architecture/decisions`) only when the parent tag alone exceeds 20 pages

### Maintenance

When completing a feature, fixing a bug, or making an architectural decision:
1. Update relevant wiki pages with what changed and why
2. Use `[[wikilinks]]` to cross-reference related pages
3. Keep `Home.md` as a clean public overview; put detailed notes on linked pages
4. Update `wiki/Changelog.md` with what changed

## Commands

### Local Development
```bash
pip install -e .                              # Install package (requires Python 3.11+)
python adapters/mimic/load_bronze.py          # Bronze: ingest NDJSON → DuckDB
python pipeline/validate_bronze.py            # Validate bronze layer
python pipeline/build_silver/apply_views.py   # Silver: flatten vitals via SQL
cd models && sqlmesh plan --auto-apply        # Gold: run SQLMesh transformations
```

### Docker (full pipeline)
```bash
docker compose run ingest                     # Bronze ingestion + validation
docker compose run transform_vitals_eda       # Silver flattening + Gold SQLMesh models
```

### Silver layer (alternative via flatquack)
```bash
python -m src.silver.loader compile           # Compile FHIR ViewDefinitions → SQL
python -m src.silver.loader materialize       # Execute compiled SQL → Parquet
python -m src.silver.loader run               # Both steps
```

### Environment Variables
- `DUCKDB_PATH` — Path to DuckDB warehouse file (default in Docker: `/data/warehouse/mimic_fhir.duckdb`)
- `RAW_DATA_PATH` — Directory containing raw NDJSON/JSON files
- `GITHUB_TOKEN` — GitHub personal access token (for MCP GitHub server)

## Architecture

### Pipeline Stages

1. **Bronze** (`adapters/mimic/load_bronze.py`): Reads NDJSON and Bundle JSON files into `bronze.fhir_resources` DuckDB table. Handles both flat NDJSON and nested Bundle entries via `unnest()`.

2. **Silver** (`pipeline/build_silver/`): SQL scripts in `pipeline/build_silver/sql/` extract 6 vital signs (HR, Temp, RR, SpO2, BP sys/dia) from FHIR Observations using LOINC codes. Creates `silver.obs_vitals` table via `json_extract_string()` parsing.

3. **Gold** (`models/`): SQLMesh models pivot vitals wide (`models/intermediate/vitals_wide.sql`) and add temporal features like delta times, encounter phases, and observation counts (`models/marts/vitals_eda.sql`).

### Key Patterns

- **DuckDB-on-file**: Single embedded database, no server. All layers share one `.duckdb` file with `bronze`/`silver` schemas.
- **FHIR ViewDefinitions** (`specs/*.vd.json`): SQL-on-FHIR spec ViewDefinitions compiled to SQL via `npx flatquack`. Alternative to hand-written silver SQL.
- **SQLMesh external models**: Silver layer declared as external in `models/external_models.yaml` so SQLMesh can reference it without managing it.
- **JSON extraction**: FHIR resources stored as raw JSON in bronze, parsed in silver via DuckDB's `json_extract_string()` and `json_extract()`.

### Data Layout
```
data/raw/          → Source NDJSON files (read-only in Docker)
data/warehouse/    → DuckDB file (bronze + silver schemas)
output/silver/     → Exported Parquet files
local/             → Untracked scratch space
wiki/              → GitHub Wiki submodule (Obsidian vault)
```

## Testing

No formal test framework. Validation is done via:
- `pipeline/validate_bronze.py` — Checks row counts, required columns, null rates (<5%)
- Jupyter notebooks in `notebooks/` — EDA and pipeline verification
