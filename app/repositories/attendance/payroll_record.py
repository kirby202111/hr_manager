"""薪资记录仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.attendance import PayrollRecord


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


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
