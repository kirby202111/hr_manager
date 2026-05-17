from datetime import date, datetime

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import attendance as attendance_repo
from app.repositories import leave as leave_repo
from app.repositories import org_unit as department_repo
from app.repositories import payroll as payroll_repo
from app.repositories import worker as worker_repo
from app.schemas.payroll import PayrollCreate, PayrollListResponse, PayrollResponse, PayrollUpdate, PayslipDetail

DAILY_SALARY_DIVISOR = 21.75


def _fill_names(record: dict, db: Session | None = None) -> dict:
    worker = worker_repo.get_worker_by_id(record["worker_id"], db)
    record["worker_name"] = worker["name"] if worker else "Unknown"
    if worker and worker.get("department_id"):
        dept = department_repo.get_department_by_id(worker["department_id"], db)
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
    import calendar

    year, month_num = _parse_month(month)
    start = date(year, month_num, 1)
    end = date(year, month_num, calendar.monthrange(year, month_num)[1])
    return start, end


def _calculate_attendance_deductions(worker_id: int, month: str, daily_salary: float, db: Session | None = None) -> tuple[float, list[dict]]:
    start, end = _month_to_date_range(month)
    records = attendance_repo.get_all_attendance(worker_id, start, end, db)
    deductions = 0.0
    details = []
    for record in records:
        if record["status"] in {"late", "early_leave"}:
            amount = round(daily_salary * 0.5, 2)
            deductions += amount
            details.append({"type": record["status"], "date": str(record["date"]), "amount": amount})
    absent_days = (end - start).days + 1 - len(records)
    if absent_days > 0:
        amount = round(daily_salary * absent_days, 2)
        deductions += amount
        details.append({"type": "absence", "days": absent_days, "amount": amount})
    return round(deductions, 2), details


def _calculate_leave_deductions(worker_id: int, month: str, daily_salary: float, db: Session | None = None) -> tuple[float, list[dict]]:
    start, end = _month_to_date_range(month)
    approved_leaves = leave_repo.get_approved_leaves_in_range(worker_id, start, end, db)
    deductions = 0.0
    details = []
    for leave in approved_leaves:
        if leave["leave_type"] == "personal":
            leave_start = max(leave["start_date"], start)
            leave_end = min(leave["end_date"], end)
            days = (leave_end - leave_start).days + 1
            amount = round(daily_salary * days, 2)
            deductions += amount
            details.append({"type": "personal_leave", "leave_type": leave["leave_type_name"], "days": days, "amount": amount})
    return round(deductions, 2), details


def create_payroll(data: PayrollCreate, db: Session | None = None) -> PayrollResponse:
    worker = worker_repo.get_worker_by_id(data.worker_id, db)
    if worker is None:
        raise NotFoundError(f"Worker {data.worker_id} not found")
    _parse_month(data.month)
    existing = payroll_repo.get_payroll_by_worker_month(data.worker_id, data.month, db)
    if existing is not None:
        raise ValidationError(f"Payroll for worker {data.worker_id} month {data.month} already exists")
    record = payroll_repo.create_payroll(
        data.model_dump()
        | {"net_salary": _calculate_net_salary(data.base_salary, data.bonuses, data.deductions), "status": "draft", "created_at": datetime.now()},
        db,
    )
    return PayrollResponse(**_fill_names(record, db))


def generate_monthly_payroll(month: str, db: Session | None = None) -> list[PayrollResponse]:
    _parse_month(month)
    results = []
    for worker in worker_repo.get_all_workers(db):
        if payroll_repo.get_payroll_by_worker_month(worker["id"], month, db) is not None:
            continue
        base_salary = worker["salary"]
        daily_salary = round(base_salary / DAILY_SALARY_DIVISOR, 2)
        attendance_deductions, _ = _calculate_attendance_deductions(worker["id"], month, daily_salary, db)
        leave_deductions, _ = _calculate_leave_deductions(worker["id"], month, daily_salary, db)
        total_deductions = round(attendance_deductions + leave_deductions, 2)
        record = payroll_repo.create_payroll(
            {
                "worker_id": worker["id"],
                "month": month,
                "base_salary": base_salary,
                "bonuses": 0,
                "deductions": total_deductions,
                "net_salary": _calculate_net_salary(base_salary, 0, total_deductions),
                "status": "draft",
                "payment_date": None,
                "created_at": datetime.now(),
            },
            db,
        )
        results.append(PayrollResponse(**_fill_names(record, db)))
    return results


def list_payrolls(worker_id: int | None = None, month: str | None = None, status: str | None = None, db: Session | None = None) -> PayrollListResponse:
    records = payroll_repo.get_all_payrolls(worker_id, month, status, db)
    return PayrollListResponse(payrolls=[PayrollResponse(**_fill_names(record, db)) for record in records], total=len(records))


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
    updated = payroll_repo.update_payroll(
        payroll_id,
        update_data | {"net_salary": _calculate_net_salary(record["base_salary"], bonuses, deductions)},
        db,
    )
    return PayrollResponse(**_fill_names(updated, db))


def pay_payroll(payroll_id: int, db: Session | None = None) -> PayrollResponse:
    record = payroll_repo.get_payroll_by_id(payroll_id, db)
    if record is None:
        raise NotFoundError(f"Payroll {payroll_id} not found")
    if record["status"] != "draft":
        raise ValidationError("Only draft payroll can be paid")
    updated = payroll_repo.update_payroll(payroll_id, {"status": "paid", "payment_date": date.today()}, db)
    return PayrollResponse(**_fill_names(updated, db))


def get_worker_payrolls(worker_id: int, db: Session | None = None) -> list[PayrollResponse]:
    worker = worker_repo.get_worker_by_id(worker_id, db)
    if worker is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    return [PayrollResponse(**_fill_names(record, db)) for record in payroll_repo.get_payrolls_by_worker(worker_id, db)]


def get_payslip(payroll_id: int, db: Session | None = None) -> PayslipDetail:
    record = payroll_repo.get_payroll_by_id(payroll_id, db)
    if record is None:
        raise NotFoundError(f"Payroll {payroll_id} not found")
    payroll_resp = PayrollResponse(**_fill_names(record, db))
    daily_salary = round(record["base_salary"] / DAILY_SALARY_DIVISOR, 2)
    _, deduction_details = _calculate_attendance_deductions(record["worker_id"], record["month"], daily_salary, db)
    _, leave_details = _calculate_leave_deductions(record["worker_id"], record["month"], daily_salary, db)
    start, end = _month_to_date_range(record["month"])
    attendance_records = attendance_repo.get_all_attendance(record["worker_id"], start, end, db)
    approved_leaves = leave_repo.get_approved_leaves_in_range(record["worker_id"], start, end, db)
    return PayslipDetail(
        payroll=payroll_resp,
        attendance_summary={
            "total_days": (end - start).days + 1,
            "actual_days": len(attendance_records),
            "late_days": sum(1 for record in attendance_records if record["status"] == "late"),
            "early_leave_days": sum(1 for record in attendance_records if record["status"] == "early_leave"),
        },
        leave_summary={
            "total_leave_days": sum(record["days"] for record in approved_leaves),
            "sick_days": sum(record["days"] for record in approved_leaves if record["leave_type"] == "sick"),
            "annual_days": sum(record["days"] for record in approved_leaves if record["leave_type"] == "annual"),
            "personal_days": sum(record["days"] for record in approved_leaves if record["leave_type"] == "personal"),
        },
        deduction_details=deduction_details + leave_details,
        bonus_details=[{"type": "bonus", "amount": record["bonuses"]}] if record["bonuses"] > 0 else [],
    )
