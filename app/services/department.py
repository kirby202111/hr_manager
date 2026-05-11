from fastapi import HTTPException

from app.repositories import department as department_repo
from app.repositories import employee as employee_repo
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentListResponse


def list_departments() -> DepartmentListResponse:
    departments = department_repo.get_all_departments()
    dept_responses = []
    for dept in departments:
        employees = employee_repo.get_employees_by_department(dept["id"])
        dept_responses.append(DepartmentResponse(employee_count=len(employees), **dept))
    return DepartmentListResponse(departments=dept_responses, total=len(dept_responses))


def get_department(department_id: int) -> DepartmentResponse:
    dept = department_repo.get_department_by_id(department_id)
    if dept is None:
        raise HTTPException(status_code=404, detail=f"Department {department_id} not found")
    employees = employee_repo.get_employees_by_department(department_id)
    return DepartmentResponse(employee_count=len(employees), **dept)


def create_department(dept_in: DepartmentCreate) -> DepartmentResponse:
    existing = department_repo.get_department_by_name(dept_in.name)
    if existing is not None:
        raise HTTPException(status_code=400, detail=f"Department '{dept_in.name}' already exists")
    dept_data = dept_in.model_dump()
    dept = department_repo.create_department(dept_data)
    return DepartmentResponse(**dept)


def update_department(department_id: int, dept_in: DepartmentUpdate) -> DepartmentResponse:
    dept = department_repo.get_department_by_id(department_id)
    if dept is None:
        raise HTTPException(status_code=404, detail=f"Department {department_id} not found")
    if dept_in.name is not None:
        existing = department_repo.get_department_by_name(dept_in.name)
        if existing is not None and existing["id"] != department_id:
            raise HTTPException(status_code=400, detail=f"Department '{dept_in.name}' already exists")
    update_data = dept_in.model_dump(exclude_unset=True)
    updated = department_repo.update_department(department_id, update_data)
    employees = employee_repo.get_employees_by_department(department_id)
    return DepartmentResponse(employee_count=len(employees), **updated)


def delete_department(department_id: int) -> dict:
    dept = department_repo.get_department_by_id(department_id)
    if dept is None:
        raise HTTPException(status_code=404, detail=f"Department {department_id} not found")
    employees = employee_repo.get_employees_by_department(department_id)
    if employees:
        raise HTTPException(status_code=400, detail="Cannot delete department with existing employees")
    department_repo.delete_department(department_id)
    return {"message": f"Department {department_id} deleted"}


def get_department_employees(department_id: int) -> list:
    dept = department_repo.get_department_by_id(department_id)
    if dept is None:
        raise HTTPException(status_code=404, detail=f"Department {department_id} not found")
    from app.schemas.employee import EmployeeResponse
    employees = employee_repo.get_employees_by_department(department_id)
    return [EmployeeResponse(**e) for e in employees]
