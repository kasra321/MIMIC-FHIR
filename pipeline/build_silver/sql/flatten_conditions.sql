-- Extract Condition resources into a flat table.
-- Reference normalization handles both MIMIC and Synthea formats.

CREATE OR REPLACE TABLE silver.conditions AS
SELECT
    r.resource_id,
    COALESCE(json_extract_string(r.resource, '$.meta.source'), r.dataset_source) AS source,
    regexp_replace(
        json_extract_string(r.resource, '$.subject.reference'),
        '^(urn:uuid:|Patient/)', ''
    ) AS patient_id,
    regexp_replace(
        json_extract_string(r.resource, '$.encounter.reference'),
        '^(urn:uuid:|Encounter/)', ''
    ) AS encounter_id,
    json_extract_string(r.resource, '$.clinicalStatus.coding[0].code') AS clinical_status,
    json_extract_string(r.resource, '$.verificationStatus.coding[0].code') AS verification_status,
    json_extract_string(r.resource, '$.category[0].coding[0].code') AS category,
    json_extract_string(r.resource, '$.code.coding[0].code') AS code,
    json_extract_string(r.resource, '$.code.coding[0].system') AS code_system,
    json_extract_string(r.resource, '$.code.coding[0].display') AS code_display,
    TRY_CAST(json_extract_string(r.resource, '$.onsetDateTime') AS TIMESTAMP) AS onset_datetime,
    TRY_CAST(json_extract_string(r.resource, '$.abatementDateTime') AS TIMESTAMP) AS abatement_datetime,
    TRY_CAST(json_extract_string(r.resource, '$.recordedDate') AS TIMESTAMP) AS recorded_date
FROM bronze.fhir_resources r
WHERE r.resource_type = 'Condition';
