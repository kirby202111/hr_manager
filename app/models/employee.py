from app.database import SessionLocal
from app.models.orm import Employee as EmployeeORM


def get_all_employees() -> list[dict]:
    with SessionLocal() as session:
        employees = session.query(EmployeeORM).all()
        return [e.to_dict() for e in employees]


def get_employee_by_id(employee_id: int) -> dict | None:
    with SessionLocal() as session:
        emp = session.get(EmployeeORM, employee_id)
        return emp.to_dict() if emp else None


def get_employees_by_department(department_id: int) -> list[dict]:
    with SessionLocal() as session:
        employees = session.query(EmployeeORM).filter_by(department_id=department_id).all()
        return [e.to_dict() for e in employees]


def create_employee(employee_data: dict) -> dict:
    with SessionLocal() as session:
        emp = EmployeeORM(**employee_data)
        session.add(emp)
        session.commit()
        session.refresh(emp)
        return emp.to_dict()


def update_employee(employee_id: int, employee_data: dict) -> dict | None:
    with SessionLocal() as session:
        emp = session.get(EmployeeORM, employee_id)
        if emp is None:
            return None
        for k, v in employee_data.items():
            if v is not None:
                setattr(emp, k, v)
        session.commit()
        session.refresh(emp)
        return emp.to_dict()


def delete_employee(employee_id: int) -> bool:
    with SessionLocal() as session:
        emp = session.get(EmployeeORM, employee_id)
        if emp is None:
            return False
        session.delete(emp)
        session.commit()
        return True
