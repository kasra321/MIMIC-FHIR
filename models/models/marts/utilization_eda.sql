MODEL (
  name marts.utilization_eda,
  kind FULL,
  grain [encounter_id]
);

SELECT
    idx.encounter_id,
    idx.source,
    idx.patient_id,
    idx.encounter_class,
    idx.period_start,
    idx.period_end,
    idx.los_hours,
    idx.gender,
    idx.birth_date,
    idx.age_at_visit,
    idx.race,
    idx.ethnicity,
    COALESCE(uh.encounters_6m, 0) AS encounters_6m,
    COALESCE(uh.encounters_12m, 0) AS encounters_12m,
    COALESCE(uh.encounters_24m, 0) AS encounters_24m,
    COALESCE(uh.ed_visits_12m, 0) AS ed_visits_12m,
    COALESCE(uh.inpatient_12m, 0) AS inpatient_12m,
    COALESCE(uh.ambulatory_12m, 0) AS ambulatory_12m,
    COALESCE(uh.wellness_12m, 0) AS wellness_12m,
    uh.earliest_prior_encounter,
    uh.most_recent_prior_encounter,
    COALESCE(cb.total_conditions, 0) AS total_conditions,
    COALESCE(cb.chronic_conditions, 0) AS chronic_conditions,
    COALESCE(cb.encounter_diagnoses, 0) AS encounter_diagnoses,
    COALESCE(cb.distinct_diagnosis_codes, 0) AS distinct_diagnosis_codes
FROM intermediate.ed_index_cohort idx
LEFT JOIN intermediate.utilization_history uh
  ON uh.index_encounter_id = idx.encounter_id
LEFT JOIN intermediate.condition_burden cb
  ON cb.index_encounter_id = idx.encounter_id
