from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.leave import LeaveApproval, LeaveBalance, LeaveCreate, LeaveListResponse, LeaveResponse, LeaveUpdate
from app.services import leave as leave_service

router = APIRouter(prefix="/leaves", tags=["请假管理"])


@router.post("/", response_model=LeaveResponse, status_code=201)
def create_leave(data: LeaveCreate, db: Session = Depends(get_db)):
    return leave_service.create_leave(data, db)


@router.get("/", response_model=LeaveListResponse)
def list_leaves(worker_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    return leave_service.list_leaves(worker_id, status, db)


@router.get("/worker/{worker_id}/balance", response_model=LeaveBalance)
def get_leave_balance(worker_id: int, db: Session = Depends(get_db)):
    return leave_service.get_leave_balance(worker_id, db)


@router.get("/{leave_id}", response_model=LeaveResponse)
def get_leave(leave_id: int, db: Session = Depends(get_db)):
    return leave_service.get_leave(leave_id, db)


@router.put("/{leave_id}", response_model=LeaveResponse)
def update_leave(leave_id: int, data: LeaveUpdate, db: Session = Depends(get_db)):
    return leave_service.update_leave(leave_id, data, db)


@router.put("/{leave_id}/approve", response_model=LeaveResponse)
def approve_leave(leave_id: int, approval: LeaveApproval, db: Session = Depends(get_db)):
    return leave_service.approve_leave(leave_id, approval, db)


@router.put("/{leave_id}/reject", response_model=LeaveResponse)
def reject_leave(leave_id: int, approval: LeaveApproval, db: Session = Depends(get_db)):
    return leave_service.reject_leave(leave_id, approval, db)


@router.delete("/{leave_id}")
def cancel_leave(leave_id: int, db: Session = Depends(get_db)):
    return leave_service.cancel_leave(leave_id, db)
