# Critic Briefing Template

Use this template to invoke the Critic agent with controlled context.

---

## Briefing: [REVIEW-ID]

**Date:** [YYYY-MM-DD]  
**PI:** [Your name]

---

## 1. Review Target

### What to Review

[Specific artifact, decision, or claim being reviewed]

### Artifact Location

[File paths or document references]

### Review Scope

[What specifically should be evaluated vs. ignored]

---

## 2. Persona Selection

Select ONE persona for this review:

- [ ] **Capstone Committee Member** — Academic rigor, methodology, contribution claims
- [ ] **Open-Source Contributor** — Usability, documentation, installation, maintainability
- [ ] **Clinical Informaticist (External)** — Generalizability, FHIR assumptions, clinical validity
- [ ] **ML Engineer (No Clinical Background)** — Clarity, documentation, code quality
- [ ] **Custom:** _______________

**Custom Persona Description (if applicable):**

[Describe the perspective you want]

---

## 3. Skepticism Level

Select ONE level:

- [ ] **Level 1: Friendly** — Assume good intent, note minor gaps only
- [ ] **Level 2: Constructive** — Balanced critique, actionable suggestions
- [ ] **Level 3: Rigorous** — Thorough challenge, demand justification
- [ ] **Level 4: Adversarial** — Actively look for weaknesses
- [ ] **Level 5: Red Team** — Assume this will fail, find how

---

## 4. Context Provided

*Only include what you want the Critic to see. Be deliberate.*

### Artifacts for Review

```
[Paste relevant code, documentation, or schema here]

OR

[Reference file paths the Critic should read]
```

### Background Information

[Any context the Critic needs to understand the artifact]

### Claims to Evaluate

[Specific claims you want validated or challenged]

- Claim 1: [Statement]
- Claim 2: [Statement]

---

## 5. Context Deliberately Withheld

*For your records only—Critic will not see this section*

### What's Hidden and Why

| Hidden Information | Reason for Withholding |
|-------------------|------------------------|
| [Information] | [Prevents bias / Tests independence / etc.] |

### Known Issues Not Disclosed

[Any known problems you're intentionally not telling the Critic about]

---

## 6. Synthetic Context (if any)

*Use to stress-test with hypothetical constraints*

### Injected Constraints

[Fake limitations or requirements to see how robust the work is]

### Injected Assumptions

[Hypothetical assumptions different from reality]

---

## 7. Specific Questions (optional)

[Direct questions you want answered, beyond general review]

1. [Question 1]
2. [Question 2]
3. [Question 3]

---

## 8. Memory Mode

Select ONE:

- [ ] **Fresh** (Default) — No memory of previous reviews. Clean slate.
- [ ] **Accumulated** — Remember previous reviews of this same artifact. Reference: [Previous review IDs]
- [ ] **Seeded** — Carry forward specific context below:

**Seeded Context (if applicable):**

[Specific prior context to inject]

---

## 9. Output Expectations

### Desired Output Format

- [ ] Full structured review (default)
- [ ] Brief assessment only
- [ ] Specific questions answered only

### Response Length Preference

- [ ] Comprehensive (detailed)
- [ ] Standard
- [ ] Concise

---

## Briefing Checklist

Before invoking Critic:

- [ ] Review target clearly specified
- [ ] Persona selected
- [ ] Skepticism level selected
- [ ] Context deliberately curated (not just dumped)
- [ ] Withheld information documented (for your records)
- [ ] Memory mode selected

---

## Post-Review Actions

*Complete after Critic responds*

### Review Received

**Date:** [YYYY-MM-DD]  
**Logged in:** `/agents/contextual/logs/CRITIC_LOG.md`

### Findings Actioned

| Finding | Action Taken | Ticket Created |
|---------|--------------|----------------|
| [Finding 1] | [Action] | [TKT-X-XXX or N/A] |

### Findings Dismissed

| Finding | Reason for Dismissal |
|---------|---------------------|
| [Finding 1] | [Reason] |

---

*Template version: 1.0*
