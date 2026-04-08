MODEL(
  name recommend.mi_procedure,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key resource_id,
  ),
  columns (
    resource_id         VARCHAR,
    patient_id          VARCHAR,
    performed_datetime  TIMESTAMP,
    snomed_ct_id        VARCHAR,
    snomed_ct_procedure VARCHAR,
    created_at          TIMESTAMP
  )
);

SELECT
  p.resource_id,
  p.patient_id,
  p.performed_datetime,
  p.snomed_ct_id,
  p.snomed_ct_procedure,
  NOW()                   AS created_at
FROM silver.procedure p
WHERE NOT EXISTS (
  SELECT 1
  FROM recommend.mi_procedure r
  WHERE r.resource_id = p.resource_id
)
