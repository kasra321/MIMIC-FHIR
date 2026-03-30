-- Silver SQL for Organization extraction

CREATE OR REPLACE TABLE silver.organization AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'name' AS name,
  resource->>'active' AS is_active,
  TRY_CAST(resource->'identifier'->0->>'value' AS INT32) AS npi_value
FROM
  bronze.fhir_resources
WHERE resource_type='Organization'