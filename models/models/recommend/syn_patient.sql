MODEL(
  name recommend.syn_patient,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key resource_id,
  ),
  columns (
    resource_id     VARCHAR,
    first_name      VARCHAR,
    middle_name     VARCHAR,
    last_name       VARCHAR,
    gender          VARCHAR,
    race            VARCHAR,
    ethnicity       VARCHAR,
    birth_date      VARCHAR,
    marital_status  VARCHAR,
    created_at      TIMESTAMP
  )
);

SELECT
  p.resource_id,
  p.first_name,
  p.middle_name,
  p.last_name,
  p.gender,
  p.race,
  p.ethnicity,
  p.birth_date,
  p.marital_status,
  NOW()             AS created_at
FROM silver.synthea_patient p
WHERE NOT EXISTS (
  SELECT 1
  FROM recommend.syn_patient r
  WHERE r.resource_id = p.resource_id
)
