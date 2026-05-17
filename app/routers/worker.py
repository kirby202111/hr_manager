from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.worker import WorkerCreate, WorkerListResponse, WorkerResponse, WorkerUpdate
from app.services import worker as worker_service

router = APIRouter(prefix="/workers", tags=["员工管理"])


@router.get("/", response_model=WorkerListResponse)
def list_workers(db: Session = Depends(get_db)):
    return worker_service.list_workers(db)


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.get_worker(worker_id, db)


@router.post("/", response_model=WorkerResponse, status_code=201)
def create_worker(worker_in: WorkerCreate, db: Session = Depends(get_db)):
    return worker_service.create_worker(worker_in, db)


@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(worker_id: int, worker_in: WorkerUpdate, db: Session = Depends(get_db)):
    return worker_service.update_worker(worker_id, worker_in, db)


@router.delete("/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.delete_worker(worker_id, db)
