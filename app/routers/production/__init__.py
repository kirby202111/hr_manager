"""Production router aggregate."""

from fastapi import APIRouter

from app.routers.production import production_operation, production_order

router = APIRouter()
router.include_router(production_order.router)
router.include_router(production_operation.router)

__all__ = ["router"]
