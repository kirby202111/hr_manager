"""Operation qualification requirement service."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.capability import skill as skill_repo
from app.repositories.production import operation_qualification_requirement as requirement_repo
from app.repositories.production import production_operation as operation_repo
from app.repositories.qualification import certification as certification_repo
from app.repositories.qualification import safety_training as training_repo
from app.schemas.production import (
    OperationQualificationRequirementCreate,
    OperationQualificationRequirementListResponse,
    OperationQualificationRequirementResponse,
    OperationQualificationRequirementUpdate,
)

VALID_REQUIREMENT_TYPES = {"skill", "certification", "training", "equipment_authorization"}
VALID_LEVELS = {"L1", "L2", "L3", "L4", "L5"}


def _to_response(row: dict) -> OperationQualificationRequirementResponse:
    return OperationQualificationRequirementResponse(**row)


def _require_row(requirement_id: int, db: Session | None = None) -> dict:
    row = requirement_repo.get_operation_qualification_requirement_by_id(requirement_id, db)
    if row is None:
        raise NotFoundError(f"Operation qualification requirement {requirement_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if operation_repo.get_production_operation_by_id(payload["production_operation_id"], db) is None:
        raise NotFoundError(f"Production operation {payload['production_operation_id']} not found")
    requirement_type = payload["requirement_type"]
    if requirement_type not in VALID_REQUIREMENT_TYPES:
        raise ValidationError("requirement_type must be one of skill, certification, training, equipment_authorization")
    if requirement_type == "skill":
        if payload.get("reference_id") is None:
            raise ValidationError("skill requirement requires reference_id")
        if skill_repo.get_skill_by_id(payload["reference_id"], db) is None:
            raise NotFoundError(f"Skill {payload['reference_id']} not found")
        if payload.get("min_proficiency_level") not in VALID_LEVELS:
            raise ValidationError("skill requirement min_proficiency_level must be one of L1, L2, L3, L4, L5")
    elif requirement_type == "certification":
        if payload.get("reference_id") is None:
            raise ValidationError("certification requirement requires reference_id")
        if certification_repo.get_certification_by_id(payload["reference_id"], db) is None:
            raise NotFoundError(f"Certification {payload['reference_id']} not found")
    elif requirement_type == "training":
        if payload.get("reference_id") is None:
            raise ValidationError("training requirement requires reference_id")
        if training_repo.get_safety_training_by_id(payload["reference_id"], db) is None:
            raise NotFoundError(f"Safety training {payload['reference_id']} not found")
    else:
        if not payload.get("equipment_code"):
            raise ValidationError("equipment_authorization requirement requires equipment_code")
        if payload.get("min_authorization_level") not in VALID_LEVELS:
            raise ValidationError("equipment_authorization min_authorization_level must be one of L1, L2, L3, L4, L5")


def _ensure_unique(payload: dict, db: Session | None = None, exclude_id: int | None = None) -> None:
    rows = requirement_repo.list_operation_qualification_requirements(
        payload["production_operation_id"],
        None,
        None,
        db,
    )
    for row in rows:
        if exclude_id is not None and row["id"] == exclude_id:
            continue
        if (
            row["requirement_type"] == payload["requirement_type"]
            and row.get("reference_id") == payload.get("reference_id")
            and row.get("equipment_code") == payload.get("equipment_code")
        ):
            raise ConflictError("Operation qualification requirement already exists")


def list_operation_qualification_requirements(
    production_operation_id: int,
    status: str | None = None,
    db: Session | None = None,
) -> OperationQualificationRequirementListResponse:
    if operation_repo.get_production_operation_by_id(production_operation_id, db) is None:
        raise NotFoundError(f"Production operation {production_operation_id} not found")
    rows = requirement_repo.list_operation_qualification_requirements(
        production_operation_id,
        None,
        status,
        db,
    )
    return OperationQualificationRequirementListResponse(
        requirements=[_to_response(row) for row in rows],
        total=len(rows),
    )


def get_operation_qualification_requirement(
    requirement_id: int,
    db: Session | None = None,
) -> OperationQualificationRequirementResponse:
    return _to_response(_require_row(requirement_id, db))


def create_operation_qualification_requirement(
    production_operation_id: int,
    data: OperationQualificationRequirementCreate,
    db: Session | None = None,
) -> OperationQualificationRequirementResponse:
    payload = {"production_operation_id": production_operation_id, **data.model_dump()}
    _validate_payload(payload, db)
    _ensure_unique(payload, db)
    row = requirement_repo.create_operation_qualification_requirement(payload, db)
    return _to_response(row)


def update_operation_qualification_requirement(
    requirement_id: int,
    data: OperationQualificationRequirementUpdate,
    db: Session | None = None,
) -> OperationQualificationRequirementResponse:
    current = _require_row(requirement_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    _ensure_unique(payload, db, exclude_id=requirement_id)
    row = requirement_repo.update_operation_qualification_requirement(
        requirement_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Operation qualification requirement {requirement_id} not found")
    return _to_response(row)


def delete_operation_qualification_requirement(requirement_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(requirement_id, db)
    requirement_repo.delete_operation_qualification_requirement(requirement_id, db)
    return {"message": f"Operation qualification requirement {requirement_id} deleted"}
