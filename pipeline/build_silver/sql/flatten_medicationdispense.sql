-- Flatten "MedicationDispense" resources into silver table

CREATE OR REPLACE TABLE silver.medication_dispense AS
SELECT
  resource->>'id' AS resource_id,
  resource->>'status' AS status,
  regexp_replace(resource->'context'->>'reference', 'Encounter/', '') AS encounter_id,
  regexp_replace(resource->'subject'->>'reference', 'Patient/', '') AS patient_id,
  resource->'medicationCodeableConcept'->'coding'->0->>'code' AS medication_code,
  resource->'medicationCodeableConcept'->>'text' AS medication_name,
  (resource->>'whenHandedOver')::TIMESTAMP AS handed_over_timestamp
FROM
  bronze.fhir_resources
WHERE resource_type='MedicationDispense'
