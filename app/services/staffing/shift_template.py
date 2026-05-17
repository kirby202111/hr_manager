"""班次模板服务。"""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories import staffing as staffing_repo
from app.schemas.staffing import (
    ShiftTemplateCreate,
    ShiftTemplateListResponse,
    ShiftTemplateResponse,
    ShiftTemplateUpdate,
)


def _to_response(row: dict) -> ShiftTemplateResponse:
    return ShiftTemplateResponse(**row)


def _require_row(shift_template_id: int, db: Session | None = None) -> dict:
    row = staffing_repo.get_shift_template_by_id(shift_template_id, db)
    if row is None:
        raise NotFoundError(f"Shift template {shift_template_id} not found")
    return row


def list_shift_templates(
    code: str | None = None,
    shift_type: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> ShiftTemplateListResponse:
    rows = staffing_repo.list_shift_templates(code, shift_type, status, db)
    return ShiftTemplateListResponse(shift_templates=[_to_response(row) for row in rows], total=len(rows))


def get_shift_template(shift_template_id: int, db: Session | None = None) -> ShiftTemplateResponse:
    return _to_response(_require_row(shift_template_id, db))


def create_shift_template(data: ShiftTemplateCreate, db: Session | None = None) -> ShiftTemplateResponse:
    if staffing_repo.get_shift_template_by_code(data.code, db) is not None:
        raise ConflictError(f"Shift template code '{data.code}' already exists")
    row = staffing_repo.create_shift_template(data.model_dump(), db)
    return _to_response(row)


def update_shift_template(
    shift_template_id: int,
    data: ShiftTemplateUpdate,
    db: Session | None = None,
) -> ShiftTemplateResponse:
    current = _require_row(shift_template_id, db)
    payload = data.model_dump(exclude_unset=True)
    if "code" in payload and payload["code"] != current["code"]:
        if staffing_repo.get_shift_template_by_code(payload["code"], db) is not None:
            raise ConflictError(f"Shift template code '{payload['code']}' already exists")
    row = staffing_repo.update_shift_template(shift_template_id, payload, db)
    if row is None:
        raise NotFoundError(f"Shift template {shift_template_id} not found")
    return _to_response(row)


def delete_shift_template(shift_template_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(shift_template_id, db)
    staffing_repo.delete_shift_template(shift_template_id, db)
    return {"message": f"Shift template {shift_template_id} deleted"}
