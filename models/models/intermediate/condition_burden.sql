MODEL (
  name intermediate.condition_burden,
  kind FULL,
  grain [index_encounter_id]
);

SELECT
    idx.encounter_id AS index_encounter_id,
    COUNT(DISTINCT c.resource_id) AS total_conditions,
    COUNT(DISTINCT c.resource_id) FILTER (
        WHERE c.category = 'problem-list-item'
    ) AS chronic_conditions,
    COUNT(DISTINCT c.resource_id) FILTER (
        WHERE c.category = 'encounter-diagnosis'
    ) AS encounter_diagnoses,
    COUNT(DISTINCT c.code) AS distinct_diagnosis_codes
FROM intermediate.encounter_index idx
LEFT JOIN silver.conditions c
  ON c.patient_id = idx.patient_id
 AND c.source = idx.source
 AND (
     c.clinical_status = 'active'
     OR c.encounter_id = idx.encounter_id
     OR (
         c.onset_datetime <= idx.period_start
         AND (c.abatement_datetime IS NULL OR c.abatement_datetime > idx.period_start)
     )
 )
GROUP BY idx.encounter_id
