_employees_db: dict[int, dict] = {}
_next_id: int = 1


def get_all_employees() -> list[dict]:
    return list(_employees_db.values())


def get_employee_by_id(employee_id: int) -> dict | None:
    return _employees_db.get(employee_id)


def get_employees_by_department(department_id: int) -> list[dict]:
    return [e for e in _employees_db.values() if e.get("department_id") == department_id]


def create_employee(employee_data: dict) -> dict:
    global _next_id
    employee = {"id": _next_id, **employee_data}
    _employees_db[_next_id] = employee
    _next_id += 1
    return employee


def update_employee(employee_id: int, employee_data: dict) -> dict | None:
    if employee_id not in _employees_db:
        return None
    _employees_db[employee_id].update({k: v for k, v in employee_data.items() if v is not None})
    return _employees_db[employee_id]


def delete_employee(employee_id: int) -> bool:
    if employee_id not in _employees_db:
        return False
    del _employees_db[employee_id]
    return True
