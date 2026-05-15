from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import department as department_repo
from app.repositories import employee as employee_repo
from app.schemas.department import DepartmentCreate, DepartmentListResponse, DepartmentResponse, DepartmentUpdate


def list_departments(db: Session | None = None) -> DepartmentListResponse:
    departments = department_repo.get_all_departments(db)
    employee_counts = department_repo.count_employees_by_department(db)
    dept_responses = []
    for dept in departments:
        dept_responses.append(DepartmentResponse(employee_count=employee_counts.get(dept["id"], 0), **dept))
    return DepartmentListResponse(departments=dept_responses, total=len(dept_responses))


def get_department(department_id: int, db: Session | None = None) -> DepartmentResponse:
    dept = department_repo.get_department_by_id(department_id, db)
    if dept is None:
        raise NotFoundError(f"Department {department_id} not found")
    employees = employee_repo.get_employees_by_department(department_id, db)
    return DepartmentResponse(employee_count=len(employees), **dept)


def create_department(dept_in: DepartmentCreate, db: Session | None = None) -> DepartmentResponse:
    existing = department_repo.get_department_by_name(dept_in.name, db)
    if existing is not None:
        raise ValidationError(f"Department '{dept_in.name}' already exists")
    dept_data = dept_in.model_dump()
    dept = department_repo.create_department(dept_data, db)
    return DepartmentResponse(**dept)


def update_department(department_id: int, dept_in: DepartmentUpdate, db: Session | None = None) -> DepartmentResponse:
    dept = department_repo.get_department_by_id(department_id, db)
    if dept is None:
        raise NotFoundError(f"Department {department_id} not found")
    if dept_in.name is not None:
        existing = department_repo.get_department_by_name(dept_in.name, db)
        if existing is not None and existing["id"] != department_id:
            raise ValidationError(f"Department '{dept_in.name}' already exists")
    update_data = dept_in.model_dump(exclude_unset=True)
    updated = department_repo.update_department(department_id, update_data, db)
    employees = employee_repo.get_employees_by_department(department_id, db)
    return DepartmentResponse(employee_count=len(employees), **updated)


def delete_department(department_id: int, db: Session | None = None) -> dict:
    dept = department_repo.get_department_by_id(department_id, db)
    if dept is None:
        raise NotFoundError(f"Department {department_id} not found")
    employees = employee_repo.get_employees_by_department(department_id, db)
    if employees:
        raise ValidationError("Cannot delete department with existing employees")
    department_repo.delete_department(department_id, db)
    return {"message": f"Department {department_id} deleted"}


def get_department_employees(department_id: int, db: Session | None = None) -> list:
    dept = department_repo.get_department_by_id(department_id, db)
    if dept is None:
        raise NotFoundError(f"Department {department_id} not found")
    from app.schemas.employee import EmployeeResponse
    employees = employee_repo.get_employees_by_department(department_id, db)
    return [EmployeeResponse(**e) for e in employees]
