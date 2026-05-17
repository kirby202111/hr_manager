"""能力域路由聚合。"""

from fastapi import APIRouter

from app.routers.capability import skill, worker_skill

router = APIRouter()
router.include_router(skill.router)
router.include_router(worker_skill.router)

__all__ = ["router"]
