"""工单工序仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.shopfloor import ProductionOperation


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_production_operations(
    production_order_id: int | None = None,
    workstation_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProductionOperation)
        if production_order_id is not None:
            query = query.filter(ProductionOperation.production_order_id == production_order_id)
        if workstation_id is not None:
            query = query.filter(ProductionOperation.workstation_id == workstation_id)
        if status is not None:
            query = query.filter(ProductionOperation.status == status)
        return [row.to_dict() for row in query.all()]


def get_production_operation_by_id(production_operation_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionOperation, production_operation_id)
        return row.to_dict() if row else None


def create_production_operation(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProductionOperation(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_production_operation(
    production_operation_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionOperation, production_operation_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_production_operation(production_operation_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProductionOperation, production_operation_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
