"""排班域 Schema，覆盖班次模板、排班计划与排班分配。"""

from datetime import date, datetime, time

from pydantic import BaseModel


class ShiftTemplateCreate(BaseModel):
    """班次模板创建输入。"""

    code: str
    name: str
    shift_type: str
    start_time: time
    end_time: time
    allowance_rate: float = 0.0
    status: str = "active"


class ShiftTemplateUpdate(BaseModel):
    """班次模板部分更新输入。"""

    code: str | None = None
    name: str | None = None
    shift_type: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    allowance_rate: float | None = None
    status: str | None = None


class ShiftTemplateResponse(BaseModel):
    """班次模板标准响应。"""

    id: int
    code: str
    name: str
    shift_type: str
    start_time: time
    end_time: time
    allowance_rate: float
    status: str
    created_at: datetime
    updated_at: datetime


class ShiftTemplateListResponse(BaseModel):
    """班次模板列表响应。"""

    shift_templates: list[ShiftTemplateResponse]
    total: int


class ShiftPlanCreate(BaseModel):
    """排班计划创建输入。"""

    production_order_id: int | None = None
    production_line_id: int
    shift_template_id: int
    work_date: date
    required_headcount: int
    status: str = "planned"
    created_by: str | None = None


class ShiftPlanUpdate(BaseModel):
    """排班计划部分更新输入。"""

    production_order_id: int | None = None
    production_line_id: int | None = None
    shift_template_id: int | None = None
    work_date: date | None = None
    required_headcount: int | None = None
    status: str | None = None
    created_by: str | None = None


class ShiftPlanResponse(BaseModel):
    """排班计划标准响应。"""

    id: int
    production_order_id: int | None = None
    production_line_id: int
    shift_template_id: int
    work_date: date
    required_headcount: int
    status: str
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime


class ShiftPlanListResponse(BaseModel):
    """排班计划列表响应。"""

    shift_plans: list[ShiftPlanResponse]
    total: int


class ShiftAssignmentCreate(BaseModel):
    """排班分配明细创建输入。"""

    shift_plan_id: int
    worker_id: int
    workstation_id: int
    assignment_type: str
    status: str = "scheduled"
    assigned_role: str | None = None


class ShiftAssignmentUpdate(BaseModel):
    """排班分配明细部分更新输入。"""

    shift_plan_id: int | None = None
    worker_id: int | None = None
    workstation_id: int | None = None
    assignment_type: str | None = None
    status: str | None = None
    assigned_role: str | None = None


class ShiftAssignmentResponse(BaseModel):
    """排班分配明细标准响应。"""

    id: int
    shift_plan_id: int
    worker_id: int
    workstation_id: int
    assignment_type: str
    status: str
    assigned_role: str | None = None
    eligibility_status: str | None = None
    eligibility_summary_reason: str | None = None
    eligibility_snapshot_id: int | None = None
    created_at: datetime
    updated_at: datetime


class ShiftAssignmentListResponse(BaseModel):
    """排班分配明细列表响应。"""

    shift_assignments: list[ShiftAssignmentResponse]
    total: int


__all__ = [
    "ShiftAssignmentCreate",
    "ShiftAssignmentListResponse",
    "ShiftAssignmentResponse",
    "ShiftAssignmentUpdate",
    "ShiftPlanCreate",
    "ShiftPlanListResponse",
    "ShiftPlanResponse",
    "ShiftPlanUpdate",
    "ShiftTemplateCreate",
    "ShiftTemplateListResponse",
    "ShiftTemplateResponse",
    "ShiftTemplateUpdate",
]
