from datetime import time

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.attendance import Attendance as AttendanceORM

LATE_THRESHOLD = time(9, 0)
EARLY_LEAVE_THRESHOLD = time(18, 0)


def calculate_status(check_in: time, check_out: time | None = None) -> str:
    is_late = check_in > LATE_THRESHOLD
    is_early = check_out is not None and check_out < EARLY_LEAVE_THRESHOLD
    if is_late and is_early:
        return "late"
    if is_late:
        return "late"
    if is_early:
        return "early_leave"
    return "normal"


def get_all_attendance(
    employee_id: int | None = None,
    start_date=None,
    end_date=None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(AttendanceORM)
        if employee_id is not None:
            query = query.filter_by(employee_id=employee_id)
        if start_date is not None:
            query = query.filter(AttendanceORM.date >= start_date)
        if end_date is not None:
            query = query.filter(AttendanceORM.date <= end_date)
        records = query.all()
        return [r.to_dict() for r in records]


def get_attendance_by_id(record_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        record = session.get(AttendanceORM, record_id)
        return record.to_dict() if record else None


def get_attendance_by_employee_date(employee_id: int, record_date, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        record = session.query(AttendanceORM).filter_by(employee_id=employee_id, date=record_date).first()
        return record.to_dict() if record else None


def get_attendance_by_employee(employee_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        records = session.query(AttendanceORM).filter_by(employee_id=employee_id).all()
        return [r.to_dict() for r in records]


def create_attendance(attendance_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        record = AttendanceORM(**attendance_data)
        session.add(record)
        session.flush()
        session.refresh(record)
        return record.to_dict()


def update_attendance(record_id: int, attendance_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        record = session.get(AttendanceORM, record_id)
        if record is None:
            return None
        for k, v in attendance_data.items():
            setattr(record, k, v)
        session.flush()
        session.refresh(record)
        return record.to_dict()
