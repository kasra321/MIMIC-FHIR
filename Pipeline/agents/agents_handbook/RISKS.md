# Risk Register

This document tracks identified risks, their assessment, and mitigation strategies.

## Risk Assessment Framework

**Likelihood:** Low (unlikely) | Medium (possible) | High (probable)  
**Impact:** Low (minor inconvenience) | Medium (significant delay) | High (project failure)  
**Priority:** Likelihood × Impact → Critical / High / Medium / Low

## Risk Entry Format

```markdown
## RISK-[NUMBER]: [Title]

**Status:** [Active | Mitigated | Realized | Closed]
**Likelihood:** [Low | Medium | High]
**Impact:** [Low | Medium | High]
**Priority:** [Critical | High | Medium | Low]
**Owner:** [Who monitors this risk]

### Description
[What could go wrong?]

### Trigger Indicators
[How would we know this is happening?]

### Mitigation Strategy
[What are we doing to reduce likelihood or impact?]

### Contingency Plan
[If this risk realizes, what do we do?]

### History
| Date | Update |
|------|--------|
```

---

## Active Risks

### RISK-001: FHIR Implementation Variability

**Status:** Active  
**Likelihood:** Medium  
**Impact:** Medium  
**Priority:** High  
**Owner:** Advisor

#### Description
MIMIC-IV FHIR export may have implementation-specific patterns that don't generalize to other FHIR sources, limiting portability claims.

#### Trigger Indicators
- Transformations require MIMIC-specific logic
- FHIR resource structures differ from spec in undocumented ways
- SQL on FHIR ViewDefinitions fail on other sources

#### Mitigation Strategy
- Document all MIMIC-specific assumptions in ASSUMPTIONS.md
- Flag any transformation that relies on MIMIC-specific patterns
- Design for spec compliance, not MIMIC compliance

#### Contingency Plan
If portability proves limited: honestly document limitations, scope claims to "MIMIC-compatible FHIR sources"

#### History
| Date | Update |
|------|--------|
| 2024-XX-XX | Risk identified during project planning |

---

### RISK-002: Time Budget Exhaustion

**Status:** Active  
**Likelihood:** Medium  
**Impact:** High  
**Priority:** High  
**Owner:** Orchestrator

#### Description
30 hours/week may prove insufficient to complete MVP scope in 6-8 weeks, especially if unexpected technical challenges emerge.

#### Trigger Indicators
- Consistent inability to close tickets within estimates
- Stage gate criteria taking 2x longer than planned
- Accumulating blocked tickets

#### Mitigation Strategy
- Aggressive scope management via NON_GOALS.md
- Half-day ticket sizing for realistic estimates
- Weekly status checks on burn rate
- Identify scope cuts before crisis

#### Contingency Plan
If time runs out: Document completed stages thoroughly, clearly mark incomplete stages as "future work", ensure what exists is coherent

#### History
| Date | Update |
|------|--------|
| 2024-XX-XX | Risk identified during project planning |

---

### RISK-003: Tooling Learning Curve

**Status:** Active  
**Likelihood:** Medium  
**Impact:** Medium  
**Priority:** Medium  
**Owner:** Developer

#### Description
SQLMesh, Dagster, and Marimo are newer tools with smaller communities. Learning curve and debugging may take longer than with mature alternatives.

#### Trigger Indicators
- Spending >4 hours debugging tool-specific issues
- Documentation gaps blocking progress
- Workarounds accumulating

#### Mitigation Strategy
- Start with simple patterns, add complexity gradually
- Maintain fallback options (could swap to dbt if SQLMesh fails)
- Document tool-specific learnings for future reference

#### Contingency Plan
If tool proves unworkable: Document the failure, swap to mature alternative (dbt for SQLMesh, Jupyter for Marimo), accept migration cost

#### History
| Date | Update |
|------|--------|
| 2024-XX-XX | Risk identified during project planning |

---

### RISK-004: Solo Developer Blind Spots

**Status:** Active  
**Likelihood:** High  
**Impact:** Medium  
**Priority:** High  
**Owner:** PI + Agent System

#### Description
Working alone means no natural pushback on decisions, no external perspective on assumptions, and risk of echo chamber thinking.

#### Trigger Indicators
- Decisions made without documentation
- Clinical assumptions not explicitly stated
- Critic reviews finding obvious gaps

#### Mitigation Strategy
- Agent system provides structured pushback
- Mandatory Delphi reviews for major decisions
- Critic reviews at stage gates
- All decisions logged in DECISIONS.md

#### Contingency Plan
If blind spots cause problems: Seek external review earlier than planned, bring in actual human reviewer for critical stages

#### History
| Date | Update |
|------|--------|
| 2024-XX-XX | Risk identified during project planning |

---

### RISK-005: MIMIC-IV Data Quality Issues

**Status:** Active  
**Likelihood:** Low  
**Impact:** Medium  
**Priority:** Medium  
**Owner:** Advisor

#### Description
Despite prior analysis, undiscovered data quality issues in MIMIC-IV FHIR export could require significant cleaning effort.

#### Trigger Indicators
- Unexpected null rates in critical fields
- Referential integrity failures between resources
- Values outside clinically plausible ranges

#### Mitigation Strategy
- Robust data quality tests at bronze layer
- Clinical plausibility checks at silver layer
- Prior exploratory analysis reduces surprise risk

#### Contingency Plan
If major data issues found: Document as project finding, scope model training to clean subset, report data quality issues upstream

#### History
| Date | Update |
|------|--------|
| 2024-XX-XX | Risk identified during project planning |

---

### RISK-006: Scope Creep

**Status:** Active  
**Likelihood:** High  
**Impact:** Medium  
**Priority:** High  
**Owner:** Orchestrator

#### Description
Temptation to add "just one more feature" could expand scope beyond MVP boundaries, delaying completion.

#### Trigger Indicators
- Frequent requests to add non-goal items
- Tickets created outside current stage scope
- "While we're here" additions

#### Mitigation Strategy
- NON_GOALS.md as explicit boundary
- Orchestrator scope-checks all work
- Future work backlog for good ideas
- Stage-gate discipline (no skipping ahead)

#### Contingency Plan
If scope expands: Formal scope review, cut lowest-priority items, extend timeline only as last resort

#### History
| Date | Update |
|------|--------|
| 2024-XX-XX | Risk identified during project planning |

---

## Closed Risks

*No risks closed yet.*

---

## Risk Review Cadence

- **Weekly:** Orchestrator reviews risk status during weekly check
- **Stage Gate:** Full risk review before advancing stages
- **Ad Hoc:** New risks logged when identified

---

*This document is maintained by Advisor with Orchestrator support.*
