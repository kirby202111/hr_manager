from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str
    description: str | None = None
    manager: str | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    manager: str | None = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    manager: str | None = None
    worker_count: int = 0


class DepartmentListResponse(BaseModel):
    departments: list[DepartmentResponse]
    total: int
