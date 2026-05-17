"""人员主数据服务。"""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories import organization as organization_repo
from app.repositories import workforce as workforce_repo
from app.schemas.workforce import WorkerCreate, WorkerListResponse, WorkerResponse, WorkerUpdate


def _to_response(row: dict) -> WorkerResponse:
    return WorkerResponse(**row)


def _require_worker(worker_id: int, db: Session | None = None) -> dict:
    row = workforce_repo.get_worker_by_id(worker_id, db)
    if row is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    return row


def list_workers(
    organization_unit_id: int | None = None,
    employment_type: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> WorkerListResponse:
    rows = workforce_repo.list_workers(organization_unit_id, employment_type, status, db)
    return WorkerListResponse(workers=[_to_response(row) for row in rows], total=len(rows))


def get_worker(worker_id: int, db: Session | None = None) -> WorkerResponse:
    return _to_response(_require_worker(worker_id, db))


def create_worker(data: WorkerCreate, db: Session | None = None) -> WorkerResponse:
    if workforce_repo.get_worker_by_code(data.worker_code, db) is not None:
        raise ConflictError(f"Worker code '{data.worker_code}' already exists")
    if (
        data.organization_unit_id is not None
        and organization_repo.get_organization_unit_by_id(data.organization_unit_id, db) is None
    ):
        raise NotFoundError(f"Organization unit {data.organization_unit_id} not found")
    row = workforce_repo.create_worker(data.model_dump(), db)
    return _to_response(row)


def update_worker(worker_id: int, data: WorkerUpdate, db: Session | None = None) -> WorkerResponse:
    current = _require_worker(worker_id, db)
    payload = data.model_dump(exclude_unset=True)
    if "worker_code" in payload and payload["worker_code"] != current["worker_code"]:
        if workforce_repo.get_worker_by_code(payload["worker_code"], db) is not None:
            raise ConflictError(f"Worker code '{payload['worker_code']}' already exists")
    if (
        payload.get("organization_unit_id") is not None
        and organization_repo.get_organization_unit_by_id(payload["organization_unit_id"], db) is None
    ):
        raise NotFoundError(f"Organization unit {payload['organization_unit_id']} not found")
    row = workforce_repo.update_worker(worker_id, payload, db)
    if row is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    return _to_response(row)


def delete_worker(worker_id: int, db: Session | None = None) -> dict[str, str]:
    _require_worker(worker_id, db)
    workforce_repo.delete_worker(worker_id, db)
    return {"message": f"Worker {worker_id} deleted"}
