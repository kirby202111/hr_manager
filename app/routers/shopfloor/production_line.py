"""产线路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shopfloor import (
    ProductionLineCreate,
    ProductionLineListResponse,
    ProductionLineResponse,
    ProductionLineUpdate,
)
from app.services.shopfloor import production_line as service

router = APIRouter(prefix="/production-lines", tags=["production lines"])


@router.get("/", response_model=ProductionLineListResponse)
def list_production_lines(
    organization_unit_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_production_lines(organization_unit_id, code, status, db)


@router.get("/{production_line_id}", response_model=ProductionLineResponse)
def get_production_line(production_line_id: int, db: Session = Depends(get_db)):
    return service.get_production_line(production_line_id, db)


@router.post("/", response_model=ProductionLineResponse, status_code=201)
def create_production_line(data: ProductionLineCreate, db: Session = Depends(get_db)):
    return service.create_production_line(data, db)


@router.put("/{production_line_id}", response_model=ProductionLineResponse)
def update_production_line(
    production_line_id: int,
    data: ProductionLineUpdate,
    db: Session = Depends(get_db),
):
    return service.update_production_line(production_line_id, data, db)


@router.delete("/{production_line_id}")
def delete_production_line(production_line_id: int, db: Session = Depends(get_db)):
    return service.delete_production_line(production_line_id, db)
