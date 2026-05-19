"""Workstation skill requirement service."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.capability import skill as skill_repo
from app.repositories.shopfloor import workstation as workstation_repo
from app.repositories.shopfloor import workstation_skill_requirement as requirement_repo
from app.schemas.shopfloor import (
    WorkstationSkillRequirementCreate,
    WorkstationSkillRequirementListResponse,
    WorkstationSkillRequirementResponse,
    WorkstationSkillRequirementUpdate,
)

VALID_LEVELS = {"L1", "L2", "L3", "L4", "L5"}


def _to_response(row: dict) -> WorkstationSkillRequirementResponse:
    return WorkstationSkillRequirementResponse(**row)


def _require_row(requirement_id: int, db: Session | None = None) -> dict:
    row = requirement_repo.get_workstation_skill_requirement_by_id(requirement_id, db)
    if row is None:
        raise NotFoundError(f"Workstation skill requirement {requirement_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if workstation_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if skill_repo.get_skill_by_id(payload["skill_id"], db) is None:
        raise NotFoundError(f"Skill {payload['skill_id']} not found")
    if payload["min_proficiency_level"] not in VALID_LEVELS:
        raise ValidationError("min_proficiency_level must be one of L1, L2, L3, L4, L5")


def list_workstation_skill_requirements(
    workstation_id: int,
    status: str | None = None,
    db: Session | None = None,
) -> WorkstationSkillRequirementListResponse:
    if workstation_repo.get_workstation_by_id(workstation_id, db) is None:
        raise NotFoundError(f"Workstation {workstation_id} not found")
    rows = requirement_repo.list_workstation_skill_requirements(workstation_id=workstation_id, status=status, db=db)
    return WorkstationSkillRequirementListResponse(requirements=[_to_response(row) for row in rows], total=len(rows))


def get_workstation_skill_requirement(
    requirement_id: int,
    db: Session | None = None,
) -> WorkstationSkillRequirementResponse:
    return _to_response(_require_row(requirement_id, db))


def create_workstation_skill_requirement(
    workstation_id: int,
    data: WorkstationSkillRequirementCreate,
    db: Session | None = None,
) -> WorkstationSkillRequirementResponse:
    payload = {"workstation_id": workstation_id, **data.model_dump()}
    _validate_payload(payload, db)
    existing = requirement_repo.get_workstation_skill_requirement_by_workstation_and_skill(
        workstation_id,
        payload["skill_id"],
        db,
    )
    if existing is not None:
        raise ConflictError("Workstation skill requirement already exists")
    row = requirement_repo.create_workstation_skill_requirement(payload, db)
    return _to_response(row)


def update_workstation_skill_requirement(
    requirement_id: int,
    data: WorkstationSkillRequirementUpdate,
    db: Session | None = None,
) -> WorkstationSkillRequirementResponse:
    current = _require_row(requirement_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = requirement_repo.get_workstation_skill_requirement_by_workstation_and_skill(
        payload["workstation_id"],
        payload["skill_id"],
        db,
    )
    if existing is not None and existing["id"] != requirement_id:
        raise ConflictError("Workstation skill requirement already exists")
    row = requirement_repo.update_workstation_skill_requirement(requirement_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Workstation skill requirement {requirement_id} not found")
    return _to_response(row)


def delete_workstation_skill_requirement(requirement_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(requirement_id, db)
    requirement_repo.delete_workstation_skill_requirement(requirement_id, db)
    return {"message": f"Workstation skill requirement {requirement_id} deleted"}
