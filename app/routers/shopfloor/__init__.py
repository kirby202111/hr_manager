"""Shopfloor router aggregate."""

from fastapi import APIRouter

from app.routers.shopfloor import production_line, production_team, workstation

router = APIRouter()
router.include_router(production_line.router)
router.include_router(production_team.router)
router.include_router(workstation.router)

__all__ = ["router"]
