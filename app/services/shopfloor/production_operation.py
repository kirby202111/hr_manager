"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.shopfloor import production_operation as production_operation_repo
from app.repositories.shopfloor import production_order as production_order_repo
from app.repositories.shopfloor import workstation as workstation_repo
from app.schemas.shopfloor import (
    ProductionOperationCreate,
    ProductionOperationListResponse,
    ProductionOperationResponse,
    ProductionOperationUpdate,
)


def _to_response(row: dict) -> ProductionOperationResponse:
    return ProductionOperationResponse(**row)


def _require_row(production_operation_id: int, db: Session | None = None) -> dict:
    row = production_operation_repo.get_production_operation_by_id(production_operation_id, db)
    if row is None:
        raise NotFoundError(f"Production operation {production_operation_id} not found")
    return row


def _exists_duplicate(payload: dict, db: Session | None = None, exclude_id: int | None = None) -> bool:
    rows = production_operation_repo.list_production_operations(payload["production_order_id"], None, None, db)
    for row in rows:
        if exclude_id is not None and row["id"] == exclude_id:
            continue
        if row["sequence_number"] == payload["sequence_number"]:
            return True
    return False


def list_production_operations(
    production_order_id: int | None = None,
    workstation_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> ProductionOperationListResponse:
    rows = production_operation_repo.list_production_operations(production_order_id, workstation_id, status, db)
    return ProductionOperationListResponse(production_operations=[_to_response(row) for row in rows], total=len(rows))


def get_production_operation(production_operation_id: int, db: Session | None = None) -> ProductionOperationResponse:
    return _to_response(_require_row(production_operation_id, db))


def create_production_operation(
    data: ProductionOperationCreate,
    db: Session | None = None,
) -> ProductionOperationResponse:
    if production_order_repo.get_production_order_by_id(data.production_order_id, db) is None:
        raise NotFoundError(f"Production order {data.production_order_id} not found")
    if workstation_repo.get_workstation_by_id(data.workstation_id, db) is None:
        raise NotFoundError(f"Workstation {data.workstation_id} not found")
    if _exists_duplicate(data.model_dump(), db):
        raise ConflictError("Production operation sequence already exists in production order")
    row = production_operation_repo.create_production_operation(data.model_dump(), db)
    return _to_response(row)


def update_production_operation(
    production_operation_id: int,
    data: ProductionOperationUpdate,
    db: Session | None = None,
) -> ProductionOperationResponse:
    current = _require_row(production_operation_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if production_order_repo.get_production_order_by_id(payload["production_order_id"], db) is None:
        raise NotFoundError(f"Production order {payload['production_order_id']} not found")
    if workstation_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if _exists_duplicate(payload, db, exclude_id=production_operation_id):
        raise ConflictError("Production operation sequence already exists in production order")
    row = production_operation_repo.update_production_operation(
        production_operation_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Production operation {production_operation_id} not found")
    return _to_response(row)


def delete_production_operation(production_operation_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(production_operation_id, db)
    production_operation_repo.delete_production_operation(production_operation_id, db)
    return {"message": f"Production operation {production_operation_id} deleted"}
