"""人员持证记录路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.qualification import (
    WorkerCertificationCreate,
    WorkerCertificationListResponse,
    WorkerCertificationResponse,
    WorkerCertificationUpdate,
)
from app.services.qualification import worker_certification as service

router = APIRouter(prefix="/worker-certifications", tags=["worker certifications"])


@router.get("/", response_model=WorkerCertificationListResponse)
def list_worker_certifications(
    worker_id: int | None = None,
    certification_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_worker_certifications(worker_id, certification_id, status, db)


@router.get("/{worker_certification_id}", response_model=WorkerCertificationResponse)
def get_worker_certification(worker_certification_id: int, db: Session = Depends(get_db)):
    return service.get_worker_certification(worker_certification_id, db)


@router.post("/", response_model=WorkerCertificationResponse, status_code=201)
def create_worker_certification(data: WorkerCertificationCreate, db: Session = Depends(get_db)):
    return service.create_worker_certification(data, db)


@router.put("/{worker_certification_id}", response_model=WorkerCertificationResponse)
def update_worker_certification(
    worker_certification_id: int,
    data: WorkerCertificationUpdate,
    db: Session = Depends(get_db),
):
    return service.update_worker_certification(worker_certification_id, data, db)


@router.delete("/{worker_certification_id}")
def delete_worker_certification(worker_certification_id: int, db: Session = Depends(get_db)):
    return service.delete_worker_certification(worker_certification_id, db)
