-- Flatten all the different synthea sheets

-- 1. Patient
CREATE OR REPLACE TABLE silver.synthea_patient AS
SELECT
    resource->>'id' AS resource_id,
    resource->'name'->0->'given'->>0 AS first_name,
    resource->'name'->0->'given'->>1 AS middle_name,
    resource->'name'->0->>'family' AS last_name,
    resource->>'gender' AS gender,
    resource->'extension'->0->'extension'->0->'valueCoding'->>'display' AS race,
    resource->'extension'->1->'extension'->1->>'valueString' AS ethnicity,
    resource->>'birthDate' AS birth_date,
    resource->'telecom'->0->>'value' AS phone_number,
    resource->'maritalStatus'->>'text' AS marital_status,
    resource->'address'->0->>'city' AS city,
    resource->'address'->0->>'state' AS state,
    resource->'address'->0->>'country' AS country,
    resource->'address'->0->'line'->>0 AS street_address,
    TRY_CAST(resource->'address'->0->'extension'->0->'extension'->0->'valueDecimal' AS DOUBLE) AS latitude,
    TRY_CAST(resource->'address'->0->'extension'->0->'extension'->1->'valueDecimal' AS DOUBLE) AS longitude,
    TRY_CAST(resource->'extension'->5->'valueDecimal' AS DOUBLE) AS disablility_adjusted_life_years,
    TRY_CAST(resource->'extension'->6->'valueDecimal' AS DOUBLE) AS quality_adjusted_life_years
FROM
  bronze.synthea
WHERE resource_type='Patient';

-- 2. Observation
CREATE OR REPLACE TABLE silver.synthea_observation AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  resource->'category'->0->'coding'->0->>'code' AS record,
  resource->'code'->'coding'->0->>'code' AS measure_code,
  resource->'code'->'coding'->0->>'display' AS measure_name,
  TRY_CAST(
    CASE WHEN resource->'valueQuantity'->>'value' IS NOT NULL
    THEN resource->'valueQuantity'->>'value'
    ELSE resource->'component'->0->'valueQuantity'->>'value' END AS DOUBLE
  ) AS value,
  CASE WHEN resource->'valueQuantity'->>'unit' IS NOT NULL THEN resource->'valueQuantity'->>'unit' ELSE resource->'component'->0->'valueQuantity'->>'unit' END AS unit,
  regexp_replace(resource->'subject'->>'reference', 'urn:uuid:', '') AS patient_id,
  (resource->>'effectiveDateTime')::TIMESTAMP AS effective_timestamp,
  (resource->>'issued')::TIMESTAMP AS issued_timestamp
FROM 
  bronze.synthea
WHERE resource_type='Observation';

-- 3. Encounter
CREATE OR REPLACE TABLE silver.synthea_encounter AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  resource->'class'->>'code' AS class,
  resource->'type'->0->'coding'->0->>'code' AS procedure_code,
  regexp_replace(resource->'type'->0->'coding'->0->>'display', ' \(procedure\)', '') AS procedure_name,
  regexp_replace(resource->'subject'->>'reference', 'urn:uuid:', '') AS patient_id,
  resource->'participant'->0->'type'->0->'coding'->0->>'code' AS practitioner_code,
  resource->'participant'->0->'type'->0->'coding'->0->>'display' AS practitioner_type,
  split_part(resource->'participant'->0->'individual'->>'reference', '|', 2) AS practitioner_id,
  resource->'participant'->0->'individual'->>'display' AS practitioner_name,
  (resource->'period'->>'start')::TIMESTAMP AS start_date,
  (resource->'period'->>'end')::TIMESTAMP AS end_date,
  split_part(resource->'location'->0->'location'->>'reference', '|', 2) AS location_id,
  resource->'location'->0->'location'->>'display' AS location_name,
  split_part(resource->'serviceProvider'->>'reference', '|', 2) AS provider_id,
  resource->'serviceProvider'->>'display' AS provider_name,
FROM 
  bronze.synthea
WHERE resource_type='Encounter';

-- 4. Condition
CREATE OR REPLACE TABLE silver.synthea_condition AS
SELECT
  resource->>'id' AS resource_id,
  resource->'clinicalStatus'->'coding'->0->>'code' AS clinical_status,
  resource->'verificationStatus'->'coding'->0->>'code' AS verification_status,
  resource->'category'->0->'coding'->0->>'code' AS category,
  resource->'code'->'coding'->0->>'code' AS condition_code,
  regexp_replace(resource->'code'->'coding'->0->>'display', ' \((.*?)\)', '') AS condition,
  regexp_extract(resource->'code'->'coding'->0->>'display', '\((.*?)\)', 1) AS condition_type,
  regexp_replace(resource->'subject'->>'reference', 'urn:uuid:', '') AS patient_id,
  regexp_replace(resource->'encounter'->>'reference', 'urn:uuid:', '') AS encounter_id,
  (resource->>'onsetDateTime')::TIMESTAMP AS onset_timestamp,
  (resource->>'recordedDate')::TIMESTAMP AS recorded_timestamp,
