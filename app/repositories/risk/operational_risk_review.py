"""Operational risk review repository."""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.risk import OperationalRiskReview


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_operational_risk_reviews(
    risk_signal_id: int | None = None,
    review_status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(OperationalRiskReview)
        if risk_signal_id is not None:
            query = query.filter(OperationalRiskReview.risk_signal_id == risk_signal_id)
        if review_status is not None:
            query = query.filter(OperationalRiskReview.review_status == review_status)
        return [row.to_dict() for row in query.all()]


def get_operational_risk_review_by_id(operational_risk_review_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationalRiskReview, operational_risk_review_id)
        return row.to_dict() if row else None


def create_operational_risk_review(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = OperationalRiskReview(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_operational_risk_review(
    operational_risk_review_id: int, data: dict, db: Session | None = None
) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationalRiskReview, operational_risk_review_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_operational_risk_review(operational_risk_review_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(OperationalRiskReview, operational_risk_review_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
