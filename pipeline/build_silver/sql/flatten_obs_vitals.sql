-- Hand-written silver SQL for vital sign extraction.
-- Planned migration: auto-generate from FHIR ViewDefinitions via FlatQuack
-- once FlatQuack stabilizes (specs/*.vd.json define the target columns).

CREATE OR REPLACE TABLE silver.obs_vitals AS
SELECT
    r.resource_id,
    json_extract_string(r.resource, '$.meta.source') AS source,
    regexp_replace(
        json_extract_string(r.resource, '$.subject.reference'),
        'Patient/', ''
    ) AS patient_id,
    regexp_replace(
        json_extract_string(r.resource, '$.encounter.reference'),
        'Encounter/', ''
    ) AS encounter_id,
    json_extract_string(
        r.resource, '$.effectiveDateTime'
    )::TIMESTAMP AS effective_datetime,
    json_extract_string(c.coding, '$.code') AS loinc_code,
    json_extract(r.resource, '$.valueQuantity.value')::DOUBLE AS value,
    json_extract_string(r.resource, '$.valueQuantity.unit') AS unit
FROM bronze.fhir_resources r,
     LATERAL unnest(
         json_extract(r.resource, '$.code.coding')::JSON[]
     ) AS c(coding)
WHERE r.resource_type = 'Observation'
  AND json_extract_string(c.coding, '$.system') = 'http://loinc.org'
  AND json_extract_string(c.coding, '$.code') IN (
      '8310-5',  -- Body Temperature
      '8867-4',  -- Heart Rate
      '9279-1',  -- Respiratory Rate
      '2708-6',  -- Oxygen Saturation
      '8480-6',  -- Systolic BP
      '8462-4'   -- Diastolic BP
  );
