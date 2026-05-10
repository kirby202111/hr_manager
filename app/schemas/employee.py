from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    name: str
    department_id: int | None = None
    salary: float


class EmployeeUpdate(BaseModel):
    name: str | None = None
    department_id: int | None = None
    salary: float | None = None


class EmployeeResponse(BaseModel):
    id: int
    name: str
    department_id: int | None = None
    department_name: str | None = None
    salary: float


class EmployeeListResponse(BaseModel):
    employees: list[EmployeeResponse]
    total: int
