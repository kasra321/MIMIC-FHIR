-- Flatten "Encounter" resources into silver table

CREATE OR REPLACE TABLE silver.encounter AS
SELECT
  resource->>'id' AS resource_id,
  resource->'class'->>'code' AS class_code,
  resource->'class'->>'display' AS class_name,
  (resource->'period'->>'start')::TIMESTAMP AS start_timestamp,
  (resource->'period'->>'end')::TIMESTAMP AS end_timestamp,
  resource->>'status' AS status,
  regexp_replace(resource->'subject'->>'reference', 'Patient/', '') AS patient_id,
  resource->'hospitalization'->'admitSource'->'coding'->0->>'code' AS admit_source,
  resource->'hospitalization'->'dischargeDisposition'->'coding'->0->>'code' AS discharge_disposition,
  regexp_replace(resource->'serviceProvider'->>'reference', 'Organization/', '') AS organization_id
FROM
  bronze.fhir_resources
WHERE resource_type='Encounter'
