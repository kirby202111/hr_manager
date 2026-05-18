"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.staffing import shift_template as shift_template_repo
from app.schemas.staffing import (
    ShiftTemplateCreate,
    ShiftTemplateListResponse,
    ShiftTemplateResponse,
    ShiftTemplateUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> ShiftTemplateResponse:
    return ShiftTemplateResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(shift_template_id: int, db: Session | None = None) -> dict:
    row = shift_template_repo.get_shift_template_by_id(shift_template_id, db)
    if row is None:
        raise NotFoundError(f"Shift template {shift_template_id} not found")
    return row


def list_shift_templates(
    code: str | None = None,
    shift_type: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> ShiftTemplateListResponse:
    rows = shift_template_repo.list_shift_templates(code, shift_type, status, db)
    return ShiftTemplateListResponse(shift_templates=[_to_response(row) for row in rows], total=len(rows))


def get_shift_template(shift_template_id: int, db: Session | None = None) -> ShiftTemplateResponse:
    return _to_response(_require_row(shift_template_id, db))


def create_shift_template(data: ShiftTemplateCreate, db: Session | None = None) -> ShiftTemplateResponse:
    if shift_template_repo.get_shift_template_by_code(data.code, db) is not None:
        raise ConflictError(f"Shift template code '{data.code}' already exists")
    row = shift_template_repo.create_shift_template(data.model_dump(), db)
    return _to_response(row)


def update_shift_template(
    shift_template_id: int,
    data: ShiftTemplateUpdate,
    db: Session | None = None,
) -> ShiftTemplateResponse:
    current = _require_row(shift_template_id, db)
    payload = data.model_dump(exclude_unset=True)
    if "code" in payload and payload["code"] != current["code"]:
        if shift_template_repo.get_shift_template_by_code(payload["code"], db) is not None:
            raise ConflictError(f"Shift template code '{payload['code']}' already exists")
    row = shift_template_repo.update_shift_template(shift_template_id, payload, db)
    if row is None:
        raise NotFoundError(f"Shift template {shift_template_id} not found")
    return _to_response(row)


def delete_shift_template(shift_template_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(shift_template_id, db)
    shift_template_repo.delete_shift_template(shift_template_id, db)
    return {"message": f"Shift template {shift_template_id} deleted"}
