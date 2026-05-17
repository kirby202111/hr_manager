from sqlalchemy.orm import Session

from app.database import db_session
from app.models.payroll import Payroll as PayrollORM


def get_all_payrolls(worker_id: int | None = None, month: str | None = None, status: str | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(PayrollORM)
        if worker_id is not None:
            query = query.filter_by(worker_id=worker_id)
        if month is not None:
            query = query.filter_by(month=month)
        if status is not None:
            query = query.filter_by(status=status)
        return [record.to_dict() for record in query.all()]


def get_payroll_by_id(payroll_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        record = session.get(PayrollORM, payroll_id)
        return record.to_dict() if record else None


def get_payroll_by_worker_month(worker_id: int, month: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        record = session.query(PayrollORM).filter_by(worker_id=worker_id, month=month).first()
        return record.to_dict() if record else None


def get_payrolls_by_worker(worker_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        return [record.to_dict() for record in session.query(PayrollORM).filter_by(worker_id=worker_id).all()]


def create_payroll(payroll_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        record = PayrollORM(**payroll_data)
        session.add(record)
        session.flush()
        session.refresh(record)
        return record.to_dict()


def update_payroll(payroll_id: int, payroll_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        record = session.get(PayrollORM, payroll_id)
        if record is None:
            return None
        for key, value in payroll_data.items():
            setattr(record, key, value)
        session.flush()
        session.refresh(record)
        return record.to_dict()
