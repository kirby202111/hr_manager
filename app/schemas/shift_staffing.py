from datetime import date, datetime, time

from pydantic import BaseModel


class ShiftDefinitionCreate(BaseModel):
    code: str
    name: str
    start_time: time
    end_time: time
    shift_type: str = "day"
    allowance_rate: float = 1.0


class ShiftDefinitionUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    shift_type: str | None = None
    allowance_rate: float | None = None


class ShiftDefinitionResponse(ShiftDefinitionCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class ProductionShiftPlanCreate(BaseModel):
    order_id: int | None = None
    line_id: int
    shift_id: int
    work_date: date
    required_headcount: int
    status: str = "draft"
    created_by: str | None = None


class ProductionShiftPlanUpdate(BaseModel):
    order_id: int | None = None
    line_id: int | None = None
    shift_id: int | None = None
    work_date: date | None = None
    required_headcount: int | None = None
    status: str | None = None
    created_by: str | None = None


class ProductionShiftPlanResponse(ProductionShiftPlanCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class WorkerShiftAssignmentCreate(BaseModel):
    plan_id: int
    worker_id: int
    workstation_id: int
    assignment_type: str = "normal"
    status: str = "planned"


class WorkerShiftAssignmentUpdate(BaseModel):
    assignment_type: str | None = None
    status: str | None = None


class WorkerShiftAssignmentResponse(WorkerShiftAssignmentCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class EligibilityCheckRequest(BaseModel):
    workstation_id: int
    create_risk_signal: bool = False


class ValidationIssue(BaseModel):
    signal_type: str
    severity: str
    message: str
    employee_id: int | None = None
    workstation_id: int | None = None
    shift_assignment_id: int | None = None


class ValidationResult(BaseModel):
    valid: bool
    issues: list[ValidationIssue]
