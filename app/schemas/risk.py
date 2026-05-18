"""Risk schemas."""

from datetime import datetime

from pydantic import BaseModel


class OperationalRiskSignalCreate(BaseModel):
    production_order_id: int | None = None
    worker_id: int | None = None
    production_line_id: int | None = None
    workstation_id: int | None = None
    shift_assignment_id: int | None = None
    signal_type: str
    severity: str
    status: str = "open"
    detected_by: str
    evidence: str


class OperationalRiskSignalUpdate(BaseModel):
    production_order_id: int | None = None
    worker_id: int | None = None
    production_line_id: int | None = None
    workstation_id: int | None = None
    shift_assignment_id: int | None = None
    signal_type: str | None = None
    severity: str | None = None
    status: str | None = None
    detected_by: str | None = None
    evidence: str | None = None


class OperationalRiskSignalResponse(BaseModel):
    id: int
    production_order_id: int | None = None
    worker_id: int | None = None
    production_line_id: int | None = None
    workstation_id: int | None = None
    shift_assignment_id: int | None = None
    signal_type: str
    severity: str
    status: str
    detected_by: str
    evidence: str
    created_at: datetime
    updated_at: datetime


class OperationalRiskSignalListResponse(BaseModel):
    operational_risk_signals: list[OperationalRiskSignalResponse]
    total: int


class OperationalRiskReviewCreate(BaseModel):
    risk_signal_id: int
    reviewer_name: str
    conclusion: str
    action_suggestion: str
    review_status: str = "completed"


class OperationalRiskReviewUpdate(BaseModel):
    risk_signal_id: int | None = None
    reviewer_name: str | None = None
    conclusion: str | None = None
    action_suggestion: str | None = None
    review_status: str | None = None


class OperationalRiskReviewResponse(BaseModel):
    id: int
    risk_signal_id: int
    reviewer_name: str
    conclusion: str
    action_suggestion: str
    review_status: str
    created_at: datetime
    updated_at: datetime


class OperationalRiskReviewListResponse(BaseModel):
    operational_risk_reviews: list[OperationalRiskReviewResponse]
    total: int


__all__ = [
    "OperationalRiskReviewCreate",
    "OperationalRiskReviewListResponse",
    "OperationalRiskReviewResponse",
    "OperationalRiskReviewUpdate",
    "OperationalRiskSignalCreate",
    "OperationalRiskSignalListResponse",
    "OperationalRiskSignalResponse",
    "OperationalRiskSignalUpdate",
]
