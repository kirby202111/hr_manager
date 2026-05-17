"""薪资记录路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attendance import (
    PayrollRecordCreate,
    PayrollRecordListResponse,
    PayrollRecordResponse,
    PayrollRecordUpdate,
)
from app.services.attendance import payroll_record as service

router = APIRouter(prefix="/payroll-records", tags=["payroll records"])


@router.get("/", response_model=PayrollRecordListResponse)
def list_payroll_records(
    worker_id: int | None = None,
    pay_period: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_payroll_records(worker_id, pay_period, status, db)


@router.get("/{payroll_record_id}", response_model=PayrollRecordResponse)
def get_payroll_record(payroll_record_id: int, db: Session = Depends(get_db)):
    return service.get_payroll_record(payroll_record_id, db)


@router.post("/", response_model=PayrollRecordResponse, status_code=201)
def create_payroll_record(data: PayrollRecordCreate, db: Session = Depends(get_db)):
    return service.create_payroll_record(data, db)


@router.put("/{payroll_record_id}", response_model=PayrollRecordResponse)
def update_payroll_record(
    payroll_record_id: int,
    data: PayrollRecordUpdate,
    db: Session = Depends(get_db),
):
    return service.update_payroll_record(payroll_record_id, data, db)


@router.delete("/{payroll_record_id}")
def delete_payroll_record(payroll_record_id: int, db: Session = Depends(get_db)):
    return service.delete_payroll_record(payroll_record_id, db)
