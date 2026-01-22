# Technical Executive Implementation Guide

## FHIR-Native MLOps Pipeline for Clinical AI

**Version:** 0.1 (MVP)
**Classification:** Technical Implementation Reference
**Audience:** Technical reviewers, clinical informaticists, future contributors

---

## Executive Summary

This document provides a comprehensive technical guide for implementing a FHIR-native Machine Learning Operations (MLOps) pipeline designed for clinical AI applications. The project demonstrates that reproducible, auditable ML infrastructure is achievable for healthcare applications while maintaining strict adherence to interoperability standards.

### North Star Objective

> A reference-grade, locally runnable, FHIR-native MLOps pipeline whose primary product is **trust**, not performance.

The pipeline prioritizes:
- **Explainable design decisions** over optimization
- **Predictable failure modes** over silent errors
- **Documented limitations** over false confidence
- **Reproducibility** over raw performance metrics

### Success Metric

*Can an external technical + clinical reviewer understand why this pipeline behaves the way it does—even when it breaks?*

---

## 1. Project Scope

### 1.1 What This Project IS

| Characteristic | Description |
|----------------|-------------|
| Reference Implementation | Demonstrates FHIR-native MLOps patterns |
| Proof of Concept | Validates reproducible, auditable infrastructure is buildable |
| Learning Instrument | Educational resource for healthcare ML systems |
| Open-Source Ready | Designed for community contribution |

### 1.2 What This Project IS NOT

| Exclusion | Rationale |
|-----------|-----------|
| Production Platform | MVP scope; lacks governance, monitoring |
| SOTA Performance Demo | Trust over metrics |
| Comprehensive MLOps | Focused vertical slice |
| Real-time System | Batch processing only |

### 1.3 Explicit Non-Goals (v0.1)

The following are intentionally excluded from MVP scope:

**Infrastructure:**
- Cloud deployment (NG-001)
- Real-time serving (NG-002)
- Governance enforcement (NG-003)

**Data:**
- Non-vital-sign data types (NG-004)
- Multi-source validation (NG-005)
- External data integration (NG-006)

**Model:**
- SOTA performance pursuit (NG-007)
- Mandatory deep learning (NG-008)
- Explainability infrastructure (NG-009)

**Output:**
- User interfaces (NG-010)
- Alerting systems (NG-011)

**Process:**
- CI/CD pipelines (NG-012)
- Formal code review (NG-013)

---

## 2. Use Case: ED Admission Prediction

### 2.1 Clinical Problem

Predicting hospital admission from Emergency Department vital signs.

### 2.2 Use Case Rationale

| Property | Value | Benefit |
|----------|-------|---------|
| Ambiguity | Low | Clear definitions, standard units |
| Data Source | Machine-generated | Reduced transcription errors |
| Frequency | High | Dense time series available |
| Missingness | Low | Routinely captured in ED |
| Outcome | Binary | Admitted vs. discharged is unambiguous |

### 2.3 Data Source

**MIMIC-IV on FHIR v2.1** — A FHIR-compliant restructuring of the Medical Information Mart for Intensive Care IV, including the Emergency Department module.

| Dataset | Source | Size |
|---------|--------|------|
| MIMIC-IV | PhysioNet | ~60,000 patients |
| MIMIC-IV-ED | PhysioNet | ED encounters |
| FHIR Format | NDJSON (gzip) | 29.2 GB uncompressed |

---

## 3. Technical Architecture

### 3.1 Core Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Local-first** | Runs on laptop, translates to cloud |
| **Code-first** | Version-controllable, testable, debuggable |
| **Separation of concerns** | Distinct stages with explicit interfaces |
| **Declarative** | SQL models declaring outputs |
| **Auditability by default** | Every transformation versioned |
| **Lean and intentional** | Start simple, build up |

### 3.2 FHIR-In → FHIR-Out Design Language

