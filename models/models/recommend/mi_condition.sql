MODEL(
  name recommend.mi_condition,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key resource_id,
  ),
  columns (
    resource_id     VARCHAR,
    patient_id      VARCHAR,
    icd_code        VARCHAR,
    icd_name        VARCHAR,
    start_timestamp TIMESTAMP,
    end_timestamp   TIMESTAMP,
    created_at      TIMESTAMP
  )
);

SELECT
  c.resource_id,
  c.patient_id,
  c.icd_code,
  c.icd_name,
  e.start_timestamp,
  e.end_timestamp,
  NOW()               AS created_at
FROM silver.condition c
LEFT JOIN silver.encounter e ON c.encounter_id = e.resource_id
WHERE NOT EXISTS (
  SELECT 1
  FROM recommend.mi_condition r
  WHERE r.resource_id = c.resource_id
)
