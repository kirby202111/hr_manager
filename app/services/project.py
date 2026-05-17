from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import worker as employee_repo
from app.repositories import project as project_repo
from app.repositories import skill_definition as catalog_repo
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


def _validate_status(status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValidationError(f"鏃犳晥鐨勯」鐩姸鎬侊紝鍙€夊€? {', '.join(sorted(VALID_STATUSES))}")


def _validate_proficiency(level: str) -> None:
    if level not in VALID_PROFICIENCIES:
        raise ValidationError(f"鏃犳晥鐨勭啛缁冪▼搴︼紝鍙€夊€? {', '.join(sorted(VALID_PROFICIENCIES))}")


def _enrich_project(p: dict, db: Session | None = None) -> dict:
    p["skill_requirement_count"] = project_repo.count_requirements(p["id"], db)
    p["member_count"] = project_repo.count_members(p["id"], db)
    return p


def _enrich_requirement(r: dict, db: Session | None = None) -> dict:
    catalog = catalog_repo.get_skill_by_id(r["skill_id"], db)
    r["skill_name"] = catalog["name"] if catalog else "Unknown"
    r["skill_category"] = catalog["category"] if catalog else None
    return r


def _enrich_member(m: dict, db: Session | None = None) -> dict:
    emp = employee_repo.get_worker_by_id(m["employee_id"], db)
    m["employee_name"] = emp["name"] if emp else None
    return m


def _enrich_timesheet(t: dict, db: Session | None = None) -> dict:
    emp = employee_repo.get_worker_by_id(t["employee_id"], db)
    t["employee_name"] = emp["name"] if emp else None
    req = project_repo.get_requirement_by_id(t["requirement_id"], db)
    if req:
        catalog = catalog_repo.get_skill_by_id(req["skill_id"], db)
        t["skill_name"] = catalog["name"] if catalog else "Unknown"
    else:
        t["skill_name"] = None
    return t


def list_projects(status: str | None = None, db: Session | None = None) -> ProjectListResponse:
    projects = project_repo.get_all_projects(status, db)
    return ProjectListResponse(
        projects=[ProjectResponse(**_enrich_project(p, db)) for p in projects],
        total=len(projects),
    )


def get_project(project_id: int, db: Session | None = None) -> ProjectResponse:
    project = project_repo.get_project_by_id(project_id, db)
    if project is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    return ProjectResponse(**_enrich_project(project, db))


def create_project(project_in: ProjectCreate, db: Session | None = None) -> ProjectResponse:
    _validate_status(project_in.status)
    if project_in.start_date and project_in.end_date and project_in.end_date < project_in.start_date:
        raise ValidationError("缁撴潫鏃ユ湡涓嶈兘鏃╀簬寮€濮嬫棩鏈?)
    project_data = project_in.model_dump()
    project_data["created_at"] = datetime.now(UTC)
    project = project_repo.create_project(project_data, db)
    return ProjectResponse(**_enrich_project(project, db))


def update_project(project_id: int, project_in: ProjectUpdate, db: Session | None = None) -> ProjectResponse:
    existing = project_repo.get_project_by_id(project_id, db)
    if existing is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    if project_in.status is not None:
        _validate_status(project_in.status)
    update_data = project_in.model_dump(exclude_unset=True)
    start = update_data.get("start_date", existing.get("start_date"))
    end = update_data.get("end_date", existing.get("end_date"))
    if start and end and end < start:
        raise ValidationError("缁撴潫鏃ユ湡涓嶈兘鏃╀簬寮€濮嬫棩鏈?)
    project = project_repo.update_project(project_id, update_data, db)
    return ProjectResponse(**_enrich_project(project, db))


def delete_project(project_id: int, db: Session | None = None) -> dict:
    existing = project_repo.get_project_by_id(project_id, db)
    if existing is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    if existing["status"] == "active":
        raise ValidationError("娲昏穬椤圭洰鏃犳硶鍒犻櫎")
    project_repo.delete_project(project_id, db)
    return {"message": "椤圭洰宸插垹闄?}


def list_skill_requirements(project_id: int, db: Session | None = None) -> ProjectSkillRequirementListResponse:
    if project_repo.get_project_by_id(project_id, db) is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    reqs = project_repo.get_requirements_by_project(project_id, db)
    return ProjectSkillRequirementListResponse(
        requirements=[ProjectSkillRequirementResponse(**_enrich_requirement(r, db)) for r in reqs],
        total=len(reqs),
    )


def create_skill_requirement(
    project_id: int, req_in: ProjectSkillRequirementCreate, db: Session | None = None
) -> ProjectSkillRequirementResponse:
    if project_repo.get_project_by_id(project_id, db) is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    if catalog_repo.get_skill_by_id(req_in.skill_id, db) is None:
        raise ValidationError(f"鎶€鑳界洰褰?{req_in.skill_id} 涓嶅瓨鍦?)
    _validate_proficiency(req_in.required_proficiency)
    if req_in.person_days <= 0:
        raise ValidationError("宸ユ椂棰勭畻蹇呴』澶т簬0")
    if req_in.headcount <= 0:
        raise ValidationError("鎵€闇€浜烘暟蹇呴』澶т簬0")
    if project_repo.get_requirement_by_project_and_skill(project_id, req_in.skill_id, db):
        raise ValidationError("椤圭洰宸插瓨鍦ㄨ鎶€鑳介渶姹?)
    req_data = req_in.model_dump()
    req_data["project_id"] = project_id
    req_data["created_at"] = datetime.now(UTC)
    req = project_repo.create_requirement(req_data, db)
    return ProjectSkillRequirementResponse(**_enrich_requirement(req, db))


def update_skill_requirement(
    project_id: int, req_id: int, req_in: ProjectSkillRequirementUpdate, db: Session | None = None
) -> ProjectSkillRequirementResponse:
    existing = project_repo.get_requirement_by_id(req_id, db)
    if existing is None or existing["project_id"] != project_id:
        raise NotFoundError(f"鎶€鑳介渶姹?{req_id} 涓嶅瓨鍦?)
    if req_in.required_proficiency is not None:
        _validate_proficiency(req_in.required_proficiency)
    if req_in.person_days is not None and req_in.person_days <= 0:
        raise ValidationError("宸ユ椂棰勭畻蹇呴』澶т簬0")
    if req_in.headcount is not None and req_in.headcount <= 0:
        raise ValidationError("鎵€闇€浜烘暟蹇呴』澶т簬0")
    update_data = req_in.model_dump(exclude_unset=True)
    req = project_repo.update_requirement(req_id, update_data, db)
    return ProjectSkillRequirementResponse(**_enrich_requirement(req, db))


def delete_skill_requirement(project_id: int, req_id: int, db: Session | None = None) -> dict:
    existing = project_repo.get_requirement_by_id(req_id, db)
    if existing is None or existing["project_id"] != project_id:
        raise NotFoundError(f"鎶€鑳介渶姹?{req_id} 涓嶅瓨鍦?)
    project_repo.delete_requirement(req_id, db)
    return {"message": "鎶€鑳介渶姹傚凡鍒犻櫎"}


def list_members(project_id: int, db: Session | None = None) -> ProjectMemberListResponse:
    if project_repo.get_project_by_id(project_id, db) is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    members = project_repo.get_members_by_project(project_id, db)
    return ProjectMemberListResponse(
        members=[ProjectMemberResponse(**_enrich_member(m, db)) for m in members],
        total=len(members),
    )


def create_member(project_id: int, member_in: ProjectMemberCreate, db: Session | None = None) -> ProjectMemberResponse:
    if project_repo.get_project_by_id(project_id, db) is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    if employee_repo.get_worker_by_id(member_in.employee_id, db) is None:
        raise ValidationError(f"鍛樺伐 {member_in.employee_id} 涓嶅瓨鍦?)
    if project_repo.get_member_by_employee_project(member_in.employee_id, project_id, db):
        raise ValidationError("鍛樺伐宸插湪姝ら」鐩腑")
    member_data = member_in.model_dump()
    member_data["project_id"] = project_id
    member_data["created_at"] = datetime.now(UTC)
    member = project_repo.create_member(member_data, db)
    return ProjectMemberResponse(**_enrich_member(member, db))


def update_member(
    project_id: int, member_id: int, member_in: ProjectMemberUpdate, db: Session | None = None
) -> ProjectMemberResponse:
    existing = project_repo.get_member_by_id(member_id, db)
    if existing is None or existing["project_id"] != project_id:
        raise NotFoundError(f"椤圭洰鎴愬憳 {member_id} 涓嶅瓨鍦?)
    update_data = member_in.model_dump(exclude_unset=True)
    member = project_repo.update_member(member_id, update_data, db)
    return ProjectMemberResponse(**_enrich_member(member, db))


def delete_member(project_id: int, member_id: int, db: Session | None = None) -> dict:
    existing = project_repo.get_member_by_id(member_id, db)
    if existing is None or existing["project_id"] != project_id:
        raise NotFoundError(f"椤圭洰鎴愬憳 {member_id} 涓嶅瓨鍦?)
    project_repo.delete_member(member_id, db)
    return {"message": "椤圭洰鎴愬憳宸茬Щ闄?}


def list_timesheets(
    project_id: int,
    employee_id: int | None = None,
    requirement_id: int | None = None,
    db: Session | None = None,
) -> ProjectTimesheetListResponse:
    if project_repo.get_project_by_id(project_id, db) is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    timesheets = project_repo.get_timesheets_by_project(project_id, employee_id, requirement_id, db)
    return ProjectTimesheetListResponse(
        timesheets=[ProjectTimesheetResponse(**_enrich_timesheet(t, db)) for t in timesheets],
        total=len(timesheets),
    )


def create_timesheet(
    project_id: int, ts_in: ProjectTimesheetCreate, db: Session | None = None
) -> ProjectTimesheetResponse:
    if project_repo.get_project_by_id(project_id, db) is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    req = project_repo.get_requirement_by_id(ts_in.requirement_id, db)
    if req is None or req["project_id"] != project_id:
        raise ValidationError(f"鎶€鑳介渶姹?{ts_in.requirement_id} 涓嶅睘浜庤椤圭洰")
    if employee_repo.get_worker_by_id(ts_in.employee_id, db) is None:
        raise ValidationError(f"鍛樺伐 {ts_in.employee_id} 涓嶅瓨鍦?)
    if project_repo.get_member_by_employee_project(ts_in.employee_id, project_id, db) is None:
        raise ValidationError("鍛樺伐涓嶆槸椤圭洰鎴愬憳")
    if ts_in.hours <= 0:
        raise ValidationError("宸ユ椂蹇呴』澶т簬0")
    if ts_in.date > date.today():
        raise ValidationError("宸ユ椂鏃ユ湡涓嶈兘鍦ㄦ湭鏉?)
    ts_data = ts_in.model_dump()
    ts_data["project_id"] = project_id
    ts_data["created_at"] = datetime.now(UTC)
    ts = project_repo.create_timesheet(ts_data, db)
    return ProjectTimesheetResponse(**_enrich_timesheet(ts, db))


def update_timesheet(
    project_id: int, timesheet_id: int, ts_in: ProjectTimesheetUpdate, db: Session | None = None
) -> ProjectTimesheetResponse:
    existing = project_repo.get_timesheet_by_id(timesheet_id, db)
    if existing is None or existing["project_id"] != project_id:
        raise NotFoundError(f"宸ユ椂璁板綍 {timesheet_id} 涓嶅瓨鍦?)
    if ts_in.requirement_id is not None:
        req = project_repo.get_requirement_by_id(ts_in.requirement_id, db)
        if req is None or req["project_id"] != project_id:
            raise ValidationError(f"鎶€鑳介渶姹?{ts_in.requirement_id} 涓嶅睘浜庤椤圭洰")
    if (
        ts_in.employee_id is not None
        and project_repo.get_member_by_employee_project(ts_in.employee_id, project_id, db) is None
    ):
        raise ValidationError("鍛樺伐涓嶆槸椤圭洰鎴愬憳")
    if ts_in.hours is not None and ts_in.hours <= 0:
        raise ValidationError("宸ユ椂蹇呴』澶т簬0")
    if ts_in.date is not None and ts_in.date > date.today():
        raise ValidationError("宸ユ椂鏃ユ湡涓嶈兘鍦ㄦ湭鏉?)
    update_data = ts_in.model_dump(exclude_unset=True)
    ts = project_repo.update_timesheet(timesheet_id, update_data, db)
    return ProjectTimesheetResponse(**_enrich_timesheet(ts, db))


def delete_timesheet(project_id: int, timesheet_id: int, db: Session | None = None) -> dict:
    existing = project_repo.get_timesheet_by_id(timesheet_id, db)
    if existing is None or existing["project_id"] != project_id:
        raise NotFoundError(f"宸ユ椂璁板綍 {timesheet_id} 涓嶅瓨鍦?)
    project_repo.delete_timesheet(timesheet_id, db)
    return {"message": "宸ユ椂璁板綍宸插垹闄?}


def get_project_progress(project_id: int, db: Session | None = None) -> ProjectProgressResponse:
    if project_repo.get_project_by_id(project_id, db) is None:
        raise NotFoundError(f"椤圭洰 {project_id} 涓嶅瓨鍦?)
    progress = project_repo.get_progress_by_project(project_id, db)

    by_requirement = []
    for r in progress["by_requirement"]:
        catalog = catalog_repo.get_skill_by_id(r["skill_id"], db)
        by_requirement.append(
            RequirementProgress(
                requirement_id=r["requirement_id"],
                skill_name=catalog["name"] if catalog else "Unknown",
                budget_person_days=r["budget_person_days"],
                used_person_days=r["used_person_days"],
                progress=r["progress"],
            )
        )

    by_member = []
    for m in progress["by_member"]:
        emp = employee_repo.get_worker_by_id(m["employee_id"], db)
        by_member.append(
            MemberWorkload(
                employee_id=m["employee_id"],
                employee_name=emp["name"] if emp else None,
                total_person_days=m["total_person_days"],
            )
        )

    return ProjectProgressResponse(
        project_id=project_id,
        total_budget_person_days=progress["total_budget_person_days"],
        total_used_person_days=progress["total_used_person_days"],
        overall_progress=progress["overall_progress"],
        by_requirement=by_requirement,
        by_member=by_member,
    )

