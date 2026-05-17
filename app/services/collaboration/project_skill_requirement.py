"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.capability import skill as skill_repo
from app.repositories.collaboration import project as project_repo
from app.repositories.collaboration import project_skill_requirement as project_skill_requirement_repo
from app.schemas.collaboration import (
    ProjectSkillRequirementCreate,
    ProjectSkillRequirementListResponse,
    ProjectSkillRequirementResponse,
    ProjectSkillRequirementUpdate,
)


def _to_response(row: dict) -> ProjectSkillRequirementResponse:
    return ProjectSkillRequirementResponse(**row)


def _require_row(project_skill_requirement_id: int, db: Session | None = None) -> dict:
    row = project_skill_requirement_repo.get_project_skill_requirement_by_id(project_skill_requirement_id, db)
    if row is None:
        raise NotFoundError(f"Project skill requirement {project_skill_requirement_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if project_repo.get_project_by_id(payload["project_id"], db) is None:
        raise NotFoundError(f"Project {payload['project_id']} not found")
    if skill_repo.get_skill_by_id(payload["skill_id"], db) is None:
        raise NotFoundError(f"Skill {payload['skill_id']} not found")
    if payload["person_days"] <= 0:
        raise ValidationError("person_days must be greater than 0")
    if payload["headcount"] <= 0:
        raise ValidationError("headcount must be greater than 0")


def list_project_skill_requirements(
    project_id: int | None = None,
    skill_id: int | None = None,
    db: Session | None = None,
) -> ProjectSkillRequirementListResponse:
    rows = project_skill_requirement_repo.list_project_skill_requirements(project_id, skill_id, db)
    return ProjectSkillRequirementListResponse(
        project_skill_requirements=[_to_response(row) for row in rows],
        total=len(rows),
    )


def get_project_skill_requirement(
    project_skill_requirement_id: int, db: Session | None = None
) -> ProjectSkillRequirementResponse:
    return _to_response(_require_row(project_skill_requirement_id, db))


def create_project_skill_requirement(
    data: ProjectSkillRequirementCreate,
    db: Session | None = None,
) -> ProjectSkillRequirementResponse:
    payload = data.model_dump()
    _validate_payload(payload, db)
    if (
        project_skill_requirement_repo.get_project_skill_requirement_by_project_and_skill(
            payload["project_id"], payload["skill_id"], db
        )
        is not None
    ):
        raise ConflictError("Project skill requirement already exists")
    row = project_skill_requirement_repo.create_project_skill_requirement(payload, db)
    return _to_response(row)


def update_project_skill_requirement(
    project_skill_requirement_id: int,
    data: ProjectSkillRequirementUpdate,
    db: Session | None = None,
) -> ProjectSkillRequirementResponse:
    current = _require_row(project_skill_requirement_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = project_skill_requirement_repo.get_project_skill_requirement_by_project_and_skill(
        payload["project_id"], payload["skill_id"], db
    )
    if existing is not None and existing["id"] != project_skill_requirement_id:
        raise ConflictError("Project skill requirement already exists")
    row = project_skill_requirement_repo.update_project_skill_requirement(
        project_skill_requirement_id, data.model_dump(exclude_unset=True), db
    )
    if row is None:
        raise NotFoundError(f"Project skill requirement {project_skill_requirement_id} not found")
    return _to_response(row)


def delete_project_skill_requirement(project_skill_requirement_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(project_skill_requirement_id, db)
    project_skill_requirement_repo.delete_project_skill_requirement(project_skill_requirement_id, db)
    return {"message": f"Project skill requirement {project_skill_requirement_id} deleted"}
