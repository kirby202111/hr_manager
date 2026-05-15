from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attendance import (
    AttendanceCheckIn,
    AttendanceCheckOut,
    AttendanceListResponse,
    AttendanceResponse,
    AttendanceStats,
)
from app.services import attendance as attendance_service

router = APIRouter(prefix="/attendance", tags=["考勤管理"])


@router.post("/check-in", response_model=AttendanceResponse, status_code=201)
def check_in(data: AttendanceCheckIn, db: Session = Depends(get_db)):
    return attendance_service.check_in(data, db)


@router.put("/check-out/{record_id}", response_model=AttendanceResponse)
def check_out(record_id: int, data: AttendanceCheckOut, db: Session = Depends(get_db)):
    return attendance_service.check_out(record_id, data, db)


@router.get("/", response_model=AttendanceListResponse)
def list_attendance(
    employee_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    return attendance_service.list_attendance(employee_id, start_date, end_date, db)


@router.get("/employee/{employee_id}/stats", response_model=AttendanceStats)
def get_employee_stats(
    employee_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    return attendance_service.get_employee_stats(employee_id, start_date, end_date, db)


@router.get("/employee/{employee_id}", response_model=list[AttendanceResponse])
def get_employee_attendance(employee_id: int, db: Session = Depends(get_db)):
    return attendance_service.get_employee_attendance(employee_id, db)


@router.get("/{record_id}", response_model=AttendanceResponse)
def get_attendance(record_id: int, db: Session = Depends(get_db)):
    return attendance_service.get_attendance(record_id, db)
