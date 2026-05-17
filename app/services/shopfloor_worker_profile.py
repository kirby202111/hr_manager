import json

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import shopfloor as repo
from app.schemas import shopfloor as schemas
from app.services.shopfloor_support import (
    decode_record,
    employee_exists,
    exists,
    line_exists,
    now,
    require,
    stamp,
)


def create_team_assignment(data: schemas.EmployeeTeamAssignmentCreate, db: Session | None = None) -> dict:
    employee_exists(data.employee_id, db)
    exists("production_team", data.team_id, db)
    line_exists(data.line_id, db)
    if data.end_date is not None and data.end_date < data.start_date:
        raise ValidationError("end_date cannot be earlier than start_date")
    return repo.create_record("employee_team_assignment", data.model_dump() | {"created_at": now()}, db)


def create_profile(data: schemas.EmployeeProductionProfileCreate, db: Session | None = None) -> dict:
    employee_exists(data.employee_id, db)
    if repo.get_one_by("employee_production_profile", {"employee_id": data.employee_id}, db):
        raise ValidationError(f"Production profile for employee {data.employee_id} already exists")
    require(data.worker_type, "worker_type", "worker_type")
    require(data.production_status, "production_status", "production_status")
    payload = data.model_dump()
    payload["can_support_lines"] = json.dumps(payload["can_support_lines"])
    return decode_record(repo.create_record("employee_production_profile", stamp(payload), db))


def get_profile(employee_id: int, db: Session | None = None) -> dict:
    employee_exists(employee_id, db)
    profile = repo.get_one_by("employee_production_profile", {"employee_id": employee_id}, db)
    if profile is None:
        raise NotFoundError(f"Production profile for employee {employee_id} not found")
    return decode_record(profile)


def update_profile(
    employee_id: int,
    data: schemas.EmployeeProductionProfileUpdate,
    db: Session | None = None,
) -> dict:
    profile = get_profile(employee_id, db)
    update = data.model_dump(exclude_unset=True)
    if "worker_type" in update:
        require(update["worker_type"], "worker_type", "worker_type")
    if "production_status" in update:
        require(update["production_status"], "production_status", "production_status")
    if "can_support_lines" in update:
        update["can_support_lines"] = json.dumps(update["can_support_lines"])
    record = repo.update_record("employee_production_profile", profile["id"], stamp(update, update=True), db)
    return decode_record(record)
