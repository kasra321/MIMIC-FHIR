"""Single wide EDA table for vital signs analysis."""

from __future__ import annotations

import pandas as pd

EDA_WIDE_SQL = """\
WITH pivoted AS (
    SELECT
        encounter_id,
        patient_id,
        effective_datetime::TIMESTAMP AS effective_datetime,
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
    FROM vitals
    GROUP BY encounter_id, patient_id, effective_datetime
),
enriched AS (
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
    FROM pivoted
)
SELECT
    *,
    CASE
        WHEN obs_position <= total_obs_in_encounter * 0.33 THEN 'Early'
        WHEN obs_position <= total_obs_in_encounter * 0.66 THEN 'Middle'
        ELSE 'Late'
    END AS encounter_phase
FROM enriched
"""


def load_eda_table(conn) -> pd.DataFrame:
    """Execute the wide EDA query and return a DataFrame."""
    df = conn.execute(EDA_WIDE_SQL).df()
    df["effective_datetime"] = pd.to_datetime(df["effective_datetime"])
    return df
