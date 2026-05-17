"""组织域路由聚合。"""

from fastapi import APIRouter

from app.routers.organization import organization_unit

router = APIRouter()
router.include_router(organization_unit.router)

__all__ = ["router"]
