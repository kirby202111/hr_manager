"""Service module."""

from app.services.shopfloor import (
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

_MODULES = (
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

for _module in _MODULES:
    for _name in dir(_module):
        if not _name.startswith(("create_", "delete_", "get_", "list_", "update_")):
            continue
        globals()[_name] = getattr(_module, _name)

__all__ = [
    name
    for module in _MODULES
    for name in dir(module)
    if name.startswith(("create_", "delete_", "get_", "list_", "update_"))
]
