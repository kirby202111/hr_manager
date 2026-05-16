from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class ProductionRiskSignal(Base):
    __tablename__ = "production_risk_signals"
    __table_args__ = (Index("ix_production_risk_signals_status", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    employee_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    workstation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shift_assignment_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    signal_type: Mapped[str] = mapped_column(String(60), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    detected_by: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class ProductionRiskReview(Base):
    __tablename__ = "production_risk_reviews"
    __table_args__ = (Index("ix_production_risk_reviews_risk_signal_id", "risk_signal_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    risk_signal_id: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewer: Mapped[str] = mapped_column(String(100), nullable=False)
    conclusion: Mapped[str] = mapped_column(String, nullable=False)
    action_suggestion: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
