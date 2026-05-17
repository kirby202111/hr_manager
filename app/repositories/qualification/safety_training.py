"""安全培训目录仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.qualification import SafetyTraining


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_safety_trainings(category: str | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(SafetyTraining)
        if category is not None:
            query = query.filter(SafetyTraining.category == category)
        return [row.to_dict() for row in query.all()]


def get_safety_training_by_id(safety_training_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(SafetyTraining, safety_training_id)
        return row.to_dict() if row else None


def get_safety_training_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(SafetyTraining).filter(SafetyTraining.code == code).first()
        return row.to_dict() if row else None


def create_safety_training(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = SafetyTraining(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_safety_training(safety_training_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(SafetyTraining, safety_training_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_safety_training(safety_training_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(SafetyTraining, safety_training_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
