from datetime import date, datetime

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import attendance as attendance_repo
from app.repositories import department as department_repo
from app.repositories import employee as employee_repo
from app.repositories import leave as leave_repo
from app.repositories import payroll as payroll_repo
from app.schemas.payroll import (
    PayrollCreate,
    PayrollListResponse,
    PayrollResponse,
    PayrollUpdate,
    PayslipDetail,
)

DAILY_SALARY_DIVISOR = 21.75


def _fill_names(record: dict, db: Session | None = None) -> dict:
    emp = employee_repo.get_employee_by_id(record["employee_id"], db)
    record["employee_name"] = emp["name"] if emp else "Unknown"
    if emp and emp.get("department_id"):
        dept = department_repo.get_department_by_id(emp["department_id"], db)
        record["department_name"] = dept["name"] if dept else None
    else:
        record["department_name"] = None
    return record


def _calculate_net_salary(base_salary: float, bonuses: float, deductions: float) -> float:
    return round(base_salary + bonuses - deductions, 2)


def _parse_month(month: str) -> tuple[int, int]:
    parts = month.split("-")
    if len(parts) != 2:
        raise ValidationError("Month format must be YYYY-MM")
    return int(parts[0]), int(parts[1])


def _month_to_date_range(month: str) -> tuple[date, date]:
    year, m = _parse_month(month)
    import calendar

    start = date(year, m, 1)
    last_day = calendar.monthrange(year, m)[1]
    end = date(year, m, last_day)
    return start, end


def _calculate_attendance_deductions(
    employee_id: int, month: str, daily_salary: float, db: Session | None = None
) -> tuple[float, list[dict]]:
    start, end = _month_to_date_range(month)
    records = attendance_repo.get_all_attendance(employee_id, start, end, db)
    deductions = 0.0
    details = []
    for r in records:
        if r["status"] == "late":
            amount = round(daily_salary * 0.5, 2)
            deductions += amount
            details.append({"type": "迟到扣款", "date": str(r["date"]), "amount": amount})
        elif r["status"] == "early_leave":
            amount = round(daily_salary * 0.5, 2)
            deductions += amount
            details.append({"type": "早退扣款", "date": str(r["date"]), "amount": amount})
    absent_days = (end - start).days + 1 - len(records)
    if absent_days > 0:
        amount = round(daily_salary * absent_days, 2)
        deductions += amount
        details.append({"type": "缺勤扣款", "days": absent_days, "amount": amount})
    return round(deductions, 2), details


def _calculate_leave_deductions(
    employee_id: int, month: str, daily_salary: float, db: Session | None = None
) -> tuple[float, list[dict]]:
    start, end = _month_to_date_range(month)
    approved_leaves = leave_repo.get_approved_leaves_in_range(employee_id, start, end, db)
    deductions = 0.0
    details = []
    for leave in approved_leaves:
        if leave["leave_type"] == "personal":
            leave_start = max(leave["start_date"], start)
            leave_end = min(leave["end_date"], end)
            days = (leave_end - leave_start).days + 1
            amount = round(daily_salary * days, 2)
            deductions += amount
            details.append(
                {
                    "type": "事假扣款",
                    "leave_type": leave["leave_type_name"],
                    "days": days,
                    "amount": amount,
                }
            )
    return round(deductions, 2), details


def create_payroll(data: PayrollCreate, db: Session | None = None) -> PayrollResponse:
    emp = employee_repo.get_employee_by_id(data.employee_id, db)
    if emp is None:
        raise NotFoundError(f"Employee {data.employee_id} not found")
    _parse_month(data.month)
    existing = payroll_repo.get_payroll_by_employee_month(data.employee_id, data.month, db)
    if existing is not None:
        raise ValidationError(f"Payroll for employee {data.employee_id} month {data.month} already exists")
    payroll_data = data.model_dump()
    payroll_data["net_salary"] = _calculate_net_salary(data.base_salary, data.bonuses, data.deductions)
    payroll_data["status"] = "draft"
    payroll_data["created_at"] = datetime.now()
    record = payroll_repo.create_payroll(payroll_data, db)
    return PayrollResponse(**_fill_names(record, db))


def generate_monthly_payroll(month: str, db: Session | None = None) -> list[PayrollResponse]:
    _parse_month(month)
    results = []
    for emp in employee_repo.get_all_employees(db):
        existing = payroll_repo.get_payroll_by_employee_month(emp["id"], month, db)
        if existing is not None:
            continue
        base_salary = emp["salary"]
        daily_salary = round(base_salary / DAILY_SALARY_DIVISOR, 2)
        attendance_deductions, _ = _calculate_attendance_deductions(emp["id"], month, daily_salary, db)
        leave_deductions, _ = _calculate_leave_deductions(emp["id"], month, daily_salary, db)
        total_deductions = round(attendance_deductions + leave_deductions, 2)
        payroll_data = {
            "employee_id": emp["id"],
            "month": month,
            "base_salary": base_salary,
            "bonuses": 0,
            "deductions": total_deductions,
            "net_salary": _calculate_net_salary(base_salary, 0, total_deductions),
            "status": "draft",
            "payment_date": None,
            "created_at": datetime.now(),
        }
        record = payroll_repo.create_payroll(payroll_data, db)
        results.append(PayrollResponse(**_fill_names(record, db)))
    return results


