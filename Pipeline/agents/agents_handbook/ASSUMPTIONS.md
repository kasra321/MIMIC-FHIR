# Assumptions Register

This document records clinical and technical assumptions that underlie the pipeline. Explicit assumptions enable validation and support portability assessment.

## Why Document Assumptions

1. **Transparency:** Others can evaluate if assumptions hold in their context
2. **Portability:** Assumptions that rely on MIMIC-specific patterns limit generalizability
3. **Debugging:** When something fails, check if an assumption was violated
4. **Clinical validity:** Ensures clinical logic is reviewable by domain experts

## Assumption Entry Format

```markdown
## ASM-[NUMBER]: [Title]

**Category:** [Clinical | Technical | Data | Process]
**Confidence:** [High | Medium | Low]
**MIMIC-Specific:** [Yes | No | Unknown]
**Validated:** [Yes | No | Partial]

### Statement
[The assumption in clear, falsifiable terms]

### Rationale
[Why we believe this assumption holds]

### Validation Method
[How we could verify this assumption]

### Violation Impact
[What happens if this assumption is false]

### References
[Supporting documentation, code, or data analysis]
```

---

## Clinical Assumptions

### ASM-001: ED Triage Time is Recorded

**Category:** Clinical  
**Confidence:** High  
**MIMIC-Specific:** Unknown  
**Validated:** Partial

#### Statement
Emergency Department encounters have a recorded triage timestamp that can be derived from the FHIR Encounter resource.

#### Rationale
ED workflow requires triage; MIMIC documentation indicates triage is captured.

#### Validation Method
Query `Encounter.period.start` for ED encounters; verify coverage and plausibility.

#### Violation Impact
If triage time is missing, feature windows cannot be anchored. Would need alternative anchor point.

#### References
- MIMIC-IV-ED documentation
- TBD: Bronze layer validation query

---

### ASM-002: Vital Signs Have Standard LOINC Codes

**Category:** Clinical  
**Confidence:** High  
**MIMIC-Specific:** No  
**Validated:** No

#### Statement
Vital sign observations use standard LOINC codes:
- Heart Rate: 8867-4
- Systolic BP: 8480-6
- Diastolic BP: 8462-4
- Respiratory Rate: 9279-1
- Temperature: 8310-5
- SpO2: 2708-6

#### Rationale
FHIR standard practice; MIMIC-IV FHIR documentation indicates LOINC usage.

#### Validation Method
Query distinct `Observation.code.coding.code` for vital sign observations; verify match.

#### Violation Impact
If codes differ, filtering logic fails. Would need code mapping layer.

#### References
- LOINC vital signs panel: https://loinc.org/85353-1/
- TBD: Bronze layer code inventory

---

### ASM-003: Admission Outcome is Unambiguous

**Category:** Clinical  
**Confidence:** High  
**MIMIC-Specific:** Partial  
**Validated:** No

#### Statement
ED encounters result in one of two outcomes: discharged home or admitted to inpatient. This can be determined from Encounter.hospitalization.dischargeDisposition or related fields.

#### Rationale
Prior MIMIC analysis confirmed clear discharge disposition. However, edge cases exist (AMA, transfers, observation stays).

#### Validation Method
Query discharge disposition distribution; verify binary classification is clinically valid.

#### Violation Impact
If outcome is ambiguous, label quality degrades. Would need explicit exclusion criteria or multi-class approach.

