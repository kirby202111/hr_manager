from fastapi import HTTPException

from app.models import items as item_model
from app.schemas.items import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse


def list_items() -> ItemListResponse:
    items = item_model.get_all_items()
    return ItemListResponse(
        items=[ItemResponse(**item) for item in items],
        total=len(items),
    )


def get_item(item_id: int) -> ItemResponse:
    item = item_model.get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return ItemResponse(**item)


def create_item(item_in: ItemCreate) -> ItemResponse:
    item_data = item_in.model_dump()
    item = item_model.create_item(item_data)
    return ItemResponse(**item)


def update_item(item_id: int, item_in: ItemUpdate) -> ItemResponse:
    existing = item_model.get_item_by_id(item_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    update_data = item_in.model_dump(exclude_unset=True)
    item = item_model.update_item(item_id, update_data)
    return ItemResponse(**item)


def delete_item(item_id: int) -> dict:
    success = item_model.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return {"message": f"Item {item_id} deleted"}
