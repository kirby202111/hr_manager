"""Operational risk review router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.risk import (
    OperationalRiskReviewCreate,
    OperationalRiskReviewListResponse,
    OperationalRiskReviewResponse,
    OperationalRiskReviewUpdate,
)
from app.services.risk import operational_risk_review as service

router = APIRouter(prefix="/operational-risk-reviews", tags=["operational risk reviews"])


@router.get("/", response_model=OperationalRiskReviewListResponse)
def list_operational_risk_reviews(
    risk_signal_id: int | None = None,
    review_status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_operational_risk_reviews(risk_signal_id, review_status, db)


@router.get("/{operational_risk_review_id}", response_model=OperationalRiskReviewResponse)
def get_operational_risk_review(operational_risk_review_id: int, db: Session = Depends(get_db)):
    return service.get_operational_risk_review(operational_risk_review_id, db)


@router.post("/", response_model=OperationalRiskReviewResponse, status_code=201)
def create_operational_risk_review(data: OperationalRiskReviewCreate, db: Session = Depends(get_db)):
    return service.create_operational_risk_review(data, db)


@router.put("/{operational_risk_review_id}", response_model=OperationalRiskReviewResponse)
def update_operational_risk_review(
    operational_risk_review_id: int,
    data: OperationalRiskReviewUpdate,
    db: Session = Depends(get_db),
):
    return service.update_operational_risk_review(operational_risk_review_id, data, db)


@router.delete("/{operational_risk_review_id}")
def delete_operational_risk_review(operational_risk_review_id: int, db: Session = Depends(get_db)):
    return service.delete_operational_risk_review(operational_risk_review_id, db)
