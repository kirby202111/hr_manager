"""人员主数据仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.workforce import Worker


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_workers(
    organization_unit_id: int | None = None,
    employment_type: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(Worker)
        if organization_unit_id is not None:
            query = query.filter(Worker.organization_unit_id == organization_unit_id)
        if employment_type is not None:
            query = query.filter(Worker.employment_type == employment_type)
        if status is not None:
            query = query.filter(Worker.status == status)
        return [row.to_dict() for row in query.all()]


def get_worker_by_id(worker_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Worker, worker_id)
        return row.to_dict() if row else None


def get_worker_by_code(worker_code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(Worker).filter(Worker.worker_code == worker_code).first()
        return row.to_dict() if row else None


def list_workers_by_organization_unit(organization_unit_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = session.query(Worker).filter(Worker.organization_unit_id == organization_unit_id).all()
        return [row.to_dict() for row in rows]


def create_worker(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = Worker(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_worker(worker_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Worker, worker_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_worker(worker_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(Worker, worker_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
