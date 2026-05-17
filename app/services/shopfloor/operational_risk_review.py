"""Service module."""

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.repositories.shopfloor import operational_risk_review as operational_risk_review_repo
from app.repositories.shopfloor import operational_risk_signal as operational_risk_signal_repo
from app.schemas.shopfloor import (
    OperationalRiskReviewCreate,
    OperationalRiskReviewListResponse,
    OperationalRiskReviewResponse,
    OperationalRiskReviewUpdate,
)


def _to_response(row: dict) -> OperationalRiskReviewResponse:
    return OperationalRiskReviewResponse(**row)


def _require_row(operational_risk_review_id: int, db: Session | None = None) -> dict:
    row = operational_risk_review_repo.get_operational_risk_review_by_id(operational_risk_review_id, db)
    if row is None:
        raise NotFoundError(f"Operational risk review {operational_risk_review_id} not found")
    return row


def list_operational_risk_reviews(
    risk_signal_id: int | None = None,
    review_status: str | None = None,
    db: Session | None = None,
) -> OperationalRiskReviewListResponse:
    rows = operational_risk_review_repo.list_operational_risk_reviews(risk_signal_id, review_status, db)
    return OperationalRiskReviewListResponse(
        operational_risk_reviews=[_to_response(row) for row in rows], total=len(rows)
    )


def get_operational_risk_review(
    operational_risk_review_id: int, db: Session | None = None
) -> OperationalRiskReviewResponse:
    return _to_response(_require_row(operational_risk_review_id, db))


def create_operational_risk_review(
    data: OperationalRiskReviewCreate,
    db: Session | None = None,
) -> OperationalRiskReviewResponse:
    if operational_risk_signal_repo.get_operational_risk_signal_by_id(data.risk_signal_id, db) is None:
        raise NotFoundError(f"Operational risk signal {data.risk_signal_id} not found")
    row = operational_risk_review_repo.create_operational_risk_review(data.model_dump(), db)
    return _to_response(row)


def update_operational_risk_review(
    operational_risk_review_id: int,
    data: OperationalRiskReviewUpdate,
    db: Session | None = None,
) -> OperationalRiskReviewResponse:
    current = _require_row(operational_risk_review_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if operational_risk_signal_repo.get_operational_risk_signal_by_id(payload["risk_signal_id"], db) is None:
        raise NotFoundError(f"Operational risk signal {payload['risk_signal_id']} not found")
    row = operational_risk_review_repo.update_operational_risk_review(
        operational_risk_review_id, data.model_dump(exclude_unset=True), db
    )
    if row is None:
        raise NotFoundError(f"Operational risk review {operational_risk_review_id} not found")
    return _to_response(row)


def delete_operational_risk_review(operational_risk_review_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(operational_risk_review_id, db)
    operational_risk_review_repo.delete_operational_risk_review(operational_risk_review_id, db)
    return {"message": f"Operational risk review {operational_risk_review_id} deleted"}
