"""Production router aggregate."""

from fastapi import APIRouter

from app.routers.production import operation_qualification_requirement, production_operation, production_order

router = APIRouter()
router.include_router(production_order.router)
router.include_router(production_operation.router)
router.include_router(operation_qualification_requirement.router)

__all__ = ["router"]
