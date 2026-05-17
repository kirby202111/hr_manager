"""人员持证记录仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.qualification import WorkerCertification


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_worker_certifications(
    worker_id: int | None = None,
    certification_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkerCertification)
        if worker_id is not None:
            query = query.filter(WorkerCertification.worker_id == worker_id)
        if certification_id is not None:
            query = query.filter(WorkerCertification.certification_id == certification_id)
        if status is not None:
            query = query.filter(WorkerCertification.status == status)
        return [row.to_dict() for row in query.all()]


def get_worker_certification_by_id(worker_certification_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerCertification, worker_certification_id)
        return row.to_dict() if row else None


def get_worker_certification_by_worker_and_certification(
    worker_id: int,
    certification_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.query(WorkerCertification).filter(
            WorkerCertification.worker_id == worker_id,
            WorkerCertification.certification_id == certification_id,
        ).first()
        return row.to_dict() if row else None


def create_worker_certification(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkerCertification(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_worker_certification(worker_certification_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerCertification, worker_certification_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_worker_certification(worker_certification_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(WorkerCertification, worker_certification_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
