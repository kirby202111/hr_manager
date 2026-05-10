from datetime import date, time

from pydantic import BaseModel


class AttendanceCheckIn(BaseModel):
    employee_id: int
    date: date
    check_in: time


class AttendanceCheckOut(BaseModel):
    check_out: time


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    date: date
    check_in: time
    check_out: time | None = None
    status: str
    work_hours: float | None = None


class AttendanceListResponse(BaseModel):
    records: list[AttendanceResponse]
    total: int


class AttendanceStats(BaseModel):
    employee_id: int
    employee_name: str
    period_start: date
    period_end: date
    total_work_days: int = 0
    actual_work_days: int = 0
    normal_days: int = 0
    late_days: int = 0
    early_leave_days: int = 0
    absent_days: int = 0
