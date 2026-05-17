"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.capability import skill as skill_repo
from app.schemas.capability import SkillCreate, SkillListResponse, SkillResponse, SkillUpdate


def _to_response(row: dict) -> SkillResponse:
    return SkillResponse(**row)


def _require_skill(skill_id: int, db: Session | None = None) -> dict:
    row = skill_repo.get_skill_by_id(skill_id, db)
    if row is None:
        raise NotFoundError(f"Skill {skill_id} not found")
    return row


def list_skills(category: str | None = None, status: str | None = None, db: Session | None = None) -> SkillListResponse:
    rows = skill_repo.list_skills(category, status, db)
    return SkillListResponse(skills=[_to_response(row) for row in rows], total=len(rows))


def get_skill(skill_id: int, db: Session | None = None) -> SkillResponse:
    return _to_response(_require_skill(skill_id, db))


def create_skill(data: SkillCreate, db: Session | None = None) -> SkillResponse:
    if skill_repo.get_skill_by_code(data.code, db) is not None:
        raise ConflictError(f"Skill code '{data.code}' already exists")
    if skill_repo.get_skill_by_name(data.name, db) is not None:
        raise ConflictError(f"Skill name '{data.name}' already exists")
    row = skill_repo.create_skill(data.model_dump(), db)
    return _to_response(row)


def update_skill(skill_id: int, data: SkillUpdate, db: Session | None = None) -> SkillResponse:
    current = _require_skill(skill_id, db)
    payload = data.model_dump(exclude_unset=True)
    if "code" in payload and payload["code"] != current["code"]:
        if skill_repo.get_skill_by_code(payload["code"], db) is not None:
            raise ConflictError(f"Skill code '{payload['code']}' already exists")
    if "name" in payload and payload["name"] != current["name"]:
        if skill_repo.get_skill_by_name(payload["name"], db) is not None:
            raise ConflictError(f"Skill name '{payload['name']}' already exists")
    row = skill_repo.update_skill(skill_id, payload, db)
    if row is None:
        raise NotFoundError(f"Skill {skill_id} not found")
    return _to_response(row)


def delete_skill(skill_id: int, db: Session | None = None) -> dict[str, str]:
    _require_skill(skill_id, db)
    skill_repo.delete_skill(skill_id, db)
    return {"message": f"Skill {skill_id} deleted"}
