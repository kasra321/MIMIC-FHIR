MODEL(
  name recommend.syn_condition,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key resource_id,
  ),
  columns (
    resource_id           VARCHAR,
    patient_id            VARCHAR,
    onset_timestamp       TIMESTAMP,
    diagnosis_timestamp   TIMESTAMP,
    condition_code        VARCHAR,
    condition             VARCHAR,
    created_at            TIMESTAMP
  )
);

SELECT
  c.resource_id,
  c.patient_id,
  c.onset_timestamp,
  e.end_date          AS diagnosis_timestamp,
  c.condition_code,
  c.condition,
  NOW()               AS created_at
FROM silver.synthea_condition c
LEFT JOIN silver.synthea_encounter e ON c.encounter_id = e.resource_id
WHERE NOT EXISTS (
  SELECT 1
  FROM recommend.syn_condition r
  WHERE r.resource_id = c.resource_id
)