"""Service module."""

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories.collaboration import project as project_repo
from app.repositories.collaboration import project_skill_requirement as project_skill_requirement_repo
from app.repositories.collaboration import project_timesheet_entry as project_timesheet_entry_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.collaboration import (
    ProjectTimesheetEntryCreate,
    ProjectTimesheetEntryListResponse,
    ProjectTimesheetEntryResponse,
    ProjectTimesheetEntryUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> ProjectTimesheetEntryResponse:
    return ProjectTimesheetEntryResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(project_timesheet_entry_id: int, db: Session | None = None) -> dict:
    row = project_timesheet_entry_repo.get_project_timesheet_entry_by_id(project_timesheet_entry_id, db)
    if row is None:
        raise NotFoundError(f"Project timesheet entry {project_timesheet_entry_id} not found")
    return row


# 校验关联对象与关键业务字段，避免写入非法数据。
def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if project_repo.get_project_by_id(payload["project_id"], db) is None:
        raise NotFoundError(f"Project {payload['project_id']} not found")
    if (
        project_skill_requirement_repo.get_project_skill_requirement_by_id(
            payload["project_skill_requirement_id"],
            db,
        )
        is None
    ):
        raise NotFoundError(f"Project skill requirement {payload['project_skill_requirement_id']} not found")
    if worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if payload["hours"] <= 0:
        raise ValidationError("hours must be greater than 0")


def list_project_timesheet_entries(
    project_id: int | None = None,
    worker_id: int | None = None,
    project_skill_requirement_id: int | None = None,
    work_date=None,
    db: Session | None = None,
) -> ProjectTimesheetEntryListResponse:
    rows = project_timesheet_entry_repo.list_project_timesheet_entries(
        project_id, worker_id, project_skill_requirement_id, work_date, db
    )
    return ProjectTimesheetEntryListResponse(
        project_timesheet_entries=[_to_response(row) for row in rows],
        total=len(rows),
    )


def get_project_timesheet_entry(
    project_timesheet_entry_id: int, db: Session | None = None
) -> ProjectTimesheetEntryResponse:
    return _to_response(_require_row(project_timesheet_entry_id, db))


def create_project_timesheet_entry(
    data: ProjectTimesheetEntryCreate,
    db: Session | None = None,
) -> ProjectTimesheetEntryResponse:
    payload = data.model_dump()
    _validate_payload(payload, db)
    row = project_timesheet_entry_repo.create_project_timesheet_entry(payload, db)
    return _to_response(row)


def update_project_timesheet_entry(
    project_timesheet_entry_id: int,
    data: ProjectTimesheetEntryUpdate,
    db: Session | None = None,
) -> ProjectTimesheetEntryResponse:
    current = _require_row(project_timesheet_entry_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    row = project_timesheet_entry_repo.update_project_timesheet_entry(
        project_timesheet_entry_id, data.model_dump(exclude_unset=True), db
    )
    if row is None:
        raise NotFoundError(f"Project timesheet entry {project_timesheet_entry_id} not found")
    return _to_response(row)


def delete_project_timesheet_entry(project_timesheet_entry_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(project_timesheet_entry_id, db)
    project_timesheet_entry_repo.delete_project_timesheet_entry(project_timesheet_entry_id, db)
    return {"message": f"Project timesheet entry {project_timesheet_entry_id} deleted"}
