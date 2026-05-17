"""证书目录仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.qualification import Certification


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_certifications(category: str | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(Certification)
        if category is not None:
            query = query.filter(Certification.category == category)
        return [row.to_dict() for row in query.all()]


def get_certification_by_id(certification_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Certification, certification_id)
        return row.to_dict() if row else None


def get_certification_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(Certification).filter(Certification.code == code).first()
        return row.to_dict() if row else None


def create_certification(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = Certification(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_certification(certification_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Certification, certification_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_certification(certification_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(Certification, certification_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
