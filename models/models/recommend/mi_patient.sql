MODEL(
  name recommend.mi_patient,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key resource_id,
  ),
  columns (
    resource_id    VARCHAR,
    name           VARCHAR,
    gender         VARCHAR,
    birth_date     VARCHAR,
    race           VARCHAR,
    ethnicity      VARCHAR,
    marital_status VARCHAR,
    created_at     TIMESTAMP
  )
);

SELECT
  s.resource_id,
  s.name,
  s.gender,
  s.birth_date,
  s.race,
  s.ethnicity,
  s.marital_status,
  NOW() AS created_at
FROM silver.patient s
WHERE NOT EXISTS (
  SELECT 1
  FROM recommend.mi_patient r
  WHERE r.resource_id = s.resource_id
)