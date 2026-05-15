from sqlalchemy.orm import Session

from app.database import db_session
from app.models.employee_skill import EmployeeSkill as EmployeeSkillORM


def get_all_skills(db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        skills = session.query(EmployeeSkillORM).all()
        return [s.to_dict() for s in skills]


def get_skill_by_id(skill_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        skill = session.get(EmployeeSkillORM, skill_id)
        return skill.to_dict() if skill else None


def get_skills_by_employee(employee_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        skills = session.query(EmployeeSkillORM).filter_by(employee_id=employee_id).all()
        return [s.to_dict() for s in skills]


def get_skills_by_name(skill_name: str, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        skills = session.query(EmployeeSkillORM).filter(EmployeeSkillORM.skill_name.contains(skill_name)).all()
        return [s.to_dict() for s in skills]


def create_skill(skill_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        skill = EmployeeSkillORM(**skill_data)
        session.add(skill)
        session.flush()
        session.refresh(skill)
        return skill.to_dict()


def update_skill(skill_id: int, skill_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        skill = session.get(EmployeeSkillORM, skill_id)
        if skill is None:
            return None
        for k, v in skill_data.items():
            if v is not None:
                setattr(skill, k, v)
        session.flush()
        session.refresh(skill)
        return skill.to_dict()


def delete_skill(skill_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        skill = session.get(EmployeeSkillORM, skill_id)
        if skill is None:
            return False
        session.delete(skill)
        session.flush()
        return True
