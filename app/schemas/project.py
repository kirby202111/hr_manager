from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel

# ── Project ──────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    status: str = "planning"
    start_date: date_type | None = None
    end_date: date_type | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    start_date: date_type | None = None
    end_date: date_type | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    status: str
    start_date: date_type | None = None
    end_date: date_type | None = None
    skill_requirement_count: int = 0
    member_count: int = 0
    created_at: datetime


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int


# ── ProjectSkillRequirement ──────────────────────────────────


class ProjectSkillRequirementCreate(BaseModel):
    skill_id: int
    required_proficiency: str
    person_days: float
    headcount: int


class ProjectSkillRequirementUpdate(BaseModel):
    required_proficiency: str | None = None
    person_days: float | None = None
    headcount: int | None = None


class ProjectSkillRequirementResponse(BaseModel):
    id: int
    project_id: int
    skill_id: int
    skill_name: str
    skill_category: str | None = None
    required_proficiency: str
    person_days: float
    headcount: int
    created_at: datetime


class ProjectSkillRequirementListResponse(BaseModel):
    requirements: list[ProjectSkillRequirementResponse]
    total: int


# ── ProjectMember ────────────────────────────────────────────


class ProjectMemberCreate(BaseModel):
    worker_id: int
    role: str
    assigned_date: date_type


class ProjectMemberUpdate(BaseModel):
    role: str | None = None
    assigned_date: date_type | None = None


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    worker_id: int
    worker_name: str | None = None
    role: str
    assigned_date: date_type
    created_at: datetime


class ProjectMemberListResponse(BaseModel):
    members: list[ProjectMemberResponse]
    total: int


# ── ProjectTimesheet ─────────────────────────────────────────


class ProjectTimesheetCreate(BaseModel):
    requirement_id: int
    worker_id: int
    date: date_type
    hours: float
    description: str | None = None


class ProjectTimesheetUpdate(BaseModel):
    requirement_id: int | None = None
    worker_id: int | None = None
    date: date_type | None = None
    hours: float | None = None
    description: str | None = None


class ProjectTimesheetResponse(BaseModel):
    id: int
    project_id: int
    requirement_id: int
    worker_id: int
    worker_name: str | None = None
    skill_name: str | None = None
    date: date_type
    hours: float
    description: str | None = None
    created_at: datetime


class ProjectTimesheetListResponse(BaseModel):
    timesheets: list[ProjectTimesheetResponse]
    total: int


# ── ProjectProgress ──────────────────────────────────────────


class RequirementProgress(BaseModel):
    requirement_id: int
    skill_name: str
    budget_person_days: float
    used_person_days: float
    progress: float


class MemberWorkload(BaseModel):
    worker_id: int
    worker_name: str | None = None
    total_person_days: float


class ProjectProgressResponse(BaseModel):
    project_id: int
    total_budget_person_days: float
    total_used_person_days: float
    overall_progress: float
    by_requirement: list[RequirementProgress]
    by_member: list[MemberWorkload]
