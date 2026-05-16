from datetime import date, datetime

from pydantic import BaseModel, Field


class EmployeeTeamAssignmentCreate(BaseModel):
    employee_id: int
    team_id: int
    line_id: int
    start_date: date
    end_date: date | None = None
    is_primary: bool = False


class EmployeeTeamAssignmentResponse(EmployeeTeamAssignmentCreate):
    id: int
    created_at: datetime


class EmployeeProductionProfileCreate(BaseModel):
    employee_id: int
    worker_type: str = "operator"
    production_status: str = "active"
    can_support_lines: list[int] = Field(default_factory=list)
    notes: str | None = None


class EmployeeProductionProfileUpdate(BaseModel):
    worker_type: str | None = None
    production_status: str | None = None
    can_support_lines: list[int] | None = None
    notes: str | None = None


class EmployeeProductionProfileResponse(EmployeeProductionProfileCreate):
    id: int
    created_at: datetime
    updated_at: datetime
