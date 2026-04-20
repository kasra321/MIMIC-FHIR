import json

from fastapi import APIRouter, Query, HTTPException
from api.database import get_connection
from api.schemas import UtilizationRecord, UtilizationStats


def _to_records(df):
    """Convert DataFrame to list of dicts with native Python types."""
    return json.loads(df.to_json(orient="records", date_format="iso"))

router = APIRouter(prefix="/utilization", tags=["utilization"])

TABLE = "marts.utilization_eda"


@router.get("", response_model=list[UtilizationRecord])
def list_utilization(
    source: str | None = None,
    gender: str | None = None,
    encounter_class: str | None = None,
    min_age: float | None = None,
    max_age: float | None = None,
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
):
    filters, params = _build_filters(source, gender, encounter_class, min_age, max_age)
    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    sql = f"SELECT * FROM {TABLE} {where} ORDER BY period_start DESC LIMIT $limit OFFSET $offset"
    params["limit"] = limit
    params["offset"] = offset

    con = get_connection()
    rows = con.execute(sql, params).fetchdf()
    con.close()
    return _to_records(rows)


@router.get("/stats", response_model=list[UtilizationStats])
def utilization_stats(
    source: str | None = None,
    encounter_class: str | None = None,
):
    filters, params = [], {}
    if source:
        filters.append("source = $source")
        params["source"] = source
    if encounter_class:
        filters.append("encounter_class = $encounter_class")
        params["encounter_class"] = encounter_class

    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    sql = f"""
        SELECT
            source,
            encounter_class,
            COUNT(*) AS total_encounters,
            AVG(los_hours) AS avg_los_hours,
            AVG(age_at_visit) AS avg_age,
            AVG(encounters_12m) AS avg_encounters_12m,
            AVG(chronic_conditions) AS avg_chronic_conditions
        FROM {TABLE}
        {where}
        GROUP BY source, encounter_class
        ORDER BY source, encounter_class
    """
    con = get_connection()
    rows = con.execute(sql, params).fetchdf()
    con.close()
    return _to_records(rows)


@router.get("/patient/{patient_id}", response_model=list[UtilizationRecord])
def patient_encounters(patient_id: str):
    sql = f"SELECT * FROM {TABLE} WHERE patient_id = $patient_id ORDER BY period_start DESC"
    con = get_connection()
    rows = con.execute(sql, {"patient_id": patient_id}).fetchdf()
    con.close()
    if rows.empty:
        raise HTTPException(status_code=404, detail="Patient not found")
    return _to_records(rows)


@router.get("/{encounter_id}", response_model=UtilizationRecord)
def get_encounter(encounter_id: str):
    sql = f"SELECT * FROM {TABLE} WHERE encounter_id = $encounter_id"
    con = get_connection()
    rows = con.execute(sql, {"encounter_id": encounter_id}).fetchdf()
    con.close()
    if rows.empty:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return _to_records(rows)[0]


def _build_filters(source, gender, encounter_class, min_age, max_age):
    filters, params = [], {}
    if source:
        filters.append("source = $source")
        params["source"] = source
    if gender:
        filters.append("gender = $gender")
        params["gender"] = gender
    if encounter_class:
        filters.append("encounter_class = $encounter_class")
        params["encounter_class"] = encounter_class
    if min_age is not None:
        filters.append("age_at_visit >= $min_age")
        params["min_age"] = min_age
    if max_age is not None:
        filters.append("age_at_visit <= $max_age")
        params["max_age"] = max_age
    return filters, params
