"""人员安全培训记录仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.qualification import WorkerSafetyTraining


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_worker_safety_trainings(
    worker_id: int | None = None,
    safety_training_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkerSafetyTraining)
        if worker_id is not None:
            query = query.filter(WorkerSafetyTraining.worker_id == worker_id)
        if safety_training_id is not None:
            query = query.filter(WorkerSafetyTraining.safety_training_id == safety_training_id)
        if status is not None:
            query = query.filter(WorkerSafetyTraining.status == status)
        return [row.to_dict() for row in query.all()]


def get_worker_safety_training_by_id(worker_safety_training_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerSafetyTraining, worker_safety_training_id)
        return row.to_dict() if row else None


def get_worker_safety_training_by_worker_and_training(
    worker_id: int,
    safety_training_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.query(WorkerSafetyTraining).filter(
            WorkerSafetyTraining.worker_id == worker_id,
            WorkerSafetyTraining.safety_training_id == safety_training_id,
        ).first()
        return row.to_dict() if row else None


def create_worker_safety_training(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkerSafetyTraining(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_worker_safety_training(
    worker_safety_training_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerSafetyTraining, worker_safety_training_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_worker_safety_training(worker_safety_training_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(WorkerSafetyTraining, worker_safety_training_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
