"""Production schemas."""

from datetime import date, datetime

from pydantic import BaseModel


class ProductionOrderCreate(BaseModel):
    order_number: str
    production_line_id: int | None = None
    product_code: str
    product_name: str
    planned_quantity: int
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    priority: str
    status: str = "planned"
    description: str | None = None


class ProductionOrderUpdate(BaseModel):
    order_number: str | None = None
    production_line_id: int | None = None
    product_code: str | None = None
    product_name: str | None = None
    planned_quantity: int | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    priority: str | None = None
    status: str | None = None
    description: str | None = None


class ProductionOrderResponse(BaseModel):
    id: int
    order_number: str
    production_line_id: int | None = None
    product_code: str
    product_name: str
    planned_quantity: int
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    priority: str
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductionOrderListResponse(BaseModel):
    production_orders: list[ProductionOrderResponse]
    total: int


class ProductionOperationCreate(BaseModel):
    production_order_id: int
    workstation_id: int
    operation_code: str
    operation_name: str
    sequence_number: int
    planned_hours: float | None = None
    required_headcount: int
    status: str = "planned"


class ProductionOperationUpdate(BaseModel):
    production_order_id: int | None = None
    workstation_id: int | None = None
    operation_code: str | None = None
    operation_name: str | None = None
    sequence_number: int | None = None
    planned_hours: float | None = None
    required_headcount: int | None = None
    status: str | None = None


class ProductionOperationResponse(BaseModel):
    id: int
    production_order_id: int
    workstation_id: int
    operation_code: str
    operation_name: str
    sequence_number: int
    planned_hours: float | None = None
    required_headcount: int
    status: str
    created_at: datetime
    updated_at: datetime


class ProductionOperationListResponse(BaseModel):
    production_operations: list[ProductionOperationResponse]
    total: int


__all__ = [
    "ProductionOperationCreate",
    "ProductionOperationListResponse",
    "ProductionOperationResponse",
    "ProductionOperationUpdate",
    "ProductionOrderCreate",
    "ProductionOrderListResponse",
    "ProductionOrderResponse",
    "ProductionOrderUpdate",
]
