"""Shopfloor router aggregate."""

from fastapi import APIRouter

from app.routers.shopfloor import (
    production_line,
    production_team,
    workstation,
    workstation_certification_requirement,
    workstation_equipment_requirement,
    workstation_skill_requirement,
    workstation_training_requirement,
)

router = APIRouter()
router.include_router(production_line.router)
router.include_router(production_team.router)
router.include_router(workstation.router)
router.include_router(workstation_skill_requirement.router)
router.include_router(workstation_certification_requirement.router)
router.include_router(workstation_training_requirement.router)
router.include_router(workstation_equipment_requirement.router)

__all__ = ["router"]
