from datetime import date, datetime

from pydantic import BaseModel


class PayrollCreate(BaseModel):
    employee_id: int
    month: str
    base_salary: float
    bonuses: float = 0
    deductions: float = 0
    payment_date: date | None = None


class PayrollUpdate(BaseModel):
    bonuses: float | None = None
    deductions: float | None = None
    payment_date: date | None = None


class PayrollResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    department_name: str | None = None
    month: str
    base_salary: float
    bonuses: float
    deductions: float
    net_salary: float
    status: str
    payment_date: date | None = None
    created_at: datetime


class PayrollListResponse(BaseModel):
    payrolls: list[PayrollResponse]
    total: int


class PayslipDetail(BaseModel):
    payroll: PayrollResponse
    attendance_summary: dict | None = None
    leave_summary: dict | None = None
    deduction_details: list[dict] = []
    bonus_details: list[dict] = []
