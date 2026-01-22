# CLAUDE.md — FHIR-Native MLOps Project Context

## Project Identity

**Project:** FHIR-Native MLOps Pipeline for Clinical AI  
**Version:** 0.1 (MVP)  
**PI:** Solo developer with MD background + Applied Data Science MS  
**Timeline:** 6-8 weeks  
**Effort:** ~30 hours/week  

## North Star

> **"A reference-grade, locally runnable, FHIR-native MLOps pipeline whose primary product is trust, not performance."**

The primary output is:
- A coherent system
- With explainable design decisions
- That fails predictably
- And whose limitations are documented and intentional

Success metric: *Can an external technical + clinical reviewer understand why this pipeline behaves the way it does—even when it breaks?*

## What This Project IS

- A reference implementation demonstrating FHIR-native MLOps
- A proof that reproducible, auditable infrastructure is buildable
- A learning instrument for healthcare ML systems
- A capstone project that can become open-source

## What This Project IS NOT

- A production platform
- A SOTA model performance demonstration
- A comprehensive MLOps solution
- A real-time serving system

## Core Principles

1. **Local-first with cloud portability** — Runs on laptop, translates to GCS/BigQuery
2. **Code-first, Python-native** — Version-controllable, testable, debuggable
3. **Separation of concerns** — Distinct stages with explicit interfaces
4. **Declarative over imperative** — SQL models declaring outputs, not scripts
5. **Auditability by default** — Every transformation versioned, every run tracked
6. **Lean and intentional** — Start simple, understand pain points, build up

## Technology Stack

| Layer | Tool | Rationale |
|-------|------|-----------|
| Database | DuckDB | Embedded, no server, excellent for analytics |
| Transformation | SQLMesh | SQL-native, dialect-portable, virtual environments |
| Orchestration | Dagster | Software-defined assets, lineage, observability |
| Notebooks | Marimo | Reactive, version-controllable, deployable |
| Training | PyTorch | Flexibility + production path |
| Tracking | MLflow | Essential capabilities, minimal config |
| Storage | Delta Lake | ACID, versioning, local + cloud |

## Use Case: ED Admission Prediction

Predicting hospital admission from emergency department vital signs.

Why this use case:
- Low ambiguity (clear definitions, standard units)
- Machine-generated (reduced transcription errors)
- High frequency (dense time series)
- Low missingness (routinely captured)
- Clear outcomes (admitted vs discharged is unambiguous)

Data source: MIMIC-IV on FHIR (already available locally)

## Stage-Gate Architecture

| Stage | Focus | Gate Criteria |
|-------|-------|---------------|
| 0 | Problem Framing & Contracts | Architecture diagram, data contracts, FHIR mapping |
| 1 | Bronze Layer (Raw Ingestion) | Immutable, append-only, schema versioned |
| 2 | Silver Layer (Clinical Semantics) | Unit normalization, time alignment, missingness handled |
| 3 | Gold Layer (Model-Ready) | Feature sets, windows, leakage controls |
| 4 | Training & Experimentation | Config-driven, reproducible, tracked |
| 5 | FHIR RiskAssessment Output | FHIR-compliant, provenance populated |
| 6 | Packaging & Documentation | Installable, readable, forkable |

## Agent System

This project uses a multi-agent system with two tiers:

### Core Agents (Trusted, Free-Roam)
- **Advisor** — Architecture, decisions, risk, FHIR guidance
- **Orchestrator** — Stage gates, tickets, prioritization, timeline
- **Developer** — Implementation, code, tests, contracts

### Contextual Agents (Invocation-Only)
- **Critic** — External perspective, bias checking (Delphi reviews)
- **Historian** — Documentation generation (feature completion)
- **Tester** — Stress testing, edge cases (stable code)

See `/agents/AGENTS.md` for detailed agent documentation.

## Workspace Structure

```
/
├── chat.md                 # Active conversation with Claude
├── {Active Files}.md       # Files currently in focus
├── Data/                   # Raw data files
├── Documents/              # Reference documents (accessible to agents)
├── .private/               # User notes (ignored by git & agents)
└── agents/                 # All agent-related content
    ├── AGENTS.md
    ├── agents_persona/     # Agent definitions (core/, contextual/)
    ├── agents_handbook/    # Decisions, risks, assumptions, roadmap
    ├── agents_tickets/     # Work items by stage
    └── agents_templates/   # Delphi, ticket, decision templates
```

**Root (Desktop):** Active workspace for focused documents. `chat.md` is the primary conversation surface. User can move files between Root and Documents to bring them in/out of focus.

**Documents:** Persistent reference storage. Agents have full access. Use for materials that inform work but aren't actively being edited.

**Private Archive:** `/.private/` is excluded from both git (`.gitignore`) and Claude Code (`.claudeignore`). User's personal notes, not exposed to agents.

## Key Artifacts

| Artifact | Purpose | Location |
|----------|---------|----------|
| Chat | Conversation with Claude | `/chat.md` |
| Reports | Multi-stage task outputs | `/report_{title}.md` |
| Decisions | Architectural choices | `/agents/agents_handbook/DECISIONS.md` |
| Non-Goals | Scope boundaries | `/agents/agents_handbook/NON_GOALS.md` |
| Risks | Risk register | `/agents/agents_handbook/RISKS.md` |
| Assumptions | Clinical/technical assumptions | `/agents/agents_handbook/ASSUMPTIONS.md` |
| Stage Status | Progress and gate criteria | `/agents/agents_handbook/STAGE_STATUS.md` |
| Roadmap | Timeline | `/agents/agents_handbook/ROADMAP.md` |
| Tickets | Work items | `/agents/agents_tickets/` |

## Obsidian Output

Claude writes outputs to markdown files:

| Output Type | Naming | Example |
|-------------|--------|---------|
| Conversation | `chat.md` | LLM responses to prompts |
| Standalone artifacts | `{Short Title}.md` | `Storage Cost Comparison.md` |
| Multi-stage reports | `report_{title}.md` | `report_bronze_layer.md` |

## Source of Truth

All agents read from and write to the filesystem. The filesystem (git-versioned) is the single source of truth. Agents do not communicate directly—they communicate through documented artifacts.

## Guiding Constraints

- No real-time inference
- No cloud infrastructure deployment (local only)
- No governance enforcement mechanisms
- No performance benchmarking vs SOTA
- FHIR-in → FHIR-out design language
- Modules must be independently swappable

## Git Safety Rules

**CRITICAL: Agents must NEVER push to the main branch.**

- All agent work must happen on feature/test branches
- Branch naming: `agent/{agent-name}/{description}` (e.g., `agent/developer/bronze-layer`)
- Before any git push, verify you are NOT on main/master
- If a branch is needed, create it first — never commit directly to main
- Pull requests required for merging to main (user approval only)
