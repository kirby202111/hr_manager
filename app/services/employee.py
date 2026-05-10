from fastapi import HTTPException

from app.models import department as department_model
from app.models import employee as employee_model
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse


def _fill_department_name(employee: dict) -> dict:
    dept_id = employee.get("department_id")
    if dept_id is not None:
        dept = department_model.get_department_by_id(dept_id)
        employee["department_name"] = dept["name"] if dept else None
    return employee


def list_employees() -> EmployeeListResponse:
    employees = employee_model.get_all_employees()
    return EmployeeListResponse(
        employees=[EmployeeResponse(**_fill_department_name(e)) for e in employees],
        total=len(employees),
    )


def get_employee(employee_id: int) -> EmployeeResponse:
    employee = employee_model.get_employee_by_id(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return EmployeeResponse(**_fill_department_name(employee))


def create_employee(employee_in: EmployeeCreate) -> EmployeeResponse:
    if employee_in.department_id is not None:
        dept = department_model.get_department_by_id(employee_in.department_id)
        if dept is None:
            raise HTTPException(status_code=400, detail=f"Department {employee_in.department_id} not found")
    employee_data = employee_in.model_dump()
    employee = employee_model.create_employee(employee_data)
    return EmployeeResponse(**_fill_department_name(employee))


def update_employee(employee_id: int, employee_in: EmployeeUpdate) -> EmployeeResponse:
    existing = employee_model.get_employee_by_id(employee_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    if employee_in.department_id is not None:
        dept = department_model.get_department_by_id(employee_in.department_id)
        if dept is None:
            raise HTTPException(status_code=400, detail=f"Department {employee_in.department_id} not found")
    update_data = employee_in.model_dump(exclude_unset=True)
    employee = employee_model.update_employee(employee_id, update_data)
    return EmployeeResponse(**_fill_department_name(employee))


def delete_employee(employee_id: int) -> dict:
    success = employee_model.delete_employee(employee_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return {"message": f"Employee {employee_id} deleted"}