```
┌─────────────────────────────────────────────────────────────────┐
│                     FHIR BOUNDARY                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FHIR Resources (NDJSON)                                        │
│  ├── MimicPatient                                               │
│  ├── MimicEncounterED                                           │
│  ├── MimicObservationVitalSignsED                               │
│  └── MimicConditionED                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                            │
│  │   BRONZE LAYER  │  Raw FHIR ingestion (immutable)            │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                            │
│  │   SILVER LAYER  │  Clinical semantics (normalized)           │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                            │
│  │   GOLD LAYER    │  Model-ready features (frozen)             │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                            │
│  │   ML TRAINING   │  Config-driven, reproducible               │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼                                                     │
│  FHIR RiskAssessment                                            │
│  └── Provenance, confidence, clinical semantics                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     FHIR BOUNDARY                               │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Technology Stack

| Layer | Tool | Version | Rationale |
|-------|------|---------|-----------|
| Database | DuckDB | ≥1.4.3 | Embedded, no server, excellent analytics |
| Storage | Delta Lake | - | ACID, versioning, local + cloud |
| Transformation | SQLMesh | - | SQL-native, dialect-portable |
| Orchestration | Dagster | - | Software-defined assets, lineage |
| Notebooks | Marimo | - | Reactive, version-controllable |
| Training | PyTorch | - | Flexibility + production path |
| Tracking | MLflow | - | Essential capabilities, minimal config |

### 3.4 Current Implementation Status

```python
# Active dependencies (pyproject.toml)
dependencies = [
    "duckdb>=1.4.3",
    "jupyter>=1.1.1",
    "pandas>=2.3.3",
]
```

**Database:** `mimic_fhir.duckdb` (1.1 GB) with ED-focused FHIR resources loaded.

---

## 4. Medallion Data Architecture

### 4.1 Bronze Layer (Raw Ingestion)

**Purpose:** Immutable, append-only storage of raw FHIR resources.

| Property | Requirement |
|----------|-------------|
| Immutability | No in-place updates |
| Schema Versioning | Track FHIR profile versions |
| Idempotency | Re-runs produce identical state |
| Validation | Row count verification |

**Current Implementation:**

```python
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
```

### 4.2 Silver Layer (Clinical Semantics)

**Purpose:** Clinically meaningful, normalized data.

| Transformation | Description |
|----------------|-------------|
| Unit Normalization | Standard units (Celsius, mmHg, etc.) |
| Time Alignment | Anchor to encounter timeline |
| Missingness Semantics | Explicit handling strategy |
| Cohort Definition | Inclusion/exclusion criteria |

**Critical Assumptions:**
- Vital signs use standard LOINC codes (ASM-002)
- Timestamps are temporally ordered (ASM-004)
- FHIR references resolve correctly (ASM-005)

### 4.3 Gold Layer (Model-Ready)

**Purpose:** Frozen, documented feature sets ready for training.

| Property | Requirement |
|----------|-------------|
| Feature Definitions | Explicit, documented |
| Time Windows | Configurable, leakage-safe |
| Aggregations | Clinically meaningful |
| Schema Freeze | No changes during training |
| Lineage | Full provenance tracking |

### 4.4 FHIR RiskAssessment Output

**Purpose:** FHIR-compliant prediction output.

**Resource Structure:**
```json
{
  "resourceType": "RiskAssessment",
  "subject": {"reference": "Patient/12345"},
  "encounter": {"reference": "Encounter/67890"},
  "prediction": [{
    "outcome": {"text": "Hospital Admission"},
    "probabilityDecimal": 0.73,
    "whenRange": {"high": {"value": 24, "unit": "hours"}}
  }],
  "basis": [
    {"reference": "Observation/vital-1"},
    {"reference": "Observation/vital-2"}
  ],
  "method": {"coding": [{"code": "logistic-regression-v1"}]}
}
```

---

## 5. MIMIC-IV on FHIR Data Model

### 5.1 ED-Relevant Profiles

| Profile | Source Table | Description |
|---------|--------------|-------------|
| MimicPatient | patients | Demographics (age, gender) |
| MimicEncounterED | edstays | ED stay details, disposition |
| MimicObservationVitalSignsED | vitalsign, triage | HR, BP, RR, Temp, SpO2 |
| MimicObservationED | vitalsign, triage | Pain, heart rhythm |
| MimicConditionED | diagnosis | ICD diagnoses |
| MimicProcedureED | triage | Triage events |
| MimicMedicationDispenseED | pyxis | Medication dispensing |
| MimicMedicationStatementED | medrecon | Medication history |

### 5.2 Key FHIR Elements for Vital Signs

| Vital Sign | LOINC Code | FHIR Path |
|------------|------------|-----------|
| Heart Rate | 8867-4 | `Observation.code.coding.code` |
| Systolic BP | 8480-6 | `Observation.code.coding.code` |
| Diastolic BP | 8462-4 | `Observation.code.coding.code` |
| Respiratory Rate | 9279-1 | `Observation.code.coding.code` |
| Temperature | 8310-5 | `Observation.code.coding.code` |
| SpO2 | 2708-6 | `Observation.code.coding.code` |

### 5.3 Encounter-Outcome Linkage

```sql
SELECT
    p.id AS patient_id,
    e.period.start AS admission_time,
    e.hospitalization.dischargeDisposition.coding[1].code AS disposition
