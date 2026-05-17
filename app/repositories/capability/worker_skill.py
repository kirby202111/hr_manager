"""人员技能仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.capability import WorkerSkill


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_worker_skills(
    worker_id: int | None = None,
    skill_id: int | None = None,
    proficiency_level: str | None = None,
    validated: bool | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkerSkill)
        if worker_id is not None:
            query = query.filter(WorkerSkill.worker_id == worker_id)
        if skill_id is not None:
            query = query.filter(WorkerSkill.skill_id == skill_id)
        if proficiency_level is not None:
            query = query.filter(WorkerSkill.proficiency_level == proficiency_level)
        if validated is not None:
            query = query.filter(WorkerSkill.validated == validated)
        return [row.to_dict() for row in query.all()]


def get_worker_skill_by_id(worker_skill_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerSkill, worker_skill_id)
        return row.to_dict() if row else None


def get_worker_skill_by_worker_and_skill(worker_id: int, skill_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(WorkerSkill).filter(
            WorkerSkill.worker_id == worker_id,
            WorkerSkill.skill_id == skill_id,
        ).first()
        return row.to_dict() if row else None


def create_worker_skill(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkerSkill(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_worker_skill(worker_skill_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerSkill, worker_skill_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_worker_skill(worker_skill_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(WorkerSkill, worker_skill_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
