"""排班分配服务。"""

from datetime import date

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories import shopfloor as shopfloor_repo
from app.repositories import staffing as staffing_repo
from app.repositories import workforce as workforce_repo
from app.schemas.staffing import (
    ShiftAssignmentCreate,
    ShiftAssignmentListResponse,
    ShiftAssignmentResponse,
    ShiftAssignmentUpdate,
)


def _to_response(row: dict) -> ShiftAssignmentResponse:
    return ShiftAssignmentResponse(**row)


def _require_row(shift_assignment_id: int, db: Session | None = None) -> dict:
    row = staffing_repo.get_shift_assignment_by_id(shift_assignment_id, db)
    if row is None:
        raise NotFoundError(f"Shift assignment {shift_assignment_id} not found")
    return row


def _exists_duplicate(payload: dict, db: Session | None = None, exclude_id: int | None = None) -> bool:
    rows = staffing_repo.list_shift_assignments(
        payload["shift_plan_id"], payload["worker_id"], payload["workstation_id"], None, db
    )
    for row in rows:
        if exclude_id is not None and row["id"] == exclude_id:
            continue
        return True
    return False


def _validate_links(payload: dict, db: Session | None = None) -> None:
    if staffing_repo.get_shift_plan_by_id(payload["shift_plan_id"], db) is None:
        raise NotFoundError(f"Shift plan {payload['shift_plan_id']} not found")
    if workforce_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if shopfloor_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")


def list_shift_assignments(
    shift_plan_id: int | None = None,
    worker_id: int | None = None,
    workstation_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> ShiftAssignmentListResponse:
    rows = staffing_repo.list_shift_assignments(shift_plan_id, worker_id, workstation_id, status, db)
    return ShiftAssignmentListResponse(shift_assignments=[_to_response(row) for row in rows], total=len(rows))


def get_shift_assignment(shift_assignment_id: int, db: Session | None = None) -> ShiftAssignmentResponse:
    return _to_response(_require_row(shift_assignment_id, db))


def create_shift_assignment(data: ShiftAssignmentCreate, db: Session | None = None) -> ShiftAssignmentResponse:
    payload = data.model_dump()
    _validate_links(payload, db)
    if _exists_duplicate(payload, db):
        raise ConflictError("Shift assignment already exists")
    row = staffing_repo.create_shift_assignment(payload, db)
    return _to_response(row)


def update_shift_assignment(
    shift_assignment_id: int,
    data: ShiftAssignmentUpdate,
    db: Session | None = None,
) -> ShiftAssignmentResponse:
    current = _require_row(shift_assignment_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_links(payload, db)
    if _exists_duplicate(payload, db, exclude_id=shift_assignment_id):
        raise ConflictError("Shift assignment already exists")
    row = staffing_repo.update_shift_assignment(shift_assignment_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Shift assignment {shift_assignment_id} not found")
    return _to_response(row)


def delete_shift_assignment(shift_assignment_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(shift_assignment_id, db)
    staffing_repo.delete_shift_assignment(shift_assignment_id, db)
    return {"message": f"Shift assignment {shift_assignment_id} deleted"}


def list_shift_assignments_by_worker_on_work_date(
    worker_id: int,
    work_date: date,
    db: Session | None = None,
) -> ShiftAssignmentListResponse:
    if workforce_repo.get_worker_by_id(worker_id, db) is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    rows = staffing_repo.list_shift_assignments_by_worker_on_work_date(worker_id, work_date, db)
    return ShiftAssignmentListResponse(shift_assignments=[_to_response(row) for row in rows], total=len(rows))
