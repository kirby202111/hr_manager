_cycles_db: dict[int, dict] = {}
_cycle_next_id: int = 1

_reviews_db: dict[int, dict] = {}
_review_next_id: int = 1


# ---- 考核周期 ----

def get_all_cycles() -> list[dict]:
    return list(_cycles_db.values())


def get_cycle_by_id(cycle_id: int) -> dict | None:
    return _cycles_db.get(cycle_id)


def create_cycle(cycle_data: dict) -> dict:
    global _cycle_next_id
    cycle = {"id": _cycle_next_id, **cycle_data}
    _cycles_db[_cycle_next_id] = cycle
    _cycle_next_id += 1
    return cycle


def update_cycle(cycle_id: int, cycle_data: dict) -> dict | None:
    if cycle_id not in _cycles_db:
        return None
    _cycles_db[cycle_id].update({k: v for k, v in cycle_data.items() if v is not None})
    return _cycles_db[cycle_id]


# ---- 绩效评分 ----

def get_all_reviews(employee_id: int | None = None, cycle_id: int | None = None) -> list[dict]:
    records = list(_reviews_db.values())
    if employee_id is not None:
        records = [r for r in records if r["employee_id"] == employee_id]
    if cycle_id is not None:
        records = [r for r in records if r["cycle_id"] == cycle_id]
    return records


def get_review_by_id(review_id: int) -> dict | None:
    return _reviews_db.get(review_id)


def get_review_by_employee_cycle(employee_id: int, cycle_id: int) -> dict | None:
    for r in _reviews_db.values():
        if r["employee_id"] == employee_id and r["cycle_id"] == cycle_id:
            return r
    return None


def get_reviews_by_employee(employee_id: int) -> list[dict]:
    return [r for r in _reviews_db.values() if r["employee_id"] == employee_id]


def get_reviews_by_cycle(cycle_id: int) -> list[dict]:
    return [r for r in _reviews_db.values() if r["cycle_id"] == cycle_id]


def create_review(review_data: dict) -> dict:
    global _review_next_id
    record = {"id": _review_next_id, **review_data}
    _reviews_db[_review_next_id] = record
    _review_next_id += 1
    return record


def update_review(review_id: int, review_data: dict) -> dict | None:
    if review_id not in _reviews_db:
        return None
    _reviews_db[review_id].update({k: v for k, v in review_data.items() if v is not None})
    return _reviews_db[review_id]
