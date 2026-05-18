"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.production import production_order as production_order_repo
from app.repositories.shopfloor import production_line as production_line_repo
from app.schemas.production import (
    ProductionOrderCreate,
    ProductionOrderListResponse,
    ProductionOrderResponse,
    ProductionOrderUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> ProductionOrderResponse:
    return ProductionOrderResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(production_order_id: int, db: Session | None = None) -> dict:
    row = production_order_repo.get_production_order_by_id(production_order_id, db)
    if row is None:
        raise NotFoundError(f"Production order {production_order_id} not found")
    return row


def list_production_orders(
    production_line_id: int | None = None,
    order_number: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> ProductionOrderListResponse:
    rows = production_order_repo.list_production_orders(production_line_id, order_number, status, db)
    return ProductionOrderListResponse(production_orders=[_to_response(row) for row in rows], total=len(rows))


def get_production_order(production_order_id: int, db: Session | None = None) -> ProductionOrderResponse:
    return _to_response(_require_row(production_order_id, db))


def create_production_order(data: ProductionOrderCreate, db: Session | None = None) -> ProductionOrderResponse:
    if (
        data.production_line_id is not None
        and production_line_repo.get_production_line_by_id(data.production_line_id, db) is None
    ):
        raise NotFoundError(f"Production line {data.production_line_id} not found")
    if production_order_repo.get_production_order_by_order_number(data.order_number, db) is not None:
        raise ConflictError(f"Production order number '{data.order_number}' already exists")
    row = production_order_repo.create_production_order(data.model_dump(), db)
    return _to_response(row)


def update_production_order(
    production_order_id: int,
    data: ProductionOrderUpdate,
    db: Session | None = None,
) -> ProductionOrderResponse:
    current = _require_row(production_order_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if (
        payload.get("production_line_id") is not None
        and production_line_repo.get_production_line_by_id(payload["production_line_id"], db) is None
    ):
        raise NotFoundError(f"Production line {payload['production_line_id']} not found")
    existing = production_order_repo.get_production_order_by_order_number(payload["order_number"], db)
    if existing is not None and existing["id"] != production_order_id:
        raise ConflictError(f"Production order number '{payload['order_number']}' already exists")
    row = production_order_repo.update_production_order(production_order_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Production order {production_order_id} not found")
    return _to_response(row)


def delete_production_order(production_order_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(production_order_id, db)
    production_order_repo.delete_production_order(production_order_id, db)
    return {"message": f"Production order {production_order_id} deleted"}
