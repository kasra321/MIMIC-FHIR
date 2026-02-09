"""SQL query registry for vital signs EDA."""

from __future__ import annotations

import pandas as pd

from src.eda.vitals import VITALS_5

QUERIES = {
    "schema": "DESCRIBE vitals",

    "sample": """
        SELECT * FROM vitals
        WHERE encounter_id = (SELECT encounter_id FROM vitals LIMIT 1)
        ORDER BY effective_datetime, loinc_code
        LIMIT 12
    """,

    "counts": """
        SELECT
            COUNT(*) as total_rows,
            COUNT(DISTINCT patient_id) as unique_patients,
            COUNT(DISTINCT encounter_id) as unique_encounters,
            COUNT(DISTINCT loinc_code) as unique_vitals
        FROM vitals
    """,

    "completeness": """
        WITH timestamp_vitals AS (
            SELECT
                encounter_id,
                effective_datetime,
                COUNT(DISTINCT loinc_code) {filter_clause} as num_vitals
            FROM vitals
            {where_clause}
            GROUP BY encounter_id, effective_datetime
        )
        SELECT
            num_vitals,
            COUNT(*) as num_timestamps,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct
        FROM timestamp_vitals
        GROUP BY num_vitals
        ORDER BY num_vitals
    """,

    "missing_vital": """
        WITH all_loinc AS (
            SELECT DISTINCT loinc_code FROM vitals
        ),
        timestamp_vitals AS (
            SELECT
                encounter_id,
                effective_datetime,
                LIST(DISTINCT loinc_code) as present_loincs
            FROM vitals
            GROUP BY encounter_id, effective_datetime
            HAVING COUNT(DISTINCT loinc_code) = 5
        )
        SELECT
            loinc_code as missing_loinc,
            COUNT(*) as times_missing,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM timestamp_vitals), 2) as pct
        FROM all_loinc, timestamp_vitals
        WHERE NOT list_contains(present_loincs, loinc_code)
        GROUP BY loinc_code
        ORDER BY times_missing DESC
    """,

    "missingness_matrix": """
        WITH all_timestamps AS (
            SELECT DISTINCT encounter_id, effective_datetime
            FROM vitals
        )
        SELECT
            t.encounter_id,
            t.effective_datetime,
            MAX(CASE WHEN v.loinc_code = '8310-5' THEN 1 ELSE 0 END) AS temp_present,
            MAX(CASE WHEN v.loinc_code = '8867-4' THEN 1 ELSE 0 END) AS hr_present,
            MAX(CASE WHEN v.loinc_code = '9279-1' THEN 1 ELSE 0 END) AS rr_present,
            MAX(CASE WHEN v.loinc_code = '2708-6' THEN 1 ELSE 0 END) AS spo2_present,
            MAX(CASE WHEN v.loinc_code = '8480-6' THEN 1 ELSE 0 END) AS sbp_present,
            MAX(CASE WHEN v.loinc_code = '8462-4' THEN 1 ELSE 0 END) AS dbp_present
        FROM all_timestamps t
        LEFT JOIN vitals v
            ON t.encounter_id = v.encounter_id
            AND t.effective_datetime = v.effective_datetime
        GROUP BY t.encounter_id, t.effective_datetime
    """,

    "temporal_features": """
        WITH all_combos AS (
            SELECT DISTINCT
                encounter_id,
                effective_datetime,
                effective_datetime::TIMESTAMP AS ts
            FROM vitals
        ),
        with_temp AS (
            SELECT
                a.encounter_id,
                a.effective_datetime,
                a.ts,
                EXTRACT(HOUR FROM a.ts) AS hour_of_day,
                EXTRACT(DOW FROM a.ts) AS day_of_week,
                MAX(CASE WHEN v.loinc_code = '8310-5' THEN 1 ELSE 0 END) AS temp_present,
                MAX(CASE WHEN v.loinc_code = '8867-4' THEN 1 ELSE 0 END) AS hr_present,
                MAX(CASE WHEN v.loinc_code = '9279-1' THEN 1 ELSE 0 END) AS rr_present,
                MAX(CASE WHEN v.loinc_code = '2708-6' THEN 1 ELSE 0 END) AS spo2_present
            FROM all_combos a
            LEFT JOIN vitals v ON a.encounter_id = v.encounter_id
                              AND a.effective_datetime = v.effective_datetime
            GROUP BY a.encounter_id, a.effective_datetime, a.ts
        ),
        with_position AS (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY encounter_id ORDER BY ts) AS obs_position,
                COUNT(*) OVER (PARTITION BY encounter_id) AS total_obs
            FROM with_temp
        )
        SELECT
            *,
            CASE
                WHEN obs_position <= total_obs * 0.33 THEN 'Early'
                WHEN obs_position <= total_obs * 0.66 THEN 'Middle'
                ELSE 'Late'
            END AS encounter_phase
        FROM with_position
    """,

    "conditional_values": """
        WITH pivoted AS (
            SELECT
                encounter_id,
                effective_datetime,
                MAX(CASE WHEN loinc_code = '8310-5' THEN value END) AS temp_value,
                MAX(CASE WHEN loinc_code = '8867-4' THEN value END) AS hr_value,
                MAX(CASE WHEN loinc_code = '9279-1' THEN value END) AS rr_value,
                MAX(CASE WHEN loinc_code = '2708-6' THEN value END) AS spo2_value,
                MAX(CASE WHEN loinc_code = '8480-6' THEN value END) AS sbp_value,
                MAX(CASE WHEN loinc_code = '8462-4' THEN value END) AS dbp_value
            FROM vitals
            GROUP BY encounter_id, effective_datetime
        )
        SELECT
            *,
            CASE WHEN temp_value IS NOT NULL THEN 1 ELSE 0 END AS temp_present
        FROM pivoted
    """,

    "time_deltas": """
        WITH timestamp_vitals AS (
            SELECT
                encounter_id,
                effective_datetime::TIMESTAMP as ts,
                COUNT(DISTINCT loinc_code) {filter_clause} as num_vitals
            FROM vitals
            GROUP BY encounter_id, effective_datetime
        ),
        complete_ts AS (
            SELECT encounter_id, ts
            FROM timestamp_vitals
            WHERE num_vitals = {required_count}
        ),
        deltas AS (
            SELECT
                encounter_id,
                ts,
                LAG(ts) OVER (PARTITION BY encounter_id ORDER BY ts) as prev_ts,
                EXTRACT(EPOCH FROM (ts - LAG(ts) OVER (PARTITION BY encounter_id ORDER BY ts))) / 60.0 as delta_min
            FROM complete_ts
        )
        SELECT
            COUNT(*) as n_deltas,
            ROUND(MIN(delta_min), 1) as min,
            ROUND(PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY delta_min), 1) as p10,
            ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY delta_min), 1) as p25,
            ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY delta_min), 1) as p50_median,
            ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY delta_min), 1) as p75,
            ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY delta_min), 1) as p90,
            ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY delta_min), 1) as p95,
            ROUND(MAX(delta_min), 1) as max
        FROM deltas
        WHERE delta_min IS NOT NULL
    """,

    "time_delta_buckets": """
        WITH timestamp_vitals AS (
            SELECT
                encounter_id,
                effective_datetime::TIMESTAMP as ts,
                COUNT(DISTINCT loinc_code) {filter_clause} as num_vitals
            FROM vitals
            GROUP BY encounter_id, effective_datetime
        ),
        complete_ts AS (
            SELECT encounter_id, ts
            FROM timestamp_vitals
            WHERE num_vitals = {required_count}
        ),
        deltas AS (
            SELECT
                EXTRACT(EPOCH FROM (ts - LAG(ts) OVER (PARTITION BY encounter_id ORDER BY ts))) / 60.0 as delta_min
            FROM complete_ts
        )
        SELECT
            CASE
                WHEN delta_min <= 60 THEN '0-1 hr'
                WHEN delta_min <= 120 THEN '1-2 hrs'
                WHEN delta_min <= 180 THEN '2-3 hrs'
                WHEN delta_min <= 240 THEN '3-4 hrs'
                WHEN delta_min <= 360 THEN '4-6 hrs'
                WHEN delta_min <= 480 THEN '6-8 hrs'
                ELSE '>8 hrs'
            END as time_bucket,
            CASE
                WHEN delta_min <= 60 THEN 1
                WHEN delta_min <= 120 THEN 2
                WHEN delta_min <= 180 THEN 3
                WHEN delta_min <= 240 THEN 4
                WHEN delta_min <= 360 THEN 5
                WHEN delta_min <= 480 THEN 6
                ELSE 7
            END as bucket_order,
            COUNT(*) as count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct
        FROM deltas
        WHERE delta_min IS NOT NULL
        GROUP BY 1, 2
        ORDER BY bucket_order
    """,

    "delta_by_position": """
        WITH timestamp_vitals AS (
            SELECT
                encounter_id,
                effective_datetime::TIMESTAMP as ts,
                COUNT(DISTINCT loinc_code) {filter_clause} as num_vitals
            FROM vitals
            GROUP BY encounter_id, effective_datetime
        ),
        complete_ts AS (
            SELECT encounter_id, ts
            FROM timestamp_vitals
            WHERE num_vitals = {required_count}
        ),
        deltas AS (
            SELECT
                encounter_id,
                ts,
                EXTRACT(EPOCH FROM (ts - LAG(ts) OVER (PARTITION BY encounter_id ORDER BY ts))) / 60.0 AS delta_min,
                ROW_NUMBER() OVER (PARTITION BY encounter_id ORDER BY ts) AS delta_idx
            FROM complete_ts
        )
        SELECT
            delta_idx,
            ROUND(AVG(delta_min), 1) AS avg_delta_min,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY delta_min), 1) AS median_delta_min,
            COUNT(*) AS n_encounters
        FROM deltas
        WHERE delta_min IS NOT NULL
        GROUP BY delta_idx
        ORDER BY delta_idx
    """,

    "encounter_metrics": """
        WITH timestamp_vitals AS (
            SELECT
                encounter_id,
                effective_datetime::TIMESTAMP as ts,
                COUNT(DISTINCT loinc_code) {filter_clause} as num_vitals
            FROM vitals
            GROUP BY encounter_id, effective_datetime
        ),
        complete_ts AS (
            SELECT encounter_id, ts
            FROM timestamp_vitals
            WHERE num_vitals = {required_count}
        ),
        encounter_stats AS (
            SELECT
                encounter_id,
                COUNT(*) AS n_observations,
                EXTRACT(EPOCH FROM (MAX(ts) - MIN(ts))) / 3600.0 AS duration_hrs
            FROM complete_ts
            GROUP BY encounter_id
            HAVING COUNT(*) >= 2
        )
        SELECT
            encounter_id,
            n_observations,
            duration_hrs,
            CASE WHEN duration_hrs > 0 THEN n_observations / duration_hrs ELSE NULL END AS obs_rate_per_hr
        FROM encounter_stats
        WHERE duration_hrs > 0
    """,

    "sequence_lengths": """
        WITH timestamp_vitals AS (
            SELECT
                encounter_id,
                effective_datetime,
                COUNT(DISTINCT loinc_code) {filter_clause} as num_vitals
            FROM vitals
            GROUP BY encounter_id, effective_datetime
        ),
        enc_counts AS (
            SELECT
                encounter_id,
                SUM(CASE WHEN num_vitals = {required_count} THEN 1 ELSE 0 END) as complete_ts
            FROM timestamp_vitals
            GROUP BY encounter_id
        )
        SELECT
            COUNT(*) as n_encounters,
            SUM(CASE WHEN complete_ts >= 2 THEN 1 ELSE 0 END) as encounters_usable,
            ROUND(100.0 * SUM(CASE WHEN complete_ts >= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_usable,
            ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY complete_ts), 0) as p25,
            ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY complete_ts), 0) as p50,
            ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY complete_ts), 0) as p75,
            ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY complete_ts), 0) as p95
        FROM enc_counts
    """,

    "sequence_length_hist": """
        WITH timestamp_vitals AS (
            SELECT
                encounter_id,
                effective_datetime,
                COUNT(DISTINCT loinc_code) {filter_clause} as num_vitals
            FROM vitals
            GROUP BY encounter_id, effective_datetime
        ),
        enc_counts AS (
            SELECT
                encounter_id,
                SUM(CASE WHEN num_vitals = {required_count} THEN 1 ELSE 0 END) as complete_ts
            FROM timestamp_vitals
            GROUP BY encounter_id
        )
        SELECT
            CASE
                WHEN complete_ts = 0 THEN '0'
                WHEN complete_ts = 1 THEN '1'
                WHEN complete_ts = 2 THEN '2'
                WHEN complete_ts = 3 THEN '3'
                WHEN complete_ts <= 5 THEN '4-5'
                WHEN complete_ts <= 10 THEN '6-10'
                ELSE '>10'
            END as seq_length,
            CASE
                WHEN complete_ts = 0 THEN 0
                WHEN complete_ts = 1 THEN 1
                WHEN complete_ts = 2 THEN 2
                WHEN complete_ts = 3 THEN 3
                WHEN complete_ts <= 5 THEN 4
                WHEN complete_ts <= 10 THEN 5
                ELSE 6
            END as bucket_order,
            COUNT(*) as num_encounters,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct
        FROM enc_counts
        GROUP BY 1, 2
        ORDER BY bucket_order
    """,

    "timestep_coverage": """
        WITH timestamp_vitals AS (
            SELECT
                encounter_id,
                effective_datetime::TIMESTAMP as ts,
                COUNT(DISTINCT loinc_code) {filter_clause} as num_vitals
            FROM vitals
            GROUP BY encounter_id, effective_datetime
        ),
        complete_ts AS (
            SELECT encounter_id, ts
            FROM timestamp_vitals
            WHERE num_vitals = {required_count}
        ),
        deltas AS (
            SELECT
                EXTRACT(EPOCH FROM (ts - LAG(ts) OVER (PARTITION BY encounter_id ORDER BY ts))) / 60.0 as delta_min
            FROM complete_ts
        )
        SELECT timestep_min, timestep_label, pct_covered FROM (
            SELECT 60 as timestep_min, '1 hour' as timestep_label,
                ROUND(100.0 * SUM(CASE WHEN delta_min <= 60 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_covered
            FROM deltas WHERE delta_min IS NOT NULL
            UNION ALL
            SELECT 120, '2 hours',
                ROUND(100.0 * SUM(CASE WHEN delta_min <= 120 THEN 1 ELSE 0 END) / COUNT(*), 1)
            FROM deltas WHERE delta_min IS NOT NULL
            UNION ALL
            SELECT 180, '3 hours',
                ROUND(100.0 * SUM(CASE WHEN delta_min <= 180 THEN 1 ELSE 0 END) / COUNT(*), 1)
            FROM deltas WHERE delta_min IS NOT NULL
            UNION ALL
            SELECT 240, '4 hours',
                ROUND(100.0 * SUM(CASE WHEN delta_min <= 240 THEN 1 ELSE 0 END) / COUNT(*), 1)
            FROM deltas WHERE delta_min IS NOT NULL
            UNION ALL
            SELECT 360, '6 hours',
                ROUND(100.0 * SUM(CASE WHEN delta_min <= 360 THEN 1 ELSE 0 END) / COUNT(*), 1)
            FROM deltas WHERE delta_min IS NOT NULL
            UNION ALL
            SELECT 480, '8 hours',
                ROUND(100.0 * SUM(CASE WHEN delta_min <= 480 THEN 1 ELSE 0 END) / COUNT(*), 1)
            FROM deltas WHERE delta_min IS NOT NULL
        ) ORDER BY timestep_min
    """,

    "median_delta_per_vital": """
        WITH ordered AS (
            SELECT encounter_id, effective_datetime,
                   LAG(effective_datetime) OVER (PARTITION BY encounter_id, loinc_code ORDER BY effective_datetime) as prev_dt,
                   loinc_code
            FROM vitals
        )
        SELECT
            loinc_code,
            ROUND(MEDIAN(EXTRACT(EPOCH FROM (effective_datetime::timestamp - prev_dt::timestamp))/60), 1) as median_delta_min
        FROM ordered
        WHERE prev_dt IS NOT NULL
        GROUP BY loinc_code
        ORDER BY median_delta_min
    """,

    "comparison_6v_vs_5v": """
        WITH ts AS (
            SELECT
                encounter_id,
                effective_datetime::TIMESTAMP as ts,
                COUNT(DISTINCT loinc_code) {filter_clause} as num_vitals
            FROM vitals
            GROUP BY encounter_id, effective_datetime
        ),
        complete_ts AS (
            SELECT encounter_id, ts
            FROM ts
            WHERE num_vitals = {required_count}
        ),
        deltas AS (
            SELECT EXTRACT(EPOCH FROM (ts - LAG(ts) OVER (PARTITION BY encounter_id ORDER BY ts))) / 60.0 as delta_min
            FROM complete_ts
        )
        SELECT
            (SELECT COUNT(*) FROM complete_ts) as n_timestamps,
            (SELECT COUNT(*) FROM deltas WHERE delta_min IS NOT NULL) as n_deltas,
            (SELECT ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY delta_min), 0) FROM deltas WHERE delta_min IS NOT NULL) as median_delta
    """,
}


