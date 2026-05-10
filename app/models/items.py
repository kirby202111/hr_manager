_items_db: dict[int, dict] = {}
_next_id: int = 1


def get_all_items() -> list[dict]:
    return list(_items_db.values())


def get_item_by_id(item_id: int) -> dict | None:
    return _items_db.get(item_id)


def create_item(item_data: dict) -> dict:
    global _next_id
    item = {"id": _next_id, **item_data}
    _items_db[_next_id] = item
    _next_id += 1
    return item


def update_item(item_id: int, item_data: dict) -> dict | None:
    if item_id not in _items_db:
        return None
    _items_db[item_id].update({k: v for k, v in item_data.items() if v is not None})
    return _items_db[item_id]


def delete_item(item_id: int) -> bool:
    if item_id not in _items_db:
        return False
    del _items_db[item_id]
    return True
