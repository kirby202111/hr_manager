from datetime import date, datetime

from pydantic import BaseModel

LEAVE_TYPE_NAMES = {
    "sick": "病假",
    "annual": "年假",
    "personal": "事假",
    "other": "其他",
}

LEAVE_BALANCE_DEFAULTS = {
    "annual": 10,
    "sick": 15,
    "personal": 5,
}


class LeaveCreate(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str | None = None


class LeaveUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = None


class LeaveApproval(BaseModel):
    approver: str
    comment: str | None = None


class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    leave_type: str
    leave_type_name: str
    start_date: date
    end_date: date
    days: int
    reason: str | None = None
    status: str
    approver: str | None = None
    approved_at: datetime | None = None
    created_at: datetime


class LeaveListResponse(BaseModel):
    leaves: list[LeaveResponse]
    total: int


class LeaveBalance(BaseModel):
    employee_id: int
    employee_name: str
    annual_total: int = 10
    annual_used: int = 0
    annual_remaining: int = 10
    sick_total: int = 15
    sick_used: int = 0
    sick_remaining: int = 15
    personal_total: int = 5
    personal_used: int = 0
    personal_remaining: int = 5