FROM 
  bronze.synthea
WHERE resource_type='Condition';

-- 5. Immunization
CREATE OR REPLACE TABLE silver.synthea_immunization AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  resource->'vaccineCode'->'coding'->0->>'code' AS vaccine_code,
  resource->'vaccineCode'->'coding'->0->>'display' AS vaccine,
  regexp_replace(resource->'patient'->>'reference', 'urn:uuid:', '') AS patient_id,
  regexp_replace(resource->'encounter'->>'reference', 'urn:uuid:', '') AS encounter_id,
  (resource->>'occurrenceDateTime')::TIMESTAMP AS occurrence_timestamp,
  split_part(resource->'location'->>'reference', '|', 2) AS location_id,
  resource->'location'->>'display' AS location_name
FROM 
  bronze.synthea
WHERE resource_type='Immunization';

-- 6. Medication
CREATE OR REPLACE TABLE silver.synthea_medication AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  resource->'code'->'coding'->0->>'code' AS medication_code,
  resource->'code'->'coding'->0->>'display' AS medication,
FROM 
  bronze.synthea
WHERE resource_type='Medication';

-- 7. Allergy Intolerance
CREATE OR REPLACE TABLE silver.synthea_allergy_intolerance AS
SELECT
  resource->>'id' AS resource_id,
  resource->'clinicalStatus'->'coding'->0->>'code' AS clinical_status,
  resource->'verificationStatus'->'coding'->0->>'code' AS verification_status,
  resource->>'type' AS type,
  resource->'category'->>0 AS category,
  resource->>'criticality' AS criticality,
  resource->'code'->'coding'->0->>'code' AS allergy_code,
  regexp_replace(resource->'code'->'coding'->0->>'display', ' \((.*?)\)', '') AS allergy,
  regexp_extract(resource->'code'->'coding'->0->>'display', '\((.*?)\)', 1) AS allergy_type,
  regexp_replace(resource->'patient'->>'reference', 'urn:uuid:', '') AS patient_id,
  (resource->>'recordedDate')::TIMESTAMP AS recorded_date
FROM
  bronze.synthea
WHERE resource_type='AllergyIntolerance';

-- 8. CarePlan
CREATE OR REPLACE TABLE silver.synthea_careplan AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  resource->>'intent' AS intent,
  resource->'category'->0->'coding'->0->>'code' AS plan,
  resource->'category'->1->'coding'->0->>'code' AS category_code,
  regexp_replace(resource->'category'->1->'coding'->0->>'display', ' \((.*?)\)', '') AS category,
  regexp_extract(resource->'category'->1->'coding'->0->>'display', '\((.*?)\)', 1) AS category_type,
  regexp_replace(resource->'subject'->>'reference', 'urn:uuid:', '') AS patient_id,
  regexp_replace(resource->'encounter'->>'reference', 'urn:uuid:', '') AS encounter_id,
  (resource->'period'->>'start')::TIMESTAMP AS start_timestamp,
  regexp_replace(resource->'careTeam'->0->>'reference', 'urn:uuid:', '') AS careteam_id,
  resource->'activity'->0->'detail'->'code'->'coding'->0->>'code' AS activity_code,
  regexp_replace(resource->'activity'->0->'detail'->'code'->'coding'->0->>'display', ' \((.*?)\)', '') AS activity,
  regexp_extract(resource->'activity'->0->'detail'->'code'->'coding'->0->>'display', '\((.*?)\)', 1) AS activity_type,
  resource->'activity'->0->'detail'->>'status' AS activity_status,
  resource->'activity'->0->'detail'->'location'->>'display' AS activity_location,
FROM
  bronze.synthea
WHERE resource_type='CarePlan';

-- 9. CareTeam
CREATE OR REPLACE TABLE silver.synthea_careteam AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  regexp_replace(resource->'subject'->>'reference', 'urn:uuid:', '') AS patient_id,
  resource->'participant'->0->'member'->>'display' AS patient_name,
  regexp_replace(resource->'encounter'->>'reference', 'urn:uuid:', '') AS encounter_id,
  (resource->'period'->>'start')::TIMESTAMP AS start_timestamp,
  split_part(resource->'participant'->1->'member'->>'reference', '|', 2) AS pactitioner_id,
  resource->'participant'->1->'member'->>'display' AS practitioner,
  split_part(resource->'participant'->2->'member'->>'reference', '|', 2) AS organization_id,
  resource->'participant'->1->'member'->>'display' AS organization,
  resource->'reasonCode'->0->'coding'->0->>'code' AS reason_code,
  regexp_replace(resource->'reasonCode'->0->'coding'->0->>'display', ' \((.*?)\)', '') AS reason,
  regexp_extract(resource->'reasonCode'->0->'coding'->0->>'display', '\((.*?)\)', 1) AS reason_type,
