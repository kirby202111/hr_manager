"""项目工时记录路由。"""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.collaboration import (
    ProjectTimesheetEntryCreate,
    ProjectTimesheetEntryListResponse,
    ProjectTimesheetEntryResponse,
    ProjectTimesheetEntryUpdate,
)
from app.services.collaboration import project_timesheet_entry as service

router = APIRouter(prefix="/project-timesheet-entries", tags=["project timesheet entries"])


@router.get("/", response_model=ProjectTimesheetEntryListResponse)
def list_project_timesheet_entries(
    project_id: int | None = None,
    worker_id: int | None = None,
    project_skill_requirement_id: int | None = None,
    work_date: date | None = None,
    db: Session = Depends(get_db),
):
    return service.list_project_timesheet_entries(
        project_id,
        worker_id,
        project_skill_requirement_id,
        work_date,
        db,
    )


@router.get("/{project_timesheet_entry_id}", response_model=ProjectTimesheetEntryResponse)
def get_project_timesheet_entry(project_timesheet_entry_id: int, db: Session = Depends(get_db)):
    return service.get_project_timesheet_entry(project_timesheet_entry_id, db)


@router.post("/", response_model=ProjectTimesheetEntryResponse, status_code=201)
def create_project_timesheet_entry(
    data: ProjectTimesheetEntryCreate,
    db: Session = Depends(get_db),
):
    return service.create_project_timesheet_entry(data, db)


@router.put("/{project_timesheet_entry_id}", response_model=ProjectTimesheetEntryResponse)
def update_project_timesheet_entry(
    project_timesheet_entry_id: int,
    data: ProjectTimesheetEntryUpdate,
    db: Session = Depends(get_db),
):
    return service.update_project_timesheet_entry(project_timesheet_entry_id, data, db)


@router.delete("/{project_timesheet_entry_id}")
def delete_project_timesheet_entry(project_timesheet_entry_id: int, db: Session = Depends(get_db)):
    return service.delete_project_timesheet_entry(project_timesheet_entry_id, db)
