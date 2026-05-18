"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.qualification import equipment_authorization as equipment_authorization_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.qualification import (
    EquipmentAuthorizationCreate,
    EquipmentAuthorizationListResponse,
    EquipmentAuthorizationResponse,
    EquipmentAuthorizationUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> EquipmentAuthorizationResponse:
    return EquipmentAuthorizationResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(equipment_authorization_id: int, db: Session | None = None) -> dict:
    row = equipment_authorization_repo.get_equipment_authorization_by_id(equipment_authorization_id, db)
    if row is None:
        raise NotFoundError(f"Equipment authorization {equipment_authorization_id} not found")
    return row


# 校验关联对象与关键业务字段，避免写入非法数据。
def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if payload.get("expires_at") is not None and payload["issued_at"] > payload["expires_at"]:
        raise ValidationError("issued_at cannot be later than expires_at")


def list_equipment_authorizations(
    worker_id: int | None = None,
    equipment_code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> EquipmentAuthorizationListResponse:
    rows = equipment_authorization_repo.list_equipment_authorizations(worker_id, equipment_code, status, db)
    return EquipmentAuthorizationListResponse(
        equipment_authorizations=[_to_response(row) for row in rows], total=len(rows)
    )


def get_equipment_authorization(
    equipment_authorization_id: int, db: Session | None = None
) -> EquipmentAuthorizationResponse:
    return _to_response(_require_row(equipment_authorization_id, db))


def create_equipment_authorization(
    data: EquipmentAuthorizationCreate,
    db: Session | None = None,
) -> EquipmentAuthorizationResponse:
    payload = data.model_dump()
    _validate_payload(payload, db)
    if (
        equipment_authorization_repo.get_equipment_authorization_by_worker_and_equipment(
            payload["worker_id"], payload["equipment_code"], db
        )
        is not None
    ):
        raise ConflictError("Equipment authorization already exists")
    row = equipment_authorization_repo.create_equipment_authorization(payload, db)
    return _to_response(row)


def update_equipment_authorization(
    equipment_authorization_id: int,
    data: EquipmentAuthorizationUpdate,
    db: Session | None = None,
) -> EquipmentAuthorizationResponse:
    current = _require_row(equipment_authorization_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = equipment_authorization_repo.get_equipment_authorization_by_worker_and_equipment(
        payload["worker_id"], payload["equipment_code"], db
    )
    if existing is not None and existing["id"] != equipment_authorization_id:
        raise ConflictError("Equipment authorization already exists")
    row = equipment_authorization_repo.update_equipment_authorization(
        equipment_authorization_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Equipment authorization {equipment_authorization_id} not found")
    return _to_response(row)


def delete_equipment_authorization(equipment_authorization_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(equipment_authorization_id, db)
    equipment_authorization_repo.delete_equipment_authorization(equipment_authorization_id, db)
    return {"message": f"Equipment authorization {equipment_authorization_id} deleted"}
