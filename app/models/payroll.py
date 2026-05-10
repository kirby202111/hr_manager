_payroll_db: dict[int, dict] = {}
_next_id: int = 1


def get_all_payrolls(employee_id: int | None = None, month: str | None = None, status: str | None = None) -> list[dict]:
    records = list(_payroll_db.values())
    if employee_id is not None:
        records = [r for r in records if r["employee_id"] == employee_id]
    if month is not None:
        records = [r for r in records if r["month"] == month]
    if status is not None:
        records = [r for r in records if r["status"] == status]
    return records


def get_payroll_by_id(payroll_id: int) -> dict | None:
    return _payroll_db.get(payroll_id)


def get_payroll_by_employee_month(employee_id: int, month: str) -> dict | None:
    for r in _payroll_db.values():
        if r["employee_id"] == employee_id and r["month"] == month:
            return r
    return None


def get_payrolls_by_employee(employee_id: int) -> list[dict]:
    return [r for r in _payroll_db.values() if r["employee_id"] == employee_id]


def create_payroll(payroll_data: dict) -> dict:
    global _next_id
    record = {"id": _next_id, **payroll_data}
    _payroll_db[_next_id] = record
    _next_id += 1
    return record


def update_payroll(payroll_id: int, payroll_data: dict) -> dict | None:
    if payroll_id not in _payroll_db:
        return None
    _payroll_db[payroll_id].update(payroll_data)
    return _payroll_db[payroll_id]
