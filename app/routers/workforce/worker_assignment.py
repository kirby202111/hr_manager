"""人员任职与归属路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.workforce import (
    WorkerAssignmentCreate,
    WorkerAssignmentListResponse,
    WorkerAssignmentResponse,
    WorkerAssignmentUpdate,
)
from app.services.workforce import worker_assignment as service

router = APIRouter(prefix="/worker-assignments", tags=["worker assignments"])


@router.get("/", response_model=WorkerAssignmentListResponse)
def list_worker_assignments(
    worker_id: int | None = None,
    organization_unit_id: int | None = None,
    production_line_id: int | None = None,
    production_team_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_worker_assignments(
        worker_id,
        organization_unit_id,
        production_line_id,
        production_team_id,
        status,
        db,
    )


@router.get("/worker/{worker_id}", response_model=WorkerAssignmentListResponse)
def list_by_worker(worker_id: int, db: Session = Depends(get_db)):
    return service.list_assignments_by_worker(worker_id, db)


@router.get("/organization-unit/{organization_unit_id}", response_model=WorkerAssignmentListResponse)
def list_by_organization_unit(organization_unit_id: int, db: Session = Depends(get_db)):
    return service.list_assignments_by_organization_unit(organization_unit_id, db)


@router.get("/production-line/{production_line_id}", response_model=WorkerAssignmentListResponse)
def list_by_production_line(production_line_id: int, db: Session = Depends(get_db)):
    return service.list_assignments_by_production_line(production_line_id, db)


@router.get("/production-team/{production_team_id}", response_model=WorkerAssignmentListResponse)
def list_by_production_team(production_team_id: int, db: Session = Depends(get_db)):
    return service.list_assignments_by_production_team(production_team_id, db)


@router.get("/{worker_assignment_id}", response_model=WorkerAssignmentResponse)
def get_worker_assignment(worker_assignment_id: int, db: Session = Depends(get_db)):
    return service.get_worker_assignment(worker_assignment_id, db)


@router.post("/", response_model=WorkerAssignmentResponse, status_code=201)
def create_worker_assignment(data: WorkerAssignmentCreate, db: Session = Depends(get_db)):
    return service.create_worker_assignment(data, db)


@router.put("/{worker_assignment_id}", response_model=WorkerAssignmentResponse)
def update_worker_assignment(
    worker_assignment_id: int,
    data: WorkerAssignmentUpdate,
    db: Session = Depends(get_db),
):
    return service.update_worker_assignment(worker_assignment_id, data, db)


@router.delete("/{worker_assignment_id}")
def delete_worker_assignment(worker_assignment_id: int, db: Session = Depends(get_db)):
    return service.delete_worker_assignment(worker_assignment_id, db)
