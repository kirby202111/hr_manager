from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import skill_definition as catalog_repo
from app.repositories import worker as worker_repo
from app.repositories import worker_skill as skill_repo
from app.schemas.worker_skill import WorkerSkillCreate, WorkerSkillListResponse, WorkerSkillResponse, WorkerSkillUpdate

VALID_LEVELS = {"beginner", "intermediate", "advanced", "expert"}


def _fill_worker_name(skill: dict, db: Session | None = None) -> dict:
    worker = worker_repo.get_worker_by_id(skill["worker_id"], db)
    skill["worker_name"] = worker["name"] if worker else None
    if skill.get("skill_id"):
        catalog = catalog_repo.get_skill_by_id(skill["skill_id"], db)
        skill["skill_category"] = catalog["category"] if catalog else None
    else:
        skill["skill_category"] = None
    return skill


def _validate_level(level: str) -> None:
    if level not in VALID_LEVELS:
        raise ValidationError(f"Invalid proficiency level, allowed values: {', '.join(sorted(VALID_LEVELS))}")


def list_skills(db: Session | None = None) -> WorkerSkillListResponse:
    skills = skill_repo.get_all_skills(db)
    return WorkerSkillListResponse(skills=[WorkerSkillResponse(**_fill_worker_name(skill, db)) for skill in skills], total=len(skills))


def list_skills_by_worker(worker_id: int, db: Session | None = None) -> WorkerSkillListResponse:
    worker = worker_repo.get_worker_by_id(worker_id, db)
    if worker is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    skills = skill_repo.get_skills_by_worker(worker_id, db)
    return WorkerSkillListResponse(skills=[WorkerSkillResponse(**_fill_worker_name(skill, db)) for skill in skills], total=len(skills))


def list_workers_by_skill(skill_name: str, db: Session | None = None) -> WorkerSkillListResponse:
    skills = skill_repo.get_skills_by_name(skill_name, db)
    return WorkerSkillListResponse(skills=[WorkerSkillResponse(**_fill_worker_name(skill, db)) for skill in skills], total=len(skills))


def get_skill(skill_id: int, db: Session | None = None) -> WorkerSkillResponse:
    skill = skill_repo.get_skill_by_id(skill_id, db)
    if skill is None:
        raise NotFoundError(f"Skill {skill_id} not found")
    return WorkerSkillResponse(**_fill_worker_name(skill, db))


def create_skill(skill_in: WorkerSkillCreate, db: Session | None = None) -> WorkerSkillResponse:
    worker = worker_repo.get_worker_by_id(skill_in.worker_id, db)
    if worker is None:
        raise ValidationError(f"Worker {skill_in.worker_id} not found")
    _validate_level(skill_in.proficiency_level)
    if skill_in.skill_id is not None and catalog_repo.get_skill_by_id(skill_in.skill_id, db) is None:
        raise ValidationError(f"Skill catalog {skill_in.skill_id} not found")
    skill = skill_repo.create_skill(skill_in.model_dump() | {"created_at": datetime.now(UTC)}, db)
    return WorkerSkillResponse(**_fill_worker_name(skill, db))


def update_skill(skill_id: int, skill_in: WorkerSkillUpdate, db: Session | None = None) -> WorkerSkillResponse:
    existing = skill_repo.get_skill_by_id(skill_id, db)
    if existing is None:
        raise NotFoundError(f"Skill {skill_id} not found")
    if skill_in.proficiency_level is not None:
        _validate_level(skill_in.proficiency_level)
    if skill_in.skill_id is not None and catalog_repo.get_skill_by_id(skill_in.skill_id, db) is None:
        raise ValidationError(f"Skill catalog {skill_in.skill_id} not found")
    skill = skill_repo.update_skill(skill_id, skill_in.model_dump(exclude_unset=True), db)
    return WorkerSkillResponse(**_fill_worker_name(skill, db))


def delete_skill(skill_id: int, db: Session | None = None) -> dict:
    if not skill_repo.delete_skill(skill_id, db):
        raise NotFoundError(f"Skill {skill_id} not found")
    return {"message": "Skill deleted"}
