"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.capability import skill as skill_repo
from app.repositories.capability import worker_skill as worker_skill_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.capability import (
    WorkerSkillCreate,
    WorkerSkillListResponse,
    WorkerSkillResponse,
    WorkerSkillUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> WorkerSkillResponse:
    return WorkerSkillResponse(**row)


# 读取员工技能记录；不存在时统一抛出未找到异常。
def _require_worker_skill(worker_skill_id: int, db: Session | None = None) -> dict:
    row = worker_skill_repo.get_worker_skill_by_id(worker_skill_id, db)
    if row is None:
        raise NotFoundError(f"Worker skill {worker_skill_id} not found")
    return row


def list_worker_skills(
    worker_id: int | None = None,
    skill_id: int | None = None,
    proficiency_level: str | None = None,
    validated: bool | None = None,
    db: Session | None = None,
) -> WorkerSkillListResponse:
    rows = worker_skill_repo.list_worker_skills(worker_id, skill_id, proficiency_level, validated, db)
    return WorkerSkillListResponse(worker_skills=[_to_response(row) for row in rows], total=len(rows))


def get_worker_skill(worker_skill_id: int, db: Session | None = None) -> WorkerSkillResponse:
    return _to_response(_require_worker_skill(worker_skill_id, db))


def create_worker_skill(data: WorkerSkillCreate, db: Session | None = None) -> WorkerSkillResponse:
    if worker_repo.get_worker_by_id(data.worker_id, db) is None:
        raise NotFoundError(f"Worker {data.worker_id} not found")
    if skill_repo.get_skill_by_id(data.skill_id, db) is None:
        raise NotFoundError(f"Skill {data.skill_id} not found")
    if worker_skill_repo.get_worker_skill_by_worker_and_skill(data.worker_id, data.skill_id, db) is not None:
        raise ConflictError("Worker skill already exists")
    row = worker_skill_repo.create_worker_skill(data.model_dump(), db)
    return _to_response(row)


def update_worker_skill(
    worker_skill_id: int, data: WorkerSkillUpdate, db: Session | None = None
) -> WorkerSkillResponse:
    current = _require_worker_skill(worker_skill_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if skill_repo.get_skill_by_id(payload["skill_id"], db) is None:
        raise NotFoundError(f"Skill {payload['skill_id']} not found")
    existing = worker_skill_repo.get_worker_skill_by_worker_and_skill(payload["worker_id"], payload["skill_id"], db)
    if existing is not None and existing["id"] != worker_skill_id:
        raise ConflictError("Worker skill already exists")
    row = worker_skill_repo.update_worker_skill(worker_skill_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Worker skill {worker_skill_id} not found")
    return _to_response(row)


def delete_worker_skill(worker_skill_id: int, db: Session | None = None) -> dict[str, str]:
    _require_worker_skill(worker_skill_id, db)
    worker_skill_repo.delete_worker_skill(worker_skill_id, db)
    return {"message": f"Worker skill {worker_skill_id} deleted"}
