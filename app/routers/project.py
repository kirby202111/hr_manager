from fastapi import APIRouter

from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectMemberCreate,
    ProjectMemberListResponse,
    ProjectMemberResponse,
    ProjectMemberUpdate,
    ProjectProgressResponse,
    ProjectResponse,
    ProjectSkillRequirementCreate,
    ProjectSkillRequirementListResponse,
    ProjectSkillRequirementResponse,
    ProjectSkillRequirementUpdate,
    ProjectTimesheetCreate,
    ProjectTimesheetListResponse,
    ProjectTimesheetResponse,
    ProjectTimesheetUpdate,
    ProjectUpdate,
)
from app.services import project as project_service

router = APIRouter(prefix="/projects", tags=["项目管理"])


# ── Project ──────────────────────────────────────────────────

@router.get("/", response_model=ProjectListResponse)
def list_projects(status: str | None = None):
    return project_service.list_projects(status)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int):
    return project_service.get_project(project_id)


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(project_in: ProjectCreate):
    return project_service.create_project(project_in)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_in: ProjectUpdate):
    return project_service.update_project(project_id, project_in)


@router.delete("/{project_id}")
def delete_project(project_id: int):
    return project_service.delete_project(project_id)


# ── Skill Requirements ───────────────────────────────────────

@router.get("/{project_id}/skill-requirements", response_model=ProjectSkillRequirementListResponse, tags=["项目技能需求"])
def list_skill_requirements(project_id: int):
    return project_service.list_skill_requirements(project_id)


@router.post("/{project_id}/skill-requirements", response_model=ProjectSkillRequirementResponse, status_code=201, tags=["项目技能需求"])
def create_skill_requirement(project_id: int, req_in: ProjectSkillRequirementCreate):
    return project_service.create_skill_requirement(project_id, req_in)


@router.put("/{project_id}/skill-requirements/{req_id}", response_model=ProjectSkillRequirementResponse, tags=["项目技能需求"])
def update_skill_requirement(project_id: int, req_id: int, req_in: ProjectSkillRequirementUpdate):
    return project_service.update_skill_requirement(project_id, req_id, req_in)


@router.delete("/{project_id}/skill-requirements/{req_id}", tags=["项目技能需求"])
def delete_skill_requirement(project_id: int, req_id: int):
    return project_service.delete_skill_requirement(project_id, req_id)


# ── Members ──────────────────────────────────────────────────

@router.get("/{project_id}/members", response_model=ProjectMemberListResponse, tags=["项目成员管理"])
def list_members(project_id: int):
    return project_service.list_members(project_id)


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=201, tags=["项目成员管理"])
def create_member(project_id: int, member_in: ProjectMemberCreate):
    return project_service.create_member(project_id, member_in)


@router.put("/{project_id}/members/{member_id}", response_model=ProjectMemberResponse, tags=["项目成员管理"])
def update_member(project_id: int, member_id: int, member_in: ProjectMemberUpdate):
    return project_service.update_member(project_id, member_id, member_in)


@router.delete("/{project_id}/members/{member_id}", tags=["项目成员管理"])
def delete_member(project_id: int, member_id: int):
    return project_service.delete_member(project_id, member_id)


# ── Timesheets ───────────────────────────────────────────────

@router.get("/{project_id}/timesheets", response_model=ProjectTimesheetListResponse, tags=["项目工时记录"])
def list_timesheets(project_id: int, employee_id: int | None = None, requirement_id: int | None = None):
    return project_service.list_timesheets(project_id, employee_id, requirement_id)


@router.post("/{project_id}/timesheets", response_model=ProjectTimesheetResponse, status_code=201, tags=["项目工时记录"])
def create_timesheet(project_id: int, ts_in: ProjectTimesheetCreate):
    return project_service.create_timesheet(project_id, ts_in)


@router.put("/{project_id}/timesheets/{timesheet_id}", response_model=ProjectTimesheetResponse, tags=["项目工时记录"])
def update_timesheet(project_id: int, timesheet_id: int, ts_in: ProjectTimesheetUpdate):
    return project_service.update_timesheet(project_id, timesheet_id, ts_in)


@router.delete("/{project_id}/timesheets/{timesheet_id}", tags=["项目工时记录"])
def delete_timesheet(project_id: int, timesheet_id: int):
    return project_service.delete_timesheet(project_id, timesheet_id)


# ── Progress ─────────────────────────────────────────────────

@router.get("/{project_id}/progress", response_model=ProjectProgressResponse, tags=["项目进度"])
def get_project_progress(project_id: int):
    return project_service.get_project_progress(project_id)
