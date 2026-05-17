from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.skill_definition import (
    SkillCatalogCreate,
    SkillCatalogListResponse,
    SkillCatalogResponse,
    SkillCatalogUpdate,
)
from app.services import skill_definition as catalog_service

router = APIRouter(prefix="/skill-catalog", tags=["技能目录管理"])


@router.get("/", response_model=SkillCatalogListResponse)
def list_skills(category: str | None = None, db: Session = Depends(get_db)):
    return catalog_service.list_skills(category, db)


@router.get("/{skill_id}", response_model=SkillCatalogResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    return catalog_service.get_skill(skill_id, db)


@router.post("/", response_model=SkillCatalogResponse, status_code=201)
def create_skill(skill_in: SkillCatalogCreate, db: Session = Depends(get_db)):
    return catalog_service.create_skill(skill_in, db)


@router.put("/{skill_id}", response_model=SkillCatalogResponse)
def update_skill(skill_id: int, skill_in: SkillCatalogUpdate, db: Session = Depends(get_db)):
    return catalog_service.update_skill(skill_id, skill_in, db)


@router.delete("/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    return catalog_service.delete_skill(skill_id, db)
