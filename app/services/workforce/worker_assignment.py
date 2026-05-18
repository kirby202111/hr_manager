"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.organization import organization_unit as organization_unit_repo
from app.repositories.shopfloor import production_line as production_line_repo
from app.repositories.shopfloor import production_team as production_team_repo
from app.repositories.workforce import worker as worker_repo
from app.repositories.workforce import worker_assignment as worker_assignment_repo
from app.schemas.workforce import (
    WorkerAssignmentCreate,
    WorkerAssignmentListResponse,
    WorkerAssignmentResponse,
    WorkerAssignmentUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> WorkerAssignmentResponse:
    return WorkerAssignmentResponse(**row)


# 读取分配记录；不存在时统一抛出未找到异常。
def _require_assignment(worker_assignment_id: int, db: Session | None = None) -> dict:
    row = worker_assignment_repo.get_worker_assignment_by_id(worker_assignment_id, db)
    if row is None:
        raise NotFoundError(f"Worker assignment {worker_assignment_id} not found")
    return row


# 校验关联资源是否存在，并检查跨实体引用是否合法。
def _validate_links(payload: dict, db: Session | None = None) -> None:
    if payload.get("worker_id") is not None and worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if (
        payload.get("organization_unit_id") is not None
        and organization_unit_repo.get_organization_unit_by_id(payload["organization_unit_id"], db) is None
    ):
        raise NotFoundError(f"Organization unit {payload['organization_unit_id']} not found")
    if (
        payload.get("production_line_id") is not None
        and production_line_repo.get_production_line_by_id(payload["production_line_id"], db) is None
    ):
        raise NotFoundError(f"Production line {payload['production_line_id']} not found")
    if (
        payload.get("production_team_id") is not None
        and production_team_repo.get_production_team_by_id(payload["production_team_id"], db) is None
    ):
        raise NotFoundError(f"Production team {payload['production_team_id']} not found")
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValidationError("start_date cannot be later than end_date")


# 校验同一员工下的分配记录是否重复。
def _ensure_unique_assignment(
    worker_id: int, data: dict, db: Session | None = None, exclude_id: int | None = None
) -> None:
    rows = worker_assignment_repo.list_assignments_by_worker(worker_id, db)
    for row in rows:
        if exclude_id is not None and row["id"] == exclude_id:
            continue
        if (
            row["organization_unit_id"] == data.get("organization_unit_id")
            and row["production_line_id"] == data.get("production_line_id")
            and row["production_team_id"] == data.get("production_team_id")
            and row["role_title"] == data.get("role_title")
            and row["assignment_type"] == data.get("assignment_type")
            and row["start_date"] == data.get("start_date")
        ):
            raise ConflictError("Worker assignment already exists")


def list_worker_assignments(
    worker_id: int | None = None,
    organization_unit_id: int | None = None,
    production_line_id: int | None = None,
    production_team_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> WorkerAssignmentListResponse:
    rows = worker_assignment_repo.list_worker_assignments(
        worker_id,
        organization_unit_id,
        production_line_id,
        production_team_id,
        status,
        db,
    )
    return WorkerAssignmentListResponse(worker_assignments=[_to_response(row) for row in rows], total=len(rows))


def get_worker_assignment(worker_assignment_id: int, db: Session | None = None) -> WorkerAssignmentResponse:
    return _to_response(_require_assignment(worker_assignment_id, db))


def create_worker_assignment(data: WorkerAssignmentCreate, db: Session | None = None) -> WorkerAssignmentResponse:
    payload = data.model_dump()
    _validate_links(payload, db)
    _ensure_unique_assignment(payload["worker_id"], payload, db)
    row = worker_assignment_repo.create_worker_assignment(payload, db)
    return _to_response(row)


def update_worker_assignment(
    worker_assignment_id: int,
    data: WorkerAssignmentUpdate,
    db: Session | None = None,
) -> WorkerAssignmentResponse:
    current = _require_assignment(worker_assignment_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_links(payload, db)
    _ensure_unique_assignment(payload["worker_id"], payload, db, exclude_id=worker_assignment_id)
    row = worker_assignment_repo.update_worker_assignment(
        worker_assignment_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Worker assignment {worker_assignment_id} not found")
    return _to_response(row)


def delete_worker_assignment(worker_assignment_id: int, db: Session | None = None) -> dict[str, str]:
    _require_assignment(worker_assignment_id, db)
    worker_assignment_repo.delete_worker_assignment(worker_assignment_id, db)
    return {"message": f"Worker assignment {worker_assignment_id} deleted"}


def list_assignments_by_worker(worker_id: int, db: Session | None = None) -> WorkerAssignmentListResponse:
    if worker_repo.get_worker_by_id(worker_id, db) is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    rows = worker_assignment_repo.list_assignments_by_worker(worker_id, db)
    return WorkerAssignmentListResponse(worker_assignments=[_to_response(row) for row in rows], total=len(rows))


def list_assignments_by_organization_unit(
    organization_unit_id: int,
    db: Session | None = None,
) -> WorkerAssignmentListResponse:
    if organization_unit_repo.get_organization_unit_by_id(organization_unit_id, db) is None:
        raise NotFoundError(f"Organization unit {organization_unit_id} not found")
    rows = worker_assignment_repo.list_assignments_by_organization_unit(organization_unit_id, db)
    return WorkerAssignmentListResponse(worker_assignments=[_to_response(row) for row in rows], total=len(rows))


def list_assignments_by_production_line(
    production_line_id: int,
    db: Session | None = None,
) -> WorkerAssignmentListResponse:
    if production_line_repo.get_production_line_by_id(production_line_id, db) is None:
        raise NotFoundError(f"Production line {production_line_id} not found")
    rows = worker_assignment_repo.list_assignments_by_production_line(production_line_id, db)
    return WorkerAssignmentListResponse(worker_assignments=[_to_response(row) for row in rows], total=len(rows))


def list_assignments_by_production_team(
    production_team_id: int,
    db: Session | None = None,
) -> WorkerAssignmentListResponse:
    if production_team_repo.get_production_team_by_id(production_team_id, db) is None:
        raise NotFoundError(f"Production team {production_team_id} not found")
    rows = worker_assignment_repo.list_assignments_by_production_team(production_team_id, db)
    return WorkerAssignmentListResponse(worker_assignments=[_to_response(row) for row in rows], total=len(rows))
