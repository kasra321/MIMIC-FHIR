-- Extract Patient resources into a flat demographics table.
-- Handles both MIMIC (Patient/xxx) and Synthea (urn:uuid:xxx) ID formats.
-- Race and ethnicity are extracted from US Core FHIR extensions.

CREATE OR REPLACE TABLE silver.patients AS
WITH base AS (
    SELECT
        r.resource_id,
        COALESCE(json_extract_string(r.resource, '$.meta.source'), r.dataset_source) AS source,
        json_extract_string(r.resource, '$.gender') AS gender,
        TRY_CAST(json_extract_string(r.resource, '$.birthDate') AS DATE) AS birth_date,
        TRY_CAST(json_extract_string(r.resource, '$.deceasedDateTime') AS TIMESTAMP) AS deceased_datetime,
        json_extract(r.resource, '$.extension')::JSON[] AS extensions
    FROM bronze.fhir_resources r
    WHERE r.resource_type = 'Patient'
),
race AS (
    SELECT
        b.resource_id,
        json_extract_string(sub.val, '$.valueString') AS race
    FROM base b,
         LATERAL unnest(b.extensions) AS ext(val),
         LATERAL unnest(json_extract(ext.val, '$.extension')::JSON[]) AS sub(val)
    WHERE json_extract_string(ext.val, '$.url') = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race'
      AND json_extract_string(sub.val, '$.url') = 'text'
),
ethnicity AS (
    SELECT
        b.resource_id,
        json_extract_string(sub.val, '$.valueString') AS ethnicity
    FROM base b,
         LATERAL unnest(b.extensions) AS ext(val),
         LATERAL unnest(json_extract(ext.val, '$.extension')::JSON[]) AS sub(val)
    WHERE json_extract_string(ext.val, '$.url') = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity'
      AND json_extract_string(sub.val, '$.url') = 'text'
)
SELECT
    b.resource_id,
    b.source,
    b.gender,
    b.birth_date,
    b.deceased_datetime,
    r.race,
    e.ethnicity
FROM base b
LEFT JOIN race r ON r.resource_id = b.resource_id
LEFT JOIN ethnicity e ON e.resource_id = b.resource_id;
