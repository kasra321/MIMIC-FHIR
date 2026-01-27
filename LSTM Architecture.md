## Tensor Shapes for IPW / Doubly Robust

Assuming batch size `B`, sequence length `T`, and feature dimensions below:

### Input Tensors

```python
# 1. Patient state embedding (static or per-encounter)
patient_embedding: (B, T, D_patient)  # e.g., D_patient=128

# 2. Current vitals (outcome variable at t, target at t+1)
vitals: (B, T, D_vitals)  # e.g., D_vitals=6 (HR, BP_sys, BP_dia, SpO2, RR, Temp)

# 3. Interventions (binary or continuous)
interventions: (B, T, D_interventions)  # e.g., D_interventions=50 (med flags, procedures)
```

### Derived Tensors (computed by propensity model)

```python
# Propensity scores: P(A_t | X_t) for each intervention
propensity_scores: (B, T, D_interventions)  # values in (0,1)

# IPW weights (for loss weighting)
ipw_weights: (B, T)  # or (B, T, 1) — scalar weight per timestep
```

### Target Tensor

```python
# Next-step vitals
vitals_target: (B, T, D_vitals)  # vitals shifted by 1 timestep
```

---

## ELT Output Schema (per patient-timestep row)

|Column|Type|Description|
|---|---|---|
|`patient_id`|str||
|`encounter_id`|str||
|`timestep`|int|sequence position|
|`timestamp`|datetime|actual time|
|`patient_embedding`|float[D]|dense vector|
|`vitals`|float[6]|current vitals|
|`interventions`|float[50]|one-hot or counts|
|`vitals_next`|float[6]|target (nullable at last step)|

At training time, you'll:

1. Group by `encounter_id`, sort by `timestep`
2. Pad/truncate to fixed `T`
3. Stack into tensors

Want a sample SQL/DuckDB query or PyTorch Dataset class?