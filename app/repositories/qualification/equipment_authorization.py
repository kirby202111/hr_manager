"""设备授权仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.qualification import EquipmentAuthorization


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_equipment_authorizations(
    worker_id: int | None = None,
    equipment_code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(EquipmentAuthorization)
        if worker_id is not None:
            query = query.filter(EquipmentAuthorization.worker_id == worker_id)
        if equipment_code is not None:
            query = query.filter(EquipmentAuthorization.equipment_code == equipment_code)
        if status is not None:
            query = query.filter(EquipmentAuthorization.status == status)
        return [row.to_dict() for row in query.all()]


def get_equipment_authorization_by_id(equipment_authorization_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(EquipmentAuthorization, equipment_authorization_id)
        return row.to_dict() if row else None


def get_equipment_authorization_by_worker_and_equipment(
    worker_id: int,
    equipment_code: str,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.query(EquipmentAuthorization).filter(
            EquipmentAuthorization.worker_id == worker_id,
            EquipmentAuthorization.equipment_code == equipment_code,
        ).first()
        return row.to_dict() if row else None


def create_equipment_authorization(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = EquipmentAuthorization(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_equipment_authorization(
    equipment_authorization_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(EquipmentAuthorization, equipment_authorization_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_equipment_authorization(equipment_authorization_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(EquipmentAuthorization, equipment_authorization_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
