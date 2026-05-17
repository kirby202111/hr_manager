"""排班计划服务。"""

from datetime import date

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories import shopfloor as shopfloor_repo
from app.repositories import staffing as staffing_repo
from app.schemas.staffing import ShiftPlanCreate, ShiftPlanListResponse, ShiftPlanResponse, ShiftPlanUpdate


def _to_response(row: dict) -> ShiftPlanResponse:
    return ShiftPlanResponse(**row)


def _require_row(shift_plan_id: int, db: Session | None = None) -> dict:
    row = staffing_repo.get_shift_plan_by_id(shift_plan_id, db)
    if row is None:
        raise NotFoundError(f"Shift plan {shift_plan_id} not found")
    return row


def _exists_duplicate(payload: dict, db: Session | None = None, exclude_id: int | None = None) -> bool:
    rows = staffing_repo.list_shift_plans(
        payload["production_line_id"],
        payload["shift_template_id"],
        payload["work_date"],
        None,
        None,
        db,
    )
    for row in rows:
        if exclude_id is not None and row["id"] == exclude_id:
            continue
        return True
    return False


def list_shift_plans(
    production_line_id: int | None = None,
    shift_template_id: int | None = None,
    work_date: date | None = None,
    status: str | None = None,
    production_order_id: int | None = None,
    db: Session | None = None,
) -> ShiftPlanListResponse:
    rows = staffing_repo.list_shift_plans(
        production_line_id, shift_template_id, work_date, status, production_order_id, db
    )
    return ShiftPlanListResponse(shift_plans=[_to_response(row) for row in rows], total=len(rows))


def get_shift_plan(shift_plan_id: int, db: Session | None = None) -> ShiftPlanResponse:
    return _to_response(_require_row(shift_plan_id, db))


def create_shift_plan(data: ShiftPlanCreate, db: Session | None = None) -> ShiftPlanResponse:
    if shopfloor_repo.get_production_line_by_id(data.production_line_id, db) is None:
        raise NotFoundError(f"Production line {data.production_line_id} not found")
    if staffing_repo.get_shift_template_by_id(data.shift_template_id, db) is None:
        raise NotFoundError(f"Shift template {data.shift_template_id} not found")
    if (
        data.production_order_id is not None
        and shopfloor_repo.get_production_order_by_id(data.production_order_id, db) is None
    ):
        raise NotFoundError(f"Production order {data.production_order_id} not found")
    if _exists_duplicate(data.model_dump(), db):
        raise ConflictError("Shift plan already exists for line, date, and template")
    row = staffing_repo.create_shift_plan(data.model_dump(), db)
    return _to_response(row)


def update_shift_plan(shift_plan_id: int, data: ShiftPlanUpdate, db: Session | None = None) -> ShiftPlanResponse:
    current = _require_row(shift_plan_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if shopfloor_repo.get_production_line_by_id(payload["production_line_id"], db) is None:
        raise NotFoundError(f"Production line {payload['production_line_id']} not found")
    if staffing_repo.get_shift_template_by_id(payload["shift_template_id"], db) is None:
        raise NotFoundError(f"Shift template {payload['shift_template_id']} not found")
    if (
        payload.get("production_order_id") is not None
        and shopfloor_repo.get_production_order_by_id(payload["production_order_id"], db) is None
    ):
        raise NotFoundError(f"Production order {payload['production_order_id']} not found")
    if _exists_duplicate(payload, db, exclude_id=shift_plan_id):
        raise ConflictError("Shift plan already exists for line, date, and template")
    row = staffing_repo.update_shift_plan(shift_plan_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Shift plan {shift_plan_id} not found")
    return _to_response(row)


def delete_shift_plan(shift_plan_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(shift_plan_id, db)
    staffing_repo.delete_shift_plan(shift_plan_id, db)
    return {"message": f"Shift plan {shift_plan_id} deleted"}
