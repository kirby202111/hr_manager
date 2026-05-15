from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import db_session
from app.models.department import Department as DepartmentORM
from app.models.employee import Employee as EmployeeORM


def get_all_departments(db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        departments = session.query(DepartmentORM).all()
        return [d.to_dict() for d in departments]


def get_department_by_id(department_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        dept = session.get(DepartmentORM, department_id)
        return dept.to_dict() if dept else None


def get_department_by_name(name: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        dept = session.query(DepartmentORM).filter_by(name=name).first()
        return dept.to_dict() if dept else None


def create_department(department_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        dept = DepartmentORM(**department_data)
        session.add(dept)
        session.flush()
        session.refresh(dept)
        return dept.to_dict()


def update_department(department_id: int, department_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        dept = session.get(DepartmentORM, department_id)
        if dept is None:
            return None
        for k, v in department_data.items():
            if v is not None:
                setattr(dept, k, v)
        session.flush()
        session.refresh(dept)
        return dept.to_dict()


def delete_department(department_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        dept = session.get(DepartmentORM, department_id)
        if dept is None:
            return False
        session.delete(dept)
        session.flush()
        return True


def count_employees_by_department(db: Session | None = None) -> dict[int, int]:
    with db_session(db) as session:
        rows = (
            session.query(EmployeeORM.department_id, func.count(EmployeeORM.id))
            .filter(EmployeeORM.department_id.isnot(None))
            .group_by(EmployeeORM.department_id)
            .all()
        )
        return {department_id: count for department_id, count in rows}
