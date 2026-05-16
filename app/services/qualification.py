from sqlalchemy.orm import Session

from app.repositories import manufacturing as repo
from app.schemas import manufacturing as schemas
from app.services.manufacturing_common import (
    decode_record,
    employee_exists,
    exists,
    expiring,
    require,
    stamp,
)

LEVEL_RANK = {"observer": 1, "operator": 2, "maintainer": 3}


def create_certification(data: schemas.CertificationCreate, db: Session | None = None) -> dict:
    require(data.category, "cert_category", "category")
    return repo.create_record("certification", stamp(data.model_dump()), db)


def update_certification(
    certification_id: int,
    data: schemas.CertificationUpdate,
    db: Session | None = None,
) -> dict:
    exists("certification", certification_id, db)
    update = data.model_dump(exclude_unset=True)
    if "category" in update:
        require(update["category"], "cert_category", "category")
    record = repo.update_record("certification", certification_id, stamp(update, update=True), db)
    return decode_record(record)


def create_employee_certification(
    data: schemas.EmployeeCertificationCreate,
    db: Session | None = None,
) -> dict:
    employee_exists(data.employee_id, db)
    exists("certification", data.certification_id, db)
    require(data.status, "validity_status", "status")
    return repo.create_record("employee_certification", stamp(data.model_dump()), db)


def update_employee_certification(
    record_id: int,
    data: schemas.EmployeeCertificationUpdate,
    db: Session | None = None,
) -> dict:
    exists("employee_certification", record_id, db)
    update = stamp(data.model_dump(exclude_unset=True), update=True)
    return decode_record(repo.update_record("employee_certification", record_id, update, db))


def create_equipment_authorization(
    data: schemas.EquipmentAuthorizationCreate,
    db: Session | None = None,
) -> dict:
    employee_exists(data.employee_id, db)
    require(data.authorization_level, "auth_level", "authorization_level")
    require(data.status, "validity_status", "status")
    return repo.create_record("equipment_authorization", stamp(data.model_dump()), db)


def update_equipment_authorization(
    record_id: int,
    data: schemas.EquipmentAuthorizationUpdate,
    db: Session | None = None,
) -> dict:
    exists("equipment_authorization", record_id, db)
    update = stamp(data.model_dump(exclude_unset=True), update=True)
    return decode_record(repo.update_record("equipment_authorization", record_id, update, db))


def expiring_certifications(days: int = 30, db: Session | None = None) -> schemas.ListResponse:
    return expiring("employee_certification", days, db)


def expiring_authorizations(days: int = 30, db: Session | None = None) -> schemas.ListResponse:
    return expiring("equipment_authorization", days, db)