#### References
- Prior MIMIC-IV analysis (PI's exploratory work)
- TBD: Label distribution analysis

---

### ASM-004: Vital Signs Are Temporally Ordered

**Category:** Clinical  
**Confidence:** Medium  
**MIMIC-Specific:** Unknown  
**Validated:** No

#### Statement
Observation.effectiveDateTime reflects the actual measurement time, and observations are not backdated or documented retrospectively in ways that affect temporal ordering.

#### Rationale
Vital signs are typically charted at measurement time in ED settings.

#### Validation Method
Check for temporal anomalies (e.g., vitals documented before encounter start).

#### Violation Impact
If vitals are backdated, temporal features could leak future information. Would need temporal validation layer.

#### References
- TBD: Temporal validation in silver layer

---

## Technical Assumptions

### ASM-005: FHIR References Resolve Correctly

**Category:** Technical  
**Confidence:** High  
**MIMIC-Specific:** No  
**Validated:** No

#### Statement
FHIR resource references (e.g., Observation.subject, Observation.encounter) correctly link to target resources that exist in the dataset.

#### Rationale
FHIR export tooling should maintain referential integrity.

#### Validation Method
Join operations on reference fields; verify match rate.

#### Violation Impact
If references are broken, joins fail. Would need reference resolution layer.

#### References
- TBD: Bronze layer referential integrity tests

---

### ASM-006: NDJSON Format is Consistent

**Category:** Technical  
**Confidence:** High  
**MIMIC-Specific:** Unknown  
**Validated:** No

#### Statement
MIMIC-IV FHIR export uses well-formed NDJSON with one resource per line, consistent field structure within resource types.

#### Rationale
Standard FHIR bulk export format.

#### Validation Method
Parse sample files; check for parsing errors.

#### Violation Impact
If format inconsistent, bronze ingestion fails. Would need robust parsing with error handling.

#### References
- TBD: Bronze ingestion error rates

---

### ASM-007: DuckDB Handles MIMIC Scale

**Category:** Technical  
**Confidence:** High  
**MIMIC-Specific:** No  
**Validated:** Partial

#### Statement
DuckDB can process full MIMIC-IV FHIR dataset (estimated: ~500K encounters, ~millions of observations) on a laptop with 16GB+ RAM.

#### Rationale
DuckDB designed for analytical workloads; MIMIC is not "big data" by modern standards.

#### Validation Method
Load full dataset; measure memory usage and query times.

#### Violation Impact
If DuckDB can't handle scale, would need query optimization or dataset sampling.

#### References
- DuckDB benchmarks
- TBD: Full load performance test

---

## Data Assumptions

### ASM-008: Null Semantics are Consistent

**Category:** Data  
**Confidence:** Medium  
**MIMIC-Specific:** Unknown  
**Validated:** No

#### Statement
Missing values in FHIR resources are represented consistently (field absent vs. field present with null value) and have consistent meaning.

#### Rationale
FHIR spec defines optionality; implementation may vary.

#### Validation Method
Analyze null patterns across resource types; verify handling matches expectation.

#### Violation Impact
If null semantics vary, transformations may mishandle missing data. Would need explicit null handling layer.

#### References
- TBD: Null pattern analysis

---

### ASM-009: Time Zones are Consistent

**Category:** Data  
**Confidence:** Medium  
**MIMIC-Specific:** Partial  
**Validated:** No

#### Statement
All timestamps in MIMIC-IV FHIR are in a consistent time zone (likely UTC or local Boston time) without mixed representations.

#### Rationale
Single-institution data should have consistent time handling.

#### Validation Method
Parse timestamp formats; check for time zone specifiers; verify temporal ordering.

#### Violation Impact
If time zones inconsistent, temporal windows could be wrong. Would need time zone normalization layer.

#### References
- MIMIC-IV documentation
- TBD: Timestamp format inventory

---

## Process Assumptions

### ASM-010: Solo Developer Can Maintain Discipline

**Category:** Process  
**Confidence:** Medium  
**MIMIC-Specific:** N/A  
**Validated:** Ongoing

#### Statement
The agent system and documented processes provide sufficient structure for a solo developer to maintain architectural discipline.

#### Rationale
Agent system designed explicitly for this purpose.

#### Validation Method
Track decision logging compliance; monitor scope creep; review at stage gates.

#### Violation Impact
If discipline fails, technical debt accumulates. Mitigation: external review checkpoint.

#### References
- AGENTS.md
- Weekly status reviews

---

## Validation Tracking

| Assumption | Validation Status | Notes |
|------------|-------------------|-------|
| ASM-001 | Partial | Need bronze query |
| ASM-002 | No | Pending bronze inventory |
| ASM-003 | No | Pending label analysis |
| ASM-004 | No | Pending temporal validation |
| ASM-005 | No | Pending integrity tests |
| ASM-006 | No | Pending parse tests |
| ASM-007 | Partial | Small scale tested |
| ASM-008 | No | Pending null analysis |
| ASM-009 | No | Pending timestamp check |
| ASM-010 | Ongoing | Process assumption |

---

*This document is maintained by Advisor. Assumptions should be validated as implementation progresses.*
