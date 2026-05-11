from app.database import SessionLocal
from app.models.department import Department as DepartmentORM


def get_all_departments() -> list[dict]:
    with SessionLocal() as session:
        departments = session.query(DepartmentORM).all()
        return [d.to_dict() for d in departments]


def get_department_by_id(department_id: int) -> dict | None:
    with SessionLocal() as session:
        dept = session.get(DepartmentORM, department_id)
        return dept.to_dict() if dept else None


def get_department_by_name(name: str) -> dict | None:
    with SessionLocal() as session:
        dept = session.query(DepartmentORM).filter_by(name=name).first()
        return dept.to_dict() if dept else None


def create_department(department_data: dict) -> dict:
    with SessionLocal() as session:
        dept = DepartmentORM(**department_data)
        session.add(dept)
        session.commit()
        session.refresh(dept)
        return dept.to_dict()


def update_department(department_id: int, department_data: dict) -> dict | None:
    with SessionLocal() as session:
        dept = session.get(DepartmentORM, department_id)
        if dept is None:
            return None
        for k, v in department_data.items():
            if v is not None:
                setattr(dept, k, v)
        session.commit()
        session.refresh(dept)
        return dept.to_dict()


def delete_department(department_id: int) -> bool:
    with SessionLocal() as session:
        dept = session.get(DepartmentORM, department_id)
        if dept is None:
            return False
        session.delete(dept)
        session.commit()
        return True
