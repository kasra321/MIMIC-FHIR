-- Flatten "Procedure" resources into silver table

CREATE OR REPLACE TABLE silver.procedure AS
SELECT
  resource->>'id' AS resource_id,
  resource->'code'->'coding'->0->>'code' AS snomed_ct_id,
  regexp_replace(resource->'code'->'coding'->0->>'display', ' \(procedure\)', '') AS snomed_ct_procedure,
  resource->>'status' AS status,
  regexp_replace(resource->'subject'->>'reference', 'Patient/', '') AS patient_id,
  regexp_replace(resource->'encounter'->>'reference', 'Encounter/', '') AS encounter_id,
  (resource->>'performedDateTime')::TIMESTAMP AS performed_datetime
FROM
  bronze.fhir_resources
WHERE resource_type='Procedure'
