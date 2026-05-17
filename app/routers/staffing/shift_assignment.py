"""排班分配路由。"""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.staffing import (
    ShiftAssignmentCreate,
    ShiftAssignmentListResponse,
    ShiftAssignmentResponse,
    ShiftAssignmentUpdate,
)
from app.services.staffing import shift_assignment as service

router = APIRouter(prefix="/shift-assignments", tags=["shift assignments"])


@router.get("/", response_model=ShiftAssignmentListResponse)
def list_shift_assignments(
    shift_plan_id: int | None = None,
    worker_id: int | None = None,
    workstation_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_shift_assignments(shift_plan_id, worker_id, workstation_id, status, db)


@router.get("/worker/{worker_id}/work-date/{work_date}", response_model=ShiftAssignmentListResponse)
def list_by_worker_on_work_date(worker_id: int, work_date: date, db: Session = Depends(get_db)):
    return service.list_shift_assignments_by_worker_on_work_date(worker_id, work_date, db)


@router.get("/{shift_assignment_id}", response_model=ShiftAssignmentResponse)
def get_shift_assignment(shift_assignment_id: int, db: Session = Depends(get_db)):
    return service.get_shift_assignment(shift_assignment_id, db)


@router.post("/", response_model=ShiftAssignmentResponse, status_code=201)
def create_shift_assignment(data: ShiftAssignmentCreate, db: Session = Depends(get_db)):
    return service.create_shift_assignment(data, db)


@router.put("/{shift_assignment_id}", response_model=ShiftAssignmentResponse)
def update_shift_assignment(
    shift_assignment_id: int,
    data: ShiftAssignmentUpdate,
    db: Session = Depends(get_db),
):
    return service.update_shift_assignment(shift_assignment_id, data, db)


@router.delete("/{shift_assignment_id}")
def delete_shift_assignment(shift_assignment_id: int, db: Session = Depends(get_db)):
    return service.delete_shift_assignment(shift_assignment_id, db)
