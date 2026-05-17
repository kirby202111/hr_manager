from sqlalchemy.orm import Session

from app.repositories import shopfloor as repo
from app.schemas import shopfloor as schemas
from app.services.shopfloor_support import employee_exists, exists, expiring, require, stamp


def create_safety_training(data: schemas.SafetyTrainingCreate, db: Session | None = None) -> dict:
    require(data.category, "training_category", "category")
    if data.required_for_certification_id is not None:
        exists("certification", data.required_for_certification_id, db)
    return repo.create_record("safety_training", stamp(data.model_dump()), db)


def create_safety_record(data: schemas.EmployeeSafetyRecordCreate, db: Session | None = None) -> dict:
    employee_exists(data.employee_id, db)
    exists("safety_training", data.training_id, db)
    require(data.status, "safety_status", "status")
    payload = data.model_dump()
    payload["created_at"] = stamp({})["created_at"]
    return repo.create_record("employee_safety_record", payload, db)


def safety_status(employee_id: int, db: Session | None = None) -> dict:
    records = repo.list_records("employee_safety_record", {"employee_id": employee_id}, db)
    return {
        "employee_id": employee_id,
        "has_valid_safety_training": any(record["status"] == "valid" for record in records),
        "records": records,
    }


def expiring_safety_records(days: int = 30, db: Session | None = None) -> schemas.ListResponse:
    return expiring("employee_safety_record", days, db)
