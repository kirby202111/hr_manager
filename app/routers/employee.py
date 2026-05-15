from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeListResponse, EmployeeResponse, EmployeeUpdate
from app.services import employee as employee_service

router = APIRouter(prefix="/employees", tags=["员工管理"])


@router.get("/", response_model=EmployeeListResponse)
def list_employees(db: Session = Depends(get_db)):
    return employee_service.list_employees(db)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return employee_service.get_employee(employee_id, db)


@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    return employee_service.create_employee(employee_in, db)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, employee_in: EmployeeUpdate, db: Session = Depends(get_db)):
    return employee_service.update_employee(employee_id, employee_in, db)


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    return employee_service.delete_employee(employee_id, db)
