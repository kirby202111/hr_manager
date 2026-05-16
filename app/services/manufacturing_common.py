import json
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import employee as employee_repo
from app.repositories import manufacturing as repo
from app.schemas.manufacturing import ListResponse

VALID = {
    "line_status": {"active", "paused", "inactive"},
    "team_shift": {"day", "night", "rotating"},
    "active_inactive": {"active", "inactive"},
    "risk": {"low", "medium", "high", "critical"},
    "proficiency": {"beginner", "intermediate", "advanced", "expert"},
    "auth_level": {"observer", "operator", "maintainer"},
    "worker_type": {"operator", "inspector", "technician", "team_leader"},
    "production_status": {"active", "inactive", "restricted"},
    "cert_category": {"safety", "equipment", "process", "quality"},
    "validity_status": {"valid", "expired", "revoked"},
    "training_category": {"general", "line", "equipment", "hazard"},
    "safety_status": {"valid", "expired", "failed"},
    "order_status": {"planned", "running", "paused", "completed", "cancelled"},
    "priority": {"low", "normal", "high", "urgent"},
    "operation_status": {"planned", "running", "completed"},
    "shift_type": {"day", "night", "overtime"},
    "plan_status": {"draft", "published", "adjusted", "closed"},
    "assignment_type": {"normal", "support", "overtime", "replacement"},
    "assignment_status": {"planned", "confirmed", "cancelled"},
    "risk_status": {"open", "reviewed", "resolved", "ignored"},
    "detected_by": {"human", "system", "agent"},
}


def now() -> datetime:
    return datetime.now(UTC)


def stamp(data: dict[str, Any], *, update: bool = False) -> dict[str, Any]:
    if update:
        data["updated_at"] = now()
    else:
        current = now()
        data.setdefault("created_at", current)
        data.setdefault("updated_at", current)
    return data


def require(value: str, allowed_key: str, field: str) -> None:
    if value not in VALID[allowed_key]:
        raise ValidationError(f"Invalid {field}: {value}")


def decode_record(record: dict | None) -> dict:
    if record is None:
        return {}
    if "can_support_lines" in record and isinstance(record["can_support_lines"], str):
        record["can_support_lines"] = json.loads(record["can_support_lines"] or "[]")
    if "evidence" in record and isinstance(record["evidence"], str):
        record["evidence"] = json.loads(record["evidence"] or "{}")
    return record


def decode_records(records: list[dict]) -> list[dict]:
    return [decode_record(record) for record in records]


def get_record(kind: str, record_id: int, db: Session | None = None) -> dict:
    record = repo.get_record(kind, record_id, db)
    if record is None:
        raise NotFoundError(f"{kind} {record_id} not found")
    return decode_record(record)


def list_response(kind: str, filters: dict[str, Any] | None = None, db: Session | None = None) -> ListResponse:
    records = decode_records(repo.list_records(kind, filters, db))
    return ListResponse(items=records, total=len(records))


def exists(kind: str, record_id: int, db: Session | None = None) -> None:
    get_record(kind, record_id, db)


def employee_exists(employee_id: int, db: Session | None = None) -> None:
    if employee_repo.get_employee_by_id(employee_id, db) is None:
        raise ValidationError(f"Employee {employee_id} not found")


def line_exists(line_id: int, db: Session | None = None) -> None:
    exists("production_line", line_id, db)


def workstation_exists(workstation_id: int, db: Session | None = None) -> None:
    exists("workstation", workstation_id, db)


def expiring(kind: str, days: int = 30, db: Session | None = None) -> ListResponse:
    cutoff = date.today() + timedelta(days=days)
    records = [
        record
        for record in repo.list_records(kind, db=db)
        if record.get("expires_at") is not None and record["expires_at"] <= cutoff
    ]
    return ListResponse(items=records, total=len(records))
