"""生产工单路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shopfloor import (
    ProductionOrderCreate,
    ProductionOrderListResponse,
    ProductionOrderResponse,
    ProductionOrderUpdate,
)
from app.services.shopfloor import production_order as service

router = APIRouter(prefix="/production-orders", tags=["production orders"])


@router.get("/", response_model=ProductionOrderListResponse)
def list_production_orders(
    production_line_id: int | None = None,
    order_number: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_production_orders(production_line_id, order_number, status, db)


@router.get("/{production_order_id}", response_model=ProductionOrderResponse)
def get_production_order(production_order_id: int, db: Session = Depends(get_db)):
    return service.get_production_order(production_order_id, db)


@router.post("/", response_model=ProductionOrderResponse, status_code=201)
def create_production_order(data: ProductionOrderCreate, db: Session = Depends(get_db)):
    return service.create_production_order(data, db)


@router.put("/{production_order_id}", response_model=ProductionOrderResponse)
def update_production_order(
    production_order_id: int,
    data: ProductionOrderUpdate,
    db: Session = Depends(get_db),
):
    return service.update_production_order(production_order_id, data, db)


@router.delete("/{production_order_id}")
def delete_production_order(production_order_id: int, db: Session = Depends(get_db)):
    return service.delete_production_order(production_order_id, db)
