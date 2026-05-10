from datetime import time, timedelta

from fastapi import HTTPException

from app.models import attendance as attendance_model
from app.models import employee as employee_model
from app.schemas.attendance import (
    AttendanceCheckIn, AttendanceCheckOut,
    AttendanceResponse, AttendanceListResponse, AttendanceStats,
)


def _fill_employee_name(record: dict) -> dict:
    emp = employee_model.get_employee_by_id(record["employee_id"])
    record["employee_name"] = emp["name"] if emp else "Unknown"
    return record


def _calculate_work_hours(check_in: time, check_out: time) -> float:
    dt_in = timedelta(hours=check_in.hour, minutes=check_in.minute, seconds=check_in.second)
    dt_out = timedelta(hours=check_out.hour, minutes=check_out.minute, seconds=check_out.second)
    return round((dt_out - dt_in).total_seconds() / 3600, 2)


def check_in(data: AttendanceCheckIn) -> AttendanceResponse:
    emp = employee_model.get_employee_by_id(data.employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {data.employee_id} not found")
    existing = attendance_model.get_attendance_by_employee_date(data.employee_id, data.date)
    if existing is not None:
        raise HTTPException(status_code=400, detail=f"Employee {data.employee_id} already checked in on {data.date}")
    status = attendance_model.calculate_status(data.check_in)
    record_data = data.model_dump()
    record_data["status"] = status
    record_data["work_hours"] = None
    record = attendance_model.create_attendance(record_data)
    return AttendanceResponse(**_fill_employee_name(record))


def check_out(record_id: int, data: AttendanceCheckOut) -> AttendanceResponse:
    record = attendance_model.get_attendance_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Attendance record {record_id} not found")
    if record.get("check_out") is not None:
        raise HTTPException(status_code=400, detail="Already checked out")
    status = attendance_model.calculate_status(record["check_in"], data.check_out)
    work_hours = _calculate_work_hours(record["check_in"], data.check_out)
    update_data = {"check_out": data.check_out, "status": status, "work_hours": work_hours}
    updated = attendance_model.update_attendance(record_id, update_data)
    return AttendanceResponse(**_fill_employee_name(updated))


def list_attendance(employee_id: int | None = None, start_date=None, end_date=None) -> AttendanceListResponse:
    records = attendance_model.get_all_attendance(employee_id, start_date, end_date)
    return AttendanceListResponse(
        records=[AttendanceResponse(**_fill_employee_name(r)) for r in records],
        total=len(records),
    )


def get_attendance(record_id: int) -> AttendanceResponse:
    record = attendance_model.get_attendance_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Attendance record {record_id} not found")
    return AttendanceResponse(**_fill_employee_name(record))


def get_employee_attendance(employee_id: int) -> list:
    emp = employee_model.get_employee_by_id(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    records = attendance_model.get_attendance_by_employee(employee_id)
    return [AttendanceResponse(**_fill_employee_name(r)) for r in records]


def get_employee_stats(employee_id: int, start_date, end_date) -> AttendanceStats:
    emp = employee_model.get_employee_by_id(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    records = attendance_model.get_all_attendance(employee_id, start_date, end_date)
    work_days = (end_date - start_date).days + 1
    normal_days = sum(1 for r in records if r["status"] == "normal")
    late_days = sum(1 for r in records if r["status"] == "late")
    early_leave_days = sum(1 for r in records if r["status"] == "early_leave")
    absent_days = work_days - len(records)
    return AttendanceStats(
        employee_id=employee_id,
        employee_name=emp["name"],
        period_start=start_date,
        period_end=end_date,
        total_work_days=work_days,
        actual_work_days=len(records),
        normal_days=normal_days,
        late_days=late_days,
        early_leave_days=early_leave_days,
        absent_days=max(absent_days, 0),
    )
