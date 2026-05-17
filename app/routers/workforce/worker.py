"""人员主数据路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.workforce import WorkerCreate, WorkerListResponse, WorkerResponse, WorkerUpdate
from app.services.workforce import worker as service

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("/", response_model=WorkerListResponse)
def list_workers(
    organization_unit_id: int | None = None,
    employment_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_workers(organization_unit_id, employment_type, status, db)


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    return service.get_worker(worker_id, db)


@router.post("/", response_model=WorkerResponse, status_code=201)
def create_worker(data: WorkerCreate, db: Session = Depends(get_db)):
    return service.create_worker(data, db)


@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(worker_id: int, data: WorkerUpdate, db: Session = Depends(get_db)):
    return service.update_worker(worker_id, data, db)


@router.delete("/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db)):
    return service.delete_worker(worker_id, db)
