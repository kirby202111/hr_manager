"""Qualification router aggregate."""

from fastapi import APIRouter

from app.routers.qualification import (
    certification,
    equipment_authorization,
    safety_training,
    worker_certification,
    worker_safety_training,
    workstation_certification_requirement,
    workstation_equipment_requirement,
    workstation_skill_requirement,
)

router = APIRouter()
router.include_router(certification.router)
router.include_router(worker_certification.router)
router.include_router(safety_training.router)
router.include_router(worker_safety_training.router)
router.include_router(equipment_authorization.router)
router.include_router(workstation_skill_requirement.router)
router.include_router(workstation_certification_requirement.router)
router.include_router(workstation_equipment_requirement.router)

__all__ = ["router"]
