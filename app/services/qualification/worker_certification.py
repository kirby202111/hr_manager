"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.qualification import certification as certification_repo
from app.repositories.qualification import worker_certification as worker_certification_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.qualification import (
    WorkerCertificationCreate,
    WorkerCertificationListResponse,
    WorkerCertificationResponse,
    WorkerCertificationUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> WorkerCertificationResponse:
    return WorkerCertificationResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(worker_certification_id: int, db: Session | None = None) -> dict:
    row = worker_certification_repo.get_worker_certification_by_id(worker_certification_id, db)
    if row is None:
        raise NotFoundError(f"Worker certification {worker_certification_id} not found")
    return row


# 校验关联对象与关键业务字段，避免写入非法数据。
def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if certification_repo.get_certification_by_id(payload["certification_id"], db) is None:
        raise NotFoundError(f"Certification {payload['certification_id']} not found")
    if payload.get("expires_at") is not None and payload["issued_at"] > payload["expires_at"]:
        raise ValidationError("issued_at cannot be later than expires_at")


def list_worker_certifications(
    worker_id: int | None = None,
    certification_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> WorkerCertificationListResponse:
    rows = worker_certification_repo.list_worker_certifications(worker_id, certification_id, status, db)
    return WorkerCertificationListResponse(worker_certifications=[_to_response(row) for row in rows], total=len(rows))


def get_worker_certification(worker_certification_id: int, db: Session | None = None) -> WorkerCertificationResponse:
    return _to_response(_require_row(worker_certification_id, db))


def create_worker_certification(
    data: WorkerCertificationCreate, db: Session | None = None
) -> WorkerCertificationResponse:
    payload = data.model_dump()
    _validate_payload(payload, db)
    if (
        worker_certification_repo.get_worker_certification_by_worker_and_certification(
            payload["worker_id"], payload["certification_id"], db
        )
        is not None
    ):
        raise ConflictError("Worker certification already exists")
    row = worker_certification_repo.create_worker_certification(payload, db)
    return _to_response(row)


def update_worker_certification(
    worker_certification_id: int,
    data: WorkerCertificationUpdate,
    db: Session | None = None,
) -> WorkerCertificationResponse:
    current = _require_row(worker_certification_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = worker_certification_repo.get_worker_certification_by_worker_and_certification(
        payload["worker_id"], payload["certification_id"], db
    )
    if existing is not None and existing["id"] != worker_certification_id:
        raise ConflictError("Worker certification already exists")
    row = worker_certification_repo.update_worker_certification(
        worker_certification_id, data.model_dump(exclude_unset=True), db
    )
    if row is None:
        raise NotFoundError(f"Worker certification {worker_certification_id} not found")
    return _to_response(row)


def delete_worker_certification(worker_certification_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(worker_certification_id, db)
    worker_certification_repo.delete_worker_certification(worker_certification_id, db)
    return {"message": f"Worker certification {worker_certification_id} deleted"}
