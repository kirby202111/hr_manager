from datetime import datetime

from pydantic import BaseModel


class WorkerSkillCreate(BaseModel):
    worker_id: int
    skill_name: str
    skill_id: int | None = None
    proficiency_level: str
    years_of_experience: float | None = None
    certification: str | None = None


class WorkerSkillUpdate(BaseModel):
    skill_name: str | None = None
    skill_id: int | None = None
    proficiency_level: str | None = None
    years_of_experience: float | None = None
    certification: str | None = None


class WorkerSkillResponse(BaseModel):
    id: int
    worker_id: int
    worker_name: str | None = None
    skill_name: str
    skill_id: int | None = None
    skill_category: str | None = None
    proficiency_level: str
    years_of_experience: float | None = None
    certification: str | None = None
    created_at: datetime


class WorkerSkillListResponse(BaseModel):
    skills: list[WorkerSkillResponse]
    total: int
