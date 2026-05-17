"""履约域仓储，覆盖考勤、请假与薪资。"""

from datetime import date

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.attendance import AttendanceRecord, LeaveRequest, PayrollRecord


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


def list_leave_requests(
    worker_id: int | None = None,
    status: str | None = None,
    leave_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(LeaveRequest)
        if worker_id is not None:
            query = query.filter(LeaveRequest.worker_id == worker_id)
        if status is not None:
            query = query.filter(LeaveRequest.status == status)
        if leave_type is not None:
            query = query.filter(LeaveRequest.leave_type == leave_type)
        if start_date is not None:
            query = query.filter(LeaveRequest.start_date >= start_date)
        if end_date is not None:
            query = query.filter(LeaveRequest.end_date <= end_date)
        return [row.to_dict() for row in query.all()]


def get_leave_request_by_id(leave_request_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(LeaveRequest, leave_request_id)
        return row.to_dict() if row else None


def create_leave_request(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = LeaveRequest(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_leave_request(leave_request_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(LeaveRequest, leave_request_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_leave_request(leave_request_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(LeaveRequest, leave_request_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_payroll_records(
    worker_id: int | None = None,
    pay_period: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(PayrollRecord)
        if worker_id is not None:
            query = query.filter(PayrollRecord.worker_id == worker_id)
        if pay_period is not None:
            query = query.filter(PayrollRecord.pay_period == pay_period)
        if status is not None:
            query = query.filter(PayrollRecord.status == status)
        return [row.to_dict() for row in query.all()]


def get_payroll_record_by_id(payroll_record_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(PayrollRecord, payroll_record_id)
        return row.to_dict() if row else None


def get_payroll_record_by_worker_and_pay_period(
    worker_id: int,
    pay_period: str,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.query(PayrollRecord).filter(
            PayrollRecord.worker_id == worker_id,
            PayrollRecord.pay_period == pay_period,
        ).first()
        return row.to_dict() if row else None


def create_payroll_record(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = PayrollRecord(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_payroll_record(payroll_record_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(PayrollRecord, payroll_record_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_payroll_record(payroll_record_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(PayrollRecord, payroll_record_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
