from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import skill_definition as catalog_repo
from app.schemas.skill_definition import (
    SkillCatalogCreate,
    SkillCatalogListResponse,
    SkillCatalogResponse,
    SkillCatalogUpdate,
)


def _enrich(skill: dict, db: Session | None = None) -> dict:
    skill["employee_count"] = catalog_repo.count_employee_skills_by_skill_id(skill["id"], db)
    return skill


def list_skills(category: str | None = None, db: Session | None = None) -> SkillCatalogListResponse:
    skills = catalog_repo.get_all_skills(category, db)
    return SkillCatalogListResponse(
        skills=[SkillCatalogResponse(**_enrich(s, db)) for s in skills],
        total=len(skills),
    )


def get_skill(skill_id: int, db: Session | None = None) -> SkillCatalogResponse:
    skill = catalog_repo.get_skill_by_id(skill_id, db)
    if skill is None:
        raise NotFoundError(f"技能目录 {skill_id} 不存在")
    return SkillCatalogResponse(**_enrich(skill, db))


def create_skill(skill_in: SkillCatalogCreate, db: Session | None = None) -> SkillCatalogResponse:
    existing = catalog_repo.get_skill_by_name(skill_in.name, db)
    if existing:
        raise ValidationError(f"技能 '{skill_in.name}' 已存在")
    skill_data = skill_in.model_dump()
    skill_data["created_at"] = datetime.now(UTC)
    skill = catalog_repo.create_skill(skill_data, db)
    return SkillCatalogResponse(**_enrich(skill, db))


def update_skill(skill_id: int, skill_in: SkillCatalogUpdate, db: Session | None = None) -> SkillCatalogResponse:
    existing = catalog_repo.get_skill_by_id(skill_id, db)
    if existing is None:
        raise NotFoundError(f"技能目录 {skill_id} 不存在")
    if skill_in.name is not None:
        dup = catalog_repo.get_skill_by_name(skill_in.name, db)
        if dup and dup["id"] != skill_id:
            raise ValidationError(f"技能 '{skill_in.name}' 已存在")
    update_data = skill_in.model_dump(exclude_unset=True)
    skill = catalog_repo.update_skill(skill_id, update_data, db)
    return SkillCatalogResponse(**_enrich(skill, db))


def delete_skill(skill_id: int, db: Session | None = None) -> dict:
    existing = catalog_repo.get_skill_by_id(skill_id, db)
    if existing is None:
        raise NotFoundError(f"技能目录 {skill_id} 不存在")
    emp_ref = catalog_repo.count_employee_skills_by_skill_id(skill_id, db)
    req_ref = catalog_repo.count_project_requirements_by_skill_id(skill_id, db)
    if emp_ref > 0 or req_ref > 0:
        raise ValidationError("技能正在被使用，无法删除")
    catalog_repo.delete_skill(skill_id, db)
    return {"message": "技能已删除"}
