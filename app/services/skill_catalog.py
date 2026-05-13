from fastapi import HTTPException

from app.repositories import skill_catalog as catalog_repo
from app.schemas.skill_catalog import (
    SkillCatalogCreate,
    SkillCatalogListResponse,
    SkillCatalogResponse,
    SkillCatalogUpdate,
)


def _enrich(skill: dict) -> dict:
    skill["employee_count"] = catalog_repo.count_employee_skills_by_skill_id(skill["id"])
    return skill


def list_skills(category: str | None = None) -> SkillCatalogListResponse:
    skills = catalog_repo.get_all_skills(category)
    return SkillCatalogListResponse(
        skills=[SkillCatalogResponse(**_enrich(s)) for s in skills],
        total=len(skills),
    )


def get_skill(skill_id: int) -> SkillCatalogResponse:
    skill = catalog_repo.get_skill_by_id(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"技能目录 {skill_id} 不存在")
    return SkillCatalogResponse(**_enrich(skill))


def create_skill(skill_in: SkillCatalogCreate) -> SkillCatalogResponse:
    existing = catalog_repo.get_skill_by_name(skill_in.name)
    if existing:
        raise HTTPException(status_code=400, detail=f"技能 '{skill_in.name}' 已存在")
    from datetime import datetime, timezone
    skill_data = skill_in.model_dump()
    skill_data["created_at"] = datetime.now(timezone.utc)
    skill = catalog_repo.create_skill(skill_data)
    return SkillCatalogResponse(**_enrich(skill))


def update_skill(skill_id: int, skill_in: SkillCatalogUpdate) -> SkillCatalogResponse:
    existing = catalog_repo.get_skill_by_id(skill_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"技能目录 {skill_id} 不存在")
    if skill_in.name is not None:
        dup = catalog_repo.get_skill_by_name(skill_in.name)
        if dup and dup["id"] != skill_id:
            raise HTTPException(status_code=400, detail=f"技能 '{skill_in.name}' 已存在")
    update_data = skill_in.model_dump(exclude_unset=True)
    skill = catalog_repo.update_skill(skill_id, update_data)
    return SkillCatalogResponse(**_enrich(skill))


def delete_skill(skill_id: int) -> dict:
    existing = catalog_repo.get_skill_by_id(skill_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"技能目录 {skill_id} 不存在")
    emp_ref = catalog_repo.count_employee_skills_by_skill_id(skill_id)
    req_ref = catalog_repo.count_project_requirements_by_skill_id(skill_id)
    if emp_ref > 0 or req_ref > 0:
        raise HTTPException(status_code=400, detail="该技能正在被使用，无法删除")
    catalog_repo.delete_skill(skill_id)
    return {"message": "技能已删除"}
