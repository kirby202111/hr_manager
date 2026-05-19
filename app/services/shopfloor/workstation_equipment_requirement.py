"""Workstation equipment requirement service."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.shopfloor import workstation as workstation_repo
from app.repositories.shopfloor import workstation_equipment_requirement as requirement_repo
from app.schemas.shopfloor import (
    WorkstationEquipmentRequirementCreate,
    WorkstationEquipmentRequirementListResponse,
    WorkstationEquipmentRequirementResponse,
    WorkstationEquipmentRequirementUpdate,
)

VALID_LEVELS = {"L1", "L2", "L3", "L4", "L5"}


def _to_response(row: dict) -> WorkstationEquipmentRequirementResponse:
    return WorkstationEquipmentRequirementResponse(**row)


def _require_row(requirement_id: int, db: Session | None = None) -> dict:
    row = requirement_repo.get_workstation_equipment_requirement_by_id(requirement_id, db)
    if row is None:
        raise NotFoundError(f"Workstation equipment requirement {requirement_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if workstation_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if payload["min_authorization_level"] not in VALID_LEVELS:
        raise ValidationError("min_authorization_level must be one of L1, L2, L3, L4, L5")


def list_workstation_equipment_requirements(
    workstation_id: int,
    status: str | None = None,
    db: Session | None = None,
) -> WorkstationEquipmentRequirementListResponse:
    if workstation_repo.get_workstation_by_id(workstation_id, db) is None:
        raise NotFoundError(f"Workstation {workstation_id} not found")
    rows = requirement_repo.list_workstation_equipment_requirements(
        workstation_id=workstation_id,
        status=status,
        db=db,
    )
    return WorkstationEquipmentRequirementListResponse(
        requirements=[_to_response(row) for row in rows],
        total=len(rows),
    )


def get_workstation_equipment_requirement(
    requirement_id: int,
    db: Session | None = None,
) -> WorkstationEquipmentRequirementResponse:
    return _to_response(_require_row(requirement_id, db))


def create_workstation_equipment_requirement(
    workstation_id: int,
    data: WorkstationEquipmentRequirementCreate,
    db: Session | None = None,
) -> WorkstationEquipmentRequirementResponse:
    payload = {"workstation_id": workstation_id, **data.model_dump()}
    _validate_payload(payload, db)
    existing = requirement_repo.get_workstation_equipment_requirement_by_workstation_and_code(
        workstation_id,
        payload["equipment_code"],
        db,
    )
    if existing is not None:
        raise ConflictError("Workstation equipment requirement already exists")
    row = requirement_repo.create_workstation_equipment_requirement(payload, db)
    return _to_response(row)


def update_workstation_equipment_requirement(
    requirement_id: int,
    data: WorkstationEquipmentRequirementUpdate,
    db: Session | None = None,
) -> WorkstationEquipmentRequirementResponse:
    current = _require_row(requirement_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = requirement_repo.get_workstation_equipment_requirement_by_workstation_and_code(
        payload["workstation_id"],
        payload["equipment_code"],
        db,
    )
    if existing is not None and existing["id"] != requirement_id:
        raise ConflictError("Workstation equipment requirement already exists")
    row = requirement_repo.update_workstation_equipment_requirement(
        requirement_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Workstation equipment requirement {requirement_id} not found")
    return _to_response(row)


def delete_workstation_equipment_requirement(requirement_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(requirement_id, db)
    requirement_repo.delete_workstation_equipment_requirement(requirement_id, db)
    return {"message": f"Workstation equipment requirement {requirement_id} deleted"}
