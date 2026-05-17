"""协同域仓储，覆盖项目、成员、技能需求与工时记录。"""

from datetime import date

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.collaboration import Project, ProjectMember, ProjectSkillRequirement, ProjectTimesheetEntry


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_projects(status: str | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(Project)
        if status is not None:
            query = query.filter(Project.status == status)
        return [row.to_dict() for row in query.all()]


def get_project_by_id(project_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Project, project_id)
        return row.to_dict() if row else None


def get_project_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(Project).filter(Project.code == code).first()
        return row.to_dict() if row else None


def create_project(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = Project(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_project(project_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Project, project_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_project(project_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(Project, project_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_project_members(
    project_id: int | None = None,
    worker_id: int | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProjectMember)
        if project_id is not None:
            query = query.filter(ProjectMember.project_id == project_id)
        if worker_id is not None:
            query = query.filter(ProjectMember.worker_id == worker_id)
        return [row.to_dict() for row in query.all()]


def get_project_member_by_id(project_member_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProjectMember, project_member_id)
        return row.to_dict() if row else None


def get_project_member_by_project_and_worker(project_id: int, worker_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.worker_id == worker_id,
        ).first()
        return row.to_dict() if row else None


def create_project_member(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProjectMember(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_project_member(project_member_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProjectMember, project_member_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_project_member(project_member_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProjectMember, project_member_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


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


def list_project_timesheet_entries(
    project_id: int | None = None,
    worker_id: int | None = None,
    project_skill_requirement_id: int | None = None,
    work_date: date | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProjectTimesheetEntry)
        if project_id is not None:
            query = query.filter(ProjectTimesheetEntry.project_id == project_id)
        if worker_id is not None:
            query = query.filter(ProjectTimesheetEntry.worker_id == worker_id)
        if project_skill_requirement_id is not None:
            query = query.filter(
                ProjectTimesheetEntry.project_skill_requirement_id == project_skill_requirement_id
            )
        if work_date is not None:
            query = query.filter(ProjectTimesheetEntry.work_date == work_date)
        return [row.to_dict() for row in query.all()]


def get_project_timesheet_entry_by_id(project_timesheet_entry_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProjectTimesheetEntry, project_timesheet_entry_id)
        return row.to_dict() if row else None


def create_project_timesheet_entry(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProjectTimesheetEntry(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_project_timesheet_entry(
    project_timesheet_entry_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProjectTimesheetEntry, project_timesheet_entry_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_project_timesheet_entry(project_timesheet_entry_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProjectTimesheetEntry, project_timesheet_entry_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
