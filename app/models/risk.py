"""Risk domain models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.production import ProductionOrder
    from app.models.shopfloor import ProductionLine, Workstation
    from app.models.staffing import ShiftAssignment
    from app.models.workforce import Worker


class OperationalRiskSignal(Base, IdentityMixin, TimestampMixin, DictMixin):
    """Operational risk signal."""

    __tablename__ = "operational_risk_signals"
    __table_args__ = (
        Index("ix_operational_risk_signals_status_created_at", "status", "created_at"),
        Index("ix_operational_risk_signals_line_workstation", "production_line_id", "workstation_id"),
    )

    production_order_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    worker_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    production_line_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    workstation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shift_assignment_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    signal_type: Mapped[str] = mapped_column(String(60), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    detected_by: Mapped[str] = mapped_column(String(40), nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)

    production_order: Mapped[ProductionOrder | None] = relationship(
        "ProductionOrder",
        back_populates="risk_signals",
        primaryjoin="foreign(OperationalRiskSignal.production_order_id) == ProductionOrder.id",
        foreign_keys=[production_order_id],
    )
    worker: Mapped[Worker | None] = relationship(
        "Worker",
        back_populates="raised_risk_signals",
        primaryjoin="foreign(OperationalRiskSignal.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )
    production_line: Mapped[ProductionLine | None] = relationship(
        "ProductionLine",
        back_populates="risk_signals",
        primaryjoin="foreign(OperationalRiskSignal.production_line_id) == ProductionLine.id",
        foreign_keys=[production_line_id],
    )
    workstation: Mapped[Workstation | None] = relationship(
        "Workstation",
        back_populates="risk_signals",
        primaryjoin="foreign(OperationalRiskSignal.workstation_id) == Workstation.id",
        foreign_keys=[workstation_id],
    )
    shift_assignment: Mapped[ShiftAssignment | None] = relationship(
        "ShiftAssignment",
        back_populates="risk_signals",
        primaryjoin="foreign(OperationalRiskSignal.shift_assignment_id) == ShiftAssignment.id",
        foreign_keys=[shift_assignment_id],
    )
    reviews: Mapped[list[OperationalRiskReview]] = relationship(
        "OperationalRiskReview",
        back_populates="risk_signal",
        primaryjoin="OperationalRiskSignal.id == foreign(OperationalRiskReview.risk_signal_id)",
        foreign_keys="OperationalRiskReview.risk_signal_id",
        cascade="all, delete-orphan",
    )


class OperationalRiskReview(Base, IdentityMixin, TimestampMixin, DictMixin):
    """Review for an operational risk signal."""

    __tablename__ = "operational_risk_reviews"
    __table_args__ = (Index("ix_operational_risk_reviews_risk_signal_id", "risk_signal_id"),)

    risk_signal_id: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    conclusion: Mapped[str] = mapped_column(Text, nullable=False)
    action_suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    review_status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")

    risk_signal: Mapped[OperationalRiskSignal] = relationship(
        "OperationalRiskSignal",
        back_populates="reviews",
        primaryjoin="foreign(OperationalRiskReview.risk_signal_id) == OperationalRiskSignal.id",
        foreign_keys=[risk_signal_id],
    )


__all__ = ["OperationalRiskReview", "OperationalRiskSignal"]
