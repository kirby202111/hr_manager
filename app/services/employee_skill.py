from fastapi import HTTPException

from app.repositories import employee as employee_repo
from app.repositories import employee_skill as skill_repo
from app.repositories import skill_catalog as catalog_repo
from app.schemas.employee_skill import (
    EmployeeSkillCreate,
    EmployeeSkillListResponse,
    EmployeeSkillResponse,
    EmployeeSkillUpdate,
)


def _fill_employee_name(skill: dict) -> dict:
    emp = employee_repo.get_employee_by_id(skill["employee_id"])
    skill["employee_name"] = emp["name"] if emp else None
    if skill.get("skill_id"):
        catalog = catalog_repo.get_skill_by_id(skill["skill_id"])
        skill["skill_category"] = catalog["category"] if catalog else None
    else:
        skill["skill_category"] = None
    return skill


def list_skills() -> EmployeeSkillListResponse:
    skills = skill_repo.get_all_skills()
    return EmployeeSkillListResponse(
        skills=[EmployeeSkillResponse(**_fill_employee_name(s)) for s in skills],
        total=len(skills),
    )


def list_skills_by_employee(employee_id: int) -> EmployeeSkillListResponse:
    emp = employee_repo.get_employee_by_id(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    skills = skill_repo.get_skills_by_employee(employee_id)
    return EmployeeSkillListResponse(
        skills=[EmployeeSkillResponse(**_fill_employee_name(s)) for s in skills],
        total=len(skills),
    )


def list_employees_by_skill(skill_name: str) -> EmployeeSkillListResponse:
    skills = skill_repo.get_skills_by_name(skill_name)
    return EmployeeSkillListResponse(
        skills=[EmployeeSkillResponse(**_fill_employee_name(s)) for s in skills],
        total=len(skills),
    )


def get_skill(skill_id: int) -> EmployeeSkillResponse:
    skill = skill_repo.get_skill_by_id(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")
    return EmployeeSkillResponse(**_fill_employee_name(skill))


def create_skill(skill_in: EmployeeSkillCreate) -> EmployeeSkillResponse:
    emp = employee_repo.get_employee_by_id(skill_in.employee_id)
    if emp is None:
        raise HTTPException(status_code=400, detail=f"员工 {skill_in.employee_id} 不存在")
    valid_levels = {"beginner", "intermediate", "advanced", "expert"}
    if skill_in.proficiency_level not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"无效的熟练程度，可选值: {', '.join(valid_levels)}",
        )
    if skill_in.skill_id is not None:
        catalog = catalog_repo.get_skill_by_id(skill_in.skill_id)
        if catalog is None:
            raise HTTPException(status_code=400, detail=f"技能目录 {skill_in.skill_id} 不存在")
    skill_data = skill_in.model_dump()
    from datetime import datetime, timezone
    skill_data["created_at"] = datetime.now(timezone.utc)
    skill = skill_repo.create_skill(skill_data)
    return EmployeeSkillResponse(**_fill_employee_name(skill))


def update_skill(skill_id: int, skill_in: EmployeeSkillUpdate) -> EmployeeSkillResponse:
    existing = skill_repo.get_skill_by_id(skill_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"技能记录 {skill_id} 不存在")
    if skill_in.proficiency_level is not None:
        valid_levels = {"beginner", "intermediate", "advanced", "expert"}
        if skill_in.proficiency_level not in valid_levels:
            raise HTTPException(
                status_code=400,
                detail=f"无效的熟练程度，可选值: {', '.join(valid_levels)}",
            )
    if skill_in.skill_id is not None:
        catalog = catalog_repo.get_skill_by_id(skill_in.skill_id)
        if catalog is None:
            raise HTTPException(status_code=400, detail=f"技能目录 {skill_in.skill_id} 不存在")
    update_data = skill_in.model_dump(exclude_unset=True)
    skill = skill_repo.update_skill(skill_id, update_data)
    return EmployeeSkillResponse(**_fill_employee_name(skill))


def delete_skill(skill_id: int) -> dict:
    success = skill_repo.delete_skill(skill_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"技能记录 {skill_id} 不存在")
    return {"message": "技能记录已删除"}
