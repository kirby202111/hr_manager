from sqlalchemy.orm import Session

from app.database import db_session
from app.models.worker import Worker as WorkerORM


def get_all_workers(db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        workers = session.query(WorkerORM).all()
        return [worker.to_dict() for worker in workers]


def get_worker_by_id(worker_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        worker = session.get(WorkerORM, worker_id)
        return worker.to_dict() if worker else None


def get_workers_by_department(department_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        workers = session.query(WorkerORM).filter_by(department_id=department_id).all()
        return [worker.to_dict() for worker in workers]


def create_worker(worker_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        worker = WorkerORM(**worker_data)
        session.add(worker)
        session.flush()
        session.refresh(worker)
        return worker.to_dict()


def update_worker(worker_id: int, worker_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        worker = session.get(WorkerORM, worker_id)
        if worker is None:
            return None
        for key, value in worker_data.items():
            if value is not None:
                setattr(worker, key, value)
        session.flush()
        session.refresh(worker)
        return worker.to_dict()


def delete_worker(worker_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        worker = session.get(WorkerORM, worker_id)
        if worker is None:
            return False
        session.delete(worker)
        session.flush()
        return True
