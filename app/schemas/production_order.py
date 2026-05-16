from datetime import date, datetime

from pydantic import BaseModel


class ProductionOrderCreate(BaseModel):
    order_no: str
    product_name: str
    line_id: int | None = None
    planned_quantity: int
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    status: str = "planned"
    priority: str = "normal"
    description: str | None = None


class ProductionOrderUpdate(BaseModel):
    product_name: str | None = None
    line_id: int | None = None
    planned_quantity: int | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    status: str | None = None
    priority: str | None = None
    description: str | None = None


class ProductionOrderResponse(ProductionOrderCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class ProductionOrderOperationCreate(BaseModel):
    workstation_id: int
    process_code: str
    sequence: int
    planned_hours: float | None = None
    required_headcount: int
    status: str = "planned"


class ProductionOrderOperationResponse(ProductionOrderOperationCreate):
    id: int
    order_id: int
    created_at: datetime
    updated_at: datetime
