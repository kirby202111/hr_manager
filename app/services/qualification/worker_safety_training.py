"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.qualification import safety_training as safety_training_repo
from app.repositories.qualification import worker_safety_training as worker_safety_training_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.qualification import (
    WorkerSafetyTrainingCreate,
    WorkerSafetyTrainingListResponse,
    WorkerSafetyTrainingResponse,
    WorkerSafetyTrainingUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> WorkerSafetyTrainingResponse:
    return WorkerSafetyTrainingResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(worker_safety_training_id: int, db: Session | None = None) -> dict:
    row = worker_safety_training_repo.get_worker_safety_training_by_id(worker_safety_training_id, db)
    if row is None:
        raise NotFoundError(f"Worker safety training {worker_safety_training_id} not found")
    return row


# 校验关联对象与关键业务字段，避免写入非法数据。
def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if safety_training_repo.get_safety_training_by_id(payload["safety_training_id"], db) is None:
        raise NotFoundError(f"Safety training {payload['safety_training_id']} not found")
    if payload.get("expires_at") is not None and payload["completed_at"] > payload["expires_at"]:
        raise ValidationError("completed_at cannot be later than expires_at")


def list_worker_safety_trainings(
    worker_id: int | None = None,
    safety_training_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> WorkerSafetyTrainingListResponse:
    rows = worker_safety_training_repo.list_worker_safety_trainings(worker_id, safety_training_id, status, db)
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
        worker_safety_training_repo.get_worker_safety_training_by_worker_and_training(
            payload["worker_id"], payload["safety_training_id"], db
        )
        is not None
    ):
        raise ConflictError("Worker safety training already exists")
    row = worker_safety_training_repo.create_worker_safety_training(payload, db)
    return _to_response(row)


def update_worker_safety_training(
    worker_safety_training_id: int,
    data: WorkerSafetyTrainingUpdate,
    db: Session | None = None,
) -> WorkerSafetyTrainingResponse:
    current = _require_row(worker_safety_training_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = worker_safety_training_repo.get_worker_safety_training_by_worker_and_training(
        payload["worker_id"], payload["safety_training_id"], db
    )
    if existing is not None and existing["id"] != worker_safety_training_id:
        raise ConflictError("Worker safety training already exists")
    row = worker_safety_training_repo.update_worker_safety_training(
        worker_safety_training_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Worker safety training {worker_safety_training_id} not found")
    return _to_response(row)


def delete_worker_safety_training(worker_safety_training_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(worker_safety_training_id, db)
    worker_safety_training_repo.delete_worker_safety_training(worker_safety_training_id, db)
    return {"message": f"Worker safety training {worker_safety_training_id} deleted"}
