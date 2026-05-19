"""Operation qualification requirement repository."""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.production import OperationQualificationRequirement


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_operation_qualification_requirements(
    production_operation_id: int | None = None,
    requirement_type: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(OperationQualificationRequirement)
        if production_operation_id is not None:
            query = query.filter(OperationQualificationRequirement.production_operation_id == production_operation_id)
        if requirement_type is not None:
            query = query.filter(OperationQualificationRequirement.requirement_type == requirement_type)
        if status is not None:
            query = query.filter(OperationQualificationRequirement.status == status)
        return [row.to_dict() for row in query.all()]


def get_operation_qualification_requirement_by_id(requirement_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationQualificationRequirement, requirement_id)
        return row.to_dict() if row else None


def create_operation_qualification_requirement(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = OperationQualificationRequirement(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_operation_qualification_requirement(
    requirement_id: int, data: dict, db: Session | None = None
) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationQualificationRequirement, requirement_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_operation_qualification_requirement(requirement_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(OperationQualificationRequirement, requirement_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
