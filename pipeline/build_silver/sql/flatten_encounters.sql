-- Extract Encounter resources into a flat table.
-- Covers ED, hospital, and ICU encounters from MIMIC + Synthea.
-- Reference normalization handles both MIMIC (Patient/xxx) and Synthea (urn:uuid:xxx).

CREATE OR REPLACE TABLE silver.encounters AS
SELECT
    r.resource_id,
    json_extract_string(r.resource, '$.meta.source') AS source,
    regexp_replace(
        json_extract_string(r.resource, '$.subject.reference'),
        '^(urn:uuid:|Patient/)', ''
    ) AS patient_id,
    json_extract_string(r.resource, '$.class.code') AS encounter_class,
    json_extract_string(r.resource, '$.status') AS status,
    TRY_CAST(json_extract_string(r.resource, '$.period.start') AS TIMESTAMP) AS period_start,
    TRY_CAST(json_extract_string(r.resource, '$.period.end') AS TIMESTAMP) AS period_end,
    json_extract_string(r.resource, '$.type[0].coding[0].code') AS type_code,
    json_extract_string(r.resource, '$.type[0].coding[0].display') AS type_display,
    json_extract_string(r.resource, '$.type[0].coding[0].system') AS type_system,
    json_extract_string(r.resource, '$.reasonCode[0].coding[0].code') AS reason_code,
    json_extract_string(r.resource, '$.reasonCode[0].coding[0].display') AS reason_display,
    -- Hospital/ICU fields (NULL for Synthea and some ED encounters)
    json_extract_string(r.resource, '$.hospitalization.admitSource.coding[0].code') AS admit_source,
    json_extract_string(r.resource, '$.hospitalization.dischargeDisposition.coding[0].code') AS discharge_disposition,
    json_extract_string(r.resource, '$.serviceType.coding[0].code') AS service_type,
    json_extract_string(r.resource, '$.priority.coding[0].code') AS priority_code,
    -- ICU parent encounter link (ICU encounters have partOf → hospital encounter)
    regexp_replace(
        json_extract_string(r.resource, '$.partOf.reference'),
        '^(urn:uuid:|Encounter/)', ''
    ) AS parent_encounter_id,
    -- First location (for ICU encounters, this is the ICU unit)
    regexp_replace(
        json_extract_string(r.resource, '$.location[0].location.reference'),
        '^Location/', ''
    ) AS location_id
FROM bronze.fhir_resources r
WHERE r.resource_type = 'Encounter';
