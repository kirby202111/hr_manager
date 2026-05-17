"""排班计划仓储。"""

from datetime import date

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.staffing import ShiftPlan


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_shift_plans(
    production_line_id: int | None = None,
    shift_template_id: int | None = None,
    work_date: date | None = None,
    status: str | None = None,
    production_order_id: int | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ShiftPlan)
        if production_line_id is not None:
            query = query.filter(ShiftPlan.production_line_id == production_line_id)
        if shift_template_id is not None:
            query = query.filter(ShiftPlan.shift_template_id == shift_template_id)
        if work_date is not None:
            query = query.filter(ShiftPlan.work_date == work_date)
        if status is not None:
            query = query.filter(ShiftPlan.status == status)
        if production_order_id is not None:
            query = query.filter(ShiftPlan.production_order_id == production_order_id)
        return [row.to_dict() for row in query.all()]


def get_shift_plan_by_id(shift_plan_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ShiftPlan, shift_plan_id)
        return row.to_dict() if row else None


def create_shift_plan(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ShiftPlan(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_shift_plan(shift_plan_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ShiftPlan, shift_plan_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_shift_plan(shift_plan_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ShiftPlan, shift_plan_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
