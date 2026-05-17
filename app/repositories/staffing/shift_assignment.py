"""排班分配仓储。"""

from datetime import date

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.staffing import ShiftAssignment, ShiftPlan


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_shift_assignments(
    shift_plan_id: int | None = None,
    worker_id: int | None = None,
    workstation_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ShiftAssignment)
        if shift_plan_id is not None:
            query = query.filter(ShiftAssignment.shift_plan_id == shift_plan_id)
        if worker_id is not None:
            query = query.filter(ShiftAssignment.worker_id == worker_id)
        if workstation_id is not None:
            query = query.filter(ShiftAssignment.workstation_id == workstation_id)
        if status is not None:
            query = query.filter(ShiftAssignment.status == status)
        return [row.to_dict() for row in query.all()]


def get_shift_assignment_by_id(shift_assignment_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ShiftAssignment, shift_assignment_id)
        return row.to_dict() if row else None


def create_shift_assignment(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ShiftAssignment(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_shift_assignment(shift_assignment_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ShiftAssignment, shift_assignment_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_shift_assignment(shift_assignment_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ShiftAssignment, shift_assignment_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_shift_assignments_by_worker_on_work_date(
    worker_id: int,
    work_date: date,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        rows = (
            session.query(ShiftAssignment)
            .join(ShiftPlan, ShiftAssignment.shift_plan_id == ShiftPlan.id)
            .filter(ShiftAssignment.worker_id == worker_id)
            .filter(ShiftPlan.work_date == work_date)
            .all()
        )
        return [row.to_dict() for row in rows]
