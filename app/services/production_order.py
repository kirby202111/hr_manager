from sqlalchemy.orm import Session

from app.repositories import manufacturing as repo
from app.schemas import manufacturing as schemas
from app.services.manufacturing_common import (
    decode_record,
    exists,
    get_record,
    line_exists,
    require,
    stamp,
    workstation_exists,
)


def create_order(data: schemas.ProductionOrderCreate, db: Session | None = None) -> dict:
    if data.line_id is not None:
        line_exists(data.line_id, db)
    require(data.status, "order_status", "status")
    require(data.priority, "priority", "priority")
    return repo.create_record("production_order", stamp(data.model_dump()), db)


def update_order(order_id: int, data: schemas.ProductionOrderUpdate, db: Session | None = None) -> dict:
    get_record("production_order", order_id, db)
    update = data.model_dump(exclude_unset=True)
    if "line_id" in update:
        line_exists(update["line_id"], db)
    if "status" in update:
        require(update["status"], "order_status", "status")
    if "priority" in update:
        require(update["priority"], "priority", "priority")
    record = repo.update_record("production_order", order_id, stamp(update, update=True), db)
    return decode_record(record)


def create_operation(
    order_id: int,
    data: schemas.ProductionOrderOperationCreate,
    db: Session | None = None,
) -> dict:
    exists("production_order", order_id, db)
    workstation_exists(data.workstation_id, db)
    require(data.status, "operation_status", "status")
    return repo.create_record("production_order_operation", stamp(data.model_dump() | {"order_id": order_id}), db)


def staffing_context(order_id: int, db: Session | None = None) -> dict:
    order = get_record("production_order", order_id, db)
    operations = repo.list_records("production_order_operation", {"order_id": order_id}, db)
    return {"order": order, "operations": operations}
