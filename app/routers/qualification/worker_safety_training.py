"""人员安全培训记录路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.qualification import (
    WorkerSafetyTrainingCreate,
    WorkerSafetyTrainingListResponse,
    WorkerSafetyTrainingResponse,
    WorkerSafetyTrainingUpdate,
)
from app.services.qualification import worker_safety_training as service

router = APIRouter(prefix="/worker-safety-trainings", tags=["worker safety trainings"])


@router.get("/", response_model=WorkerSafetyTrainingListResponse)
def list_worker_safety_trainings(
    worker_id: int | None = None,
    safety_training_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_worker_safety_trainings(worker_id, safety_training_id, status, db)


@router.get("/{worker_safety_training_id}", response_model=WorkerSafetyTrainingResponse)
def get_worker_safety_training(worker_safety_training_id: int, db: Session = Depends(get_db)):
    return service.get_worker_safety_training(worker_safety_training_id, db)


@router.post("/", response_model=WorkerSafetyTrainingResponse, status_code=201)
def create_worker_safety_training(data: WorkerSafetyTrainingCreate, db: Session = Depends(get_db)):
    return service.create_worker_safety_training(data, db)


@router.put("/{worker_safety_training_id}", response_model=WorkerSafetyTrainingResponse)
def update_worker_safety_training(
    worker_safety_training_id: int,
    data: WorkerSafetyTrainingUpdate,
    db: Session = Depends(get_db),
):
    return service.update_worker_safety_training(worker_safety_training_id, data, db)


@router.delete("/{worker_safety_training_id}")
def delete_worker_safety_training(worker_safety_training_id: int, db: Session = Depends(get_db)):
    return service.delete_worker_safety_training(worker_safety_training_id, db)
