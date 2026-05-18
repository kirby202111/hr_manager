"""Risk router aggregate."""

from fastapi import APIRouter

from app.routers.risk import operational_risk_review, operational_risk_signal

router = APIRouter()
router.include_router(operational_risk_signal.router)
router.include_router(operational_risk_review.router)

__all__ = ["router"]
