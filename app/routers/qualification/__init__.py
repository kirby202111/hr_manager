"""Qualification router aggregate."""

from fastapi import APIRouter

from app.routers.qualification import (
    certification,
    eligibility,
    equipment_authorization,
    safety_training,
    worker_certification,
    worker_safety_training,
)

router = APIRouter()
router.include_router(certification.router)
router.include_router(worker_certification.router)
router.include_router(safety_training.router)
router.include_router(worker_safety_training.router)
router.include_router(equipment_authorization.router)
router.include_router(eligibility.router)

__all__ = ["router"]
