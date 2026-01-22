# Stage Status

**Current Stage:** 0 — Problem Framing & Contracts
**Last Updated:** 2024-12-17
**Current Sprint:** Week 1

---

## Stage Overview

| Stage | Name | Status | Gate Progress |
|-------|------|--------|---------------|
| 0 | Problem Framing & Contracts | 🔵 In Progress | 2/5 |
| 1 | Bronze Layer (Raw Ingestion) | ⬜ Not Started | 0/7 |
| 2 | Silver Layer (Clinical Semantics) | ⬜ Not Started | 0/6 |
| 3 | Gold Layer (Model-Ready) | ⬜ Not Started | 0/6 |
| 4 | Training & Experimentation | ⬜ Not Started | 0/5 |
| 5 | FHIR RiskAssessment Output | ⬜ Not Started | 0/4 |
| 6 | Packaging & Documentation | ⬜ Not Started | 0/6 |

**Legend:**
⬜ Not Started | 🔵 In Progress | ✅ Complete | 🔴 Blocked

---

## Stage 0: Problem Framing & Contracts

**Status:** 🔵 In Progress
**Target Completion:** Week 1-2

### Gate Criteria

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | Architecture diagram exists | ⬜ | TKT-0-001 proposed |
| 2 | Data contracts defined per layer | ⬜ | TKT-0-002/003/004 proposed |
| 3 | FHIR resource mapping complete | ⬜ | TKT-0-005 proposed |
| 4 | DECISIONS.md initialized | ✅ | 3 decisions logged (DEC-001/002/003) |
| 5 | NON_GOALS.md complete | ✅ | 13 non-goals documented |

### Active Tickets

| Ticket | Title | Status | Owner |
|--------|-------|--------|-------|
| TKT-0-001 | Create Architecture Diagram | Proposed | Developer |
| TKT-0-002 | Define Bronze Layer Data Contract | Proposed | Developer |
| TKT-0-003 | Define Silver Layer Data Contract | Proposed | Developer |
| TKT-0-004 | Define Gold Layer Data Contract | Proposed | Developer |
| TKT-0-005 | Formalize FHIR Resource Mapping | Proposed | Developer |

### Blockers

None currently identified.

### Notes

Stage 0 focuses on establishing contracts and architecture before any code is written. This prevents "build first, design later" anti-patterns.

**Observation (2024-12-17):** Exploratory work exists (`create_db.py`, `explore.ipynb`, `mimic_fhir.duckdb` with 22M+ records) that was done before contracts were formalized. This is acceptable as exploration, but contracts must be defined before this work is considered "Bronze layer complete." The existing code informs the contracts but does not satisfy Stage 0 gate criteria.

---

## Stage 1: Bronze Layer (Raw Ingestion)

**Status:** ⬜ Not Started  
**Target Completion:** Week 2-3

### Gate Criteria

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | Encounter ingestion working | ⬜ | |
| 2 | Patient ingestion working | ⬜ | |
| 3 | Observation (vital signs) ingestion working | ⬜ | |
| 4 | Data immutable and append-only | ⬜ | |
| 5 | Schema versioned | ⬜ | |
| 6 | Load is idempotent | ⬜ | |
| 7 | Row counts validated | ⬜ | |

### Active Tickets

*Stage not started*

### Blockers

Requires Stage 0 completion.

---

## Stage 2: Silver Layer (Clinical Semantics)

**Status:** ⬜ Not Started  
**Target Completion:** Week 3-4

### Gate Criteria

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | Unit normalization implemented | ⬜ | |
| 2 | Time alignment to encounters | ⬜ | |
| 3 | Missingness semantics defined | ⬜ | |
| 4 | Cohort definitions implemented | ⬜ | |
| 5 | Transformations explainable to clinician | ⬜ | |
| 6 | No model-specific logic | ⬜ | |

### Active Tickets

*Stage not started*

### Blockers

Requires Stage 1 completion.

---

## Stage 3: Gold Layer (Model-Ready)

**Status:** ⬜ Not Started  
**Target Completion:** Week 4-5

### Gate Criteria

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | Feature sets defined | ⬜ | |
| 2 | Time windows implemented | ⬜ | |
| 3 | Aggregations complete | ⬜ | |
| 4 | Leakage controls explicit | ⬜ | |
| 5 | Schema frozen | ⬜ | |
| 6 | Feature lineage documented | ⬜ | |

### Active Tickets

*Stage not started*

### Blockers

Requires Stage 2 completion.

---

## Stage 4: Training & Experimentation

**Status:** ⬜ Not Started  
**Target Completion:** Week 5-6

### Gate Criteria

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | Config-driven training | ⬜ | |
| 2 | At least 2 model types tested | ⬜ | |
| 3 | MLflow tracking operational | ⬜ | |
| 4 | Experiments reproducible | ⬜ | |
| 5 | Results traceable to data + code + config | ⬜ | |

### Active Tickets

*Stage not started*

### Blockers

Requires Stage 3 completion.

---

## Stage 5: FHIR RiskAssessment Output

**Status:** ⬜ Not Started  
**Target Completion:** Week 6-7

### Gate Criteria

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | RiskAssessment schema valid | ⬜ | |
| 2 | Provenance fields populated | ⬜ | |
| 3 | Confidence/uncertainty encoded | ⬜ | |
| 4 | Semantics clinically defensible | ⬜ | |

### Active Tickets

*Stage not started*

### Blockers

Requires Stage 4 completion.

---

## Stage 6: Packaging & Documentation

**Status:** ⬜ Not Started  
**Target Completion:** Week 7-8

### Gate Criteria

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | One-command setup works | ⬜ | |
| 2 | Sample run documented | ⬜ | |
| 3 | Architecture narrative complete | ⬜ | |
| 4 | Failure modes documented | ⬜ | |
| 5 | "How to extend" guide exists | ⬜ | |
| 6 | Model card complete | ⬜ | |

### Active Tickets

*Stage not started*

### Blockers

Requires Stage 5 completion.

---

## Weekly Status Log

### Week 1 — Project Setup

**Hours Spent:** TBD / 30
**Focus:** Agent system setup, project documentation, data exploration

**Accomplishments:**
- Agent system designed and documented (AGENTS.md, 6 agent personas)
- Core project documentation created (CLAUDE.md, handbook docs)
- Stage gate criteria defined (7 stages, 39 total criteria)
- IMPLEMENTATION_GUIDE.md created (comprehensive methodology reference)
- Exploratory data ingestion completed (10 FHIR resource types, 22M+ records)
- DuckDB database created (mimic_fhir.duckdb, 1.1 GB)
- 5 Stage 0 tickets proposed (TKT-0-001 through TKT-0-005)

**Current State:**
- Stage 0: 2/5 gate criteria complete
- 5 tickets proposed, awaiting PI approval
- Estimated remaining effort for Stage 0: ~4 shifts (16 hours)

**Blockers:**
- None

**Key Observation:**
Exploratory work (`create_db.py`) was done before contracts were formalized. This informs the contracts but creates a sequencing debt — contracts must now be written to match/refine what exists rather than driving implementation. Acceptable for MVP but noted.

**Next Actions:**
- PI to approve proposed tickets
- Execute TKT-0-001 through TKT-0-005
- Pass Stage 0 gate
- Begin Stage 1 (Bronze layer formalization)

---

*This document is maintained by Orchestrator. Updated at minimum weekly.*
