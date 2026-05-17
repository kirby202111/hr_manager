"""工单工序路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shopfloor import (
    ProductionOperationCreate,
    ProductionOperationListResponse,
    ProductionOperationResponse,
    ProductionOperationUpdate,
)
from app.services.shopfloor import production_operation as service

router = APIRouter(prefix="/production-operations", tags=["production operations"])


@router.get("/", response_model=ProductionOperationListResponse)
def list_production_operations(
    production_order_id: int | None = None,
    workstation_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_production_operations(production_order_id, workstation_id, status, db)


@router.get("/{production_operation_id}", response_model=ProductionOperationResponse)
def get_production_operation(production_operation_id: int, db: Session = Depends(get_db)):
    return service.get_production_operation(production_operation_id, db)


@router.post("/", response_model=ProductionOperationResponse, status_code=201)
def create_production_operation(data: ProductionOperationCreate, db: Session = Depends(get_db)):
    return service.create_production_operation(data, db)


@router.put("/{production_operation_id}", response_model=ProductionOperationResponse)
def update_production_operation(
    production_operation_id: int,
    data: ProductionOperationUpdate,
    db: Session = Depends(get_db),
):
    return service.update_production_operation(production_operation_id, data, db)


@router.delete("/{production_operation_id}")
def delete_production_operation(production_operation_id: int, db: Session = Depends(get_db)):
    return service.delete_production_operation(production_operation_id, db)
