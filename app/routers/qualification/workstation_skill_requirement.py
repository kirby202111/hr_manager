"""Workstation skill requirement router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.qualification import (
    WorkstationSkillRequirementCreate,
    WorkstationSkillRequirementListResponse,
    WorkstationSkillRequirementResponse,
    WorkstationSkillRequirementUpdate,
)
from app.services.qualification import workstation_skill_requirement as service

router = APIRouter(prefix="/workstation-skill-requirements", tags=["workstation skill requirements"])


@router.get("/", response_model=WorkstationSkillRequirementListResponse)
def list_workstation_skill_requirements(workstation_id: int | None = None, db: Session = Depends(get_db)):
    return service.list_workstation_skill_requirements(workstation_id, db)


@router.get("/{requirement_id}", response_model=WorkstationSkillRequirementResponse)
def get_workstation_skill_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.get_workstation_skill_requirement(requirement_id, db)


@router.post("/", response_model=WorkstationSkillRequirementResponse, status_code=201)
def create_workstation_skill_requirement(
    data: WorkstationSkillRequirementCreate,
    db: Session = Depends(get_db),
):
    return service.create_workstation_skill_requirement(data, db)


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
