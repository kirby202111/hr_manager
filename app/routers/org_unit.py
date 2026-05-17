from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.org_unit import DepartmentCreate, DepartmentListResponse, DepartmentResponse, DepartmentUpdate
from app.schemas.worker import WorkerResponse
from app.services import org_unit as department_service

router = APIRouter(prefix="/departments", tags=["部门管理"])


@router.get("/", response_model=DepartmentListResponse)
def list_departments(db: Session = Depends(get_db)):
    return department_service.list_departments(db)


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db)):
    return department_service.get_department(department_id, db)


@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department(dept_in: DepartmentCreate, db: Session = Depends(get_db)):
    return department_service.create_department(dept_in, db)


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(department_id: int, dept_in: DepartmentUpdate, db: Session = Depends(get_db)):
    return department_service.update_department(department_id, dept_in, db)


@router.delete("/{department_id}")
def delete_department(department_id: int, db: Session = Depends(get_db)):
    return department_service.delete_department(department_id, db)


@router.get("/{department_id}/workers", response_model=list[WorkerResponse])
def get_department_workers(department_id: int, db: Session = Depends(get_db)):
    return department_service.get_department_workers(department_id, db)
