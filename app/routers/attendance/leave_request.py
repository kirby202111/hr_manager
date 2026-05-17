"""请假申请路由。"""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attendance import (
    LeaveRequestCreate,
    LeaveRequestListResponse,
    LeaveRequestResponse,
    LeaveRequestUpdate,
)
from app.services.attendance import leave_request as service

router = APIRouter(prefix="/leave-requests", tags=["leave requests"])


@router.get("/", response_model=LeaveRequestListResponse)
def list_leave_requests(
    worker_id: int | None = None,
    status: str | None = None,
    leave_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    return service.list_leave_requests(worker_id, status, leave_type, start_date, end_date, db)


@router.get("/{leave_request_id}", response_model=LeaveRequestResponse)
def get_leave_request(leave_request_id: int, db: Session = Depends(get_db)):
    return service.get_leave_request(leave_request_id, db)


@router.post("/", response_model=LeaveRequestResponse, status_code=201)
def create_leave_request(data: LeaveRequestCreate, db: Session = Depends(get_db)):
    return service.create_leave_request(data, db)


@router.put("/{leave_request_id}", response_model=LeaveRequestResponse)
def update_leave_request(
    leave_request_id: int,
    data: LeaveRequestUpdate,
    db: Session = Depends(get_db),
):
    return service.update_leave_request(leave_request_id, data, db)


@router.delete("/{leave_request_id}")
def delete_leave_request(leave_request_id: int, db: Session = Depends(get_db)):
    return service.delete_leave_request(leave_request_id, db)
