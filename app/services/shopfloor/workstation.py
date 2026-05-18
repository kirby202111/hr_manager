"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.shopfloor import production_line as production_line_repo
from app.repositories.shopfloor import workstation as workstation_repo
from app.schemas.shopfloor import WorkstationCreate, WorkstationListResponse, WorkstationResponse, WorkstationUpdate


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> WorkstationResponse:
    return WorkstationResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(workstation_id: int, db: Session | None = None) -> dict:
    row = workstation_repo.get_workstation_by_id(workstation_id, db)
    if row is None:
        raise NotFoundError(f"Workstation {workstation_id} not found")
    return row


def list_workstations(
    production_line_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> WorkstationListResponse:
    rows = workstation_repo.list_workstations(production_line_id, code, status, db)
    return WorkstationListResponse(workstations=[_to_response(row) for row in rows], total=len(rows))


def get_workstation(workstation_id: int, db: Session | None = None) -> WorkstationResponse:
    return _to_response(_require_row(workstation_id, db))


def create_workstation(data: WorkstationCreate, db: Session | None = None) -> WorkstationResponse:
    if production_line_repo.get_production_line_by_id(data.production_line_id, db) is None:
        raise NotFoundError(f"Production line {data.production_line_id} not found")
    if workstation_repo.get_workstation_by_code(data.production_line_id, data.code, db) is not None:
        raise ConflictError("Workstation code already exists on production line")
    row = workstation_repo.create_workstation(data.model_dump(), db)
    return _to_response(row)


def update_workstation(workstation_id: int, data: WorkstationUpdate, db: Session | None = None) -> WorkstationResponse:
    current = _require_row(workstation_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if production_line_repo.get_production_line_by_id(payload["production_line_id"], db) is None:
        raise NotFoundError(f"Production line {payload['production_line_id']} not found")
    existing = workstation_repo.get_workstation_by_code(payload["production_line_id"], payload["code"], db)
    if existing is not None and existing["id"] != workstation_id:
        raise ConflictError("Workstation code already exists on production line")
    row = workstation_repo.update_workstation(workstation_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Workstation {workstation_id} not found")
    return _to_response(row)


def delete_workstation(workstation_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(workstation_id, db)
    workstation_repo.delete_workstation(workstation_id, db)
    return {"message": f"Workstation {workstation_id} deleted"}
