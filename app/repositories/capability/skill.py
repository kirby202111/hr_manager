"""技能目录仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.capability import Skill


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_skills(
    category: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(Skill)
        if category is not None:
            query = query.filter(Skill.category == category)
        if status is not None:
            query = query.filter(Skill.status == status)
        return [row.to_dict() for row in query.all()]


def get_skill_by_id(skill_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Skill, skill_id)
        return row.to_dict() if row else None


def get_skill_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(Skill).filter(Skill.code == code).first()
        return row.to_dict() if row else None


def get_skill_by_name(name: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(Skill).filter(Skill.name == name).first()
        return row.to_dict() if row else None


def create_skill(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = Skill(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_skill(skill_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Skill, skill_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_skill(skill_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(Skill, skill_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
