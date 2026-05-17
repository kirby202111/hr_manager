"""人员任职与归属仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.workforce import WorkerAssignment


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_worker_assignments(
    worker_id: int | None = None,
    organization_unit_id: int | None = None,
    production_line_id: int | None = None,
    production_team_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkerAssignment)
        if worker_id is not None:
            query = query.filter(WorkerAssignment.worker_id == worker_id)
        if organization_unit_id is not None:
            query = query.filter(WorkerAssignment.organization_unit_id == organization_unit_id)
        if production_line_id is not None:
            query = query.filter(WorkerAssignment.production_line_id == production_line_id)
        if production_team_id is not None:
            query = query.filter(WorkerAssignment.production_team_id == production_team_id)
        if status is not None:
            query = query.filter(WorkerAssignment.status == status)
        return [row.to_dict() for row in query.all()]


def get_worker_assignment_by_id(worker_assignment_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerAssignment, worker_assignment_id)
        return row.to_dict() if row else None


def list_assignments_by_worker(worker_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = session.query(WorkerAssignment).filter(WorkerAssignment.worker_id == worker_id).all()
        return [row.to_dict() for row in rows]


def list_assignments_by_organization_unit(organization_unit_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = session.query(WorkerAssignment).filter(
            WorkerAssignment.organization_unit_id == organization_unit_id
        ).all()
        return [row.to_dict() for row in rows]


def list_assignments_by_production_line(production_line_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = session.query(WorkerAssignment).filter(
            WorkerAssignment.production_line_id == production_line_id
        ).all()
        return [row.to_dict() for row in rows]


def list_assignments_by_production_team(production_team_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = session.query(WorkerAssignment).filter(
            WorkerAssignment.production_team_id == production_team_id
        ).all()
        return [row.to_dict() for row in rows]


def create_worker_assignment(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkerAssignment(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_worker_assignment(worker_assignment_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerAssignment, worker_assignment_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_worker_assignment(worker_assignment_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(WorkerAssignment, worker_assignment_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
