"""项目仓储。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.collaboration import Project


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
