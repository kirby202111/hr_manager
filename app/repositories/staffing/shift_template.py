"""班次模板仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.staffing import ShiftTemplate


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
