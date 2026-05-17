"""工位设备授权要求仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.shopfloor import WorkstationEquipmentRequirement


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_workstation_equipment_requirements(
    workstation_id: int | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkstationEquipmentRequirement)
        if workstation_id is not None:
            query = query.filter(WorkstationEquipmentRequirement.workstation_id == workstation_id)
        return [row.to_dict() for row in query.all()]


def get_workstation_equipment_requirement_by_id(
    workstation_equipment_requirement_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationEquipmentRequirement, workstation_equipment_requirement_id)
        return row.to_dict() if row else None


def create_workstation_equipment_requirement(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkstationEquipmentRequirement(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_workstation_equipment_requirement(
    workstation_equipment_requirement_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationEquipmentRequirement, workstation_equipment_requirement_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_workstation_equipment_requirement(
    workstation_equipment_requirement_id: int,
    db: Session | None = None,
) -> bool:
    with db_session(db) as session:
        row = session.get(WorkstationEquipmentRequirement, workstation_equipment_requirement_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
