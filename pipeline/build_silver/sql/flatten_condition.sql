-- Flatten "Condition" resources into silver table

CREATE OR REPLACE TABLE silver.condition AS
SELECT
  resource->>'id' AS resource_id,
  resource->'code'->'coding'->0->>'code' AS icd_code,
  resource->'code'->'coding'->0->>'display' AS icd_name,
  regexp_replace(resource->'subject'->>'reference', 'Patient/', '') AS patient_id,
  resource->'category'->0->'coding'->0->>'code' AS condition_category,
  regexp_replace(resource->'encounter'->>'reference', 'Encounter/', '') AS encounter_id
FROM
  bronze.fhir_resources
WHERE resource_type='Condition'
