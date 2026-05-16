from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProductionRiskSignalCreate(BaseModel):
    order_id: int | None = None
    employee_id: int | None = None
    line_id: int | None = None
    workstation_id: int | None = None
    shift_assignment_id: int | None = None
    signal_type: str
    severity: str = "medium"
    evidence: dict[str, Any] = Field(default_factory=dict)
    status: str = "open"
    detected_by: str = "human"


class ProductionRiskSignalUpdate(BaseModel):
    status: str | None = None
    severity: str | None = None
    evidence: dict[str, Any] | None = None


class ProductionRiskSignalResponse(ProductionRiskSignalCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class ProductionRiskReviewCreate(BaseModel):
    reviewer: str
    conclusion: str
    action_suggestion: str


class ProductionRiskReviewResponse(ProductionRiskReviewCreate):
    id: int
    risk_signal_id: int
    created_at: datetime
