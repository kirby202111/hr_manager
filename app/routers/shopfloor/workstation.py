"""工位路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shopfloor import WorkstationCreate, WorkstationListResponse, WorkstationResponse, WorkstationUpdate
from app.services.shopfloor import workstation as service

router = APIRouter(prefix="/workstations", tags=["workstations"])


@router.get("/", response_model=WorkstationListResponse)
def list_workstations(
    production_line_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_workstations(production_line_id, code, status, db)


@router.get("/{workstation_id}", response_model=WorkstationResponse)
def get_workstation(workstation_id: int, db: Session = Depends(get_db)):
    return service.get_workstation(workstation_id, db)


@router.post("/", response_model=WorkstationResponse, status_code=201)
def create_workstation(data: WorkstationCreate, db: Session = Depends(get_db)):
    return service.create_workstation(data, db)


@router.put("/{workstation_id}", response_model=WorkstationResponse)
def update_workstation(workstation_id: int, data: WorkstationUpdate, db: Session = Depends(get_db)):
    return service.update_workstation(workstation_id, data, db)


@router.delete("/{workstation_id}")
def delete_workstation(workstation_id: int, db: Session = Depends(get_db)):
    return service.delete_workstation(workstation_id, db)
