from datetime import time, timedelta

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import attendance as attendance_repo
from app.repositories import worker as worker_repo
from app.schemas.attendance import (
    AttendanceCheckIn,
    AttendanceCheckOut,
    AttendanceListResponse,
    AttendanceResponse,
    AttendanceStats,
)


def _fill_worker_name(record: dict, db: Session | None = None) -> dict:
    worker = worker_repo.get_worker_by_id(record["worker_id"], db)
    record["worker_name"] = worker["name"] if worker else "Unknown"
    return record


def _calculate_work_hours(check_in: time, check_out: time) -> float:
    dt_in = timedelta(hours=check_in.hour, minutes=check_in.minute, seconds=check_in.second)
    dt_out = timedelta(hours=check_out.hour, minutes=check_out.minute, seconds=check_out.second)
    return round((dt_out - dt_in).total_seconds() / 3600, 2)


def check_in(data: AttendanceCheckIn, db: Session | None = None) -> AttendanceResponse:
    worker = worker_repo.get_worker_by_id(data.worker_id, db)
    if worker is None:
        raise NotFoundError(f"Worker {data.worker_id} not found")
    existing = attendance_repo.get_attendance_by_worker_date(data.worker_id, data.date, db)
    if existing is not None:
        raise ValidationError(f"Worker {data.worker_id} already checked in on {data.date}")
    record = attendance_repo.create_attendance(
        data.model_dump() | {"status": attendance_repo.calculate_status(data.check_in), "work_hours": None},
        db,
    )
    return AttendanceResponse(**_fill_worker_name(record, db))


def check_out(record_id: int, data: AttendanceCheckOut, db: Session | None = None) -> AttendanceResponse:
    record = attendance_repo.get_attendance_by_id(record_id, db)
    if record is None:
        raise NotFoundError(f"Attendance record {record_id} not found")
    if record.get("check_out") is not None:
        raise ValidationError("Already checked out")
    updated = attendance_repo.update_attendance(
        record_id,
        {
            "check_out": data.check_out,
            "status": attendance_repo.calculate_status(record["check_in"], data.check_out),
            "work_hours": _calculate_work_hours(record["check_in"], data.check_out),
        },
        db,
    )
    return AttendanceResponse(**_fill_worker_name(updated, db))


def list_attendance(worker_id: int | None = None, start_date=None, end_date=None, db: Session | None = None) -> AttendanceListResponse:
    records = attendance_repo.get_all_attendance(worker_id, start_date, end_date, db)
    return AttendanceListResponse(records=[AttendanceResponse(**_fill_worker_name(record, db)) for record in records], total=len(records))


def get_attendance(record_id: int, db: Session | None = None) -> AttendanceResponse:
    record = attendance_repo.get_attendance_by_id(record_id, db)
    if record is None:
        raise NotFoundError(f"Attendance record {record_id} not found")
    return AttendanceResponse(**_fill_worker_name(record, db))


def get_worker_attendance(worker_id: int, db: Session | None = None) -> list[AttendanceResponse]:
    worker = worker_repo.get_worker_by_id(worker_id, db)
    if worker is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    records = attendance_repo.get_attendance_by_worker(worker_id, db)
    return [AttendanceResponse(**_fill_worker_name(record, db)) for record in records]


def get_worker_stats(worker_id: int, start_date, end_date, db: Session | None = None) -> AttendanceStats:
    worker = worker_repo.get_worker_by_id(worker_id, db)
    if worker is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    records = attendance_repo.get_all_attendance(worker_id, start_date, end_date, db)
    work_days = (end_date - start_date).days + 1
    normal_days = sum(1 for record in records if record["status"] == "normal")
    late_days = sum(1 for record in records if record["status"] == "late")
    early_leave_days = sum(1 for record in records if record["status"] == "early_leave")
    absent_days = max(work_days - len(records), 0)
    return AttendanceStats(
        worker_id=worker_id,
        worker_name=worker["name"],
        period_start=start_date,
        period_end=end_date,
        total_work_days=work_days,
        actual_work_days=len(records),
        normal_days=normal_days,
        late_days=late_days,
        early_leave_days=early_leave_days,
        absent_days=absent_days,
    )
