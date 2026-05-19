"""Shopfloor services."""

from app.services.shopfloor.production_line import (
    create_production_line,
    delete_production_line,
    get_production_line,
    list_production_lines,
    update_production_line,
)
from app.services.shopfloor.production_team import (
    create_production_team,
    delete_production_team,
    get_production_team,
    list_production_teams,
    update_production_team,
)
from app.services.shopfloor.workstation import (
    create_workstation,
    delete_workstation,
    get_workstation,
    list_workstations,
    update_workstation,
)
from app.services.shopfloor.workstation_certification_requirement import (
    create_workstation_certification_requirement,
    delete_workstation_certification_requirement,
    get_workstation_certification_requirement,
    list_workstation_certification_requirements,
    update_workstation_certification_requirement,
)
from app.services.shopfloor.workstation_equipment_requirement import (
    create_workstation_equipment_requirement,
    delete_workstation_equipment_requirement,
    get_workstation_equipment_requirement,
    list_workstation_equipment_requirements,
    update_workstation_equipment_requirement,
)
from app.services.shopfloor.workstation_skill_requirement import (
    create_workstation_skill_requirement,
    delete_workstation_skill_requirement,
    get_workstation_skill_requirement,
    list_workstation_skill_requirements,
    update_workstation_skill_requirement,
)
from app.services.shopfloor.workstation_training_requirement import (
    create_workstation_training_requirement,
    delete_workstation_training_requirement,
    get_workstation_training_requirement,
    list_workstation_training_requirements,
    update_workstation_training_requirement,
)

__all__ = [
    "create_production_line",
    "create_production_team",
    "create_workstation",
    "delete_production_line",
    "delete_production_team",
    "delete_workstation",
    "get_production_line",
    "get_production_team",
    "get_workstation",
    "get_workstation_certification_requirement",
    "get_workstation_equipment_requirement",
    "get_workstation_skill_requirement",
    "get_workstation_training_requirement",
    "list_production_lines",
    "list_production_teams",
    "list_workstations",
    "list_workstation_certification_requirements",
    "list_workstation_equipment_requirements",
    "list_workstation_skill_requirements",
    "list_workstation_training_requirements",
    "create_workstation_certification_requirement",
    "create_workstation_equipment_requirement",
    "create_workstation_skill_requirement",
    "create_workstation_training_requirement",
    "delete_workstation_certification_requirement",
    "delete_workstation_equipment_requirement",
    "delete_workstation_skill_requirement",
    "delete_workstation_training_requirement",
    "update_production_line",
    "update_production_team",
    "update_workstation",
    "update_workstation_certification_requirement",
    "update_workstation_equipment_requirement",
    "update_workstation_skill_requirement",
    "update_workstation_training_requirement",
]