FROM patient p
JOIN encounter e
    ON e.subject.reference = 'Patient/' || p.id::VARCHAR
```

---

## 6. Multi-Agent Governance System

### 6.1 Architecture Overview

```
                         ┌─────────────────┐
                         │   PI (Human)    │
                         │ Final Authority │
                         └────────┬────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
   │   ADVISOR    │       │ ORCHESTRATOR │       │  DEVELOPER   │
   │              │       │              │       │              │
   │ Architecture │       │ Stage gates  │       │ Code/tests   │
   │ Decisions    │       │ Tickets      │       │ Contracts    │
   │ Risk         │       │ Timeline     │       │              │
   └──────────────┘       └──────────────┘       └──────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                          ┌───────┴───────┐
                          │ SOURCE OF     │
                          │ TRUTH         │
                          │ (Filesystem)  │
                          └───────┬───────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
   │    CRITIC    │       │  HISTORIAN   │       │    TESTER    │
   │              │       │              │       │              │
   │ Briefing-    │       │ Reads stable │       │ Edge cases   │
   │ based only   │       │ artifacts    │       │ Stress tests │
   └──────────────┘       └──────────────┘       └──────────────┘
```

### 6.2 Core Agents (Trusted, Free-Roam)

| Agent | Role | Artifacts |
|-------|------|-----------|
| **Advisor** | Skeptical Staff Engineer + Clinical Informaticist | DECISIONS.md, RISKS.md, NON_GOALS.md, ASSUMPTIONS.md |
| **Orchestrator** | No-nonsense Product Manager | STAGE_STATUS.md, ROADMAP.md, tickets/ |
| **Developer** | Disciplined Staff ML Engineer | Code, tests, contracts |

### 6.3 Contextual Agents (Invocation-Only)

| Agent | Role | Trigger |
|-------|------|---------|
| **Critic** | Skeptical External Reviewer | Delphi reviews, major decisions |
| **Historian** | Technical Writer | Feature completion, stage gates |
| **Tester** | QA Engineer | Stable code verification |

### 6.4 Agent Interaction Protocol

**Core Rule:** Agents never communicate directly. All information flows through documented artifacts in the filesystem.

**Delphi Review Process (Major Decisions):**
1. Frame the decision clearly
2. Gather independent perspectives from each core agent
3. Invoke Critic with controlled briefing
4. Synthesize agreements and disagreements
5. Challenge round with agent responses
6. PI makes final decision, logged with all perspectives

---

## 7. Stage-Gate Development Model

### 7.1 Stage Overview

| Stage | Name | Gate Criteria Count | Target Week |
|-------|------|---------------------|-------------|
| 0 | Problem Framing & Contracts | 5 | 1-2 |
| 1 | Bronze Layer (Raw Ingestion) | 7 | 2-3 |
| 2 | Silver Layer (Clinical Semantics) | 6 | 3-4 |
| 3 | Gold Layer (Model-Ready) | 6 | 4-5 |
| 4 | Training & Experimentation | 5 | 5-6 |
| 5 | FHIR RiskAssessment Output | 4 | 6-7 |
| 6 | Packaging & Documentation | 6 | 7-8 |

### 7.2 Gate Criteria Details

#### Stage 0: Problem Framing & Contracts
- [ ] Architecture diagram exists
- [ ] Data contracts defined per layer
- [ ] FHIR resource mapping complete
- [x] DECISIONS.md initialized
- [x] NON_GOALS.md complete

#### Stage 1: Bronze Layer
- [ ] Encounter ingestion working
- [ ] Patient ingestion working
- [ ] Observation (vital signs) ingestion working
- [ ] Data immutable and append-only
- [ ] Schema versioned
- [ ] Load is idempotent
- [ ] Row counts validated

#### Stage 2: Silver Layer
- [ ] Unit normalization implemented
- [ ] Time alignment to encounters
- [ ] Missingness semantics defined
- [ ] Cohort definitions implemented
- [ ] Transformations explainable to clinician
- [ ] No model-specific logic

#### Stage 3: Gold Layer
- [ ] Feature sets defined
- [ ] Time windows implemented
- [ ] Aggregations complete
- [ ] Leakage controls explicit
- [ ] Schema frozen
- [ ] Feature lineage documented

#### Stage 4: Training & Experimentation
- [ ] Config-driven training
- [ ] At least 2 model types tested
- [ ] MLflow tracking operational
- [ ] Experiments reproducible
- [ ] Results traceable to data + code + config

#### Stage 5: FHIR RiskAssessment Output
- [ ] RiskAssessment schema valid
- [ ] Provenance fields populated
- [ ] Confidence/uncertainty encoded
- [ ] Semantics clinically defensible

#### Stage 6: Packaging & Documentation
- [ ] One-command setup works
- [ ] Sample run documented
- [ ] Architecture narrative complete
- [ ] Failure modes documented
- [ ] "How to extend" guide exists
- [ ] Model card complete

---

## 8. Risk Management Framework

### 8.1 Active Risks

| ID | Risk | Likelihood | Impact | Priority | Owner |
|----|------|------------|--------|----------|-------|
| RISK-001 | FHIR Implementation Variability | Medium | Medium | High | Advisor |
| RISK-002 | Time Budget Exhaustion | Medium | High | High | Orchestrator |
| RISK-003 | Tooling Learning Curve | Medium | Medium | Medium | Developer |
| RISK-004 | Solo Developer Blind Spots | High | Medium | High | PI + Agents |
| RISK-005 | MIMIC-IV Data Quality Issues | Low | Medium | Medium | Advisor |
| RISK-006 | Scope Creep | High | Medium | High | Orchestrator |

### 8.2 Mitigation Strategies

**RISK-001 (FHIR Variability):**
- Document all MIMIC-specific assumptions
- Flag MIMIC-specific transformations
- Design for spec compliance, not MIMIC compliance

**RISK-002 (Time Exhaustion):**
- Aggressive scope management via NON_GOALS.md
- Half-day ticket sizing
- Weekly burn rate checks
- Pre-identify scope cuts

**RISK-004 (Blind Spots):**
- Agent system provides structured pushback
- Mandatory Delphi reviews for major decisions
- All decisions logged in DECISIONS.md

**RISK-006 (Scope Creep):**
- NON_GOALS.md as explicit boundary
- Orchestrator scope-checks all work
- Future work backlog for good ideas

---

## 9. Assumptions Register

### 9.1 Clinical Assumptions

| ID | Assumption | Confidence | MIMIC-Specific | Validated |
|----|------------|------------|----------------|-----------|
| ASM-001 | ED Triage time is recorded | High | Unknown | Partial |
| ASM-002 | Vital signs have standard LOINC codes | High | No | No |
| ASM-003 | Admission outcome is unambiguous | High | Partial | No |
| ASM-004 | Vital signs are temporally ordered | Medium | Unknown | No |

### 9.2 Technical Assumptions

| ID | Assumption | Confidence | MIMIC-Specific | Validated |
|----|------------|------------|----------------|-----------|
| ASM-005 | FHIR references resolve correctly | High | No | No |
| ASM-006 | NDJSON format is consistent | High | Unknown | No |
| ASM-007 | DuckDB handles MIMIC scale | High | No | Partial |
| ASM-008 | Null semantics are consistent | Medium | Unknown | No |
| ASM-009 | Time zones are consistent | Medium | Partial | No |

### 9.3 Validation Priority

Assumptions should be validated during Bronze layer implementation through explicit data quality tests.

---

## 10. Accepted Architectural Decisions

### DEC-001: Stage-Gate Development Model

**Decision:** Adopt a 7-stage gate model (Stage 0-6) where each stage must pass explicit gate criteria before advancing.

**Rationale:**
- Prevents "everything at once" chaos
- Creates natural checkpoints for reflection
- Gate criteria are verifiable, not subjective

**Consequences:**
- Slower initial progress
- Clearer progress visibility

### DEC-002: FHIR-In → FHIR-Out Design Language

**Decision:** All pipeline outputs representing clinical predictions must be valid FHIR resources (specifically RiskAssessment).

**Rationale:**
- Aligns with interoperability goals
- Proves the "FHIR-native" claim
- Forces disciplined output schema design

**Consequences:**
- More complex output generation
- Must learn FHIR RiskAssessment specification

### DEC-003: Local-First with DuckDB

**Decision:** Use DuckDB as the primary database for all local development, with Delta Lake for table storage format.

**Rationale:**
- Zero infrastructure (embedded database)
- SQLMesh can transpile to BigQuery later
- Reduces dependency complexity

**Consequences:**
- Some SQL features may differ from production target
- Must validate BigQuery compatibility of critical queries

---

## 11. Implementation Roadmap

### 11.1 Timeline Overview

```
Week 1   Week 2   Week 3   Week 4   Week 5   Week 6   Week 7   Week 8
  │        │        │        │        │        │        │        │
  ├──Stage 0──┤                                                   │
  │ Framing   │                                                   │
  │           ├──Stage 1──┤                                       │
  │           │ Bronze    │                                       │
  │           │           ├──Stage 2──┤                           │
  │           │           │ Silver    │                           │
  │           │           │           ├──Stage 3──┤               │
  │           │           │           │ Gold      │               │
  │           │           │           │           ├──Stage 4──┤   │
  │           │           │           │           │ Training  │   │
  │           │           │           │           │           ├──Stage 5──┤
  │           │           │           │           │           │ FHIR Out  │
  │           │           │           │           │           │     ├──Stage 6──┤
  │           │           │           │           │           │     │ Packaging │
