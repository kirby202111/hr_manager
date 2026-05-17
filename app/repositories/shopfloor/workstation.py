"""工位仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.shopfloor import Workstation


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_workstations(
    production_line_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(Workstation)
        if production_line_id is not None:
            query = query.filter(Workstation.production_line_id == production_line_id)
        if code is not None:
            query = query.filter(Workstation.code == code)
        if status is not None:
            query = query.filter(Workstation.status == status)
        return [row.to_dict() for row in query.all()]


def get_workstation_by_id(workstation_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Workstation, workstation_id)
        return row.to_dict() if row else None


def get_workstation_by_code(production_line_id: int, code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(Workstation).filter(
            Workstation.production_line_id == production_line_id,
            Workstation.code == code,
        ).first()
        return row.to_dict() if row else None


def create_workstation(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = Workstation(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_workstation(workstation_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Workstation, workstation_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_workstation(workstation_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(Workstation, workstation_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
