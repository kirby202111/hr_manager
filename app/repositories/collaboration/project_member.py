"""项目成员仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.collaboration import ProjectMember


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


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
