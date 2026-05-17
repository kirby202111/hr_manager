"""产线服务。"""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories import organization as organization_repo
from app.repositories import shopfloor as shopfloor_repo
from app.repositories import workforce as workforce_repo
from app.schemas.shopfloor import (
    ProductionLineCreate,
    ProductionLineListResponse,
    ProductionLineResponse,
    ProductionLineUpdate,
)


def _to_response(row: dict) -> ProductionLineResponse:
    return ProductionLineResponse(**row)


def _require_row(production_line_id: int, db: Session | None = None) -> dict:
    row = shopfloor_repo.get_production_line_by_id(production_line_id, db)
    if row is None:
        raise NotFoundError(f"Production line {production_line_id} not found")
    return row


def list_production_lines(
    organization_unit_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> ProductionLineListResponse:
    rows = shopfloor_repo.list_production_lines(organization_unit_id, code, status, db)
    return ProductionLineListResponse(production_lines=[_to_response(row) for row in rows], total=len(rows))


def get_production_line(production_line_id: int, db: Session | None = None) -> ProductionLineResponse:
    return _to_response(_require_row(production_line_id, db))


def create_production_line(data: ProductionLineCreate, db: Session | None = None) -> ProductionLineResponse:
    if organization_repo.get_organization_unit_by_id(data.organization_unit_id, db) is None:
        raise NotFoundError(f"Organization unit {data.organization_unit_id} not found")
    if data.supervisor_worker_id is not None and workforce_repo.get_worker_by_id(data.supervisor_worker_id, db) is None:
        raise NotFoundError(f"Worker {data.supervisor_worker_id} not found")
    existing = shopfloor_repo.get_production_line_by_code(data.code, db)
    if existing is not None and existing["organization_unit_id"] == data.organization_unit_id:
        raise ConflictError("Production line code already exists in organization unit")
    row = shopfloor_repo.create_production_line(data.model_dump(), db)
    return _to_response(row)


def update_production_line(
    production_line_id: int,
    data: ProductionLineUpdate,
    db: Session | None = None,
) -> ProductionLineResponse:
    current = _require_row(production_line_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if organization_repo.get_organization_unit_by_id(payload["organization_unit_id"], db) is None:
        raise NotFoundError(f"Organization unit {payload['organization_unit_id']} not found")
    if (
        payload.get("supervisor_worker_id") is not None
        and workforce_repo.get_worker_by_id(payload["supervisor_worker_id"], db) is None
    ):
        raise NotFoundError(f"Worker {payload['supervisor_worker_id']} not found")
    existing = shopfloor_repo.get_production_line_by_code(payload["code"], db)
    if (
        existing is not None
        and existing["id"] != production_line_id
        and existing["organization_unit_id"] == payload["organization_unit_id"]
    ):
        raise ConflictError("Production line code already exists in organization unit")
    row = shopfloor_repo.update_production_line(production_line_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Production line {production_line_id} not found")
    return _to_response(row)


def delete_production_line(production_line_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(production_line_id, db)
    shopfloor_repo.delete_production_line(production_line_id, db)
    return {"message": f"Production line {production_line_id} deleted"}
