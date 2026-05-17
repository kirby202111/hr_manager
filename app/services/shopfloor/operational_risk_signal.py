"""风险信号服务。"""

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.repositories import shopfloor as shopfloor_repo
from app.repositories import staffing as staffing_repo
from app.repositories import workforce as workforce_repo
from app.schemas.shopfloor import (
    OperationalRiskSignalCreate,
    OperationalRiskSignalListResponse,
    OperationalRiskSignalResponse,
    OperationalRiskSignalUpdate,
)


def _to_response(row: dict) -> OperationalRiskSignalResponse:
    return OperationalRiskSignalResponse(**row)


def _require_row(operational_risk_signal_id: int, db: Session | None = None) -> dict:
    row = shopfloor_repo.get_operational_risk_signal_by_id(operational_risk_signal_id, db)
    if row is None:
        raise NotFoundError(f"Operational risk signal {operational_risk_signal_id} not found")
    return row


def _validate_links(payload: dict, db: Session | None = None) -> None:
    if (
        payload.get("production_order_id") is not None
        and shopfloor_repo.get_production_order_by_id(payload["production_order_id"], db) is None
    ):
        raise NotFoundError(f"Production order {payload['production_order_id']} not found")
    if payload.get("worker_id") is not None and workforce_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")
    if (
        payload.get("production_line_id") is not None
        and shopfloor_repo.get_production_line_by_id(payload["production_line_id"], db) is None
    ):
        raise NotFoundError(f"Production line {payload['production_line_id']} not found")
    if (
        payload.get("workstation_id") is not None
        and shopfloor_repo.get_workstation_by_id(payload["workstation_id"], db) is None
    ):
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if (
        payload.get("shift_assignment_id") is not None
        and staffing_repo.get_shift_assignment_by_id(payload["shift_assignment_id"], db) is None
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
    rows = shopfloor_repo.list_operational_risk_signals(
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
    row = shopfloor_repo.create_operational_risk_signal(payload, db)
    return _to_response(row)


def update_operational_risk_signal(
    operational_risk_signal_id: int,
    data: OperationalRiskSignalUpdate,
    db: Session | None = None,
) -> OperationalRiskSignalResponse:
    current = _require_row(operational_risk_signal_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_links(payload, db)
    row = shopfloor_repo.update_operational_risk_signal(
        operational_risk_signal_id, data.model_dump(exclude_unset=True), db
    )
    if row is None:
        raise NotFoundError(f"Operational risk signal {operational_risk_signal_id} not found")
    return _to_response(row)


def delete_operational_risk_signal(operational_risk_signal_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(operational_risk_signal_id, db)
    shopfloor_repo.delete_operational_risk_signal(operational_risk_signal_id, db)
    return {"message": f"Operational risk signal {operational_risk_signal_id} deleted"}
