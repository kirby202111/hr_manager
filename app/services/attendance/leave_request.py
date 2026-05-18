"""Service module."""

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories.attendance import leave_request as leave_request_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.attendance import (
    LeaveRequestCreate,
    LeaveRequestListResponse,
    LeaveRequestResponse,
    LeaveRequestUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> LeaveRequestResponse:
    return LeaveRequestResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(leave_request_id: int, db: Session | None = None) -> dict:
    row = leave_request_repo.get_leave_request_by_id(leave_request_id, db)
    if row is None:
        raise NotFoundError(f"Leave request {leave_request_id} not found")
    return row


# 校验关联对象与关键业务字段，避免写入非法数据。
def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if payload["start_date"] > payload["end_date"]:
        raise ValidationError("start_date cannot be later than end_date")


def list_leave_requests(
    worker_id: int | None = None,
    status: str | None = None,
    leave_type: str | None = None,
    start_date=None,
    end_date=None,
    db: Session | None = None,
) -> LeaveRequestListResponse:
    rows = leave_request_repo.list_leave_requests(worker_id, status, leave_type, start_date, end_date, db)
    return LeaveRequestListResponse(leave_requests=[_to_response(row) for row in rows], total=len(rows))


def get_leave_request(leave_request_id: int, db: Session | None = None) -> LeaveRequestResponse:
    return _to_response(_require_row(leave_request_id, db))


def create_leave_request(data: LeaveRequestCreate, db: Session | None = None) -> LeaveRequestResponse:
    payload = data.model_dump()
    _validate_payload(payload, db)
    row = leave_request_repo.create_leave_request(payload, db)
    return _to_response(row)


def update_leave_request(
    leave_request_id: int, data: LeaveRequestUpdate, db: Session | None = None
) -> LeaveRequestResponse:
    current = _require_row(leave_request_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    row = leave_request_repo.update_leave_request(leave_request_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Leave request {leave_request_id} not found")
    return _to_response(row)


def delete_leave_request(leave_request_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(leave_request_id, db)
    leave_request_repo.delete_leave_request(leave_request_id, db)
    return {"message": f"Leave request {leave_request_id} deleted"}
