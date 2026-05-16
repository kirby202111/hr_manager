from fastapi import APIRouter

from app.routers import (
    employee_production_profile,
    production_foundation,
    production_order,
    production_risk,
    production_safety,
    production_schedule,
    qualification,
)

router = APIRouter(tags=["manufacturing"])

router.include_router(production_foundation.router)
router.include_router(employee_production_profile.router)
router.include_router(qualification.router)
router.include_router(production_safety.router)
router.include_router(production_order.router)
router.include_router(production_schedule.router)
router.include_router(production_risk.router)
