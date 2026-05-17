"""项目路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.collaboration import ProjectCreate, ProjectListResponse, ProjectResponse, ProjectUpdate
from app.services.collaboration import project as service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=ProjectListResponse)
def list_projects(status: str | None = None, db: Session = Depends(get_db)):
    return service.list_projects(status, db)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return service.get_project(project_id, db)


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    return service.create_project(data, db)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    return service.update_project(project_id, data, db)


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    return service.delete_project(project_id, db)
