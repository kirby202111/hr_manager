"""Eligibility snapshot router."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.qualification import WorkerEligibilitySnapshotListResponse, WorkerEligibilitySnapshotResponse
from app.services.qualification import eligibility as service

router = APIRouter(prefix="/qualification/workers/{worker_id}/eligibility-snapshots", tags=["eligibility snapshots"])


@router.get("/", response_model=WorkerEligibilitySnapshotListResponse)
def list_worker_eligibility_snapshots(
    worker_id: int,
    workstation_id: int | None = None,
    shift_plan_id: int | None = None,
    status: str | None = None,
    work_date_from: date | None = None,
    work_date_to: date | None = None,
    db: Session = Depends(get_db),
):
    return service.list_worker_eligibility_snapshots(
        worker_id,
        workstation_id,
        shift_plan_id,
        status,
        work_date_from,
        work_date_to,
        db,
    )


@router.get("/{snapshot_id}", response_model=WorkerEligibilitySnapshotResponse)
def get_worker_eligibility_snapshot(worker_id: int, snapshot_id: int, db: Session = Depends(get_db)):
    return service.get_worker_eligibility_snapshot(worker_id, snapshot_id, db)
