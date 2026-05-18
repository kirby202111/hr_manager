"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.capability import skill as skill_repo
from app.repositories.qualification import workstation_skill_requirement as workstation_skill_requirement_repo
from app.repositories.shopfloor import workstation as workstation_repo
from app.schemas.qualification import (
    WorkstationSkillRequirementCreate,
    WorkstationSkillRequirementListResponse,
    WorkstationSkillRequirementResponse,
    WorkstationSkillRequirementUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> WorkstationSkillRequirementResponse:
    return WorkstationSkillRequirementResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(requirement_id: int, db: Session | None = None) -> dict:
    row = workstation_skill_requirement_repo.get_workstation_skill_requirement_by_id(requirement_id, db)
    if row is None:
        raise NotFoundError(f"Workstation skill requirement {requirement_id} not found")
    return row


# 检查是否存在重复业务数据，供新增和更新流程复用。
def _exists_duplicate(payload: dict, db: Session | None = None, exclude_id: int | None = None) -> bool:
    rows = workstation_skill_requirement_repo.list_workstation_skill_requirements(payload["workstation_id"], db)
    for row in rows:
        if exclude_id is not None and row["id"] == exclude_id:
            continue
        if row["skill_id"] == payload["skill_id"]:
            return True
    return False


def list_workstation_skill_requirements(
    workstation_id: int | None = None,
    db: Session | None = None,
) -> WorkstationSkillRequirementListResponse:
    rows = workstation_skill_requirement_repo.list_workstation_skill_requirements(workstation_id, db)
    return WorkstationSkillRequirementListResponse(
        workstation_skill_requirements=[_to_response(row) for row in rows],
        total=len(rows),
    )


def get_workstation_skill_requirement(
    requirement_id: int, db: Session | None = None
) -> WorkstationSkillRequirementResponse:
    return _to_response(_require_row(requirement_id, db))


def create_workstation_skill_requirement(
    data: WorkstationSkillRequirementCreate,
    db: Session | None = None,
) -> WorkstationSkillRequirementResponse:
    payload = data.model_dump()
    if workstation_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if skill_repo.get_skill_by_id(payload["skill_id"], db) is None:
        raise NotFoundError(f"Skill {payload['skill_id']} not found")
    if _exists_duplicate(payload, db):
        raise ConflictError("Workstation skill requirement already exists")
    row = workstation_skill_requirement_repo.create_workstation_skill_requirement(payload, db)
    return _to_response(row)


def update_workstation_skill_requirement(
    requirement_id: int,
    data: WorkstationSkillRequirementUpdate,
    db: Session | None = None,
) -> WorkstationSkillRequirementResponse:
    current = _require_row(requirement_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if workstation_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if skill_repo.get_skill_by_id(payload["skill_id"], db) is None:
        raise NotFoundError(f"Skill {payload['skill_id']} not found")
    if _exists_duplicate(payload, db, exclude_id=requirement_id):
        raise ConflictError("Workstation skill requirement already exists")
    row = workstation_skill_requirement_repo.update_workstation_skill_requirement(
        requirement_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Workstation skill requirement {requirement_id} not found")
    return _to_response(row)


def delete_workstation_skill_requirement(requirement_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(requirement_id, db)
    workstation_skill_requirement_repo.delete_workstation_skill_requirement(requirement_id, db)
    return {"message": f"Workstation skill requirement {requirement_id} deleted"}
