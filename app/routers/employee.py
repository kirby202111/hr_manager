from fastapi import APIRouter

from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
from app.services import employee as employee_service

router = APIRouter(prefix="/employees", tags=["员工管理"])


@router.get("/", response_model=EmployeeListResponse)
def list_employees():
    return employee_service.list_employees()


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int):
    return employee_service.get_employee(employee_id)


@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(employee_in: EmployeeCreate):
    return employee_service.create_employee(employee_in)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, employee_in: EmployeeUpdate):
    return employee_service.update_employee(employee_id, employee_in)


@router.delete("/{employee_id}")
def delete_employee(employee_id: int):
    return employee_service.delete_employee(employee_id)
