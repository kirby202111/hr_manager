from datetime import date, datetime, timezone

from fastapi import HTTPException

from app.repositories import employee as employee_repo
from app.repositories import project as project_repo
from app.repositories import skill_catalog as catalog_repo
from app.schemas.project import (
    MemberWorkload,
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
    RequirementProgress,
)

VALID_STATUSES = {"planning", "active", "completed"}
VALID_PROFICIENCIES = {"beginner", "intermediate", "advanced", "expert"}


def _enrich_project(p: dict) -> dict:
    p["skill_requirement_count"] = project_repo.count_requirements(p["id"])
    p["member_count"] = project_repo.count_members(p["id"])
    return p


def _enrich_requirement(r: dict) -> dict:
    catalog = catalog_repo.get_skill_by_id(r["skill_id"])
    r["skill_name"] = catalog["name"] if catalog else "未知"
    r["skill_category"] = catalog["category"] if catalog else None
    return r


def _enrich_member(m: dict) -> dict:
    emp = employee_repo.get_employee_by_id(m["employee_id"])
    m["employee_name"] = emp["name"] if emp else None
    return m


def _enrich_timesheet(t: dict) -> dict:
    emp = employee_repo.get_employee_by_id(t["employee_id"])
    t["employee_name"] = emp["name"] if emp else None
    req = project_repo.get_requirement_by_id(t["requirement_id"])
    if req:
        catalog = catalog_repo.get_skill_by_id(req["skill_id"])
        t["skill_name"] = catalog["name"] if catalog else "未知"
    else:
        t["skill_name"] = None
    return t


# ── Project ──────────────────────────────────────────────────

def list_projects(status: str | None = None) -> ProjectListResponse:
    projects = project_repo.get_all_projects(status)
    return ProjectListResponse(
        projects=[ProjectResponse(**_enrich_project(p)) for p in projects],
        total=len(projects),
    )


def get_project(project_id: int) -> ProjectResponse:
    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    return ProjectResponse(**_enrich_project(project))


def create_project(project_in: ProjectCreate) -> ProjectResponse:
    if project_in.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"无效的项目状态，可选值: {', '.join(VALID_STATUSES)}")
    if project_in.start_date and project_in.end_date and project_in.end_date < project_in.start_date:
        raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
    project_data = project_in.model_dump()
    project_data["created_at"] = datetime.now(timezone.utc)
    project = project_repo.create_project(project_data)
    return ProjectResponse(**_enrich_project(project))


def update_project(project_id: int, project_in: ProjectUpdate) -> ProjectResponse:
    existing = project_repo.get_project_by_id(project_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    if project_in.status is not None and project_in.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"无效的项目状态，可选值: {', '.join(VALID_STATUSES)}")
    update_data = project_in.model_dump(exclude_unset=True)
    if "status" in update_data and update_data.get("status") and update_data.get("start_date") is None and update_data.get("end_date") is None:
        start = update_data.get("start_date") or existing.get("start_date")
        end = update_data.get("end_date") or existing.get("end_date")
        if start and end and end < start:
            raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
    project = project_repo.update_project(project_id, update_data)
    return ProjectResponse(**_enrich_project(project))


