"""安全培训目录路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.qualification import (
    SafetyTrainingCreate,
    SafetyTrainingListResponse,
    SafetyTrainingResponse,
    SafetyTrainingUpdate,
)
from app.services.qualification import safety_training as service

router = APIRouter(prefix="/safety-trainings", tags=["safety trainings"])


@router.get("/", response_model=SafetyTrainingListResponse)
def list_safety_trainings(category: str | None = None, db: Session = Depends(get_db)):
    return service.list_safety_trainings(category, db)


@router.get("/{safety_training_id}", response_model=SafetyTrainingResponse)
def get_safety_training(safety_training_id: int, db: Session = Depends(get_db)):
    return service.get_safety_training(safety_training_id, db)


@router.post("/", response_model=SafetyTrainingResponse, status_code=201)
def create_safety_training(data: SafetyTrainingCreate, db: Session = Depends(get_db)):
    return service.create_safety_training(data, db)


@router.put("/{safety_training_id}", response_model=SafetyTrainingResponse)
def update_safety_training(
    safety_training_id: int,
    data: SafetyTrainingUpdate,
    db: Session = Depends(get_db),
):
    return service.update_safety_training(safety_training_id, data, db)


@router.delete("/{safety_training_id}")
def delete_safety_training(safety_training_id: int, db: Session = Depends(get_db)):
    return service.delete_safety_training(safety_training_id, db)
