"""考勤记录仓储。"""

from datetime import date

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.attendance import AttendanceRecord


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_attendance_records(
    worker_id: int | None = None,
    work_date: date | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(AttendanceRecord)
        if worker_id is not None:
            query = query.filter(AttendanceRecord.worker_id == worker_id)
        if work_date is not None:
            query = query.filter(AttendanceRecord.work_date == work_date)
        if status is not None:
            query = query.filter(AttendanceRecord.status == status)
        return [row.to_dict() for row in query.all()]


def get_attendance_record_by_id(attendance_record_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(AttendanceRecord, attendance_record_id)
        return row.to_dict() if row else None


def get_attendance_record_by_worker_and_work_date(
    worker_id: int,
    work_date: date,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.query(AttendanceRecord).filter(
            AttendanceRecord.worker_id == worker_id,
            AttendanceRecord.work_date == work_date,
        ).first()
        return row.to_dict() if row else None


def create_attendance_record(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = AttendanceRecord(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_attendance_record(attendance_record_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(AttendanceRecord, attendance_record_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_attendance_record(attendance_record_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(AttendanceRecord, attendance_record_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
