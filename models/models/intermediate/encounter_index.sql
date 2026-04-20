MODEL (
  name intermediate.encounter_index,
  kind FULL,
  grain [encounter_id]
);

SELECT
    e.resource_id AS encounter_id,
    e.source,
    e.patient_id,
    e.encounter_class,
    e.period_start,
    e.period_end,
    EXTRACT(EPOCH FROM (e.period_end - e.period_start)) / 3600.0 AS los_hours,
    p.gender,
    p.birth_date,
    DATE_DIFF('year', p.birth_date, CAST(e.period_start AS DATE)) AS age_at_visit,
    p.race,
    p.ethnicity
FROM silver.encounters e
JOIN silver.patients p
  ON e.patient_id = p.resource_id
 AND e.source = p.source
WHERE e.status = 'finished'
