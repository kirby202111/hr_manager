from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.payroll import (
    PayrollCreate,
    PayrollListResponse,
    PayrollResponse,
    PayrollUpdate,
    PayslipDetail,
)
from app.services import payroll as payroll_service

router = APIRouter(prefix="/payroll", tags=["薪资管理"])


@router.post("/", response_model=PayrollResponse, status_code=201)
def create_payroll(data: PayrollCreate, db: Session = Depends(get_db)):
    return payroll_service.create_payroll(data, db)


@router.post("/generate/{month}", response_model=list[PayrollResponse], status_code=201)
def generate_monthly_payroll(month: str, db: Session = Depends(get_db)):
    return payroll_service.generate_monthly_payroll(month, db)


@router.get("/", response_model=PayrollListResponse)
def list_payrolls(
    employee_id: int | None = None,
    month: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return payroll_service.list_payrolls(employee_id, month, status, db)


@router.get("/employee/{employee_id}", response_model=list[PayrollResponse])
def get_employee_payrolls(employee_id: int, db: Session = Depends(get_db)):
    return payroll_service.get_employee_payrolls(employee_id, db)


@router.get("/payslip/{payroll_id}", response_model=PayslipDetail)
def get_payslip(payroll_id: int, db: Session = Depends(get_db)):
    return payroll_service.get_payslip(payroll_id, db)


@router.get("/{payroll_id}", response_model=PayrollResponse)
def get_payroll(payroll_id: int, db: Session = Depends(get_db)):
    return payroll_service.get_payroll(payroll_id, db)


@router.put("/{payroll_id}", response_model=PayrollResponse)
def update_payroll(payroll_id: int, data: PayrollUpdate, db: Session = Depends(get_db)):
    return payroll_service.update_payroll(payroll_id, data, db)


@router.put("/{payroll_id}/pay", response_model=PayrollResponse)
def pay_payroll(payroll_id: int, db: Session = Depends(get_db)):
    return payroll_service.pay_payroll(payroll_id, db)