def run_query(
    conn, query_name: str, vitals: dict | None = None, **params
) -> pd.DataFrame:
    """Look up a named SQL query, apply parameter substitution, and execute.

    Parameters
    ----------
    conn : duckdb connection
    query_name : key into QUERIES dict
    vitals : optional dict mapping loinc_code -> name.  When provided the
        ``{filter_clause}`` placeholder becomes a FILTER restricting to those
        codes and ``{required_count}`` becomes ``len(vitals)``.  When *None*
        the full dataset (6 vitals) is assumed unless ``exclude_temp`` is set.
    **params : legacy keyword args.  ``exclude_temp=True`` is converted to
        ``vitals=VITALS_5`` for backward compatibility.
    """
    sql = QUERIES[query_name]

    # Backward compatibility: translate exclude_temp into vitals dict
    if vitals is None and params.get("exclude_temp"):
        vitals = VITALS_5

    if vitals is not None:
        codes = ", ".join(f"'{c}'" for c in vitals)
        sql = sql.replace(
            "{filter_clause}",
            f"FILTER (WHERE loinc_code IN ({codes}))",
        )
        sql = sql.replace("{required_count}", str(len(vitals)))
        sql = sql.replace(
            "{where_clause}",
            f"WHERE loinc_code IN ({codes})",
        )
    else:
        sql = sql.replace("{filter_clause}", "")
        sql = sql.replace("{required_count}", "6")
        sql = sql.replace("{where_clause}", "")

    return conn.execute(sql).df()
