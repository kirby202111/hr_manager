"""Workstation equipment requirement router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shopfloor import (
    WorkstationEquipmentRequirementCreate,
    WorkstationEquipmentRequirementListResponse,
    WorkstationEquipmentRequirementResponse,
    WorkstationEquipmentRequirementUpdate,
)
from app.services.shopfloor import workstation_equipment_requirement as service

router = APIRouter(
    prefix="/workstations/{workstation_id}/equipment-requirements",
    tags=["workstation equipment requirements"],
)


@router.get("/", response_model=WorkstationEquipmentRequirementListResponse)
def list_workstation_equipment_requirements(
    workstation_id: int,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_workstation_equipment_requirements(workstation_id, status, db)


@router.get("/{requirement_id}", response_model=WorkstationEquipmentRequirementResponse)
def get_workstation_equipment_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.get_workstation_equipment_requirement(requirement_id, db)


@router.post("/", response_model=WorkstationEquipmentRequirementResponse, status_code=201)
def create_workstation_equipment_requirement(
    workstation_id: int,
    data: WorkstationEquipmentRequirementCreate,
    db: Session = Depends(get_db),
):
    return service.create_workstation_equipment_requirement(workstation_id, data, db)


@router.put("/{requirement_id}", response_model=WorkstationEquipmentRequirementResponse)
def update_workstation_equipment_requirement(
    requirement_id: int,
    data: WorkstationEquipmentRequirementUpdate,
    db: Session = Depends(get_db),
):
    return service.update_workstation_equipment_requirement(requirement_id, data, db)


@router.delete("/{requirement_id}")
def delete_workstation_equipment_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.delete_workstation_equipment_requirement(requirement_id, db)
