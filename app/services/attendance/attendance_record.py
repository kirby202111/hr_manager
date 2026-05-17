"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.attendance import attendance_record as attendance_record_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.attendance import (
    AttendanceRecordCreate,
    AttendanceRecordListResponse,
    AttendanceRecordResponse,
    AttendanceRecordUpdate,
)


def _to_response(row: dict) -> AttendanceRecordResponse:
    return AttendanceRecordResponse(**row)


def _require_row(attendance_record_id: int, db: Session | None = None) -> dict:
    row = attendance_record_repo.get_attendance_record_by_id(attendance_record_id, db)
    if row is None:
        raise NotFoundError(f"Attendance record {attendance_record_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if payload.get("check_out_time") is not None and payload["check_in_time"] > payload["check_out_time"]:
        raise ValidationError("check_in_time cannot be later than check_out_time")


def list_attendance_records(
    worker_id: int | None = None,
    work_date=None,
    status: str | None = None,
    db: Session | None = None,
) -> AttendanceRecordListResponse:
    rows = attendance_record_repo.list_attendance_records(worker_id, work_date, status, db)
    return AttendanceRecordListResponse(attendance_records=[_to_response(row) for row in rows], total=len(rows))


def get_attendance_record(attendance_record_id: int, db: Session | None = None) -> AttendanceRecordResponse:
    return _to_response(_require_row(attendance_record_id, db))


def create_attendance_record(data: AttendanceRecordCreate, db: Session | None = None) -> AttendanceRecordResponse:
    payload = data.model_dump()
    _validate_payload(payload, db)
    if (
        attendance_record_repo.get_attendance_record_by_worker_and_work_date(
            payload["worker_id"],
            payload["work_date"],
            db,
        )
        is not None
    ):
        raise ConflictError("Attendance record already exists")
    row = attendance_record_repo.create_attendance_record(payload, db)
    return _to_response(row)


def update_attendance_record(
    attendance_record_id: int,
    data: AttendanceRecordUpdate,
    db: Session | None = None,
) -> AttendanceRecordResponse:
    current = _require_row(attendance_record_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = attendance_record_repo.get_attendance_record_by_worker_and_work_date(
        payload["worker_id"], payload["work_date"], db
    )
    if existing is not None and existing["id"] != attendance_record_id:
        raise ConflictError("Attendance record already exists")
    row = attendance_record_repo.update_attendance_record(attendance_record_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Attendance record {attendance_record_id} not found")
    return _to_response(row)


def delete_attendance_record(attendance_record_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(attendance_record_id, db)
    attendance_record_repo.delete_attendance_record(attendance_record_id, db)
    return {"message": f"Attendance record {attendance_record_id} deleted"}
