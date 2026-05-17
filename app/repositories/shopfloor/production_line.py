"""产线仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.shopfloor import ProductionLine


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_production_lines(
    organization_unit_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProductionLine)
        if organization_unit_id is not None:
            query = query.filter(ProductionLine.organization_unit_id == organization_unit_id)
        if code is not None:
            query = query.filter(ProductionLine.code == code)
        if status is not None:
            query = query.filter(ProductionLine.status == status)
        return [row.to_dict() for row in query.all()]


def get_production_line_by_id(production_line_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionLine, production_line_id)
        return row.to_dict() if row else None


def get_production_line_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(ProductionLine).filter(ProductionLine.code == code).first()
        return row.to_dict() if row else None


def create_production_line(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProductionLine(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_production_line(production_line_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionLine, production_line_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_production_line(production_line_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProductionLine, production_line_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
