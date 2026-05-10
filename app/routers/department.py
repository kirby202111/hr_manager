from fastapi import APIRouter

from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentListResponse
from app.schemas.employee import EmployeeResponse
from app.services import department as department_service

router = APIRouter(prefix="/departments", tags=["部门管理"])


@router.get("/", response_model=DepartmentListResponse)
def list_departments():
    return department_service.list_departments()


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int):
    return department_service.get_department(department_id)


@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department(dept_in: DepartmentCreate):
    return department_service.create_department(dept_in)


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(department_id: int, dept_in: DepartmentUpdate):
    return department_service.update_department(department_id, dept_in)


@router.delete("/{department_id}")
def delete_department(department_id: int):
    return department_service.delete_department(department_id)


@router.get("/{department_id}/employees", response_model=list[EmployeeResponse])
def get_department_employees(department_id: int):
    return department_service.get_department_employees(department_id)
