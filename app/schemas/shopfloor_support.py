from typing import Any

from pydantic import BaseModel


class ListResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int
