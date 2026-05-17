"""项目成员路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.collaboration import (
    ProjectMemberCreate,
    ProjectMemberListResponse,
    ProjectMemberResponse,
    ProjectMemberUpdate,
)
from app.services.collaboration import project_member as service

router = APIRouter(prefix="/project-members", tags=["project members"])


@router.get("/", response_model=ProjectMemberListResponse)
def list_project_members(
    project_id: int | None = None,
    worker_id: int | None = None,
    db: Session = Depends(get_db),
):
    return service.list_project_members(project_id, worker_id, db)


@router.get("/{project_member_id}", response_model=ProjectMemberResponse)
def get_project_member(project_member_id: int, db: Session = Depends(get_db)):
    return service.get_project_member(project_member_id, db)


@router.post("/", response_model=ProjectMemberResponse, status_code=201)
def create_project_member(data: ProjectMemberCreate, db: Session = Depends(get_db)):
    return service.create_project_member(data, db)


@router.put("/{project_member_id}", response_model=ProjectMemberResponse)
def update_project_member(
    project_member_id: int,
    data: ProjectMemberUpdate,
    db: Session = Depends(get_db),
):
    return service.update_project_member(project_member_id, data, db)


@router.delete("/{project_member_id}")
def delete_project_member(project_member_id: int, db: Session = Depends(get_db)):
    return service.delete_project_member(project_member_id, db)
