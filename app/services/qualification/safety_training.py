"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.capability import skill as skill_repo
from app.repositories.qualification import certification as certification_repo
from app.repositories.qualification import safety_training as safety_training_repo
from app.schemas.qualification import (
    SafetyTrainingCreate,
    SafetyTrainingListResponse,
    SafetyTrainingResponse,
    SafetyTrainingUpdate,
)


def _to_response(row: dict) -> SafetyTrainingResponse:
    return SafetyTrainingResponse(**row)


def _require_row(safety_training_id: int, db: Session | None = None) -> dict:
    row = safety_training_repo.get_safety_training_by_id(safety_training_id, db)
    if row is None:
        raise NotFoundError(f"Safety training {safety_training_id} not found")
    return row


def _validate_links(payload: dict, db: Session | None = None) -> None:
    if payload.get("skill_id") is not None and skill_repo.get_skill_by_id(payload["skill_id"], db) is None:
        raise NotFoundError(f"Skill {payload['skill_id']} not found")
    if (
        payload.get("required_certification_id") is not None
        and certification_repo.get_certification_by_id(payload["required_certification_id"], db) is None
    ):
        raise NotFoundError(f"Certification {payload['required_certification_id']} not found")


def list_safety_trainings(category: str | None = None, db: Session | None = None) -> SafetyTrainingListResponse:
    rows = safety_training_repo.list_safety_trainings(category, db)
    return SafetyTrainingListResponse(safety_trainings=[_to_response(row) for row in rows], total=len(rows))


def get_safety_training(safety_training_id: int, db: Session | None = None) -> SafetyTrainingResponse:
    return _to_response(_require_row(safety_training_id, db))


def create_safety_training(data: SafetyTrainingCreate, db: Session | None = None) -> SafetyTrainingResponse:
    if safety_training_repo.get_safety_training_by_code(data.code, db) is not None:
        raise ConflictError(f"Safety training code '{data.code}' already exists")
    payload = data.model_dump()
    _validate_links(payload, db)
    row = safety_training_repo.create_safety_training(payload, db)
    return _to_response(row)


def update_safety_training(
    safety_training_id: int,
    data: SafetyTrainingUpdate,
    db: Session | None = None,
) -> SafetyTrainingResponse:
    current = _require_row(safety_training_id, db)
    payload = data.model_dump(exclude_unset=True)
    if "code" in payload and payload["code"] != current["code"]:
        if safety_training_repo.get_safety_training_by_code(payload["code"], db) is not None:
            raise ConflictError(f"Safety training code '{payload['code']}' already exists")
    _validate_links({**current, **payload}, db)
    row = safety_training_repo.update_safety_training(safety_training_id, payload, db)
    if row is None:
        raise NotFoundError(f"Safety training {safety_training_id} not found")
    return _to_response(row)


def delete_safety_training(safety_training_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(safety_training_id, db)
    safety_training_repo.delete_safety_training(safety_training_id, db)
    return {"message": f"Safety training {safety_training_id} deleted"}
