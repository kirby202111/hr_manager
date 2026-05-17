"""项目技能需求路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.collaboration import (
    ProjectSkillRequirementCreate,
    ProjectSkillRequirementListResponse,
    ProjectSkillRequirementResponse,
    ProjectSkillRequirementUpdate,
)
from app.services.collaboration import project_skill_requirement as service

router = APIRouter(prefix="/project-skill-requirements", tags=["project skill requirements"])


@router.get("/", response_model=ProjectSkillRequirementListResponse)
def list_project_skill_requirements(
    project_id: int | None = None,
    skill_id: int | None = None,
    db: Session = Depends(get_db),
):
    return service.list_project_skill_requirements(project_id, skill_id, db)


@router.get("/{project_skill_requirement_id}", response_model=ProjectSkillRequirementResponse)
def get_project_skill_requirement(project_skill_requirement_id: int, db: Session = Depends(get_db)):
    return service.get_project_skill_requirement(project_skill_requirement_id, db)


@router.post("/", response_model=ProjectSkillRequirementResponse, status_code=201)
def create_project_skill_requirement(
    data: ProjectSkillRequirementCreate,
    db: Session = Depends(get_db),
):
    return service.create_project_skill_requirement(data, db)


@router.put("/{project_skill_requirement_id}", response_model=ProjectSkillRequirementResponse)
def update_project_skill_requirement(
    project_skill_requirement_id: int,
    data: ProjectSkillRequirementUpdate,
    db: Session = Depends(get_db),
):
    return service.update_project_skill_requirement(project_skill_requirement_id, data, db)


@router.delete("/{project_skill_requirement_id}")
def delete_project_skill_requirement(project_skill_requirement_id: int, db: Session = Depends(get_db)):
    return service.delete_project_skill_requirement(project_skill_requirement_id, db)
