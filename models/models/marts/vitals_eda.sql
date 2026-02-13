MODEL (
  name marts.vitals_eda,
  kind FULL,
  grain [encounter_id, patient_id, effective_datetime]
);

WITH enriched AS (
    SELECT
        *,
        temp_present + hr_present + rr_present + spo2_present
            + sbp_present + dbp_present AS n_vitals_6,
        hr_present + rr_present + spo2_present
            + sbp_present + dbp_present AS n_vitals_5,
        hr_present + sbp_present + dbp_present AS n_vitals_3,
        EXTRACT(HOUR FROM effective_datetime) AS hour_of_day,
        EXTRACT(DOW FROM effective_datetime) AS day_of_week,
        ROW_NUMBER() OVER (
            PARTITION BY encounter_id ORDER BY effective_datetime
        ) AS obs_position,
        COUNT(*) OVER (PARTITION BY encounter_id) AS total_obs_in_encounter,
        EXTRACT(EPOCH FROM (
            effective_datetime
            - LAG(effective_datetime) OVER (
                PARTITION BY encounter_id ORDER BY effective_datetime)
        )) / 60.0 AS delta_min,
        EXTRACT(EPOCH FROM (
            MAX(effective_datetime) OVER (PARTITION BY encounter_id)
            - MIN(effective_datetime) OVER (PARTITION BY encounter_id)
        )) / 3600.0 AS encounter_duration_hrs
    FROM intermediate.vitals_wide
)
SELECT
    *,
    CASE
        WHEN obs_position <= total_obs_in_encounter * 0.33 THEN 'Early'
        WHEN obs_position <= total_obs_in_encounter * 0.66 THEN 'Middle'
        ELSE 'Late'
    END AS encounter_phase
FROM enriched
