MODEL(
  name recommend.syn_vitals,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key resource_id,
  ),
  columns (
    resource_id         VARCHAR,
    patient_id          VARCHAR,
    effective_timestamp TIMESTAMP,
    vitals_code         VARCHAR,
    value               DOUBLE,
    unit                VARCHAR,
    created_at          TIMESTAMP
  )
);

SELECT
  o.resource_id,
  o.patient_id,
  o.issued_timestamp  AS effective_timestamp,
  o.measure_code      AS vitals_code,
  o.value,
  o.unit,
  NOW()               AS created_at
FROM silver.synthea_observation o
WHERE record = 'vital-signs'
AND NOT EXISTS (
  SELECT 1
  FROM recommend.syn_vitals r
  WHERE r.resource_id = o.resource_id
)
