import json

from sqlalchemy.orm import Session

from app.repositories import manufacturing as repo
from app.schemas import manufacturing as schemas
from app.services.manufacturing_common import decode_record, decode_records, exists, get_record, require, stamp
from app.services.production_schedule import validate_shift_plan


def create_risk_signal(data: schemas.ProductionRiskSignalCreate, db: Session | None = None) -> dict:
    require(data.severity, "risk", "severity")
    require(data.status, "risk_status", "status")
    require(data.detected_by, "detected_by", "detected_by")
    payload = data.model_dump()
    payload["evidence"] = json.dumps(payload["evidence"])
    return decode_record(repo.create_record("production_risk_signal", stamp(payload), db))


def update_risk_signal(
    risk_id: int,
    data: schemas.ProductionRiskSignalUpdate,
    db: Session | None = None,
) -> dict:
    exists("production_risk_signal", risk_id, db)
    payload = data.model_dump(exclude_unset=True)
    if "evidence" in payload:
        payload["evidence"] = json.dumps(payload["evidence"])
    record = repo.update_record("production_risk_signal", risk_id, stamp(payload, update=True), db)
    return decode_record(record)


def generate_shift_plan_risks(plan_id: int, db: Session | None = None) -> schemas.ListResponse:
    plan = get_record("production_shift_plan", plan_id, db)
    validation = validate_shift_plan(plan_id, db)
    rows = []
    for issue in validation.issues:
        rows.append(
            {
                "order_id": plan["order_id"],
                "employee_id": issue.employee_id,
                "line_id": plan["line_id"],
                "workstation_id": issue.workstation_id,
                "shift_assignment_id": issue.shift_assignment_id,
                "signal_type": issue.signal_type,
                "severity": issue.severity,
                "evidence": json.dumps({"plan_id": plan_id, "message": issue.message}),
                "status": "open",
                "detected_by": "system",
                **stamp({}),
            }
        )
    created = decode_records(repo.create_records("production_risk_signal", rows, db)) if rows else []
    return schemas.ListResponse(items=created, total=len(created))


def create_risk_review(risk_id: int, data: schemas.ProductionRiskReviewCreate, db: Session | None = None) -> dict:
    exists("production_risk_signal", risk_id, db)
    review = repo.create_record(
        "production_risk_review",
        data.model_dump() | {"risk_signal_id": risk_id, "created_at": stamp({})["created_at"]},
        db,
    )
    repo.update_record("production_risk_signal", risk_id, stamp({"status": "reviewed"}, update=True), db)
    return review
