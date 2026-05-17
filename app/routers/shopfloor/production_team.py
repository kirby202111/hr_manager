"""班组路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shopfloor import (
    ProductionTeamCreate,
    ProductionTeamListResponse,
    ProductionTeamResponse,
    ProductionTeamUpdate,
)
from app.services.shopfloor import production_team as service

router = APIRouter(prefix="/production-teams", tags=["production teams"])


@router.get("/", response_model=ProductionTeamListResponse)
def list_production_teams(
    production_line_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_production_teams(production_line_id, code, status, db)


@router.get("/{production_team_id}", response_model=ProductionTeamResponse)
def get_production_team(production_team_id: int, db: Session = Depends(get_db)):
    return service.get_production_team(production_team_id, db)


@router.post("/", response_model=ProductionTeamResponse, status_code=201)
def create_production_team(data: ProductionTeamCreate, db: Session = Depends(get_db)):
    return service.create_production_team(data, db)


@router.put("/{production_team_id}", response_model=ProductionTeamResponse)
def update_production_team(
    production_team_id: int,
    data: ProductionTeamUpdate,
    db: Session = Depends(get_db),
):
    return service.update_production_team(production_team_id, data, db)


@router.delete("/{production_team_id}")
def delete_production_team(production_team_id: int, db: Session = Depends(get_db)):
    return service.delete_production_team(production_team_id, db)