def delete_project(project_id: int) -> dict:
    existing = project_repo.get_project_by_id(project_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    if existing["status"] == "active":
        raise HTTPException(status_code=400, detail="活跃项目无法删除，请先变更项目状态")
    project_repo.delete_project(project_id)
    return {"message": "项目已删除"}


# ── ProjectSkillRequirement ──────────────────────────────────

def list_skill_requirements(project_id: int) -> ProjectSkillRequirementListResponse:
    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    reqs = project_repo.get_requirements_by_project(project_id)
    return ProjectSkillRequirementListResponse(
        requirements=[ProjectSkillRequirementResponse(**_enrich_requirement(r)) for r in reqs],
        total=len(reqs),
    )


def create_skill_requirement(project_id: int, req_in: ProjectSkillRequirementCreate) -> ProjectSkillRequirementResponse:
    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    catalog = catalog_repo.get_skill_by_id(req_in.skill_id)
    if catalog is None:
        raise HTTPException(status_code=400, detail=f"技能目录 {req_in.skill_id} 不存在")
    if req_in.required_proficiency not in VALID_PROFICIENCIES:
        raise HTTPException(status_code=400, detail=f"无效的熟练程度，可选值: {', '.join(VALID_PROFICIENCIES)}")
    if req_in.person_days <= 0:
        raise HTTPException(status_code=400, detail="工时预算必须大于0")
    if req_in.headcount <= 0:
        raise HTTPException(status_code=400, detail="所需人数必须大于0")
    dup = project_repo.get_requirement_by_project_and_skill(project_id, req_in.skill_id)
    if dup:
        raise HTTPException(status_code=400, detail="该项目已存在该技能需求")
    req_data = req_in.model_dump()
    req_data["project_id"] = project_id
    req_data["created_at"] = datetime.now(timezone.utc)
    req = project_repo.create_requirement(req_data)
    return ProjectSkillRequirementResponse(**_enrich_requirement(req))


def update_skill_requirement(project_id: int, req_id: int, req_in: ProjectSkillRequirementUpdate) -> ProjectSkillRequirementResponse:
    existing = project_repo.get_requirement_by_id(req_id)
    if existing is None or existing["project_id"] != project_id:
        raise HTTPException(status_code=404, detail=f"技能需求 {req_id} 不存在")
    if req_in.required_proficiency is not None and req_in.required_proficiency not in VALID_PROFICIENCIES:
        raise HTTPException(status_code=400, detail=f"无效的熟练程度，可选值: {', '.join(VALID_PROFICIENCIES)}")
    if req_in.person_days is not None and req_in.person_days <= 0:
        raise HTTPException(status_code=400, detail="工时预算必须大于0")
    if req_in.headcount is not None and req_in.headcount <= 0:
        raise HTTPException(status_code=400, detail="所需人数必须大于0")
    update_data = req_in.model_dump(exclude_unset=True)
    req = project_repo.update_requirement(req_id, update_data)
    return ProjectSkillRequirementResponse(**_enrich_requirement(req))


def delete_skill_requirement(project_id: int, req_id: int) -> dict:
    existing = project_repo.get_requirement_by_id(req_id)
    if existing is None or existing["project_id"] != project_id:
        raise HTTPException(status_code=404, detail=f"技能需求 {req_id} 不存在")
    project_repo.delete_requirement(req_id)
    return {"message": "技能需求已删除"}


# ── ProjectMember ────────────────────────────────────────────

def list_members(project_id: int) -> ProjectMemberListResponse:
    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    members = project_repo.get_members_by_project(project_id)
    return ProjectMemberListResponse(
        members=[ProjectMemberResponse(**_enrich_member(m)) for m in members],
        total=len(members),
    )


def create_member(project_id: int, member_in: ProjectMemberCreate) -> ProjectMemberResponse:
    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    emp = employee_repo.get_employee_by_id(member_in.employee_id)
    if emp is None:
        raise HTTPException(status_code=400, detail=f"员工 {member_in.employee_id} 不存在")
    dup = project_repo.get_member_by_employee_project(member_in.employee_id, project_id)
    if dup:
        raise HTTPException(status_code=400, detail="该员工已在此项目中")
    member_data = member_in.model_dump()
    member_data["project_id"] = project_id
    member_data["created_at"] = datetime.now(timezone.utc)
    member = project_repo.create_member(member_data)
    return ProjectMemberResponse(**_enrich_member(member))


def update_member(project_id: int, member_id: int, member_in: ProjectMemberUpdate) -> ProjectMemberResponse:
    existing = project_repo.get_member_by_id(member_id)
    if existing is None or existing["project_id"] != project_id:
        raise HTTPException(status_code=404, detail=f"项目成员 {member_id} 不存在")
    update_data = member_in.model_dump(exclude_unset=True)
    member = project_repo.update_member(member_id, update_data)
    return ProjectMemberResponse(**_enrich_member(member))


def delete_member(project_id: int, member_id: int) -> dict:
    existing = project_repo.get_member_by_id(member_id)
    if existing is None or existing["project_id"] != project_id:
        raise HTTPException(status_code=404, detail=f"项目成员 {member_id} 不存在")
    project_repo.delete_member(member_id)
    return {"message": "项目成员已移除"}


# ── ProjectTimesheet ─────────────────────────────────────────

def list_timesheets(project_id: int, employee_id: int | None = None, requirement_id: int | None = None) -> ProjectTimesheetListResponse:
    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    timesheets = project_repo.get_timesheets_by_project(project_id, employee_id, requirement_id)
    return ProjectTimesheetListResponse(
        timesheets=[ProjectTimesheetResponse(**_enrich_timesheet(t)) for t in timesheets],
        total=len(timesheets),
    )


def create_timesheet(project_id: int, ts_in: ProjectTimesheetCreate) -> ProjectTimesheetResponse:
    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    req = project_repo.get_requirement_by_id(ts_in.requirement_id)
    if req is None or req["project_id"] != project_id:
        raise HTTPException(status_code=400, detail=f"技能需求 {ts_in.requirement_id} 不属于该项目")
    emp = employee_repo.get_employee_by_id(ts_in.employee_id)
    if emp is None:
        raise HTTPException(status_code=400, detail=f"员工 {ts_in.employee_id} 不存在")
    member = project_repo.get_member_by_employee_project(ts_in.employee_id, project_id)
    if member is None:
        raise HTTPException(status_code=400, detail="该员工不是项目成员，无法记录工时")
    if ts_in.hours <= 0:
        raise HTTPException(status_code=400, detail="工时必须大于0")
    if ts_in.date > date.today():
        raise HTTPException(status_code=400, detail="工时日期不能在未来")
    ts_data = ts_in.model_dump()
    ts_data["project_id"] = project_id
    ts_data["created_at"] = datetime.now(timezone.utc)
    ts = project_repo.create_timesheet(ts_data)
    return ProjectTimesheetResponse(**_enrich_timesheet(ts))


def update_timesheet(project_id: int, timesheet_id: int, ts_in: ProjectTimesheetUpdate) -> ProjectTimesheetResponse:
    existing = project_repo.get_timesheet_by_id(timesheet_id)
    if existing is None or existing["project_id"] != project_id:
        raise HTTPException(status_code=404, detail=f"工时记录 {timesheet_id} 不存在")
    if ts_in.requirement_id is not None:
        req = project_repo.get_requirement_by_id(ts_in.requirement_id)
        if req is None or req["project_id"] != project_id:
            raise HTTPException(status_code=400, detail=f"技能需求 {ts_in.requirement_id} 不属于该项目")
    if ts_in.employee_id is not None:
        member = project_repo.get_member_by_employee_project(ts_in.employee_id, project_id)
        if member is None:
            raise HTTPException(status_code=400, detail="该员工不是项目成员")
    if ts_in.hours is not None and ts_in.hours <= 0:
        raise HTTPException(status_code=400, detail="工时必须大于0")
    if ts_in.date is not None and ts_in.date > date.today():
        raise HTTPException(status_code=400, detail="工时日期不能在未来")
    update_data = ts_in.model_dump(exclude_unset=True)
    ts = project_repo.update_timesheet(timesheet_id, update_data)
    return ProjectTimesheetResponse(**_enrich_timesheet(ts))


def delete_timesheet(project_id: int, timesheet_id: int) -> dict:
    existing = project_repo.get_timesheet_by_id(timesheet_id)
    if existing is None or existing["project_id"] != project_id:
        raise HTTPException(status_code=404, detail=f"工时记录 {timesheet_id} 不存在")
    project_repo.delete_timesheet(timesheet_id)
    return {"message": "工时记录已删除"}


# ── ProjectProgress ──────────────────────────────────────────

def get_project_progress(project_id: int) -> ProjectProgressResponse:
    project = project_repo.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    progress = project_repo.get_progress_by_project(project_id)

    by_requirement = []
    for r in progress["by_requirement"]:
        catalog = catalog_repo.get_skill_by_id(r["skill_id"])
        by_requirement.append(RequirementProgress(
            requirement_id=r["requirement_id"],
            skill_name=catalog["name"] if catalog else "未知",
            budget_person_days=r["budget_person_days"],
            used_person_days=r["used_person_days"],
            progress=r["progress"],
        ))

    by_member = []
    for m in progress["by_member"]:
        emp = employee_repo.get_employee_by_id(m["employee_id"])
        by_member.append(MemberWorkload(
            employee_id=m["employee_id"],
            employee_name=emp["name"] if emp else None,
            total_person_days=m["total_person_days"],
        ))

    return ProjectProgressResponse(
        project_id=project_id,
        total_budget_person_days=progress["total_budget_person_days"],
        total_used_person_days=progress["total_used_person_days"],
        overall_progress=progress["overall_progress"],
        by_requirement=by_requirement,
        by_member=by_member,
    )
