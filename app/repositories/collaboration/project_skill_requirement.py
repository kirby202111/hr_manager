"""项目技能需求仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.collaboration import ProjectSkillRequirement


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_project_skill_requirements(
    project_id: int | None = None,
    skill_id: int | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProjectSkillRequirement)
        if project_id is not None:
            query = query.filter(ProjectSkillRequirement.project_id == project_id)
        if skill_id is not None:
            query = query.filter(ProjectSkillRequirement.skill_id == skill_id)
        return [row.to_dict() for row in query.all()]


def get_project_skill_requirement_by_id(project_skill_requirement_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProjectSkillRequirement, project_skill_requirement_id)
        return row.to_dict() if row else None


def get_project_skill_requirement_by_project_and_skill(
    project_id: int,
    skill_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.query(ProjectSkillRequirement).filter(
            ProjectSkillRequirement.project_id == project_id,
            ProjectSkillRequirement.skill_id == skill_id,
        ).first()
        return row.to_dict() if row else None


def create_project_skill_requirement(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProjectSkillRequirement(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_project_skill_requirement(
    project_skill_requirement_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProjectSkillRequirement, project_skill_requirement_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_project_skill_requirement(project_skill_requirement_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProjectSkillRequirement, project_skill_requirement_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
