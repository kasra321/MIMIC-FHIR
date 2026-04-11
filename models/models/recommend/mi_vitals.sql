MODEL(
  name recommend.mi_vitals,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key resource_id,
  ),
  columns (
    resource_id      VARCHAR,
    patient_id       VARCHAR,
    observation_date TIMESTAMP,
    obs_code         VARCHAR,
    value            DOUBLE,
    unit             VARCHAR,
    created_at       TIMESTAMP
  )
);

SELECT
  v.resource_id,
  v.patient_id,
  v.effective_datetime AS observation_date,
  v.loinc_code         AS obs_code,
  v.value,
  v.unit,
  NOW()                AS created_at
FROM silver.obs_vitals v
WHERE NOT EXISTS (
  SELECT 1
  FROM recommend.mi_vitals r
  WHERE r.resource_id = v.resource_id
)
