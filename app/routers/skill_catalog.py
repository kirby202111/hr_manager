from fastapi import APIRouter

from app.schemas.skill_catalog import (
    SkillCatalogCreate,
    SkillCatalogListResponse,
    SkillCatalogResponse,
    SkillCatalogUpdate,
)
from app.services import skill_catalog as catalog_service

router = APIRouter(prefix="/skill-catalog", tags=["技能目录管理"])


@router.get("/", response_model=SkillCatalogListResponse)
def list_skills(category: str | None = None):
    return catalog_service.list_skills(category)


@router.get("/{skill_id}", response_model=SkillCatalogResponse)
def get_skill(skill_id: int):
    return catalog_service.get_skill(skill_id)


@router.post("/", response_model=SkillCatalogResponse, status_code=201)
def create_skill(skill_in: SkillCatalogCreate):
    return catalog_service.create_skill(skill_in)


@router.put("/{skill_id}", response_model=SkillCatalogResponse)
def update_skill(skill_id: int, skill_in: SkillCatalogUpdate):
    return catalog_service.update_skill(skill_id, skill_in)


@router.delete("/{skill_id}")
def delete_skill(skill_id: int):
    return catalog_service.delete_skill(skill_id)
