"""人员域路由聚合。"""

from fastapi import APIRouter

from app.routers.workforce import worker, worker_assignment

router = APIRouter()
router.include_router(worker.router)
router.include_router(worker_assignment.router)

__all__ = ["router"]
