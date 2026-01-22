# Non-Goals (v0.1)

This document explicitly lists what is **out of scope** for v0.1. These boundaries are intentional design decisions, not deferrals due to time constraints.

## Purpose

Non-goals serve three functions:
1. **Prevent scope creep** — When tempted to add something, check here first
2. **Signal maturity** — Knowing what not to build shows architectural clarity
3. **Set expectations** — External reviewers understand the boundaries

## Format

Each non-goal includes:
- What's excluded
- Why it's excluded (for v0.1)
- When it might be reconsidered

---

## Infrastructure Non-Goals

### NG-001: No Cloud Deployment

**Excluded:** Any cloud infrastructure provisioning, deployment, or configuration.

**Why:** The MVP proves the architecture locally. Cloud deployment adds infrastructure complexity without validating core data pipeline logic.

**Reconsider when:** Local pipeline is stable and documented; specific cloud target identified.

---

### NG-002: No Real-Time Serving

**Excluded:** Online inference, streaming data, real-time predictions.

**Why:** Real-time serving requires different infrastructure (message queues, serving frameworks, latency optimization). The MVP validates batch processing.

**Reconsider when:** Batch pipeline complete; specific real-time use case identified.

---

### NG-003: No Governance Enforcement

**Excluded:** Access control, audit logging for compliance, data retention policies, consent management.

**Why:** Governance requires organizational context and policy decisions beyond technical implementation. MVP uses research data (MIMIC) with existing agreements.

**Reconsider when:** Production deployment planned; regulatory requirements identified.

---

## Data Non-Goals

### NG-004: Vital Signs Only

**Excluded:** Lab results, medications, procedures, clinical notes, imaging.

**Why:** Vital signs are the "best case" for healthcare ML (low ambiguity, machine-generated, low missingness). Proving architecture with simple data first.

**Reconsider when:** Vital signs pipeline complete; architecture validated for extension.

---

### NG-005: No Multi-Source Validation

**Excluded:** Testing against Synthea or other FHIR implementations.

**Why:** MIMIC-IV FHIR is sufficient to validate core architecture. Multi-source adds complexity without proving fundamentals.

**Reconsider when:** Core pipeline complete; portability claims need validation.

---

### NG-006: No External Data Integration

**Excluded:** Social determinants, external registries, supplementary datasets.

**Why:** External data requires integration infrastructure beyond MVP scope.

**Reconsider when:** Core prediction pipeline complete; specific external source identified.

---

## Model Non-Goals

### NG-007: No SOTA Performance Pursuit

**Excluded:** Hyperparameter optimization, architecture search, performance benchmarking against published results.

**Why:** The primary product is trust and reproducibility, not model performance. Simple models that prove the pipeline work are sufficient.

**Reconsider when:** Pipeline fully reproducible; specific performance requirements identified.

---

### NG-008: No Deep Learning Required

**Excluded:** Mandatory use of neural networks, transformers, or complex architectures.

**Why:** Simple models (logistic regression, XGBoost) validate pipeline logic more clearly. Deep learning complexity is orthogonal to infrastructure goals.

**Reconsider when:** Pipeline validated; temporal modeling specifically required.

---

### NG-009: No Model Explainability Infrastructure

**Excluded:** SHAP values, LIME, attention visualization, fairness auditing frameworks.

**Why:** Explainability is important but requires stable models first. MVP focuses on reproducibility and auditability of training, not interpretation.

**Reconsider when:** Training pipeline stable; specific explainability requirements identified.

---

## Output Non-Goals

### NG-010: No User Interface

**Excluded:** Web dashboards, clinical decision support interfaces, visualization applications.

**Why:** UI requires frontend development skills and clinical workflow integration beyond MVP scope.

**Reconsider when:** Pipeline complete; specific user/workflow identified.

---

### NG-011: No Alerting or Notifications

**Excluded:** Pipeline failure alerts, prediction-triggered notifications, monitoring dashboards.

**Why:** Alerting requires production context (who receives alerts, what actions follow).

**Reconsider when:** Production deployment planned; operational requirements defined.

---

## Process Non-Goals

### NG-012: No CI/CD Pipeline

**Excluded:** Automated testing on commit, deployment pipelines, container registries.

**Why:** MVP development is solo with manual verification. CI/CD adds overhead without proportional benefit at this scale.

**Reconsider when:** Multiple contributors; release cadence established.

---

### NG-013: No Formal Code Review Process

**Excluded:** Pull request requirements, approval workflows, branch protection.

**Why:** Solo development. Agent system provides review function without process overhead.

**Reconsider when:** Contributors added; code quality concerns emerge.

---

## How to Use This Document

### When Adding a Feature
1. Check if it's listed here
2. If yes: Stop. Log the temptation in your decision log, note why you wanted it, move on.
3. If no but seems out of scope: Add it here with rationale

### When External Reviewer Asks "Why Didn't You..."
1. Point to this document
2. Explain the intentionality of the boundary
3. Discuss reconsideration criteria

### When Reconsidering a Non-Goal
1. Check if reconsideration criteria are met
2. If yes: Create a DECISIONS.md entry proposing the change
3. Move item from NON_GOALS.md to active scope with decision reference

---

*This document reflects v0.1 scope. Items may move to active scope in future versions.*
