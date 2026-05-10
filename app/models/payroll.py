from app.database import SessionLocal
from app.models.orm import Payroll as PayrollORM


def get_all_payrolls(employee_id: int | None = None, month: str | None = None, status: str | None = None) -> list[dict]:
    with SessionLocal() as session:
        query = session.query(PayrollORM)
        if employee_id is not None:
            query = query.filter_by(employee_id=employee_id)
        if month is not None:
            query = query.filter_by(month=month)
        if status is not None:
            query = query.filter_by(status=status)
        records = query.all()
        return [r.to_dict() for r in records]


def get_payroll_by_id(payroll_id: int) -> dict | None:
    with SessionLocal() as session:
        record = session.get(PayrollORM, payroll_id)
        return record.to_dict() if record else None


def get_payroll_by_employee_month(employee_id: int, month: str) -> dict | None:
    with SessionLocal() as session:
        record = session.query(PayrollORM).filter_by(employee_id=employee_id, month=month).first()
        return record.to_dict() if record else None


def get_payrolls_by_employee(employee_id: int) -> list[dict]:
    with SessionLocal() as session:
        records = session.query(PayrollORM).filter_by(employee_id=employee_id).all()
        return [r.to_dict() for r in records]


def create_payroll(payroll_data: dict) -> dict:
    with SessionLocal() as session:
        record = PayrollORM(**payroll_data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record.to_dict()


def update_payroll(payroll_id: int, payroll_data: dict) -> dict | None:
    with SessionLocal() as session:
        record = session.get(PayrollORM, payroll_id)
        if record is None:
            return None
        for k, v in payroll_data.items():
            setattr(record, k, v)
        session.commit()
        session.refresh(record)
        return record.to_dict()
