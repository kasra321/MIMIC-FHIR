# Architectural Decision Log

This document records significant architectural and design decisions with their rationale. It serves as institutional memory for the project.

## Decision Entry Format

```markdown
## DEC-[NUMBER]: [Title]

**Date:** [YYYY-MM-DD]
**Status:** [Proposed | Accepted | Superseded | Deprecated]
**Supersedes:** [DEC-XXX if applicable]

### Context
[What situation or problem prompted this decision?]

### Decision
[What was decided?]

### Rationale
[Why was this decision made? What alternatives were considered?]

### Consequences
[What are the implications? What trade-offs were accepted?]

### Risks
[What could go wrong? Link to RISKS.md entries if applicable]

### Revisit Criteria
[Under what conditions should this decision be reconsidered?]
```

---

## Decisions

### DEC-001: Stage-Gate Development Model

**Date:** 2024-XX-XX  
**Status:** Accepted

#### Context
The project needs a development methodology that enforces discipline while remaining lightweight for a solo developer with limited time (30 hrs/week).

#### Decision
Adopt a 7-stage gate model (Stage 0-6) where each stage must pass explicit gate criteria before advancing.

#### Rationale
- Prevents "everything at once" chaos common in solo projects
- Creates natural checkpoints for reflection
- Aligns with the project's emphasis on trust and auditability
- Gate criteria are verifiable, not subjective

#### Consequences
- Slower initial progress (can't skip ahead)
- More explicit planning required
- Clearer progress visibility
- Natural documentation points

#### Risks
- Gate criteria might be wrong (see RISKS.md)
- Temptation to skip gates under time pressure

#### Revisit Criteria
- If a gate blocks progress for >2 weeks without resolution
- If gate criteria prove unmeasurable

---

### DEC-002: FHIR-In → FHIR-Out Design Language

**Date:** 2024-XX-XX  
**Status:** Accepted

#### Context
The project could output predictions in various formats (JSON, CSV, custom schema). Need to decide output format philosophy.

#### Decision
All pipeline outputs that represent clinical predictions must be valid FHIR resources (specifically RiskAssessment).

#### Rationale
- Aligns with interoperability goals
- Proves the "FHIR-native" claim
- Enables integration with other FHIR-aware systems
- Forces disciplined output schema design

#### Consequences
- More complex output generation
- Must learn FHIR RiskAssessment specification
- Output validation required
- May limit some output flexibility

#### Risks
- FHIR RiskAssessment may not capture all needed semantics
- Performance overhead for FHIR serialization

#### Revisit Criteria
- If RiskAssessment proves inadequate for prediction output
- If FHIR overhead impacts usability

---

### DEC-003: Local-First with DuckDB

**Date:** 2024-XX-XX  
**Status:** Accepted

#### Context
Need to choose a database strategy that supports local development while maintaining cloud portability.

#### Decision
Use DuckDB as the primary database for all local development, with Delta Lake for table storage format.

#### Rationale
- Zero infrastructure (embedded database)
- Excellent analytical performance
- Delta Lake provides ACID and versioning
- SQLMesh can transpile to BigQuery later
- Reduces dependency complexity

#### Consequences
- Some SQL features may differ from production target
- Delta Lake adds dependency
- Must validate BigQuery compatibility of critical queries

#### Risks
- DuckDB-specific behaviors might not translate
- Delta Lake ecosystem still maturing

#### Revisit Criteria
- If critical query fails BigQuery transpilation
- If DuckDB performance becomes blocking

---

*Additional decisions will be logged as the project progresses.*
