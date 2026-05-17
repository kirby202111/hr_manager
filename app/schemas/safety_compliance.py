from datetime import date, datetime

from pydantic import BaseModel


class SafetyTrainingCreate(BaseModel):
    title: str
    category: str = "general"
    required_for_certification_id: int | None = None
    validity_months: int | None = None
    description: str | None = None


class SafetyTrainingResponse(SafetyTrainingCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class WorkerSafetyRecordCreate(BaseModel):
    worker_id: int
    training_id: int
    completed_at: date
    score: float | None = None
    expires_at: date | None = None
    status: str = "valid"


class WorkerSafetyRecordResponse(WorkerSafetyRecordCreate):
    id: int
    created_at: datetime
