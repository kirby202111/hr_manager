"""Service module."""

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.repositories.shopfloor import operational_risk_signal as operational_risk_signal_repo
from app.repositories.shopfloor import production_line as production_line_repo
from app.repositories.shopfloor import production_order as production_order_repo
from app.repositories.shopfloor import workstation as workstation_repo
from app.repositories.staffing import shift_assignment as shift_assignment_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.shopfloor import (
    OperationalRiskSignalCreate,
    OperationalRiskSignalListResponse,
    OperationalRiskSignalResponse,
    OperationalRiskSignalUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> OperationalRiskSignalResponse:
    return OperationalRiskSignalResponse(**row)


# 读取单条记录；不存在时统一抛出未找到异常。
def _require_row(operational_risk_signal_id: int, db: Session | None = None) -> dict:
    row = operational_risk_signal_repo.get_operational_risk_signal_by_id(operational_risk_signal_id, db)
    if row is None:
        raise NotFoundError(f"Operational risk signal {operational_risk_signal_id} not found")
    return row


# 校验关联资源是否存在，并检查跨实体引用是否合法。
def _validate_links(payload: dict, db: Session | None = None) -> None:
    if (
        payload.get("production_order_id") is not None
        and production_order_repo.get_production_order_by_id(payload["production_order_id"], db) is None
    ):
        raise NotFoundError(f"Production order {payload['production_order_id']} not found")
    if payload.get("worker_id") is not None and worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if (
        payload.get("production_line_id") is not None
        and production_line_repo.get_production_line_by_id(payload["production_line_id"], db) is None
    ):
        raise NotFoundError(f"Production line {payload['production_line_id']} not found")
    if (
        payload.get("workstation_id") is not None
        and workstation_repo.get_workstation_by_id(payload["workstation_id"], db) is None
    ):
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if (
        payload.get("shift_assignment_id") is not None
        and shift_assignment_repo.get_shift_assignment_by_id(payload["shift_assignment_id"], db) is None
    ):
        raise NotFoundError(f"Shift assignment {payload['shift_assignment_id']} not found")


def list_operational_risk_signals(
    production_order_id: int | None = None,
    worker_id: int | None = None,
    production_line_id: int | None = None,
    workstation_id: int | None = None,
    shift_assignment_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> OperationalRiskSignalListResponse:
    rows = operational_risk_signal_repo.list_operational_risk_signals(
        production_order_id,
        worker_id,
        production_line_id,
        workstation_id,
        shift_assignment_id,
        status,
        db,
    )
    return OperationalRiskSignalListResponse(
        operational_risk_signals=[_to_response(row) for row in rows], total=len(rows)
    )


def get_operational_risk_signal(
    operational_risk_signal_id: int, db: Session | None = None
) -> OperationalRiskSignalResponse:
    return _to_response(_require_row(operational_risk_signal_id, db))


def create_operational_risk_signal(
    data: OperationalRiskSignalCreate,
    db: Session | None = None,
) -> OperationalRiskSignalResponse:
    payload = data.model_dump()
    _validate_links(payload, db)
    row = operational_risk_signal_repo.create_operational_risk_signal(payload, db)
    return _to_response(row)


def update_operational_risk_signal(
    operational_risk_signal_id: int,
    data: OperationalRiskSignalUpdate,
    db: Session | None = None,
) -> OperationalRiskSignalResponse:
    current = _require_row(operational_risk_signal_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_links(payload, db)
    row = operational_risk_signal_repo.update_operational_risk_signal(
        operational_risk_signal_id, data.model_dump(exclude_unset=True), db
    )
    if row is None:
        raise NotFoundError(f"Operational risk signal {operational_risk_signal_id} not found")
    return _to_response(row)


def delete_operational_risk_signal(operational_risk_signal_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(operational_risk_signal_id, db)
    operational_risk_signal_repo.delete_operational_risk_signal(operational_risk_signal_id, db)
    return {"message": f"Operational risk signal {operational_risk_signal_id} deleted"}
