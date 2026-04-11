MODEL(
  name recommend.mi_medication_dispense,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key resource_id,
  ),
  columns (
    resource_id            VARCHAR,
    patient_id             VARCHAR,
    administered_date      TIMESTAMP,
    medication_code        VARCHAR,
    medication             VARCHAR,
    created_at             TIMESTAMP
  )
);

SELECT
  m.resource_id,
  m.patient_id,
  m.handed_over_timestamp AS administered_date,
  m.medication_code,
  m.medication_name       AS medication,
  NOW()                   AS created_at
FROM silver.medication_dispense m
WHERE NOT EXISTS (
  SELECT 1
  FROM recommend.mi_medication_dispense r
  WHERE r.resource_id = m.resource_id
)
