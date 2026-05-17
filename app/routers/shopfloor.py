from fastapi import APIRouter

from app.routers import (
    credential,
    operational_risk,
    safety_compliance,
    shift_staffing,
    shopfloor_structure,
    shopfloor_worker_profile,
    work_order,
)

router = APIRouter(tags=["shopfloor"])

router.include_router(shopfloor_structure.router)
router.include_router(shopfloor_worker_profile.router)
router.include_router(credential.router)
router.include_router(safety_compliance.router)
router.include_router(work_order.router)
router.include_router(shift_staffing.router)
router.include_router(operational_risk.router)
