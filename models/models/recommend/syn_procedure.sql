MODEL(
  name recommend.syn_procedure,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key resource_id,
  ),
  columns (
    resource_id     VARCHAR,
    patient_id      VARCHAR,
    performed_date  TIMESTAMP,
    procedure_code  VARCHAR,
    procedure       VARCHAR,
    created_at      TIMESTAMP
  )
);

SELECT
  p.resource_id,
  p.patient_id,
  p.start_timestamp   AS performed_date,
  p.procedure_code,
  p.reason            AS procedure,
  NOW()               AS created_at
FROM silver.synthea_procedure p
WHERE NOT EXISTS (
  SELECT 1
  FROM recommend.syn_procedure r
  WHERE r.resource_id = p.resource_id
)
