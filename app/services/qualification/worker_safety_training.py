"""人员安全培训完成记录服务。"""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories import qualification as qualification_repo
from app.repositories import workforce as workforce_repo
from app.schemas.qualification import (
    WorkerSafetyTrainingCreate,
    WorkerSafetyTrainingListResponse,
    WorkerSafetyTrainingResponse,
    WorkerSafetyTrainingUpdate,
)


def _to_response(row: dict) -> WorkerSafetyTrainingResponse:
    return WorkerSafetyTrainingResponse(**row)


def _require_row(worker_safety_training_id: int, db: Session | None = None) -> dict:
    row = qualification_repo.get_worker_safety_training_by_id(worker_safety_training_id, db)
    if row is None:
        raise NotFoundError(f"Worker safety training {worker_safety_training_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if workforce_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if qualification_repo.get_safety_training_by_id(payload["safety_training_id"], db) is None:
        raise NotFoundError(f"Safety training {payload['safety_training_id']} not found")
    if payload.get("expires_at") is not None and payload["completed_at"] > payload["expires_at"]:
        raise ValidationError("completed_at cannot be later than expires_at")


def list_worker_safety_trainings(
    worker_id: int | None = None,
    safety_training_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> WorkerSafetyTrainingListResponse:
    rows = qualification_repo.list_worker_safety_trainings(worker_id, safety_training_id, status, db)
    return WorkerSafetyTrainingListResponse(
        worker_safety_trainings=[_to_response(row) for row in rows], total=len(rows)
    )


def get_worker_safety_training(
    worker_safety_training_id: int, db: Session | None = None
) -> WorkerSafetyTrainingResponse:
    return _to_response(_require_row(worker_safety_training_id, db))


def create_worker_safety_training(
    data: WorkerSafetyTrainingCreate, db: Session | None = None
) -> WorkerSafetyTrainingResponse:
    payload = data.model_dump()
    _validate_payload(payload, db)
    if (
        qualification_repo.get_worker_safety_training_by_worker_and_training(
            payload["worker_id"], payload["safety_training_id"], db
        )
        is not None
    ):
        raise ConflictError("Worker safety training already exists")
    row = qualification_repo.create_worker_safety_training(payload, db)
    return _to_response(row)


def update_worker_safety_training(
    worker_safety_training_id: int,
    data: WorkerSafetyTrainingUpdate,
    db: Session | None = None,
) -> WorkerSafetyTrainingResponse:
    current = _require_row(worker_safety_training_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = qualification_repo.get_worker_safety_training_by_worker_and_training(
        payload["worker_id"], payload["safety_training_id"], db
    )
    if existing is not None and existing["id"] != worker_safety_training_id:
        raise ConflictError("Worker safety training already exists")
    row = qualification_repo.update_worker_safety_training(
        worker_safety_training_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Worker safety training {worker_safety_training_id} not found")
    return _to_response(row)


def delete_worker_safety_training(worker_safety_training_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(worker_safety_training_id, db)
    qualification_repo.delete_worker_safety_training(worker_safety_training_id, db)
    return {"message": f"Worker safety training {worker_safety_training_id} deleted"}
