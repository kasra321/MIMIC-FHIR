-- Flatten "Patient" resources into silver table

CREATE OR REPLACE TABLE silver.patient AS
SELECT
  resource->>'id' AS resource_id,
  resource->'name'->0->>'family' AS name,
  resource->>'gender' AS gender,
  resource->>'birthDate' AS birth_date,
  resource->'extension'->0->'extension'->0->'valueCoding'->>'display' AS race,
  resource->'extension'->1->'extension'->0->'valueCoding'->>'display' AS ethnicity,
  resource->'identifier'->0->>'value' AS patient_num,
  resource->'communication'->0->'language'->'coding'->0->>'code' AS language,
  resource->'maritalStatus'->'coding'->0->>'code' AS marital_status,
  regexp_replace(resource->'managingOrganization'->>'reference', 'Organization/', '') AS organization_id
FROM
  bronze.fhir_resources
WHERE resource_type='Patient'
