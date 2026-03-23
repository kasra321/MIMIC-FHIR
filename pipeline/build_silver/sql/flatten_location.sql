-- Flatten "Location" resources into silver table

CREATE OR REPLACE TABLE silver.location AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'name' AS name,
  CASE WHEN resource->>'status' = 'active' THEN 1 ELSE 0 END AS is_active,
  resource->'physicalType'->'coding'->0->>'display' AS loaction_physical_type,
  regexp_replace(resource->'managingOrganization'->>'reference', 'Organization/', '') AS organization_id
FROM
  bronze.fhir_resources
WHERE resource_type='Location'