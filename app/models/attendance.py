from datetime import time

_attendance_db: dict[int, dict] = {}
_next_id: int = 1

LATE_THRESHOLD = time(9, 0)
EARLY_LEAVE_THRESHOLD = time(18, 0)


def calculate_status(check_in: time, check_out: time | None = None) -> str:
    is_late = check_in > LATE_THRESHOLD
    is_early = check_out is not None and check_out < EARLY_LEAVE_THRESHOLD
    if is_late and is_early:
        return "late"
    if is_late:
        return "late"
    if is_early:
        return "early_leave"
    return "normal"


def get_all_attendance(employee_id: int | None = None, start_date=None, end_date=None) -> list[dict]:
    records = list(_attendance_db.values())
    if employee_id is not None:
        records = [r for r in records if r["employee_id"] == employee_id]
    if start_date is not None:
        records = [r for r in records if r["date"] >= start_date]
    if end_date is not None:
        records = [r for r in records if r["date"] <= end_date]
    return records


def get_attendance_by_id(record_id: int) -> dict | None:
    return _attendance_db.get(record_id)


def get_attendance_by_employee_date(employee_id: int, record_date) -> dict | None:
    for record in _attendance_db.values():
        if record["employee_id"] == employee_id and record["date"] == record_date:
            return record
    return None


def get_attendance_by_employee(employee_id: int) -> list[dict]:
    return [r for r in _attendance_db.values() if r["employee_id"] == employee_id]


def create_attendance(attendance_data: dict) -> dict:
    global _next_id
    record = {"id": _next_id, **attendance_data}
    _attendance_db[_next_id] = record
    _next_id += 1
    return record


def update_attendance(record_id: int, attendance_data: dict) -> dict | None:
    if record_id not in _attendance_db:
        return None
    _attendance_db[record_id].update(attendance_data)
    return _attendance_db[record_id]
