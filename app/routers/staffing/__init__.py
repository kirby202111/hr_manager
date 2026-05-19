"""排班域路由聚合。"""

from fastapi import APIRouter

from app.routers.staffing import eligibility, shift_assignment, shift_plan, shift_template

router = APIRouter()
router.include_router(shift_template.router)
router.include_router(shift_plan.router)
router.include_router(shift_assignment.router)
router.include_router(eligibility.router)

__all__ = ["router"]
