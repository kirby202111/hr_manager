"""Workstation training requirement repository."""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.shopfloor import WorkstationTrainingRequirement


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_workstation_training_requirements(
    workstation_id: int | None = None,
    safety_training_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkstationTrainingRequirement)
        if workstation_id is not None:
            query = query.filter(WorkstationTrainingRequirement.workstation_id == workstation_id)
        if safety_training_id is not None:
            query = query.filter(WorkstationTrainingRequirement.safety_training_id == safety_training_id)
        if status is not None:
            query = query.filter(WorkstationTrainingRequirement.status == status)
        return [row.to_dict() for row in query.all()]


def get_workstation_training_requirement_by_id(requirement_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationTrainingRequirement, requirement_id)
        return row.to_dict() if row else None


def get_workstation_training_requirement_by_workstation_and_training(
    workstation_id: int, safety_training_id: int, db: Session | None = None
) -> dict | None:
    with db_session(db) as session:
        row = session.query(WorkstationTrainingRequirement).filter(
            WorkstationTrainingRequirement.workstation_id == workstation_id,
            WorkstationTrainingRequirement.safety_training_id == safety_training_id,
        ).first()
        return row.to_dict() if row else None


def create_workstation_training_requirement(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkstationTrainingRequirement(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_workstation_training_requirement(requirement_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationTrainingRequirement, requirement_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_workstation_training_requirement(requirement_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(WorkstationTrainingRequirement, requirement_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