```

### 11.2 Milestones

| Milestone | Target | Criteria |
|-----------|--------|----------|
| M1: Contracts Complete | Week 2 | Stage 0 gate passed |
| M2: Data Pipeline Working | Week 3 | Bronze layer ingesting data |
| M3: Clinical Layer Ready | Week 4 | Silver layer transformations complete |
| M4: Features Ready | Week 5 | Gold layer frozen |
| M5: Model Trained | Week 6 | Reproducible training pipeline |
| M6: FHIR Output | Week 7 | Valid RiskAssessment generation |
| M7: MVP Complete | Week 8 | Stage 6 gate passed |

### 11.3 Contingency Planning

**If Behind Schedule:**
1. Reduce model variety (one model type instead of two)
2. Simplify documentation (README-only instead of full docs)
3. Reduce test coverage to critical paths only

**If Ahead of Schedule:**
1. Add Synthea validation
2. Expand model types
3. Create demo notebook

---

## 12. MVP Success Criteria

At completion, success means:

| Criterion | Requirement |
|-----------|-------------|
| **Functional** | End-to-end pipeline runs locally without errors |
| **Reproducible** | Same inputs produce same outputs |
| **Documented** | External reviewer can understand design decisions |
| **Installable** | Stranger can set up and run demo |
| **FHIR-compliant** | RiskAssessment output validates against spec |
| **Honest** | Limitations documented, claims bounded |

---

## 13. Quick Start (Current State)

### 13.1 Prerequisites

- Python ≥3.13
- `uv` package manager (recommended)
- MIMIC-IV FHIR access (PhysioNet credentialed)

### 13.2 Setup

```bash
# Clone and setup
cd Pipeline
uv sync

