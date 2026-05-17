"""生产现场域路由聚合。"""

from fastapi import APIRouter

from app.routers.shopfloor import (
    operational_risk_review,
    operational_risk_signal,
    production_line,
    production_operation,
    production_order,
    production_team,
    workstation,
    workstation_certification_requirement,
    workstation_equipment_requirement,
    workstation_skill_requirement,
)

router = APIRouter()
for module in (
    production_line,
    production_team,
    workstation,
    workstation_skill_requirement,
    workstation_certification_requirement,
    workstation_equipment_requirement,
    production_order,
    production_operation,
    operational_risk_signal,
    operational_risk_review,
):
    router.include_router(module.router)

__all__ = ["router"]
