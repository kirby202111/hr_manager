"""Workstation certification requirement service."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.qualification import certification as certification_repo
from app.repositories.shopfloor import workstation as workstation_repo
from app.repositories.shopfloor import workstation_certification_requirement as requirement_repo
from app.schemas.shopfloor import (
    WorkstationCertificationRequirementCreate,
    WorkstationCertificationRequirementListResponse,
    WorkstationCertificationRequirementResponse,
    WorkstationCertificationRequirementUpdate,
)


def _to_response(row: dict) -> WorkstationCertificationRequirementResponse:
    return WorkstationCertificationRequirementResponse(**row)


def _require_row(requirement_id: int, db: Session | None = None) -> dict:
    row = requirement_repo.get_workstation_certification_requirement_by_id(requirement_id, db)
    if row is None:
        raise NotFoundError(f"Workstation certification requirement {requirement_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if workstation_repo.get_workstation_by_id(payload["workstation_id"], db) is None:
        raise NotFoundError(f"Workstation {payload['workstation_id']} not found")
    if certification_repo.get_certification_by_id(payload["certification_id"], db) is None:
        raise NotFoundError(f"Certification {payload['certification_id']} not found")
    if payload["grace_days"] < 0:
        raise ValidationError("grace_days cannot be negative")


def list_workstation_certification_requirements(
    workstation_id: int,
    status: str | None = None,
    db: Session | None = None,
) -> WorkstationCertificationRequirementListResponse:
    if workstation_repo.get_workstation_by_id(workstation_id, db) is None:
        raise NotFoundError(f"Workstation {workstation_id} not found")
    rows = requirement_repo.list_workstation_certification_requirements(
        workstation_id=workstation_id,
        status=status,
        db=db,
    )
    return WorkstationCertificationRequirementListResponse(
        requirements=[_to_response(row) for row in rows],
        total=len(rows),
    )


def get_workstation_certification_requirement(
    requirement_id: int,
    db: Session | None = None,
) -> WorkstationCertificationRequirementResponse:
    return _to_response(_require_row(requirement_id, db))


def create_workstation_certification_requirement(
    workstation_id: int,
    data: WorkstationCertificationRequirementCreate,
    db: Session | None = None,
) -> WorkstationCertificationRequirementResponse:
    payload = {"workstation_id": workstation_id, **data.model_dump()}
    _validate_payload(payload, db)
    existing = requirement_repo.get_workstation_certification_requirement_by_workstation_and_certification(
        workstation_id,
        payload["certification_id"],
        db,
    )
    if existing is not None:
        raise ConflictError("Workstation certification requirement already exists")
    row = requirement_repo.create_workstation_certification_requirement(payload, db)
    return _to_response(row)


def update_workstation_certification_requirement(
    requirement_id: int,
    data: WorkstationCertificationRequirementUpdate,
    db: Session | None = None,
) -> WorkstationCertificationRequirementResponse:
    current = _require_row(requirement_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = requirement_repo.get_workstation_certification_requirement_by_workstation_and_certification(
        payload["workstation_id"],
        payload["certification_id"],
        db,
    )
    if existing is not None and existing["id"] != requirement_id:
        raise ConflictError("Workstation certification requirement already exists")
    row = requirement_repo.update_workstation_certification_requirement(
        requirement_id,
        data.model_dump(exclude_unset=True),
        db,
    )
    if row is None:
        raise NotFoundError(f"Workstation certification requirement {requirement_id} not found")
    return _to_response(row)


def delete_workstation_certification_requirement(requirement_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(requirement_id, db)
    requirement_repo.delete_workstation_certification_requirement(requirement_id, db)
    return {"message": f"Workstation certification requirement {requirement_id} deleted"}
