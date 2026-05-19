"""Workstation skill requirement router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shopfloor import (
    WorkstationSkillRequirementCreate,
    WorkstationSkillRequirementListResponse,
    WorkstationSkillRequirementResponse,
    WorkstationSkillRequirementUpdate,
)
from app.services.shopfloor import workstation_skill_requirement as service

router = APIRouter(prefix="/workstations/{workstation_id}/skill-requirements", tags=["workstation skill requirements"])


@router.get("/", response_model=WorkstationSkillRequirementListResponse)
def list_workstation_skill_requirements(
    workstation_id: int,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_workstation_skill_requirements(workstation_id, status, db)


@router.get("/{requirement_id}", response_model=WorkstationSkillRequirementResponse)
def get_workstation_skill_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.get_workstation_skill_requirement(requirement_id, db)


@router.post("/", response_model=WorkstationSkillRequirementResponse, status_code=201)
def create_workstation_skill_requirement(
    workstation_id: int,
    data: WorkstationSkillRequirementCreate,
    db: Session = Depends(get_db),
):
    return service.create_workstation_skill_requirement(workstation_id, data, db)


@router.put("/{requirement_id}", response_model=WorkstationSkillRequirementResponse)
def update_workstation_skill_requirement(
    requirement_id: int,
    data: WorkstationSkillRequirementUpdate,
    db: Session = Depends(get_db),
):
    return service.update_workstation_skill_requirement(requirement_id, data, db)


@router.delete("/{requirement_id}")
def delete_workstation_skill_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.delete_workstation_skill_requirement(requirement_id, db)
