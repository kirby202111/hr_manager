from datetime import datetime

from pydantic import BaseModel


class EmployeeSkillCreate(BaseModel):
    employee_id: int
    skill_name: str
    proficiency_level: str
    years_of_experience: float | None = None
    certification: str | None = None


class EmployeeSkillUpdate(BaseModel):
    skill_name: str | None = None
    proficiency_level: str | None = None
    years_of_experience: float | None = None
    certification: str | None = None


class EmployeeSkillResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str | None = None
    skill_name: str
    proficiency_level: str
    years_of_experience: float | None = None
    certification: str | None = None
    created_at: datetime


class EmployeeSkillListResponse(BaseModel):
    skills: list[EmployeeSkillResponse]
    total: int
