from sqlalchemy.orm import Session

from app.database import db_session
from app.models.worker_skill import WorkerSkill as WorkerSkillORM


def get_all_skills(db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        return [skill.to_dict() for skill in session.query(WorkerSkillORM).all()]


def get_skill_by_id(skill_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        skill = session.get(WorkerSkillORM, skill_id)
        return skill.to_dict() if skill else None


def get_skills_by_worker(worker_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        return [skill.to_dict() for skill in session.query(WorkerSkillORM).filter_by(worker_id=worker_id).all()]


def get_skills_by_name(skill_name: str, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkerSkillORM).filter(WorkerSkillORM.skill_name.contains(skill_name))
        return [skill.to_dict() for skill in query.all()]


def create_skill(skill_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        skill = WorkerSkillORM(**skill_data)
        session.add(skill)
        session.flush()
        session.refresh(skill)
        return skill.to_dict()


def update_skill(skill_id: int, skill_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        skill = session.get(WorkerSkillORM, skill_id)
        if skill is None:
            return None
        for key, value in skill_data.items():
            if value is not None:
                setattr(skill, key, value)
        session.flush()
        session.refresh(skill)
        return skill.to_dict()


def delete_skill(skill_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        skill = session.get(WorkerSkillORM, skill_id)
        if skill is None:
            return False
        session.delete(skill)
        session.flush()
        return True
