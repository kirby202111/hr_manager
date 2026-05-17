"""排班域仓储，覆盖班次模板、排班计划与排班分配。"""

from datetime import date

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.staffing import ShiftAssignment, ShiftPlan, ShiftTemplate


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_shift_templates(
    code: str | None = None,
    shift_type: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ShiftTemplate)
        if code is not None:
            query = query.filter(ShiftTemplate.code == code)
        if shift_type is not None:
            query = query.filter(ShiftTemplate.shift_type == shift_type)
        if status is not None:
            query = query.filter(ShiftTemplate.status == status)
        return [row.to_dict() for row in query.all()]


def get_shift_template_by_id(shift_template_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ShiftTemplate, shift_template_id)
        return row.to_dict() if row else None


def get_shift_template_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(ShiftTemplate).filter(ShiftTemplate.code == code).first()
        return row.to_dict() if row else None


def create_shift_template(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ShiftTemplate(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_shift_template(shift_template_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ShiftTemplate, shift_template_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_shift_template(shift_template_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ShiftTemplate, shift_template_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


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
