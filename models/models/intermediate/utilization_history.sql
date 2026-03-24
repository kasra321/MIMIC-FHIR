MODEL (
  name intermediate.utilization_history,
  kind FULL,
  grain [index_encounter_id]
);

WITH prior_encounters AS (
    SELECT
        idx.encounter_id AS index_encounter_id,
        e.encounter_class,
        e.period_start AS prior_start,
        DATE_DIFF('month', e.period_start, idx.period_start) AS months_before
    FROM intermediate.ed_index_cohort idx
    JOIN silver.encounters e
      ON e.patient_id = idx.patient_id
     AND e.source = idx.source
     AND e.period_start < idx.period_start
     AND e.period_start >= idx.period_start - INTERVAL '24' MONTH
)
SELECT
    index_encounter_id,
    COUNT(*) AS encounters_24m,
    COUNT(*) FILTER (WHERE months_before <= 12) AS encounters_12m,
    COUNT(*) FILTER (WHERE months_before <= 6) AS encounters_6m,
    COUNT(*) FILTER (WHERE encounter_class = 'EMER' AND months_before <= 12) AS ed_visits_12m,
    COUNT(*) FILTER (WHERE encounter_class = 'IMP' AND months_before <= 12) AS inpatient_12m,
    COUNT(*) FILTER (WHERE encounter_class = 'AMB' AND months_before <= 12) AS ambulatory_12m,
    COUNT(*) FILTER (WHERE encounter_class = 'WELLNESS' AND months_before <= 12) AS wellness_12m,
    MIN(prior_start) AS earliest_prior_encounter,
    MAX(prior_start) AS most_recent_prior_encounter
FROM prior_encounters
GROUP BY index_encounter_id
