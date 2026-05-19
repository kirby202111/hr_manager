"""Workstation training requirement service."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.qualification import safety_training as training_repo
from app.repositories.shopfloor import workstation as workstation_repo
from app.repositories.shopfloor import workstation_training_requirement as requirement_repo
from app.schemas.shopfloor import (
    WorkstationTrainingRequirementCreate,
    WorkstationTrainingRequirementListResponse,
    WorkstationTrainingRequirementResponse,
    WorkstationTrainingRequirementUpdate,
)


def _to_response(row: dict) -> WorkstationTrainingRequirementResponse:
    return WorkstationTrainingRequirementResponse(**row)


def _require_row(requirement_id: int, db: Session | None = None) -> dict:
    row = requirement_repo.get_workstation_training_requirement_by_id(requirement_id, db)
    if row is None:
        raise NotFoundError(f"Workstation training requirement {requirement_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if workstation_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if training_repo.get_safety_training_by_id(payload["safety_training_id"], db) is None:
        raise NotFoundError(f"Safety training {payload['safety_training_id']} not found")
    if payload.get("min_score") is not None and payload["min_score"] < 0:
        raise ValidationError("min_score cannot be negative")


def list_workstation_training_requirements(
    workstation_id: int,
    status: str | None = None,
    db: Session | None = None,
) -> WorkstationTrainingRequirementListResponse:
    if workstation_repo.get_workstation_by_id(workstation_id, db) is None:
        raise NotFoundError(f"Workstation {workstation_id} not found")
    rows = requirement_repo.list_workstation_training_requirements(workstation_id=workstation_id, status=status, db=db)
    return WorkstationTrainingRequirementListResponse(requirements=[_to_response(row) for row in rows], total=len(rows))


def get_workstation_training_requirement(
    requirement_id: int,
    db: Session | None = None,
) -> WorkstationTrainingRequirementResponse:
    return _to_response(_require_row(requirement_id, db))


def create_workstation_training_requirement(
    workstation_id: int,
    data: WorkstationTrainingRequirementCreate,
    db: Session | None = None,
) -> WorkstationTrainingRequirementResponse:
    payload = {"workstation_id": workstation_id, **data.model_dump()}
    _validate_payload(payload, db)
    existing = requirement_repo.get_workstation_training_requirement_by_workstation_and_training(
        workstation_id,
        payload["safety_training_id"],
        db,
    )
    if existing is not None:
        raise ConflictError("Workstation training requirement already exists")
    row = requirement_repo.create_workstation_training_requirement(payload, db)
    return _to_response(row)


def update_workstation_training_requirement(
    requirement_id: int,
    data: WorkstationTrainingRequirementUpdate,
    db: Session | None = None,
) -> WorkstationTrainingRequirementResponse:
    current = _require_row(requirement_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = requirement_repo.get_workstation_training_requirement_by_workstation_and_training(
        payload["workstation_id"],
        payload["safety_training_id"],
        db,
    )
    if existing is not None and existing["id"] != requirement_id:
        raise ConflictError("Workstation training requirement already exists")
    row = requirement_repo.update_workstation_training_requirement(
        requirement_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Workstation training requirement {requirement_id} not found")
    return _to_response(row)


def delete_workstation_training_requirement(requirement_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(requirement_id, db)
    requirement_repo.delete_workstation_training_requirement(requirement_id, db)
    return {"message": f"Workstation training requirement {requirement_id} deleted"}
