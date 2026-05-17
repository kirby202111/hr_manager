"""协同域 Schema，覆盖项目、成员、技能需求与工时记录。"""

from datetime import date, datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    """项目创建输入。"""

    code: str
    name: str
    status: str
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class ProjectUpdate(BaseModel):
    """项目部分更新输入。"""

    code: str | None = None
    name: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    """项目标准响应。"""

    id: int
    code: str
    name: str
    status: str
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """项目列表响应。"""

    projects: list[ProjectResponse]
    total: int


class ProjectMemberCreate(BaseModel):
    """项目成员记录创建输入。"""

    project_id: int
    worker_id: int
    role_name: str
    assigned_date: date
    allocation_percent: float | None = None


class ProjectMemberUpdate(BaseModel):
    """项目成员记录部分更新输入。"""

    project_id: int | None = None
    worker_id: int | None = None
    role_name: str | None = None
    assigned_date: date | None = None
    allocation_percent: float | None = None


class ProjectMemberResponse(BaseModel):
    """项目成员记录标准响应。"""

    id: int
    project_id: int
    worker_id: int
    role_name: str
    assigned_date: date
    allocation_percent: float | None = None
    created_at: datetime
    updated_at: datetime


class ProjectMemberListResponse(BaseModel):
    """项目成员记录列表响应。"""

    project_members: list[ProjectMemberResponse]
    total: int


class ProjectSkillRequirementCreate(BaseModel):
    """项目技能需求创建输入。"""

    project_id: int
    skill_id: int
    required_proficiency: str
    person_days: float
    headcount: int


class ProjectSkillRequirementUpdate(BaseModel):
    """项目技能需求部分更新输入。"""

    project_id: int | None = None
    skill_id: int | None = None
    required_proficiency: str | None = None
    person_days: float | None = None
    headcount: int | None = None


class ProjectSkillRequirementResponse(BaseModel):
    """项目技能需求标准响应。"""

    id: int
    project_id: int
    skill_id: int
    required_proficiency: str
    person_days: float
    headcount: int
    created_at: datetime
    updated_at: datetime


class ProjectSkillRequirementListResponse(BaseModel):
    """项目技能需求列表响应。"""

    project_skill_requirements: list[ProjectSkillRequirementResponse]
    total: int


class ProjectTimesheetEntryCreate(BaseModel):
    """项目工时记录创建输入。"""

    project_id: int
    project_skill_requirement_id: int
    worker_id: int
    work_date: date
    hours: float
    description: str | None = None


class ProjectTimesheetEntryUpdate(BaseModel):
    """项目工时记录部分更新输入。"""

    project_id: int | None = None
    project_skill_requirement_id: int | None = None
    worker_id: int | None = None
    work_date: date | None = None
    hours: float | None = None
    description: str | None = None


class ProjectTimesheetEntryResponse(BaseModel):
    """项目工时记录标准响应。"""

    id: int
    project_id: int
    project_skill_requirement_id: int
    worker_id: int
    work_date: date
    hours: float
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class ProjectTimesheetEntryListResponse(BaseModel):
    """项目工时记录列表响应。"""

    project_timesheet_entries: list[ProjectTimesheetEntryResponse]
    total: int


__all__ = [
    "ProjectCreate",
    "ProjectListResponse",
    "ProjectMemberCreate",
    "ProjectMemberListResponse",
    "ProjectMemberResponse",
    "ProjectMemberUpdate",
    "ProjectResponse",
    "ProjectSkillRequirementCreate",
    "ProjectSkillRequirementListResponse",
    "ProjectSkillRequirementResponse",
    "ProjectSkillRequirementUpdate",
    "ProjectTimesheetEntryCreate",
    "ProjectTimesheetEntryListResponse",
    "ProjectTimesheetEntryResponse",
    "ProjectTimesheetEntryUpdate",
    "ProjectUpdate",
]
