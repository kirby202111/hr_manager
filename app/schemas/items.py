from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
