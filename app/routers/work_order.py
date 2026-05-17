from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import shopfloor as s
from app.services import work_order as svc
from app.services.shopfloor_support import get_record, list_response

router = APIRouter(tags=["production orders"])


@router.post("/production-orders", status_code=201)
def create_order(data: s.ProductionOrderCreate, db: Session = Depends(get_db)):
    return svc.create_order(data, db)


@router.get("/production-orders", response_model=s.ListResponse)
def list_orders(db: Session = Depends(get_db)):
    return list_response("production_order", db=db)


@router.get("/production-orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    return get_record("production_order", order_id, db)


@router.patch("/production-orders/{order_id}")
def update_order(order_id: int, data: s.ProductionOrderUpdate, db: Session = Depends(get_db)):
    return svc.update_order(order_id, data, db)


@router.post("/production-orders/{order_id}/operations", status_code=201)
def create_operation(order_id: int, data: s.ProductionOrderOperationCreate, db: Session = Depends(get_db)):
    return svc.create_operation(order_id, data, db)


@router.get("/production-orders/{order_id}/operations", response_model=s.ListResponse)
def list_operations(order_id: int, db: Session = Depends(get_db)):
    return list_response("production_order_operation", {"order_id": order_id}, db)


@router.get("/production-orders/{order_id}/staffing-context")
def order_staffing_context(order_id: int, db: Session = Depends(get_db)):
    return svc.staffing_context(order_id, db)
