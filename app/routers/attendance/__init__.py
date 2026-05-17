"""履约域路由聚合。"""

from fastapi import APIRouter

from app.routers.attendance import attendance_record, leave_request, payroll_record

router = APIRouter()
router.include_router(attendance_record.router)
router.include_router(leave_request.router)
router.include_router(payroll_record.router)

__all__ = ["router"]
