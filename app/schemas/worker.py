from pydantic import BaseModel


class WorkerCreate(BaseModel):
    name: str
    department_id: int | None = None
    salary: float


class WorkerUpdate(BaseModel):
    name: str | None = None
    department_id: int | None = None
    salary: float | None = None


class WorkerResponse(BaseModel):
    id: int
    name: str
    department_id: int | None = None
    department_name: str | None = None
    salary: float


class WorkerListResponse(BaseModel):
    workers: list[WorkerResponse]
    total: int
