from sqlalchemy.orm import Session

from app.database import db_session
from app.models.employee import Employee as EmployeeORM


def get_all_employees(db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        employees = session.query(EmployeeORM).all()
        return [e.to_dict() for e in employees]


def get_employee_by_id(employee_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        emp = session.get(EmployeeORM, employee_id)
        return emp.to_dict() if emp else None


def get_employees_by_department(department_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        employees = session.query(EmployeeORM).filter_by(department_id=department_id).all()
        return [e.to_dict() for e in employees]


def create_employee(employee_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        emp = EmployeeORM(**employee_data)
        session.add(emp)
        session.flush()
        session.refresh(emp)
        return emp.to_dict()


def update_employee(employee_id: int, employee_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        emp = session.get(EmployeeORM, employee_id)
        if emp is None:
            return None
        for k, v in employee_data.items():
            if v is not None:
                setattr(emp, k, v)
        session.flush()
        session.refresh(emp)
        return emp.to_dict()


def delete_employee(employee_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        emp = session.get(EmployeeORM, employee_id)
        if emp is None:
            return False
        session.delete(emp)
        session.flush()
        return True
