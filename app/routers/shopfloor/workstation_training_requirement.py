"""Workstation training requirement router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shopfloor import (
    WorkstationTrainingRequirementCreate,
    WorkstationTrainingRequirementListResponse,
    WorkstationTrainingRequirementResponse,
    WorkstationTrainingRequirementUpdate,
)
from app.services.shopfloor import workstation_training_requirement as service

router = APIRouter(
    prefix="/workstations/{workstation_id}/training-requirements",
    tags=["workstation training requirements"],
)


@router.get("/", response_model=WorkstationTrainingRequirementListResponse)
def list_workstation_training_requirements(
    workstation_id: int,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_workstation_training_requirements(workstation_id, status, db)


@router.get("/{requirement_id}", response_model=WorkstationTrainingRequirementResponse)
def get_workstation_training_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.get_workstation_training_requirement(requirement_id, db)


@router.post("/", response_model=WorkstationTrainingRequirementResponse, status_code=201)
def create_workstation_training_requirement(
    workstation_id: int,
    data: WorkstationTrainingRequirementCreate,
    db: Session = Depends(get_db),
):
    return service.create_workstation_training_requirement(workstation_id, data, db)


@router.put("/{requirement_id}", response_model=WorkstationTrainingRequirementResponse)
def update_workstation_training_requirement(
    requirement_id: int,
    data: WorkstationTrainingRequirementUpdate,
    db: Session = Depends(get_db),
):
    return service.update_workstation_training_requirement(requirement_id, data, db)


@router.delete("/{requirement_id}")
def delete_workstation_training_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.delete_workstation_training_requirement(requirement_id, db)
