"""项目成员服务。"""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories import collaboration as collaboration_repo
from app.repositories import workforce as workforce_repo
from app.schemas.collaboration import (
    ProjectMemberCreate,
    ProjectMemberListResponse,
    ProjectMemberResponse,
    ProjectMemberUpdate,
)


def _to_response(row: dict) -> ProjectMemberResponse:
    return ProjectMemberResponse(**row)


def _require_row(project_member_id: int, db: Session | None = None) -> dict:
    row = collaboration_repo.get_project_member_by_id(project_member_id, db)
    if row is None:
        raise NotFoundError(f"Project member {project_member_id} not found")
    return row


def _validate_links(payload: dict, db: Session | None = None) -> None:
    if collaboration_repo.get_project_by_id(payload["project_id"], db) is None:
        raise NotFoundError(f"Project {payload['project_id']} not found")
    if workforce_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")


def list_project_members(
    project_id: int | None = None,
    worker_id: int | None = None,
    db: Session | None = None,
) -> ProjectMemberListResponse:
    rows = collaboration_repo.list_project_members(project_id, worker_id, db)
    return ProjectMemberListResponse(project_members=[_to_response(row) for row in rows], total=len(rows))


def get_project_member(project_member_id: int, db: Session | None = None) -> ProjectMemberResponse:
    return _to_response(_require_row(project_member_id, db))


def create_project_member(data: ProjectMemberCreate, db: Session | None = None) -> ProjectMemberResponse:
    payload = data.model_dump()
    _validate_links(payload, db)
    if (
        collaboration_repo.get_project_member_by_project_and_worker(payload["project_id"], payload["worker_id"], db)
        is not None
    ):
        raise ConflictError("Project member already exists")
    row = collaboration_repo.create_project_member(payload, db)
    return _to_response(row)


def update_project_member(
    project_member_id: int, data: ProjectMemberUpdate, db: Session | None = None
) -> ProjectMemberResponse:
    current = _require_row(project_member_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_links(payload, db)
    existing = collaboration_repo.get_project_member_by_project_and_worker(
        payload["project_id"], payload["worker_id"], db
    )
    if existing is not None and existing["id"] != project_member_id:
        raise ConflictError("Project member already exists")
    row = collaboration_repo.update_project_member(project_member_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Project member {project_member_id} not found")
    return _to_response(row)


def delete_project_member(project_member_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(project_member_id, db)
    collaboration_repo.delete_project_member(project_member_id, db)
    return {"message": f"Project member {project_member_id} deleted"}
