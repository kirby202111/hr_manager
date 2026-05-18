"""Workstation skill requirement repository."""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.qualification import WorkstationSkillRequirement


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_workstation_skill_requirements(workstation_id: int | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkstationSkillRequirement)
        if workstation_id is not None:
            query = query.filter(WorkstationSkillRequirement.workstation_id == workstation_id)
        return [row.to_dict() for row in query.all()]


def get_workstation_skill_requirement_by_id(
    workstation_skill_requirement_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationSkillRequirement, workstation_skill_requirement_id)
        return row.to_dict() if row else None


def create_workstation_skill_requirement(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkstationSkillRequirement(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_workstation_skill_requirement(
    workstation_skill_requirement_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationSkillRequirement, workstation_skill_requirement_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_workstation_skill_requirement(
    workstation_skill_requirement_id: int,
    db: Session | None = None,
) -> bool:
    with db_session(db) as session:
        row = session.get(WorkstationSkillRequirement, workstation_skill_requirement_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