def list_payrolls(
    employee_id: int | None = None,
    month: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> PayrollListResponse:
    records = payroll_repo.get_all_payrolls(employee_id, month, status, db)
    return PayrollListResponse(
        payrolls=[PayrollResponse(**_fill_names(r, db)) for r in records],
        total=len(records),
    )


def get_payroll(payroll_id: int, db: Session | None = None) -> PayrollResponse:
    record = payroll_repo.get_payroll_by_id(payroll_id, db)
    if record is None:
        raise NotFoundError(f"Payroll {payroll_id} not found")
    return PayrollResponse(**_fill_names(record, db))


def update_payroll(payroll_id: int, data: PayrollUpdate, db: Session | None = None) -> PayrollResponse:
    record = payroll_repo.get_payroll_by_id(payroll_id, db)
    if record is None:
        raise NotFoundError(f"Payroll {payroll_id} not found")
    if record["status"] != "draft":
        raise ValidationError("Only draft payroll can be updated")
    update_data = data.model_dump(exclude_unset=True)
    bonuses = update_data.get("bonuses", record["bonuses"])
    deductions = update_data.get("deductions", record["deductions"])
    update_data["net_salary"] = _calculate_net_salary(record["base_salary"], bonuses, deductions)
    updated = payroll_repo.update_payroll(payroll_id, update_data, db)
    return PayrollResponse(**_fill_names(updated, db))


def pay_payroll(payroll_id: int, db: Session | None = None) -> PayrollResponse:
    record = payroll_repo.get_payroll_by_id(payroll_id, db)
    if record is None:
        raise NotFoundError(f"Payroll {payroll_id} not found")
    if record["status"] != "draft":
        raise ValidationError("Only draft payroll can be paid")
    update_data = {"status": "paid", "payment_date": date.today()}
    updated = payroll_repo.update_payroll(payroll_id, update_data, db)
    return PayrollResponse(**_fill_names(updated, db))


def get_employee_payrolls(employee_id: int, db: Session | None = None) -> list[PayrollResponse]:
    emp = employee_repo.get_employee_by_id(employee_id, db)
    if emp is None:
        raise NotFoundError(f"Employee {employee_id} not found")
    records = payroll_repo.get_payrolls_by_employee(employee_id, db)
    return [PayrollResponse(**_fill_names(r, db)) for r in records]


def get_payslip(payroll_id: int, db: Session | None = None) -> PayslipDetail:
    record = payroll_repo.get_payroll_by_id(payroll_id, db)
    if record is None:
        raise NotFoundError(f"Payroll {payroll_id} not found")
    payroll_resp = PayrollResponse(**_fill_names(record, db))
    daily_salary = round(record["base_salary"] / DAILY_SALARY_DIVISOR, 2)
    attendance_deductions, deduction_details = _calculate_attendance_deductions(
        record["employee_id"], record["month"], daily_salary, db
    )
    leave_deductions, leave_details = _calculate_leave_deductions(
        record["employee_id"], record["month"], daily_salary, db
    )
    start, end = _month_to_date_range(record["month"])
    attendance_records = attendance_repo.get_all_attendance(record["employee_id"], start, end, db)
    attendance_summary = {
        "total_days": (end - start).days + 1,
        "actual_days": len(attendance_records),
        "late_days": sum(1 for r in attendance_records if r["status"] == "late"),
        "early_leave_days": sum(1 for r in attendance_records if r["status"] == "early_leave"),
    }
    approved_leaves = leave_repo.get_approved_leaves_in_range(record["employee_id"], start, end, db)
    leave_summary = {
        "total_leave_days": sum(r["days"] for r in approved_leaves),
        "sick_days": sum(r["days"] for r in approved_leaves if r["leave_type"] == "sick"),
        "annual_days": sum(r["days"] for r in approved_leaves if r["leave_type"] == "annual"),
        "personal_days": sum(r["days"] for r in approved_leaves if r["leave_type"] == "personal"),
    }
    bonus_details = []
    if record["bonuses"] > 0:
        bonus_details.append({"type": "奖金", "amount": record["bonuses"]})
    return PayslipDetail(
        payroll=payroll_resp,
        attendance_summary=attendance_summary,
        leave_summary=leave_summary,
        deduction_details=deduction_details + leave_details,
        bonus_details=bonus_details,
    )
