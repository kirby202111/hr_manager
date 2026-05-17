"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.qualification import certification as certification_repo
from app.schemas.qualification import (
    CertificationCreate,
    CertificationListResponse,
    CertificationResponse,
    CertificationUpdate,
)


def _to_response(row: dict) -> CertificationResponse:
    return CertificationResponse(**row)


def _require_certification(certification_id: int, db: Session | None = None) -> dict:
    row = certification_repo.get_certification_by_id(certification_id, db)
    if row is None:
        raise NotFoundError(f"Certification {certification_id} not found")
    return row


def list_certifications(category: str | None = None, db: Session | None = None) -> CertificationListResponse:
    rows = certification_repo.list_certifications(category, db)
    return CertificationListResponse(certifications=[_to_response(row) for row in rows], total=len(rows))


def get_certification(certification_id: int, db: Session | None = None) -> CertificationResponse:
    return _to_response(_require_certification(certification_id, db))


def create_certification(data: CertificationCreate, db: Session | None = None) -> CertificationResponse:
    if certification_repo.get_certification_by_code(data.code, db) is not None:
        raise ConflictError(f"Certification code '{data.code}' already exists")
    row = certification_repo.create_certification(data.model_dump(), db)
    return _to_response(row)


def update_certification(
    certification_id: int,
    data: CertificationUpdate,
    db: Session | None = None,
) -> CertificationResponse:
    current = _require_certification(certification_id, db)
    payload = data.model_dump(exclude_unset=True)
    if "code" in payload and payload["code"] != current["code"]:
        if certification_repo.get_certification_by_code(payload["code"], db) is not None:
            raise ConflictError(f"Certification code '{payload['code']}' already exists")
    row = certification_repo.update_certification(certification_id, payload, db)
    if row is None:
        raise NotFoundError(f"Certification {certification_id} not found")
    return _to_response(row)


def delete_certification(certification_id: int, db: Session | None = None) -> dict[str, str]:
    _require_certification(certification_id, db)
    certification_repo.delete_certification(certification_id, db)
    return {"message": f"Certification {certification_id} deleted"}
