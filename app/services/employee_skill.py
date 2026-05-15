from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import employee as employee_repo
from app.repositories import employee_skill as skill_repo
from app.repositories import skill_catalog as catalog_repo
from app.schemas.employee_skill import (
    EmployeeSkillCreate,
    EmployeeSkillListResponse,
    EmployeeSkillResponse,
    EmployeeSkillUpdate,
)

VALID_LEVELS = {"beginner", "intermediate", "advanced", "expert"}


def _fill_employee_name(skill: dict, db: Session | None = None) -> dict:
    emp = employee_repo.get_employee_by_id(skill["employee_id"], db)
    skill["employee_name"] = emp["name"] if emp else None
    if skill.get("skill_id"):
        catalog = catalog_repo.get_skill_by_id(skill["skill_id"], db)
        skill["skill_category"] = catalog["category"] if catalog else None
    else:
        skill["skill_category"] = None
    return skill


def list_skills(db: Session | None = None) -> EmployeeSkillListResponse:
    skills = skill_repo.get_all_skills(db)
    return EmployeeSkillListResponse(
        skills=[EmployeeSkillResponse(**_fill_employee_name(s, db)) for s in skills],
        total=len(skills),
    )


def list_skills_by_employee(employee_id: int, db: Session | None = None) -> EmployeeSkillListResponse:
    emp = employee_repo.get_employee_by_id(employee_id, db)
    if emp is None:
        raise NotFoundError(f"Employee {employee_id} not found")
    skills = skill_repo.get_skills_by_employee(employee_id, db)
    return EmployeeSkillListResponse(
        skills=[EmployeeSkillResponse(**_fill_employee_name(s, db)) for s in skills],
        total=len(skills),
    )


def list_employees_by_skill(skill_name: str, db: Session | None = None) -> EmployeeSkillListResponse:
    skills = skill_repo.get_skills_by_name(skill_name, db)
    return EmployeeSkillListResponse(
        skills=[EmployeeSkillResponse(**_fill_employee_name(s, db)) for s in skills],
        total=len(skills),
    )


def get_skill(skill_id: int, db: Session | None = None) -> EmployeeSkillResponse:
    skill = skill_repo.get_skill_by_id(skill_id, db)
    if skill is None:
        raise NotFoundError(f"Skill {skill_id} not found")
    return EmployeeSkillResponse(**_fill_employee_name(skill, db))


def _validate_level(level: str) -> None:
    if level not in VALID_LEVELS:
        raise ValidationError(f"无效的熟练程度，可选值: {', '.join(sorted(VALID_LEVELS))}")


def create_skill(skill_in: EmployeeSkillCreate, db: Session | None = None) -> EmployeeSkillResponse:
    emp = employee_repo.get_employee_by_id(skill_in.employee_id, db)
    if emp is None:
        raise ValidationError(f"员工 {skill_in.employee_id} 不存在")
    _validate_level(skill_in.proficiency_level)
    if skill_in.skill_id is not None:
        catalog = catalog_repo.get_skill_by_id(skill_in.skill_id, db)
        if catalog is None:
            raise ValidationError(f"技能目录 {skill_in.skill_id} 不存在")
    skill_data = skill_in.model_dump()
    skill_data["created_at"] = datetime.now(UTC)
    skill = skill_repo.create_skill(skill_data, db)
    return EmployeeSkillResponse(**_fill_employee_name(skill, db))


def update_skill(skill_id: int, skill_in: EmployeeSkillUpdate, db: Session | None = None) -> EmployeeSkillResponse:
    existing = skill_repo.get_skill_by_id(skill_id, db)
    if existing is None:
        raise NotFoundError(f"技能记录 {skill_id} 不存在")
    if skill_in.proficiency_level is not None:
        _validate_level(skill_in.proficiency_level)
    if skill_in.skill_id is not None:
        catalog = catalog_repo.get_skill_by_id(skill_in.skill_id, db)
        if catalog is None:
            raise ValidationError(f"技能目录 {skill_in.skill_id} 不存在")
    update_data = skill_in.model_dump(exclude_unset=True)
    skill = skill_repo.update_skill(skill_id, update_data, db)
    return EmployeeSkillResponse(**_fill_employee_name(skill, db))


def delete_skill(skill_id: int, db: Session | None = None) -> dict:
    success = skill_repo.delete_skill(skill_id, db)
    if not success:
        raise NotFoundError(f"技能记录 {skill_id} 不存在")
    return {"message": "技能记录已删除"}
