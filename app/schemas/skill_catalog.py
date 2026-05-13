from datetime import datetime

from pydantic import BaseModel


class SkillCatalogCreate(BaseModel):
    name: str
    category: str | None = None
    description: str | None = None


class SkillCatalogUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None


class SkillCatalogResponse(BaseModel):
    id: int
    name: str
    category: str | None = None
    description: str | None = None
    employee_count: int = 0
    created_at: datetime


class SkillCatalogListResponse(BaseModel):
    skills: list[SkillCatalogResponse]
    total: int
