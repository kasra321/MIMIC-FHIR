# Delphi Review Template

Use this template for major decisions requiring multi-agent input: stage gates, tool choices, scope changes.

---

## DELPHI-[NUMBER]: [Decision Question]

**Date:** [YYYY-MM-DD]  
**Status:** In Progress | Complete  
**Decision Type:** Stage Gate | Tool Choice | Scope Change | Architecture | Other  
**Related:** [DEC-XXX if this will create a decision entry]

---

## 1. Frame the Question

### Decision Required

[State the decision/question clearly and specifically]

### Why Delphi Review

[Why does this decision warrant multi-agent input?]

### Constraints

[Any constraints that limit options: time, budget, dependencies]

### Information Provided to Agents

[What context/artifacts each agent received]

---

## 2. Independent Perspectives

*Each agent responds without seeing others' responses*

### Advisor Assessment

**Focus:** Architectural soundness, risk, alignment with principles

[Advisor's response]

**Key Points:**
- [Point 1]
- [Point 2]

**Recommendation:** [Proceed / Caution / Reject]

---

### Orchestrator Assessment

**Focus:** Scope, timeline, resource impact

[Orchestrator's response]

**Key Points:**
- [Point 1]
- [Point 2]

**Recommendation:** [Proceed / Caution / Reject]

---

### Developer Assessment

**Focus:** Implementation feasibility, technical debt, effort

[Developer's response]

**Key Points:**
- [Point 1]
- [Point 2]

**Recommendation:** [Proceed / Caution / Reject]

---

### Critic Assessment (if invoked)

**Persona Used:** [Committee / OSS Contributor / External Clinician / etc.]  
**Skepticism Level:** [1-5]

[Critic's response]

**Key Points:**
- [Point 1]
- [Point 2]

**Recommendation:** [Acceptable / Needs Work / Significant Concerns]

---

## 3. Synthesis

### Points of Agreement

[Where all agents align]

- [Agreement 1]
- [Agreement 2]

### Points of Disagreement

| Issue | Advisor | Orchestrator | Developer | Critic |
|-------|---------|--------------|-----------|--------|
| [Issue 1] | [Position] | [Position] | [Position] | [Position] |
| [Issue 2] | [Position] | [Position] | [Position] | [Position] |

### Unresolved Questions

- [Question 1]
- [Question 2]

---

## 4. Challenge Round (if disagreements exist)

### Issue 1: [Description]

**Advisor response to disagreement:**
[Response]

**Orchestrator response to disagreement:**
[Response]

**Developer response to disagreement:**
[Response]

---

## 5. PI Decision

### Decision Made

[Your final decision, stated clearly]

### Rationale

[Why you made this decision, referencing agent input]

### Dissent Acknowledged

[If you overrode any agent recommendation, explain why]

### Action Items

- [ ] [Action 1]
- [ ] [Action 2]
- [ ] Update DECISIONS.md with DEC-XXX
- [ ] Update relevant documentation

---

## 6. Follow-up

### Decision Entry Created

[Link to DECISIONS.md entry: DEC-XXX]

### Agents Notified

- [ ] Advisor log updated
- [ ] Orchestrator log updated
- [ ] Developer log updated
- [ ] Critic log updated (if participated)

---

*Template version: 1.0*
