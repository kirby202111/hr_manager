from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import department as department_repo
from app.repositories import employee as employee_repo
from app.schemas.employee import EmployeeCreate, EmployeeListResponse, EmployeeResponse, EmployeeUpdate


def _fill_department_name(employee: dict, db: Session | None = None) -> dict:
    dept_id = employee.get("department_id")
    if dept_id is not None:
        dept = department_repo.get_department_by_id(dept_id, db)
        employee["department_name"] = dept["name"] if dept else None
    return employee


def list_employees(db: Session | None = None) -> EmployeeListResponse:
    employees = employee_repo.get_all_employees(db)
    return EmployeeListResponse(
        employees=[EmployeeResponse(**_fill_department_name(e, db)) for e in employees],
        total=len(employees),
    )


def get_employee(employee_id: int, db: Session | None = None) -> EmployeeResponse:
    employee = employee_repo.get_employee_by_id(employee_id, db)
    if employee is None:
        raise NotFoundError(f"Employee {employee_id} not found")
    return EmployeeResponse(**_fill_department_name(employee, db))


def create_employee(employee_in: EmployeeCreate, db: Session | None = None) -> EmployeeResponse:
    if employee_in.department_id is not None:
        dept = department_repo.get_department_by_id(employee_in.department_id, db)
        if dept is None:
            raise ValidationError(f"Department {employee_in.department_id} not found")
    employee_data = employee_in.model_dump()
    employee = employee_repo.create_employee(employee_data, db)
    return EmployeeResponse(**_fill_department_name(employee, db))


def update_employee(employee_id: int, employee_in: EmployeeUpdate, db: Session | None = None) -> EmployeeResponse:
    existing = employee_repo.get_employee_by_id(employee_id, db)
    if existing is None:
        raise NotFoundError(f"Employee {employee_id} not found")
    if employee_in.department_id is not None:
        dept = department_repo.get_department_by_id(employee_in.department_id, db)
        if dept is None:
            raise ValidationError(f"Department {employee_in.department_id} not found")
    update_data = employee_in.model_dump(exclude_unset=True)
    employee = employee_repo.update_employee(employee_id, update_data, db)
    return EmployeeResponse(**_fill_department_name(employee, db))


def delete_employee(employee_id: int, db: Session | None = None) -> dict:
    success = employee_repo.delete_employee(employee_id, db)
    if not success:
        raise NotFoundError(f"Employee {employee_id} not found")
    return {"message": f"Employee {employee_id} deleted"}
