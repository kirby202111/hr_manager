from fastapi import APIRouter

from app.schemas.items import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
from app.services import items as item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemListResponse)
def list_items():
    return item_service.list_items()


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    return item_service.get_item(item_id)


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(item_in: ItemCreate):
    return item_service.create_item(item_in)


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_in: ItemUpdate):
    return item_service.update_item(item_id, item_in)


@router.delete("/{item_id}")
def delete_item(item_id: int):
    return item_service.delete_item(item_id)
