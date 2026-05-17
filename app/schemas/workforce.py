"""人员域 Schema，覆盖人员主数据与任职分配。"""

from datetime import date, datetime

from pydantic import BaseModel


class WorkerCreate(BaseModel):
    """人员创建输入。"""

    worker_code: str
    full_name: str
    employment_type: str
    status: str = "active"
    organization_unit_id: int | None = None
    hire_date: date | None = None
    exit_date: date | None = None
    base_salary: float | None = None
    phone_number: str | None = None
    notes: str | None = None


class WorkerUpdate(BaseModel):
    """人员部分更新输入。"""

    worker_code: str | None = None
    full_name: str | None = None
    employment_type: str | None = None
    status: str | None = None
    organization_unit_id: int | None = None
    hire_date: date | None = None
    exit_date: date | None = None
    base_salary: float | None = None
    phone_number: str | None = None
    notes: str | None = None


class WorkerResponse(BaseModel):
    """人员标准响应。"""

    id: int
    worker_code: str
    full_name: str
    employment_type: str
    status: str
    organization_unit_id: int | None = None
    hire_date: date | None = None
    exit_date: date | None = None
    base_salary: float | None = None
    phone_number: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkerListResponse(BaseModel):
    """人员列表响应。"""

    workers: list[WorkerResponse]
    total: int


class WorkerAssignmentCreate(BaseModel):
    """人员任职/归属记录创建输入。"""

    worker_id: int
    organization_unit_id: int | None = None
    production_line_id: int | None = None
    production_team_id: int | None = None
    role_title: str
    assignment_type: str
    status: str = "active"
    start_date: date
    end_date: date | None = None
    is_primary: bool = True
    notes: str | None = None


class WorkerAssignmentUpdate(BaseModel):
    """人员任职/归属记录部分更新输入。"""

    worker_id: int | None = None
    organization_unit_id: int | None = None
    production_line_id: int | None = None
    production_team_id: int | None = None
    role_title: str | None = None
    assignment_type: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_primary: bool | None = None
    notes: str | None = None


class WorkerAssignmentResponse(BaseModel):
    """人员任职/归属记录标准响应。"""

    id: int
    worker_id: int
    organization_unit_id: int | None = None
    production_line_id: int | None = None
    production_team_id: int | None = None
    role_title: str
    assignment_type: str
    status: str
    start_date: date
    end_date: date | None = None
    is_primary: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkerAssignmentListResponse(BaseModel):
    """人员任职/归属记录列表响应。"""

    worker_assignments: list[WorkerAssignmentResponse]
    total: int


__all__ = [
    "WorkerAssignmentCreate",
    "WorkerAssignmentListResponse",
    "WorkerAssignmentResponse",
    "WorkerAssignmentUpdate",
    "WorkerCreate",
    "WorkerListResponse",
    "WorkerResponse",
    "WorkerUpdate",
]
