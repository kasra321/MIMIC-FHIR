# Project Roadmap

**Version:** 0.1 (MVP)  
**Timeline:** 6-8 weeks  
**Effort:** 30 hours/week (~180-240 total hours)

---

## High-Level Timeline

```
Week 1   Week 2   Week 3   Week 4   Week 5   Week 6   Week 7   Week 8
  │        │        │        │        │        │        │        │
  ├──Stage 0──┤        │        │        │        │        │        │
  │ Framing   │        │        │        │        │        │        │
  │           ├──Stage 1──┤        │        │        │        │        │
  │           │ Bronze    │        │        │        │        │        │
  │           │           ├──Stage 2──┤        │        │        │        │
  │           │           │ Silver    │        │        │        │        │
  │           │           │           ├──Stage 3──┤        │        │        │
  │           │           │           │ Gold      │        │        │        │
  │           │           │           │           ├──Stage 4──┤        │        │
  │           │           │           │           │ Training  │        │        │
  │           │           │           │           │           ├──Stage 5──┤        │
  │           │           │           │           │           │ FHIR Out  │        │
  │           │           │           │           │           │           ├──Stage 6──┤
  │           │           │           │           │           │           │ Packaging │
  │           │           │           │           │           │           │           │
  └───────────┴───────────┴───────────┴───────────┴───────────┴───────────┴───────────┘
```

---

## Stage Breakdown

### Stage 0: Problem Framing & Contracts (Week 1-2)

**Effort Estimate:** ~30 hours  
**Key Deliverables:**
- Architecture diagram
- Data contracts for all layers
- FHIR resource mapping
- Project documentation

**Critical Path Items:**
- Contract definitions (blocks Stage 1)

**Risk Factors:**
- Underestimating contract complexity
- FHIR resource structure surprises

---

### Stage 1: Bronze Layer (Week 2-3)

**Effort Estimate:** ~30 hours  
**Key Deliverables:**
- Encounter ingestion pipeline
- Patient ingestion pipeline
- Observation ingestion pipeline
- Data quality tests
- Schema versioning

**Critical Path Items:**
- NDJSON parsing (blocks all ingestion)
- Schema contract validation

**Risk Factors:**
- Data format surprises
- DuckDB/Delta Lake integration issues

---

### Stage 2: Silver Layer (Week 3-4)

**Effort Estimate:** ~40 hours  
**Key Deliverables:**
- Unit normalization logic
- Time alignment to encounters
- Missingness handling
- Cohort definitions
- Clinical transformation documentation

**Critical Path Items:**
- Time alignment logic (clinical correctness critical)
- Cohort exclusion criteria

**Risk Factors:**
- Clinical assumption errors
- Complex temporal logic

---

### Stage 3: Gold Layer (Week 4-5)

**Effort Estimate:** ~30 hours  
**Key Deliverables:**
- Feature definitions
- Aggregation logic
- Leakage prevention
- Feature documentation
- Schema freeze

**Critical Path Items:**
- Leakage controls (model validity depends on this)

**Risk Factors:**
- Leakage detection difficulty
- Feature explosion

---

### Stage 4: Training & Experimentation (Week 5-6)

**Effort Estimate:** ~30 hours  
**Key Deliverables:**
- Config-driven training pipeline
- MLflow integration
- Baseline models (logistic regression, XGBoost)
- Reproducibility verification
- Experiment documentation

**Critical Path Items:**
- MLflow setup (blocks experiment tracking)
- Reproducibility tests

**Risk Factors:**
- Environment reproducibility issues
- Configuration management complexity

---

### Stage 5: FHIR RiskAssessment Output (Week 6-7)

**Effort Estimate:** ~20 hours  
**Key Deliverables:**
- RiskAssessment schema implementation
- Provenance generation
- Uncertainty encoding
- Output validation

**Critical Path Items:**
- FHIR schema compliance

**Risk Factors:**
- FHIR RiskAssessment complexity
- Provenance chain completeness

---

### Stage 6: Packaging & Documentation (Week 7-8)

**Effort Estimate:** ~30 hours  
**Key Deliverables:**
- Installation documentation
- Sample run guide
- Architecture narrative
- Failure mode documentation
- Extension guide
- Model card

**Critical Path Items:**
- Installation testing (stranger test)

**Risk Factors:**
- Documentation debt accumulated
- Environment setup complexity

---

## Milestones

| Milestone | Target | Criteria |
|-----------|--------|----------|
| M1: Contracts Complete | Week 2 | Stage 0 gate passed |
| M2: Data Pipeline Working | Week 3 | Bronze layer ingesting data |
| M3: Clinical Layer Ready | Week 4 | Silver layer transformations complete |
| M4: Features Ready | Week 5 | Gold layer frozen |
| M5: Model Trained | Week 6 | Reproducible training pipeline |
| M6: FHIR Output | Week 7 | Valid RiskAssessment generation |
| M7: MVP Complete | Week 8 | Stage 6 gate passed |

---

## Buffer and Contingency

**Built-in Buffer:** ~30 hours (1 week)

**If Behind Schedule:**
1. Reduce model variety (one model type instead of two)
2. Simplify documentation (README-only instead of full docs site)
3. Reduce test coverage to critical paths only

**If Ahead of Schedule:**
1. Add Synthea validation
2. Expand model types
3. Create demo notebook

---

## Dependencies

### External Dependencies
- MIMIC-IV FHIR export (available ✅)
- DuckDB (stable ✅)
- SQLMesh (requires learning)
- MLflow (stable ✅)

### Internal Dependencies
```
Stage 0 ──► Stage 1 ──► Stage 2 ──► Stage 3 ──► Stage 4 ──► Stage 5 ──► Stage 6
                                                              │
                                                              └─► Stage 6 (parallel possible)
```

Stage 6 documentation can partially overlap with Stage 5 for completed components.

---

## Review Points

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

## Success Criteria (MVP)

At Week 8, success means:

1. **Functional:** End-to-end pipeline runs locally without errors
2. **Reproducible:** Same inputs produce same outputs
3. **Documented:** External reviewer can understand design decisions
4. **Installable:** Stranger can set up and run demo
5. **FHIR-compliant:** RiskAssessment output validates against spec
6. **Honest:** Limitations documented, claims bounded

---

*This roadmap is a planning tool, not a commitment. Adjust based on actual progress and learnings.*
