"""Production order repository."""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.production import ProductionOrder


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_production_orders(
    production_line_id: int | None = None,
    order_number: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProductionOrder)
        if production_line_id is not None:
            query = query.filter(ProductionOrder.production_line_id == production_line_id)
        if order_number is not None:
            query = query.filter(ProductionOrder.order_number == order_number)
        if status is not None:
            query = query.filter(ProductionOrder.status == status)
        return [row.to_dict() for row in query.all()]


def get_production_order_by_id(production_order_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionOrder, production_order_id)
        return row.to_dict() if row else None


def get_production_order_by_order_number(order_number: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(ProductionOrder).filter(ProductionOrder.order_number == order_number).first()
        return row.to_dict() if row else None


def create_production_order(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProductionOrder(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_production_order(production_order_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionOrder, production_order_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_production_order(production_order_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProductionOrder, production_order_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
