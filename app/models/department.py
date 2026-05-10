_departments_db: dict[int, dict] = {}
_next_id: int = 1


def get_all_departments() -> list[dict]:
    return list(_departments_db.values())


def get_department_by_id(department_id: int) -> dict | None:
    return _departments_db.get(department_id)


def get_department_by_name(name: str) -> dict | None:
    for dept in _departments_db.values():
        if dept["name"] == name:
            return dept
    return None


def create_department(department_data: dict) -> dict:
    global _next_id
    department = {"id": _next_id, **department_data}
    _departments_db[_next_id] = department
    _next_id += 1
    return department


def update_department(department_id: int, department_data: dict) -> dict | None:
    if department_id not in _departments_db:
        return None
    _departments_db[department_id].update({k: v for k, v in department_data.items() if v is not None})
    return _departments_db[department_id]


def delete_department(department_id: int) -> bool:
    if department_id not in _departments_db:
        return False
    del _departments_db[department_id]
    return True
