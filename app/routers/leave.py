from fastapi import APIRouter

from app.schemas.leave import (
    LeaveCreate, LeaveUpdate, LeaveApproval,
    LeaveResponse, LeaveListResponse, LeaveBalance,
)
from app.services import leave as leave_service

router = APIRouter(prefix="/leaves", tags=["请假管理"])


@router.post("/", response_model=LeaveResponse, status_code=201)
def create_leave(data: LeaveCreate):
    return leave_service.create_leave(data)


@router.get("/", response_model=LeaveListResponse)
def list_leaves(
    employee_id: int | None = None,
    status: str | None = None,
):
    return leave_service.list_leaves(employee_id, status)


@router.get("/{leave_id}", response_model=LeaveResponse)
def get_leave(leave_id: int):
    return leave_service.get_leave(leave_id)


@router.put("/{leave_id}", response_model=LeaveResponse)
def update_leave(leave_id: int, data: LeaveUpdate):
    return leave_service.update_leave(leave_id, data)


@router.put("/{leave_id}/approve", response_model=LeaveResponse)
def approve_leave(leave_id: int, approval: LeaveApproval):
    return leave_service.approve_leave(leave_id, approval)


@router.put("/{leave_id}/reject", response_model=LeaveResponse)
def reject_leave(leave_id: int, approval: LeaveApproval):
    return leave_service.reject_leave(leave_id, approval)


@router.delete("/{leave_id}")
def cancel_leave(leave_id: int):
    return leave_service.cancel_leave(leave_id)


@router.get("/employee/{employee_id}/balance", response_model=LeaveBalance)
def get_leave_balance(employee_id: int):
    return leave_service.get_leave_balance(employee_id)
