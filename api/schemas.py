from datetime import datetime
from pydantic import BaseModel


class UtilizationRecord(BaseModel):
    encounter_id: str
    source: str | None
    patient_id: str | None
    encounter_class: str | None
    period_start: datetime | None
    period_end: datetime | None
    los_hours: float | None
    gender: str | None
    birth_date: datetime | None
    age_at_visit: float | None
    race: str | None
    ethnicity: str | None
    encounters_6m: int
    encounters_12m: int
    encounters_24m: int
    ed_visits_12m: int
    inpatient_12m: int
    ambulatory_12m: int
    wellness_12m: int
    earliest_prior_encounter: datetime | None
    most_recent_prior_encounter: datetime | None
    total_conditions: int
    chronic_conditions: int
    encounter_diagnoses: int
    distinct_diagnosis_codes: int


class UtilizationStats(BaseModel):
    source: str | None
    encounter_class: str | None
    total_encounters: int
    avg_los_hours: float | None
    avg_age: float | None
    avg_encounters_12m: float | None
    avg_chronic_conditions: float | None
