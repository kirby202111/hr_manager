"""人员持证记录服务。"""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories import qualification as qualification_repo
from app.repositories import workforce as workforce_repo
from app.schemas.qualification import (
    WorkerCertificationCreate,
    WorkerCertificationListResponse,
    WorkerCertificationResponse,
    WorkerCertificationUpdate,
)


def _to_response(row: dict) -> WorkerCertificationResponse:
    return WorkerCertificationResponse(**row)


def _require_row(worker_certification_id: int, db: Session | None = None) -> dict:
    row = qualification_repo.get_worker_certification_by_id(worker_certification_id, db)
    if row is None:
        raise NotFoundError(f"Worker certification {worker_certification_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if workforce_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if qualification_repo.get_certification_by_id(payload["certification_id"], db) is None:
        raise NotFoundError(f"Certification {payload['certification_id']} not found")
    if payload.get("expires_at") is not None and payload["issued_at"] > payload["expires_at"]:
        raise ValidationError("issued_at cannot be later than expires_at")


def list_worker_certifications(
    worker_id: int | None = None,
    certification_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> WorkerCertificationListResponse:
    rows = qualification_repo.list_worker_certifications(worker_id, certification_id, status, db)
    return WorkerCertificationListResponse(worker_certifications=[_to_response(row) for row in rows], total=len(rows))


def get_worker_certification(worker_certification_id: int, db: Session | None = None) -> WorkerCertificationResponse:
    return _to_response(_require_row(worker_certification_id, db))


def create_worker_certification(
    data: WorkerCertificationCreate, db: Session | None = None
) -> WorkerCertificationResponse:
    payload = data.model_dump()
    _validate_payload(payload, db)
    if (
        qualification_repo.get_worker_certification_by_worker_and_certification(
            payload["worker_id"], payload["certification_id"], db
        )
        is not None
    ):
        raise ConflictError("Worker certification already exists")
    row = qualification_repo.create_worker_certification(payload, db)
    return _to_response(row)


def update_worker_certification(
    worker_certification_id: int,
    data: WorkerCertificationUpdate,
    db: Session | None = None,
) -> WorkerCertificationResponse:
    current = _require_row(worker_certification_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = qualification_repo.get_worker_certification_by_worker_and_certification(
        payload["worker_id"], payload["certification_id"], db
    )
    if existing is not None and existing["id"] != worker_certification_id:
        raise ConflictError("Worker certification already exists")
    row = qualification_repo.update_worker_certification(
        worker_certification_id, data.model_dump(exclude_unset=True), db
    )
    if row is None:
        raise NotFoundError(f"Worker certification {worker_certification_id} not found")
    return _to_response(row)


def delete_worker_certification(worker_certification_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(worker_certification_id, db)
    qualification_repo.delete_worker_certification(worker_certification_id, db)
    return {"message": f"Worker certification {worker_certification_id} deleted"}
