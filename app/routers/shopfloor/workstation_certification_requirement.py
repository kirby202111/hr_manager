"""Workstation certification requirement router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shopfloor import (
    WorkstationCertificationRequirementCreate,
    WorkstationCertificationRequirementListResponse,
    WorkstationCertificationRequirementResponse,
    WorkstationCertificationRequirementUpdate,
)
from app.services.shopfloor import workstation_certification_requirement as service

router = APIRouter(
    prefix="/workstations/{workstation_id}/certification-requirements",
    tags=["workstation certification requirements"],
)


@router.get("/", response_model=WorkstationCertificationRequirementListResponse)
def list_workstation_certification_requirements(
    workstation_id: int,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_workstation_certification_requirements(workstation_id, status, db)


@router.get("/{requirement_id}", response_model=WorkstationCertificationRequirementResponse)
def get_workstation_certification_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.get_workstation_certification_requirement(requirement_id, db)


@router.post("/", response_model=WorkstationCertificationRequirementResponse, status_code=201)
def create_workstation_certification_requirement(
    workstation_id: int,
    data: WorkstationCertificationRequirementCreate,
    db: Session = Depends(get_db),
):
    return service.create_workstation_certification_requirement(workstation_id, data, db)


@router.put("/{requirement_id}", response_model=WorkstationCertificationRequirementResponse)
def update_workstation_certification_requirement(
    requirement_id: int,
    data: WorkstationCertificationRequirementUpdate,
    db: Session = Depends(get_db),
):
    return service.update_workstation_certification_requirement(requirement_id, data, db)


@router.delete("/{requirement_id}")
def delete_workstation_certification_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.delete_workstation_certification_requirement(requirement_id, db)
