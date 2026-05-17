from datetime import date, datetime

from pydantic import BaseModel, Field


class WorkerTeamAssignmentCreate(BaseModel):
    worker_id: int
    team_id: int
    line_id: int
    start_date: date
    end_date: date | None = None
    is_primary: bool = False


class WorkerTeamAssignmentResponse(WorkerTeamAssignmentCreate):
    id: int
    created_at: datetime


class WorkerProductionProfileCreate(BaseModel):
    worker_id: int
    worker_type: str = "operator"
    production_status: str = "active"
    can_support_lines: list[int] = Field(default_factory=list)
    notes: str | None = None


class WorkerProductionProfileUpdate(BaseModel):
    worker_type: str | None = None
    production_status: str | None = None
    can_support_lines: list[int] | None = None
    notes: str | None = None


class WorkerProductionProfileResponse(WorkerProductionProfileCreate):
    id: int
    created_at: datetime
    updated_at: datetime
