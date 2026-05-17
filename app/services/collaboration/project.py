"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.collaboration import project as project_repo
from app.schemas.collaboration import ProjectCreate, ProjectListResponse, ProjectResponse, ProjectUpdate


def _to_response(row: dict) -> ProjectResponse:
    return ProjectResponse(**row)


def _require_row(project_id: int, db: Session | None = None) -> dict:
    row = project_repo.get_project_by_id(project_id, db)
    if row is None:
        raise NotFoundError(f"Project {project_id} not found")
    return row


def _validate_dates(payload: dict) -> None:
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValidationError("start_date cannot be later than end_date")


def list_projects(status: str | None = None, db: Session | None = None) -> ProjectListResponse:
    rows = project_repo.list_projects(status, db)
    return ProjectListResponse(projects=[_to_response(row) for row in rows], total=len(rows))


def get_project(project_id: int, db: Session | None = None) -> ProjectResponse:
    return _to_response(_require_row(project_id, db))


def create_project(data: ProjectCreate, db: Session | None = None) -> ProjectResponse:
    if project_repo.get_project_by_code(data.code, db) is not None:
        raise ConflictError(f"Project code '{data.code}' already exists")
    payload = data.model_dump()
    _validate_dates(payload)
    row = project_repo.create_project(payload, db)
    return _to_response(row)


def update_project(project_id: int, data: ProjectUpdate, db: Session | None = None) -> ProjectResponse:
    current = _require_row(project_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_dates(payload)
    existing = project_repo.get_project_by_code(payload["code"], db)
    if existing is not None and existing["id"] != project_id:
        raise ConflictError(f"Project code '{payload['code']}' already exists")
    row = project_repo.update_project(project_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Project {project_id} not found")
    return _to_response(row)


def delete_project(project_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(project_id, db)
    project_repo.delete_project(project_id, db)
    return {"message": f"Project {project_id} deleted"}
