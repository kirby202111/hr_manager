from datetime import datetime

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import employee as employee_repo
from app.repositories import leave as leave_repo
from app.schemas.leave import (
    LEAVE_BALANCE_DEFAULTS,
    LEAVE_TYPE_NAMES,
    LeaveApproval,
    LeaveBalance,
    LeaveCreate,
    LeaveListResponse,
    LeaveResponse,
    LeaveUpdate,
)


def _fill_employee_name(record: dict, db: Session | None = None) -> dict:
    emp = employee_repo.get_employee_by_id(record["employee_id"], db)
    record["employee_name"] = emp["name"] if emp else "Unknown"
    return record


def _calculate_days(start_date, end_date) -> int:
    return (end_date - start_date).days + 1


def _check_date_overlap(
    employee_id: int,
    start_date,
    end_date,
    exclude_id: int | None = None,
    db: Session | None = None,
):
    approved = leave_repo.get_approved_leaves_in_range(employee_id, start_date, end_date, db)
    if exclude_id is not None:
        approved = [r for r in approved if r["id"] != exclude_id]
    if approved:
        raise ValidationError("Leave dates overlap with an approved leave")


def _check_balance(employee_id: int, leave_type: str, days: int, db: Session | None = None):
    if leave_type not in LEAVE_BALANCE_DEFAULTS:
        return
    used = sum(r["days"] for r in leave_repo.get_approved_leaves_by_type(employee_id, leave_type, db))
    remaining = LEAVE_BALANCE_DEFAULTS[leave_type] - used
    if days > remaining:
        raise ValidationError(f"Insufficient {leave_type} leave balance: {remaining} days remaining")


def create_leave(data: LeaveCreate, db: Session | None = None) -> LeaveResponse:
    emp = employee_repo.get_employee_by_id(data.employee_id, db)
    if emp is None:
        raise NotFoundError(f"Employee {data.employee_id} not found")
    if data.end_date < data.start_date:
        raise ValidationError("end_date must be >= start_date")
    if data.leave_type not in LEAVE_TYPE_NAMES:
        raise ValidationError(f"Invalid leave_type: {data.leave_type}")
    days = _calculate_days(data.start_date, data.end_date)
    _check_date_overlap(data.employee_id, data.start_date, data.end_date, db=db)
    _check_balance(data.employee_id, data.leave_type, days, db)
    leave_data = data.model_dump()
    leave_data["days"] = days
    leave_data["status"] = "pending"
    leave_data["approver"] = None
    leave_data["approved_at"] = None
    leave_data["created_at"] = datetime.now()
    leave_data["leave_type_name"] = LEAVE_TYPE_NAMES[data.leave_type]
    record = leave_repo.create_leave(leave_data, db)
    return LeaveResponse(**_fill_employee_name(record, db))


def list_leaves(
    employee_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> LeaveListResponse:
    records = leave_repo.get_all_leaves(employee_id, status, db)
    return LeaveListResponse(
        leaves=[LeaveResponse(**_fill_employee_name(r, db)) for r in records],
        total=len(records),
    )


def get_leave(leave_id: int, db: Session | None = None) -> LeaveResponse:
    record = leave_repo.get_leave_by_id(leave_id, db)
    if record is None:
        raise NotFoundError(f"Leave {leave_id} not found")
    return LeaveResponse(**_fill_employee_name(record, db))


def update_leave(leave_id: int, data: LeaveUpdate, db: Session | None = None) -> LeaveResponse:
    record = leave_repo.get_leave_by_id(leave_id, db)
    if record is None:
        raise NotFoundError(f"Leave {leave_id} not found")
    if record["status"] != "pending":
        raise ValidationError("Only pending leaves can be updated")
    update_data = data.model_dump(exclude_unset=True)
    start_date = update_data.get("start_date", record["start_date"])
    end_date = update_data.get("end_date", record["end_date"])
    if end_date < start_date:
        raise ValidationError("end_date must be >= start_date")
    update_data["days"] = _calculate_days(start_date, end_date)
    _check_date_overlap(record["employee_id"], start_date, end_date, exclude_id=leave_id, db=db)
    updated = leave_repo.update_leave(leave_id, update_data, db)
    return LeaveResponse(**_fill_employee_name(updated, db))


def approve_leave(leave_id: int, approval: LeaveApproval, db: Session | None = None) -> LeaveResponse:
    record = leave_repo.get_leave_by_id(leave_id, db)
    if record is None:
        raise NotFoundError(f"Leave {leave_id} not found")
    if record["status"] != "pending":
        raise ValidationError("Only pending leaves can be approved")
    _check_date_overlap(record["employee_id"], record["start_date"], record["end_date"], exclude_id=leave_id, db=db)
    _check_balance(record["employee_id"], record["leave_type"], record["days"], db)
    update_data = {
        "status": "approved",
        "approver": approval.approver,
        "approved_at": datetime.now(),
    }
    updated = leave_repo.update_leave(leave_id, update_data, db)
    return LeaveResponse(**_fill_employee_name(updated, db))


def reject_leave(leave_id: int, approval: LeaveApproval, db: Session | None = None) -> LeaveResponse:
    record = leave_repo.get_leave_by_id(leave_id, db)
    if record is None:
        raise NotFoundError(f"Leave {leave_id} not found")
    if record["status"] != "pending":
        raise ValidationError("Only pending leaves can be rejected")
    update_data = {
        "status": "rejected",
        "approver": approval.approver,
        "approved_at": datetime.now(),
    }
    updated = leave_repo.update_leave(leave_id, update_data, db)
    return LeaveResponse(**_fill_employee_name(updated, db))


def cancel_leave(leave_id: int, db: Session | None = None) -> dict:
    record = leave_repo.get_leave_by_id(leave_id, db)
    if record is None:
        raise NotFoundError(f"Leave {leave_id} not found")
    if record["status"] != "pending":
        raise ValidationError("Only pending leaves can be cancelled")
    leave_repo.update_leave(leave_id, {"status": "cancelled"}, db)
    return {"message": f"Leave {leave_id} cancelled"}


def get_leave_balance(employee_id: int, db: Session | None = None) -> LeaveBalance:
    emp = employee_repo.get_employee_by_id(employee_id, db)
    if emp is None:
        raise NotFoundError(f"Employee {employee_id} not found")
    balance = {"employee_id": employee_id, "employee_name": emp["name"]}
    for leave_type, total in LEAVE_BALANCE_DEFAULTS.items():
        used = sum(r["days"] for r in leave_repo.get_approved_leaves_by_type(employee_id, leave_type, db))
        balance[f"{leave_type}_total"] = total
        balance[f"{leave_type}_used"] = used
        balance[f"{leave_type}_remaining"] = total - used
    return LeaveBalance(**balance)
