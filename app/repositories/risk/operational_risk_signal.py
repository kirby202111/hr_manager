"""Operational risk signal repository."""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.risk import OperationalRiskSignal


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_operational_risk_signals(
    production_order_id: int | None = None,
    worker_id: int | None = None,
    production_line_id: int | None = None,
    workstation_id: int | None = None,
    shift_assignment_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(OperationalRiskSignal)
        if production_order_id is not None:
            query = query.filter(OperationalRiskSignal.production_order_id == production_order_id)
        if worker_id is not None:
            query = query.filter(OperationalRiskSignal.worker_id == worker_id)
        if production_line_id is not None:
            query = query.filter(OperationalRiskSignal.production_line_id == production_line_id)
        if workstation_id is not None:
            query = query.filter(OperationalRiskSignal.workstation_id == workstation_id)
        if shift_assignment_id is not None:
            query = query.filter(OperationalRiskSignal.shift_assignment_id == shift_assignment_id)
        if status is not None:
            query = query.filter(OperationalRiskSignal.status == status)
        return [row.to_dict() for row in query.all()]


def get_operational_risk_signal_by_id(operational_risk_signal_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationalRiskSignal, operational_risk_signal_id)
        return row.to_dict() if row else None


def create_operational_risk_signal(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = OperationalRiskSignal(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_operational_risk_signal(
    operational_risk_signal_id: int, data: dict, db: Session | None = None
) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationalRiskSignal, operational_risk_signal_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_operational_risk_signal(operational_risk_signal_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(OperationalRiskSignal, operational_risk_signal_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
