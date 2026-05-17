"""考勤记录路由。"""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attendance import (
    AttendanceRecordCreate,
    AttendanceRecordListResponse,
    AttendanceRecordResponse,
    AttendanceRecordUpdate,
)
from app.services.attendance import attendance_record as service

router = APIRouter(prefix="/attendance-records", tags=["attendance records"])


@router.get("/", response_model=AttendanceRecordListResponse)
def list_attendance_records(
    worker_id: int | None = None,
    work_date: date | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_attendance_records(worker_id, work_date, status, db)


@router.get("/{attendance_record_id}", response_model=AttendanceRecordResponse)
def get_attendance_record(attendance_record_id: int, db: Session = Depends(get_db)):
    return service.get_attendance_record(attendance_record_id, db)


@router.post("/", response_model=AttendanceRecordResponse, status_code=201)
def create_attendance_record(data: AttendanceRecordCreate, db: Session = Depends(get_db)):
    return service.create_attendance_record(data, db)


@router.put("/{attendance_record_id}", response_model=AttendanceRecordResponse)
def update_attendance_record(
    attendance_record_id: int,
    data: AttendanceRecordUpdate,
    db: Session = Depends(get_db),
):
    return service.update_attendance_record(attendance_record_id, data, db)


@router.delete("/{attendance_record_id}")
def delete_attendance_record(attendance_record_id: int, db: Session = Depends(get_db)):
    return service.delete_attendance_record(attendance_record_id, db)
