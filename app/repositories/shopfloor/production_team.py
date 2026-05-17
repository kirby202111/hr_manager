"""班组仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.shopfloor import ProductionTeam


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_production_teams(
    production_line_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProductionTeam)
        if production_line_id is not None:
            query = query.filter(ProductionTeam.production_line_id == production_line_id)
        if code is not None:
            query = query.filter(ProductionTeam.code == code)
        if status is not None:
            query = query.filter(ProductionTeam.status == status)
        return [row.to_dict() for row in query.all()]


def get_production_team_by_id(production_team_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionTeam, production_team_id)
        return row.to_dict() if row else None


def get_production_team_by_code(production_line_id: int, code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(ProductionTeam).filter(
            ProductionTeam.production_line_id == production_line_id,
            ProductionTeam.code == code,
        ).first()
        return row.to_dict() if row else None


def create_production_team(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProductionTeam(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_production_team(production_team_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionTeam, production_team_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_production_team(production_team_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProductionTeam, production_team_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
