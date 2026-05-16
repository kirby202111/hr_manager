from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import manufacturing as s
from app.services import production_risk as svc
from app.services.manufacturing_common import get_record, list_response

router = APIRouter(tags=["production risks"])


@router.post("/production-risk-signals", status_code=201)
def create_risk_signal(data: s.ProductionRiskSignalCreate, db: Session = Depends(get_db)):
    return svc.create_risk_signal(data, db)


@router.get("/production-risk-signals", response_model=s.ListResponse)
def list_risk_signals(db: Session = Depends(get_db)):
    return list_response("production_risk_signal", db=db)


@router.get("/production-risk-signals/{risk_id}")
def get_risk_signal(risk_id: int, db: Session = Depends(get_db)):
    return get_record("production_risk_signal", risk_id, db)


@router.patch("/production-risk-signals/{risk_id}")
def update_risk_signal(risk_id: int, data: s.ProductionRiskSignalUpdate, db: Session = Depends(get_db)):
    return svc.update_risk_signal(risk_id, data, db)


@router.post("/production-risk-signals/{risk_id}/reviews", status_code=201)
def create_risk_review(risk_id: int, data: s.ProductionRiskReviewCreate, db: Session = Depends(get_db)):
    return svc.create_risk_review(risk_id, data, db)


@router.get("/production-risk-signals/{risk_id}/reviews", response_model=s.ListResponse)
def list_risk_reviews(risk_id: int, db: Session = Depends(get_db)):
    return list_response("production_risk_review", {"risk_signal_id": risk_id}, db)


@router.post("/production-risks/detect/shift-plan/{plan_id}", response_model=s.ListResponse)
def detect_shift_plan_risks(plan_id: int, db: Session = Depends(get_db)):
    return svc.generate_shift_plan_risks(plan_id, db)
