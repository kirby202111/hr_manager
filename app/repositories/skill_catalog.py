from app.database import SessionLocal
from app.models.skill_catalog import SkillCatalog as SkillCatalogORM


def get_all_skills(category: str | None = None) -> list[dict]:
    with SessionLocal() as session:
        query = session.query(SkillCatalogORM)
        if category:
            query = query.filter_by(category=category)
        skills = query.all()
        return [s.to_dict() for s in skills]


def get_skill_by_id(skill_id: int) -> dict | None:
    with SessionLocal() as session:
        skill = session.get(SkillCatalogORM, skill_id)
        return skill.to_dict() if skill else None


def get_skill_by_name(name: str) -> dict | None:
    with SessionLocal() as session:
        skill = session.query(SkillCatalogORM).filter_by(name=name).first()
        return skill.to_dict() if skill else None


def create_skill(skill_data: dict) -> dict:
    with SessionLocal() as session:
        skill = SkillCatalogORM(**skill_data)
        session.add(skill)
        session.commit()
        session.refresh(skill)
        return skill.to_dict()


def update_skill(skill_id: int, skill_data: dict) -> dict | None:
    with SessionLocal() as session:
        skill = session.get(SkillCatalogORM, skill_id)
        if skill is None:
            return None
        for k, v in skill_data.items():
            if v is not None:
                setattr(skill, k, v)
        session.commit()
        session.refresh(skill)
        return skill.to_dict()


def delete_skill(skill_id: int) -> bool:
    with SessionLocal() as session:
        skill = session.get(SkillCatalogORM, skill_id)
        if skill is None:
            return False
        session.delete(skill)
        session.commit()
        return True


def count_employee_skills_by_skill_id(skill_id: int) -> int:
    from app.models.employee_skill import EmployeeSkill as EmployeeSkillORM
    with SessionLocal() as session:
        return session.query(EmployeeSkillORM).filter_by(skill_id=skill_id).count()


def count_project_requirements_by_skill_id(skill_id: int) -> int:
    from app.models.project import ProjectSkillRequirement as ReqORM
    with SessionLocal() as session:
        return session.query(ReqORM).filter_by(skill_id=skill_id).count()
