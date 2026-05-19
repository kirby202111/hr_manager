"""Worker eligibility snapshot repository."""

from datetime import date

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.qualification import WorkerEligibilitySnapshot


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_worker_eligibility_snapshots(
    worker_id: int | None = None,
    workstation_id: int | None = None,
    shift_plan_id: int | None = None,
    status: str | None = None,
    work_date_from: date | None = None,
    work_date_to: date | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkerEligibilitySnapshot)
        if worker_id is not None:
            query = query.filter(WorkerEligibilitySnapshot.worker_id == worker_id)
        if workstation_id is not None:
            query = query.filter(WorkerEligibilitySnapshot.workstation_id == workstation_id)
        if shift_plan_id is not None:
            query = query.filter(WorkerEligibilitySnapshot.shift_plan_id == shift_plan_id)
        if status is not None:
            query = query.filter(WorkerEligibilitySnapshot.status == status)
        if work_date_from is not None:
            query = query.filter(WorkerEligibilitySnapshot.work_date >= work_date_from)
        if work_date_to is not None:
            query = query.filter(WorkerEligibilitySnapshot.work_date <= work_date_to)
        query = query.order_by(WorkerEligibilitySnapshot.checked_at.desc(), WorkerEligibilitySnapshot.id.desc())
        return [row.to_dict() for row in query.all()]


def get_worker_eligibility_snapshot_by_id(snapshot_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerEligibilitySnapshot, snapshot_id)
        return row.to_dict() if row else None


def get_latest_worker_eligibility_snapshot_by_shift_assignment_id(
    shift_assignment_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = (
            session.query(WorkerEligibilitySnapshot)
            .filter(WorkerEligibilitySnapshot.shift_assignment_id == shift_assignment_id)
            .order_by(WorkerEligibilitySnapshot.checked_at.desc(), WorkerEligibilitySnapshot.id.desc())
            .first()
        )
        return row.to_dict() if row else None


def list_latest_worker_eligibility_snapshots_by_shift_assignment_ids(
    shift_assignment_ids: list[int],
    db: Session | None = None,
) -> dict[int, dict]:
    if not shift_assignment_ids:
        return {}
    with db_session(db) as session:
        rows = (
            session.query(WorkerEligibilitySnapshot)
            .filter(WorkerEligibilitySnapshot.shift_assignment_id.in_(shift_assignment_ids))
            .order_by(WorkerEligibilitySnapshot.checked_at.desc(), WorkerEligibilitySnapshot.id.desc())
            .all()
        )
        snapshots_by_assignment: dict[int, dict] = {}
        for row in rows:
            if row.shift_assignment_id is None or row.shift_assignment_id in snapshots_by_assignment:
                continue
            snapshots_by_assignment[row.shift_assignment_id] = row.to_dict()
        return snapshots_by_assignment


def create_worker_eligibility_snapshot(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkerEligibilitySnapshot(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_worker_eligibility_snapshot(snapshot_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerEligibilitySnapshot, snapshot_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()
