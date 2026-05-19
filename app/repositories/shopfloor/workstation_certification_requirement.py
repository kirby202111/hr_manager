"""Workstation certification requirement repository."""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.shopfloor import WorkstationCertificationRequirement


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_workstation_certification_requirements(
    workstation_id: int | None = None,
    certification_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkstationCertificationRequirement)
        if workstation_id is not None:
            query = query.filter(WorkstationCertificationRequirement.workstation_id == workstation_id)
        if certification_id is not None:
            query = query.filter(WorkstationCertificationRequirement.certification_id == certification_id)
        if status is not None:
            query = query.filter(WorkstationCertificationRequirement.status == status)
        return [row.to_dict() for row in query.all()]


def get_workstation_certification_requirement_by_id(requirement_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationCertificationRequirement, requirement_id)
        return row.to_dict() if row else None


def get_workstation_certification_requirement_by_workstation_and_certification(
    workstation_id: int, certification_id: int, db: Session | None = None
) -> dict | None:
    with db_session(db) as session:
        row = session.query(WorkstationCertificationRequirement).filter(
            WorkstationCertificationRequirement.workstation_id == workstation_id,
            WorkstationCertificationRequirement.certification_id == certification_id,
        ).first()
        return row.to_dict() if row else None


def create_workstation_certification_requirement(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkstationCertificationRequirement(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_workstation_certification_requirement(
    requirement_id: int, data: dict, db: Session | None = None
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationCertificationRequirement, requirement_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_workstation_certification_requirement(requirement_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(WorkstationCertificationRequirement, requirement_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
