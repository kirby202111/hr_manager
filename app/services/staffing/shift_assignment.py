"""Service module."""

from datetime import date

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.shopfloor import workstation as workstation_repo
from app.repositories.staffing import shift_assignment as shift_assignment_repo
from app.repositories.staffing import shift_plan as shift_plan_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.staffing import (
    ShiftAssignmentCreate,
    ShiftAssignmentListResponse,
    ShiftAssignmentResponse,
    ShiftAssignmentUpdate,
)
from app.services.qualification import eligibility as eligibility_service


def _to_response(row: dict) -> ShiftAssignmentResponse:
    return ShiftAssignmentResponse(**row)


def _attach_eligibility(row: dict, evaluation: object | None = None) -> ShiftAssignmentResponse:
    payload = dict(row)
    if evaluation is not None:
        payload["eligibility_status"] = evaluation.status
        payload["eligibility_summary_reason"] = evaluation.summary_reason
        payload["eligibility_snapshot_id"] = evaluation.snapshot_id
    return ShiftAssignmentResponse(**payload)


def _require_row(shift_assignment_id: int, db: Session | None = None) -> dict:
    row = shift_assignment_repo.get_shift_assignment_by_id(shift_assignment_id, db)
    if row is None:
        raise NotFoundError(f"Shift assignment {shift_assignment_id} not found")
    return row


def _exists_duplicate(payload: dict, db: Session | None = None, exclude_id: int | None = None) -> bool:
    rows = shift_assignment_repo.list_shift_assignments(
        payload["shift_plan_id"],
        payload["worker_id"],
        payload["workstation_id"],
        None,
        db,
    )
    for row in rows:
        if exclude_id is not None and row["id"] == exclude_id:
            continue
        return True
    return False


def _validate_links(payload: dict, db: Session | None = None) -> None:
    if shift_plan_repo.get_shift_plan_by_id(payload["shift_plan_id"], db) is None:
        raise NotFoundError(f"Shift plan {payload['shift_plan_id']} not found")
    if worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if workstation_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")


def list_shift_assignments(
    shift_plan_id: int | None = None,
    worker_id: int | None = None,
    workstation_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> ShiftAssignmentListResponse:
    rows = shift_assignment_repo.list_shift_assignments(shift_plan_id, worker_id, workstation_id, status, db)
    return ShiftAssignmentListResponse(shift_assignments=[_to_response(row) for row in rows], total=len(rows))


def get_shift_assignment(shift_assignment_id: int, db: Session | None = None) -> ShiftAssignmentResponse:
    return _attach_eligibility(_require_row(shift_assignment_id, db))


def create_shift_assignment(data: ShiftAssignmentCreate, db: Session | None = None) -> ShiftAssignmentResponse:
    payload = data.model_dump()
    _validate_links(payload, db)
    if _exists_duplicate(payload, db):
        raise ConflictError("Shift assignment already exists")
    evaluation = eligibility_service.evaluate_shift_assignment_payload(
        shift_plan_id=payload["shift_plan_id"],
        worker_id=payload["worker_id"],
        workstation_id=payload["workstation_id"],
        assignment_type=payload["assignment_type"],
        assigned_role=payload.get("assigned_role"),
        db=db,
    )
    if evaluation.status == "blocked":
        raise ValidationError(evaluation.summary_reason)
    row = shift_assignment_repo.create_shift_assignment(payload, db)
    if evaluation.snapshot_id is not None:
        eligibility_service.link_snapshot_to_shift_assignment(evaluation.snapshot_id, row["id"], db)
    return _attach_eligibility(row, evaluation)


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
    evaluation = eligibility_service.evaluate_shift_assignment_payload(
        shift_plan_id=payload["shift_plan_id"],
        worker_id=payload["worker_id"],
        workstation_id=payload["workstation_id"],
        assignment_type=payload["assignment_type"],
        assigned_role=payload.get("assigned_role"),
        existing_shift_assignment_id=shift_assignment_id,
        db=db,
    )
    if evaluation.status == "blocked":
        raise ValidationError(evaluation.summary_reason)
    row = shift_assignment_repo.update_shift_assignment(shift_assignment_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Shift assignment {shift_assignment_id} not found")
    if evaluation.snapshot_id is not None:
        eligibility_service.link_snapshot_to_shift_assignment(evaluation.snapshot_id, row["id"], db)
    return _attach_eligibility(row, evaluation)


def delete_shift_assignment(shift_assignment_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(shift_assignment_id, db)
    shift_assignment_repo.delete_shift_assignment(shift_assignment_id, db)
    return {"message": f"Shift assignment {shift_assignment_id} deleted"}


def list_shift_assignments_by_worker_on_work_date(
    worker_id: int,
    work_date: date,
    db: Session | None = None,
) -> ShiftAssignmentListResponse:
    if worker_repo.get_worker_by_id(worker_id, db) is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    rows = shift_assignment_repo.list_shift_assignments_by_worker_on_work_date(worker_id, work_date, db)
    return ShiftAssignmentListResponse(shift_assignments=[_to_response(row) for row in rows], total=len(rows))
