from datetime import datetime

from fastapi import HTTPException

from app.repositories import employee as employee_repo
from app.repositories import leave as leave_repo
from app.schemas.leave import (
    LeaveCreate, LeaveUpdate, LeaveApproval, LeaveResponse,
    LeaveListResponse, LeaveBalance, LEAVE_TYPE_NAMES, LEAVE_BALANCE_DEFAULTS,
)


def _fill_employee_name(record: dict) -> dict:
    emp = employee_repo.get_employee_by_id(record["employee_id"])
    record["employee_name"] = emp["name"] if emp else "Unknown"
    return record


def _calculate_days(start_date, end_date) -> int:
    return (end_date - start_date).days + 1


def _check_date_overlap(employee_id: int, start_date, end_date, exclude_id: int | None = None):
    approved = leave_repo.get_approved_leaves_in_range(employee_id, start_date, end_date)
    if exclude_id is not None:
        approved = [r for r in approved if r["id"] != exclude_id]
    if approved:
        raise HTTPException(status_code=400, detail="Leave dates overlap with an approved leave")


def _check_balance(employee_id: int, leave_type: str, days: int):
    if leave_type not in LEAVE_BALANCE_DEFAULTS:
        return
    used = sum(r["days"] for r in leave_repo.get_approved_leaves_by_type(employee_id, leave_type))
    remaining = LEAVE_BALANCE_DEFAULTS[leave_type] - used
    if days > remaining:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient {leave_type} leave balance: {remaining} days remaining",
        )


def create_leave(data: LeaveCreate) -> LeaveResponse:
    emp = employee_repo.get_employee_by_id(data.employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {data.employee_id} not found")
    if data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")
    if data.leave_type not in LEAVE_TYPE_NAMES:
        raise HTTPException(status_code=400, detail=f"Invalid leave_type: {data.leave_type}")
    days = _calculate_days(data.start_date, data.end_date)
    _check_date_overlap(data.employee_id, data.start_date, data.end_date)
    _check_balance(data.employee_id, data.leave_type, days)
    leave_data = data.model_dump()
    leave_data["days"] = days
    leave_data["status"] = "pending"
    leave_data["approver"] = None
    leave_data["approved_at"] = None
    leave_data["created_at"] = datetime.now()
    leave_data["leave_type_name"] = LEAVE_TYPE_NAMES[data.leave_type]
    record = leave_repo.create_leave(leave_data)
    return LeaveResponse(**_fill_employee_name(record))


def list_leaves(employee_id: int | None = None, status: str | None = None) -> LeaveListResponse:
    records = leave_repo.get_all_leaves(employee_id, status)
    return LeaveListResponse(
        leaves=[LeaveResponse(**_fill_employee_name(r)) for r in records],
        total=len(records),
    )


def get_leave(leave_id: int) -> LeaveResponse:
    record = leave_repo.get_leave_by_id(leave_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Leave {leave_id} not found")
    return LeaveResponse(**_fill_employee_name(record))


def update_leave(leave_id: int, data: LeaveUpdate) -> LeaveResponse:
    record = leave_repo.get_leave_by_id(leave_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Leave {leave_id} not found")
    if record["status"] != "pending":
        raise HTTPException(status_code=400, detail="Only pending leaves can be updated")
    update_data = data.model_dump(exclude_unset=True)
    start_date = update_data.get("start_date", record["start_date"])
    end_date = update_data.get("end_date", record["end_date"])
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")
    update_data["days"] = _calculate_days(start_date, end_date)
    _check_date_overlap(record["employee_id"], start_date, end_date, exclude_id=leave_id)
    updated = leave_repo.update_leave(leave_id, update_data)
    return LeaveResponse(**_fill_employee_name(updated))


def approve_leave(leave_id: int, approval: LeaveApproval) -> LeaveResponse:
    record = leave_repo.get_leave_by_id(leave_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Leave {leave_id} not found")
    if record["status"] != "pending":
        raise HTTPException(status_code=400, detail="Only pending leaves can be approved")
    _check_date_overlap(record["employee_id"], record["start_date"], record["end_date"], exclude_id=leave_id)
    _check_balance(record["employee_id"], record["leave_type"], record["days"])
    update_data = {
        "status": "approved",
        "approver": approval.approver,
        "approved_at": datetime.now(),
    }
    updated = leave_repo.update_leave(leave_id, update_data)
    return LeaveResponse(**_fill_employee_name(updated))


def reject_leave(leave_id: int, approval: LeaveApproval) -> LeaveResponse:
    record = leave_repo.get_leave_by_id(leave_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Leave {leave_id} not found")
    if record["status"] != "pending":
        raise HTTPException(status_code=400, detail="Only pending leaves can be rejected")
    update_data = {
        "status": "rejected",
        "approver": approval.approver,
        "approved_at": datetime.now(),
    }
    updated = leave_repo.update_leave(leave_id, update_data)
    return LeaveResponse(**_fill_employee_name(updated))


def cancel_leave(leave_id: int) -> dict:
    record = leave_repo.get_leave_by_id(leave_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Leave {leave_id} not found")
    if record["status"] != "pending":
        raise HTTPException(status_code=400, detail="Only pending leaves can be cancelled")
    leave_repo.update_leave(leave_id, {"status": "cancelled"})
    return {"message": f"Leave {leave_id} cancelled"}


def get_leave_balance(employee_id: int) -> LeaveBalance:
    emp = employee_repo.get_employee_by_id(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    balance = {"employee_id": employee_id, "employee_name": emp["name"]}
    for leave_type, total in LEAVE_BALANCE_DEFAULTS.items():
        used = sum(r["days"] for r in leave_repo.get_approved_leaves_by_type(employee_id, leave_type))
        balance[f"{leave_type}_total"] = total
        balance[f"{leave_type}_used"] = used
        balance[f"{leave_type}_remaining"] = total - used
    return LeaveBalance(**balance)
