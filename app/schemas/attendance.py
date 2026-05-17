"""履约域 Schema，覆盖考勤、请假与薪资记录。"""

from datetime import date, datetime, time

from pydantic import BaseModel


class AttendanceRecordCreate(BaseModel):
    """考勤记录创建输入。"""

    worker_id: int
    work_date: date
    check_in_time: time
    check_out_time: time | None = None
    status: str
    work_hours: float | None = None


class AttendanceRecordUpdate(BaseModel):
    """考勤记录部分更新输入。"""

    worker_id: int | None = None
    work_date: date | None = None
    check_in_time: time | None = None
    check_out_time: time | None = None
    status: str | None = None
    work_hours: float | None = None


class AttendanceRecordResponse(BaseModel):
    """考勤记录标准响应。"""

    id: int
    worker_id: int
    work_date: date
    check_in_time: time
    check_out_time: time | None = None
    status: str
    work_hours: float | None = None
    created_at: datetime
    updated_at: datetime


class AttendanceRecordListResponse(BaseModel):
    """考勤记录列表响应。"""

    attendance_records: list[AttendanceRecordResponse]
    total: int


class LeaveRequestCreate(BaseModel):
    """请假申请创建输入。"""

    worker_id: int
    leave_type: str
    leave_type_name: str
    start_date: date
    end_date: date
    requested_days: int
    reason: str | None = None
    status: str = "draft"
    approver_name: str | None = None
    approved_at: date | None = None


class LeaveRequestUpdate(BaseModel):
    """请假申请部分更新输入。"""

    worker_id: int | None = None
    leave_type: str | None = None
    leave_type_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    requested_days: int | None = None
    reason: str | None = None
    status: str | None = None
    approver_name: str | None = None
    approved_at: date | None = None


class LeaveRequestResponse(BaseModel):
    """请假申请标准响应。"""

    id: int
    worker_id: int
    leave_type: str
    leave_type_name: str
    start_date: date
    end_date: date
    requested_days: int
    reason: str | None = None
    status: str
    approver_name: str | None = None
    approved_at: date | None = None
    created_at: datetime
    updated_at: datetime


class LeaveRequestListResponse(BaseModel):
    """请假申请列表响应。"""

    leave_requests: list[LeaveRequestResponse]
    total: int


class PayrollRecordCreate(BaseModel):
    """薪资记录创建输入。"""

    worker_id: int
    pay_period: str
    base_salary: float
    bonuses: float = 0.0
    deductions: float = 0.0
    net_salary: float
    status: str = "draft"
    payment_date: date | None = None


class PayrollRecordUpdate(BaseModel):
    """薪资记录部分更新输入。"""

    worker_id: int | None = None
    pay_period: str | None = None
    base_salary: float | None = None
    bonuses: float | None = None
    deductions: float | None = None
    net_salary: float | None = None
    status: str | None = None
    payment_date: date | None = None


class PayrollRecordResponse(BaseModel):
    """薪资记录标准响应。"""

    id: int
    worker_id: int
    pay_period: str
    base_salary: float
    bonuses: float
    deductions: float
    net_salary: float
    status: str
    payment_date: date | None = None
    created_at: datetime
    updated_at: datetime


class PayrollRecordListResponse(BaseModel):
    """薪资记录列表响应。"""

    payroll_records: list[PayrollRecordResponse]
    total: int


__all__ = [
    "AttendanceRecordCreate",
    "AttendanceRecordListResponse",
    "AttendanceRecordResponse",
    "AttendanceRecordUpdate",
    "LeaveRequestCreate",
    "LeaveRequestListResponse",
    "LeaveRequestResponse",
    "LeaveRequestUpdate",
    "PayrollRecordCreate",
    "PayrollRecordListResponse",
    "PayrollRecordResponse",
    "PayrollRecordUpdate",
]
