_leaves_db: dict[int, dict] = {}
_next_id: int = 1


def get_all_leaves(employee_id: int | None = None, status: str | None = None) -> list[dict]:
    records = list(_leaves_db.values())
    if employee_id is not None:
        records = [r for r in records if r["employee_id"] == employee_id]
    if status is not None:
        records = [r for r in records if r["status"] == status]
    return records


def get_leave_by_id(leave_id: int) -> dict | None:
    return _leaves_db.get(leave_id)


def get_leaves_by_employee(employee_id: int) -> list[dict]:
    return [r for r in _leaves_db.values() if r["employee_id"] == employee_id]


def get_approved_leaves_by_type(employee_id: int, leave_type: str) -> list[dict]:
    return [
        r for r in _leaves_db.values()
        if r["employee_id"] == employee_id and r["leave_type"] == leave_type and r["status"] == "approved"
    ]


def get_approved_leaves_in_range(employee_id: int, start_date, end_date) -> list[dict]:
    return [
        r for r in _leaves_db.values()
        if r["employee_id"] == employee_id
        and r["status"] == "approved"
        and r["start_date"] <= end_date
        and r["end_date"] >= start_date
    ]


def create_leave(leave_data: dict) -> dict:
    global _next_id
    record = {"id": _next_id, **leave_data}
    _leaves_db[_next_id] = record
    _next_id += 1
    return record


def update_leave(leave_id: int, leave_data: dict) -> dict | None:
    if leave_id not in _leaves_db:
        return None
    _leaves_db[leave_id].update(leave_data)
    return _leaves_db[leave_id]
