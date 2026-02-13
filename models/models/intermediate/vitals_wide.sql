MODEL (
  name intermediate.vitals_wide,
  kind FULL,
  grain [encounter_id, patient_id, effective_datetime]
);

SELECT
    encounter_id,
    patient_id,
    effective_datetime,
    MAX(CASE WHEN loinc_code = '8310-5' THEN value END) AS temp_value,
    MAX(CASE WHEN loinc_code = '8867-4' THEN value END) AS hr_value,
    MAX(CASE WHEN loinc_code = '9279-1' THEN value END) AS rr_value,
    MAX(CASE WHEN loinc_code = '2708-6' THEN value END) AS spo2_value,
    MAX(CASE WHEN loinc_code = '8480-6' THEN value END) AS sbp_value,
    MAX(CASE WHEN loinc_code = '8462-4' THEN value END) AS dbp_value,
    MAX(CASE WHEN loinc_code = '8310-5' THEN 1 ELSE 0 END) AS temp_present,
    MAX(CASE WHEN loinc_code = '8867-4' THEN 1 ELSE 0 END) AS hr_present,
    MAX(CASE WHEN loinc_code = '9279-1' THEN 1 ELSE 0 END) AS rr_present,
    MAX(CASE WHEN loinc_code = '2708-6' THEN 1 ELSE 0 END) AS spo2_present,
    MAX(CASE WHEN loinc_code = '8480-6' THEN 1 ELSE 0 END) AS sbp_present,
    MAX(CASE WHEN loinc_code = '8462-4' THEN 1 ELSE 0 END) AS dbp_present
FROM silver.observation_vitals
GROUP BY encounter_id, patient_id, effective_datetime
