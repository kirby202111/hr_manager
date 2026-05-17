"""工位设备授权要求服务。"""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories import shopfloor as shopfloor_repo
from app.schemas.shopfloor import (
    WorkstationEquipmentRequirementCreate,
    WorkstationEquipmentRequirementListResponse,
    WorkstationEquipmentRequirementResponse,
    WorkstationEquipmentRequirementUpdate,
)


def _to_response(row: dict) -> WorkstationEquipmentRequirementResponse:
    return WorkstationEquipmentRequirementResponse(**row)


def _require_row(requirement_id: int, db: Session | None = None) -> dict:
    row = shopfloor_repo.get_workstation_equipment_requirement_by_id(requirement_id, db)
    if row is None:
        raise NotFoundError(f"Workstation equipment requirement {requirement_id} not found")
    return row


def _exists_duplicate(payload: dict, db: Session | None = None, exclude_id: int | None = None) -> bool:
    rows = shopfloor_repo.list_workstation_equipment_requirements(payload["workstation_id"], db)
    for row in rows:
        if exclude_id is not None and row["id"] == exclude_id:
            continue
        if row["equipment_code"] == payload["equipment_code"]:
            return True
    return False


def list_workstation_equipment_requirements(
    workstation_id: int | None = None,
    db: Session | None = None,
) -> WorkstationEquipmentRequirementListResponse:
    rows = shopfloor_repo.list_workstation_equipment_requirements(workstation_id, db)
    return WorkstationEquipmentRequirementListResponse(
        workstation_equipment_requirements=[_to_response(row) for row in rows],
        total=len(rows),
    )


def get_workstation_equipment_requirement(
    requirement_id: int,
    db: Session | None = None,
) -> WorkstationEquipmentRequirementResponse:
    return _to_response(_require_row(requirement_id, db))


def create_workstation_equipment_requirement(
    data: WorkstationEquipmentRequirementCreate,
    db: Session | None = None,
) -> WorkstationEquipmentRequirementResponse:
    payload = data.model_dump()
    if shopfloor_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if _exists_duplicate(payload, db):
        raise ConflictError("Workstation equipment requirement already exists")
    row = shopfloor_repo.create_workstation_equipment_requirement(payload, db)
    return _to_response(row)


def update_workstation_equipment_requirement(
    requirement_id: int,
    data: WorkstationEquipmentRequirementUpdate,
    db: Session | None = None,
) -> WorkstationEquipmentRequirementResponse:
    current = _require_row(requirement_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if shopfloor_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if _exists_duplicate(payload, db, exclude_id=requirement_id):
        raise ConflictError("Workstation equipment requirement already exists")
    row = shopfloor_repo.update_workstation_equipment_requirement(
        requirement_id, data.model_dump(exclude_unset=True), db
    )
    if row is None:
        raise NotFoundError(f"Workstation equipment requirement {requirement_id} not found")
    return _to_response(row)


def delete_workstation_equipment_requirement(requirement_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(requirement_id, db)
    shopfloor_repo.delete_workstation_equipment_requirement(requirement_id, db)
    return {"message": f"Workstation equipment requirement {requirement_id} deleted"}
