"""组织域 Schema，描述组织单元的输入输出结构。"""

from datetime import datetime

from pydantic import BaseModel


class OrganizationUnitCreate(BaseModel):
    """组织单元创建输入。"""

    name: str
    code: str
    unit_type: str
    parent_id: int | None = None
    manager_worker_id: int | None = None
    status: str = "active"
    description: str | None = None


class OrganizationUnitUpdate(BaseModel):
    """组织单元部分更新输入。"""

    name: str | None = None
    code: str | None = None
    unit_type: str | None = None
    parent_id: int | None = None
    manager_worker_id: int | None = None
    status: str | None = None
    description: str | None = None


class OrganizationUnitResponse(BaseModel):
    """组织单元标准响应。"""

    id: int
    name: str
    code: str
    unit_type: str
    parent_id: int | None = None
    manager_worker_id: int | None = None
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class OrganizationUnitListResponse(BaseModel):
    """组织单元列表响应。"""

    organization_units: list[OrganizationUnitResponse]
    total: int


__all__ = [
    "OrganizationUnitCreate",
    "OrganizationUnitListResponse",
    "OrganizationUnitResponse",
    "OrganizationUnitUpdate",
]
