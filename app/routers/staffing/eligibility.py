"""Staffing eligibility router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.qualification import EligibilityCheckRequest, WorkerEligibilityEvaluationResponse
from app.services.qualification import eligibility as service

router = APIRouter(prefix="/staffing/eligibility", tags=["staffing eligibility"])


@router.post("/check", response_model=WorkerEligibilityEvaluationResponse)
def check_eligibility(data: EligibilityCheckRequest, db: Session = Depends(get_db)):
    return service.evaluate_worker_eligibility(
        worker_id=data.worker_id,
        workstation_id=data.workstation_id,
        work_date=data.work_date,
        production_operation_id=data.production_operation_id,
        persist_snapshot=data.persist_snapshot,
        source_context="manual_check",
        db=db,
    )