# Download MIMIC-IV FHIR ED files to Data/
# (Requires PhysioNet credentials)

# Create database
uv run python create_db.py

# Explore data
uv run jupyter notebook explore.ipynb
```

### 13.3 Current Database Schema

```sql
SHOW TABLES;
-- organization, location, patient, encounter, condition,
-- procedure, observation, observation_vital_signs,
-- medication_dispense, medication_statement
```

---

## 14. Workspace Structure

```
Pipeline/
├── CLAUDE.md                 # Project context (agents read this)
├── IMPLEMENTATION_GUIDE.md   # This document
├── chat.md                   # Active conversation log
├── create_db.py              # Bronze layer ingestion script
├── explore.ipynb             # Data exploration notebook
├── mimic_fhir.duckdb         # DuckDB database
├── pyproject.toml            # Python dependencies
├── uv.lock                   # Locked dependencies
├── Data/                     # Raw FHIR NDJSON files
├── Documents/                # Reference documentation
├── agents/                   # Agent system
│   ├── AGENTS.md             # Agent specifications
│   ├── agents_persona/       # Agent definitions
│   │   ├── core/             # Advisor, Orchestrator, Developer
│   │   └── contextual/       # Critic, Historian, Tester
│   ├── agents_handbook/      # Living documents
│   │   ├── DECISIONS.md
│   │   ├── RISKS.md
│   │   ├── NON_GOALS.md
│   │   ├── ASSUMPTIONS.md
│   │   ├── STAGE_STATUS.md
│   │   └── ROADMAP.md
│   ├── agents_tickets/       # Work items
│   └── agents_templates/     # Templates
└── .private/                 # User notes (git/agent ignored)
```

---

## 15. Git Safety Protocol

**Critical Rule:** Agents must NEVER push to the main branch.

| Action | Protocol |
|--------|----------|
| Branch Creation | `agent/{agent-name}/{description}` |
| Pre-Push Check | Verify NOT on main/master |
| Merge to Main | PR required, user approval only |

---

## Appendix A: FHIR Resource Quick Reference

### Vital Signs Observation Structure

```json
{
  "resourceType": "Observation",
  "id": "vital-123",
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "8867-4",
      "display": "Heart rate"
    }]
  },
  "subject": {"reference": "Patient/456"},
  "encounter": {"reference": "Encounter/789"},
  "effectiveDateTime": "2024-01-15T10:30:00Z",
  "valueQuantity": {
    "value": 72,
    "unit": "beats/minute",
    "system": "http://unitsofmeasure.org",
    "code": "/min"
  }
}
```

### Encounter Structure (ED)

```json
{
  "resourceType": "Encounter",
  "id": "789",
  "status": "finished",
  "class": {"code": "EMER"},
  "subject": {"reference": "Patient/456"},
  "period": {
    "start": "2024-01-15T08:00:00Z",
    "end": "2024-01-15T14:30:00Z"
  },
  "hospitalization": {
    "dischargeDisposition": {
      "coding": [{
        "code": "home"
      }]
    }
  }
}
```

---

## Appendix B: Ticket Lifecycle

```
PROPOSED → APPROVED → IN PROGRESS → REVIEW → DONE
    │                      │
    ▼                      ▼
REJECTED                BLOCKED
```

**Naming Convention:** `TKT-[STAGE]-[NUMBER]`

**Sizing Target:** Completable in ~4 hours (half-day shift)

---

## Appendix C: Review Schedule

| Week | Review Type | Focus |
|------|-------------|-------|
| 2 | Stage Gate | Stage 0 → 1 transition |
| 3 | Progress Check | Bronze layer status |
| 4 | Stage Gate + Delphi | Silver design decisions |
| 5 | Progress Check | Gold layer status |
| 6 | Stage Gate | Training pipeline review |
| 7 | Critic Review | External perspective on MVP |
| 8 | Final Review | MVP completeness |

---

*Document Version: 1.0*
*Last Updated: 2024-XX-XX*
*Maintained by: Advisor Agent*
