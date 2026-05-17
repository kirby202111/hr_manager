"""项目工时记录仓储。"""

from datetime import date

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.collaboration import ProjectTimesheetEntry


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


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
