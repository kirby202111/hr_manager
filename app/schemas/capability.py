"""能力域 Schema，覆盖技能目录与人员技能画像。"""

from datetime import datetime

from pydantic import BaseModel


class SkillCreate(BaseModel):
    """技能目录创建输入。"""

    name: str
    code: str
    category: str
    status: str = "active"
    description: str | None = None


class SkillUpdate(BaseModel):
    """技能目录部分更新输入。"""

    name: str | None = None
    code: str | None = None
    category: str | None = None
    status: str | None = None
    description: str | None = None


class SkillResponse(BaseModel):
    """技能目录标准响应。"""

    id: int
    name: str
    code: str
    category: str
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class SkillListResponse(BaseModel):
    """技能目录列表响应。"""

    skills: list[SkillResponse]
    total: int


class WorkerSkillCreate(BaseModel):
    """人员技能记录创建输入。"""

    worker_id: int
    skill_id: int
    proficiency_level: str
    years_of_experience: float | None = None
    validated: bool = False
    notes: str | None = None


class WorkerSkillUpdate(BaseModel):
    """人员技能记录部分更新输入。"""

    worker_id: int | None = None
    skill_id: int | None = None
    proficiency_level: str | None = None
    years_of_experience: float | None = None
    validated: bool | None = None
    notes: str | None = None


class WorkerSkillResponse(BaseModel):
    """人员技能记录标准响应。"""

    id: int
    worker_id: int
    skill_id: int
    proficiency_level: str
    years_of_experience: float | None = None
    validated: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkerSkillListResponse(BaseModel):
    """人员技能记录列表响应。"""

    worker_skills: list[WorkerSkillResponse]
    total: int


__all__ = [
    "SkillCreate",
    "SkillListResponse",
    "SkillResponse",
    "SkillUpdate",
    "WorkerSkillCreate",
    "WorkerSkillListResponse",
    "WorkerSkillResponse",
    "WorkerSkillUpdate",
]
