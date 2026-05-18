"""Operational risk signal router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.risk import (
    OperationalRiskSignalCreate,
    OperationalRiskSignalListResponse,
    OperationalRiskSignalResponse,
    OperationalRiskSignalUpdate,
)
from app.services.risk import operational_risk_signal as service

router = APIRouter(prefix="/operational-risk-signals", tags=["operational risk signals"])


@router.get("/", response_model=OperationalRiskSignalListResponse)
def list_operational_risk_signals(
    production_order_id: int | None = None,
    worker_id: int | None = None,
    production_line_id: int | None = None,
    workstation_id: int | None = None,
    shift_assignment_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_operational_risk_signals(
        production_order_id,
        worker_id,
        production_line_id,
        workstation_id,
        shift_assignment_id,
        status,
        db,
    )


@router.get("/{operational_risk_signal_id}", response_model=OperationalRiskSignalResponse)
def get_operational_risk_signal(operational_risk_signal_id: int, db: Session = Depends(get_db)):
    return service.get_operational_risk_signal(operational_risk_signal_id, db)


@router.post("/", response_model=OperationalRiskSignalResponse, status_code=201)
def create_operational_risk_signal(data: OperationalRiskSignalCreate, db: Session = Depends(get_db)):
    return service.create_operational_risk_signal(data, db)


@router.put("/{operational_risk_signal_id}", response_model=OperationalRiskSignalResponse)
def update_operational_risk_signal(
    operational_risk_signal_id: int,
    data: OperationalRiskSignalUpdate,
    db: Session = Depends(get_db),
):
    return service.update_operational_risk_signal(operational_risk_signal_id, data, db)


@router.delete("/{operational_risk_signal_id}")
def delete_operational_risk_signal(operational_risk_signal_id: int, db: Session = Depends(get_db)):
    return service.delete_operational_risk_signal(operational_risk_signal_id, db)
