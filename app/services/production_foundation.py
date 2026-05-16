from sqlalchemy.orm import Session

from app.errors import ValidationError
from app.repositories import department as department_repo
from app.repositories import manufacturing as repo
from app.repositories import skill_catalog as skill_catalog_repo
from app.schemas import manufacturing as schemas
from app.services.manufacturing_common import (
    decode_record,
    employee_exists,
    exists,
    get_record,
    line_exists,
    list_response,
    now,
    require,
    stamp,
    workstation_exists,
)


def create_line(data: schemas.ProductionLineCreate, db: Session | None = None) -> dict:
    if department_repo.get_department_by_id(data.department_id, db) is None:
        raise ValidationError(f"Department {data.department_id} not found")
    if data.supervisor_employee_id is not None:
        employee_exists(data.supervisor_employee_id, db)
    require(data.status, "line_status", "status")
    return repo.create_record("production_line", stamp(data.model_dump()), db)


def list_lines(db: Session | None = None) -> schemas.ListResponse:
    return list_response("production_line", db=db)


def get_line(line_id: int, db: Session | None = None) -> dict:
    return get_record("production_line", line_id, db)


def update_line(line_id: int, data: schemas.ProductionLineUpdate, db: Session | None = None) -> dict:
    get_line(line_id, db)
    update = data.model_dump(exclude_unset=True)
    if "status" in update:
        require(update["status"], "line_status", "status")
    return decode_record(repo.update_record("production_line", line_id, stamp(update, update=True), db))


def create_team(data: schemas.ProductionTeamCreate, db: Session | None = None) -> dict:
    line_exists(data.line_id, db)
    if data.leader_employee_id is not None:
        employee_exists(data.leader_employee_id, db)
    require(data.shift_type, "team_shift", "shift_type")
    require(data.status, "active_inactive", "status")
    return repo.create_record("production_team", stamp(data.model_dump()), db)


def get_team(team_id: int, db: Session | None = None) -> dict:
    return get_record("production_team", team_id, db)


def update_team(team_id: int, data: schemas.ProductionTeamUpdate, db: Session | None = None) -> dict:
    get_team(team_id, db)
    update = data.model_dump(exclude_unset=True)
    if "line_id" in update:
        line_exists(update["line_id"], db)
    if "shift_type" in update:
        require(update["shift_type"], "team_shift", "shift_type")
    if "status" in update:
        require(update["status"], "active_inactive", "status")
    return decode_record(repo.update_record("production_team", team_id, stamp(update, update=True), db))


def create_workstation(data: schemas.WorkstationCreate, db: Session | None = None) -> dict:
    line_exists(data.line_id, db)
    require(data.risk_level, "risk", "risk_level")
    require(data.status, "active_inactive", "status")
    return repo.create_record("workstation", stamp(data.model_dump()), db)


def get_workstation(workstation_id: int, db: Session | None = None) -> dict:
    return get_record("workstation", workstation_id, db)


def update_workstation(workstation_id: int, data: schemas.WorkstationUpdate, db: Session | None = None) -> dict:
    get_workstation(workstation_id, db)
    update = data.model_dump(exclude_unset=True)
    if "line_id" in update:
        line_exists(update["line_id"], db)
    if "risk_level" in update:
        require(update["risk_level"], "risk", "risk_level")
    if "status" in update:
        require(update["status"], "active_inactive", "status")
    return decode_record(repo.update_record("workstation", workstation_id, stamp(update, update=True), db))


def add_required_skill(
    workstation_id: int,
    data: schemas.WorkstationRequiredSkillCreate,
    db: Session | None = None,
) -> dict:
    workstation_exists(workstation_id, db)
    if skill_catalog_repo.get_skill_by_id(data.skill_id, db) is None:
        raise ValidationError(f"Skill {data.skill_id} not found")
    require(data.required_proficiency, "proficiency", "required_proficiency")
    payload = data.model_dump() | {"workstation_id": workstation_id, "created_at": now()}
    return repo.create_record("workstation_required_skill", payload, db)


def add_required_certification(
    workstation_id: int,
    data: schemas.WorkstationRequiredCertificationCreate,
    db: Session | None = None,
) -> dict:
    workstation_exists(workstation_id, db)
    exists("certification", data.certification_id, db)
    payload = data.model_dump() | {"workstation_id": workstation_id, "created_at": now()}
    return repo.create_record("workstation_required_certification", payload, db)


def add_equipment_requirement(
    workstation_id: int,
    data: schemas.WorkstationEquipmentRequirementCreate,
    db: Session | None = None,
) -> dict:
    workstation_exists(workstation_id, db)
    require(data.required_authorization_level, "auth_level", "required_authorization_level")
    payload = data.model_dump() | {"workstation_id": workstation_id, "created_at": now()}
    return repo.create_record("workstation_equipment_requirement", payload, db)