FROM 
  bronze.synthea
WHERE resource_type='CareTeam';

-- 10. Medication Administration
CREATE OR REPLACE TABLE silver.synthea_medication_administration AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  resource->'medicationCodeableConcept'->'coding'->0->>'code' AS medication_code,
  resource->'medicationCodeableConcept'->'coding'->0->>'display' AS medication,
  regexp_replace(resource->'subject'->>'reference', 'urn:uuid:', '') AS patient_id,
  regexp_replace(resource->'context'->>'reference', 'urn:uuid:', '') AS context_id,
  (resource->>'effectiveDateTime')::TIMESTAMP AS effective_timestamp,
  CASE WHEN regexp_replace(resource->'reasonReference'->0->>'reference', 'urn:uuid:', '') IS NOT NULL
    THEN regexp_replace(resource->'reasonReference'->0->>'reference', 'urn:uuid:', '')
    ELSE resource->'reasonCode'->0->'coding'->0->>'code' END
  AS reason_id,
  CASE WHEN regexp_replace(resource->'reasonReference'->0->>'display', ' \((.*?)\)', '') IS NOT NULL
    THEN regexp_replace(resource->'reasonReference'->0->>'display', ' \((.*?)\)', '')
    ELSE regexp_replace(resource->'reasonCode'->0->'coding'->0->>'display', '\((.*?)\)', '') END
  AS reason,
  CASE WHEN regexp_extract(resource->'reasonReference'->0->>'display', '\((.*?)\)', 1) IS NOT NULL
    THEN regexp_extract(resource->'reasonReference'->0->>'display', '\((.*?)\)', 1) 
    ELSE regexp_extract(resource->'reasonCode'->0->'coding'->0->>'display', '\((.*?)\)', 1) END
  AS reason_type,
FROM
  bronze.synthea
WHERE
  resource_type='MedicationAdministration';

-- 11. Medication Request
CREATE OR REPLACE TABLE silver.synthea_medication_request AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  resource->>'intent' AS intent,
  resource->'category'->0->'coding'->0->>'code' AS category,
  CASE WHEN regexp_replace(resource->'medicationReference'->>'reference', 'urn:uuid:', '') IS NOT NULL
    THEN regexp_replace(resource->'medicationReference'->>'reference', 'urn:uuid:', '')
    ELSE resource->'medicationCodeableConcept'->'coding'->0->>'code' END
    AS medication_id,
  regexp_replace(resource->'subject'->>'reference', 'urn:uuid:', '') AS patient_id,
  regexp_replace(resource->'encounter'->>'reference', 'urn:uuid:', '') AS encounter_id,
  (resource->>'authoredOn')::TIMESTAMP AS authored_on,
  split_part(resource->'requester'->>'reference', '|', 2) AS practitioner_id,
  resource->'requester'->>'display' AS practitioner,
  regexp_replace(resource->'reasonReference'->0->>'reference', 'urn:uuid:', '') AS reason_id,
  regexp_replace(resource->'reasonReference'->0->>'display', ' \((.*?)\)', '') AS reason,
  regexp_extract(resource->'reasonReference'->0->>'display', '\((.*?)\)', 1) AS reason_type
FROM
  bronze.synthea
WHERE resource_type='MedicationRequest';

-- 12. Procedure
CREATE OR REPLACE TABLE silver.synthea_procedure AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  resource->'code'->'coding'->0->>'code' AS procedure_code,
  regexp_replace(resource->'code'->'coding'->0->>'display', ' \((.*?)\)', '') AS reason,
  regexp_extract(resource->'code'->'coding'->0->>'display', '\((.*?)\)', 1) AS reason_type,
  regexp_replace(resource->'subject'->>'reference', 'urn:uuid:', '') as patient_id,
  regexp_replace(resource->'encounter'->>'reference', 'urn:uuid:', '') AS encounter,
  (resource->'performedPeriod'->>'start')::TIMESTAMP AS start_timestamp,
  (resource-> 'performedPeriod'->>'end')::TIMESTAMP AS end_timpstamp,
  resource->'code'->'coding'->0->>'code' AS procedure_code,
  regexp_replace(resource->'code'->'coding'->0->>'display', ' \((.*?)\)', '') AS procedure,
  regexp_extract(resource->'code'->'coding'->0->>'display', '\((.*?)\)', 1) AS procedure_type,
  split_part(resource->'location'->>'reference', '|', 2) AS location_id,
  resource->'location'->>'display' AS name
FROM 
  bronze.synthea
WHERE resource_type='Procedure';