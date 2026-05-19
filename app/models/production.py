"""Production domain models."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.risk import OperationalRiskSignal
    from app.models.shopfloor import ProductionLine, Workstation
    from app.models.staffing import ShiftPlan


class ProductionOrder(Base, IdentityMixin, TimestampMixin, DictMixin):
    """Production order."""

    __tablename__ = "production_orders"
    __table_args__ = (UniqueConstraint("order_number"),)

    order_number: Mapped[str] = mapped_column(String(60), nullable=False)
    production_line_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_code: Mapped[str] = mapped_column(String(60), nullable=False)
    product_name: Mapped[str] = mapped_column(String(150), nullable=False)
    planned_quantity: Mapped[int] = mapped_column(nullable=False)
    planned_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planned")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    production_line: Mapped[ProductionLine | None] = relationship(
        "ProductionLine",
        back_populates="production_orders",
        primaryjoin="foreign(ProductionOrder.production_line_id) == ProductionLine.id",
        foreign_keys=[production_line_id],
    )
    operations: Mapped[list[ProductionOperation]] = relationship(
        "ProductionOperation",
        back_populates="production_order",
        primaryjoin="ProductionOrder.id == foreign(ProductionOperation.production_order_id)",
        foreign_keys="ProductionOperation.production_order_id",
        cascade="all, delete-orphan",
    )
    shift_plans: Mapped[list[ShiftPlan]] = relationship(
        "ShiftPlan",
        back_populates="production_order",
        primaryjoin="ProductionOrder.id == foreign(ShiftPlan.production_order_id)",
        foreign_keys="ShiftPlan.production_order_id",
    )
    risk_signals: Mapped[list[OperationalRiskSignal]] = relationship(
        "OperationalRiskSignal",
        back_populates="production_order",
        primaryjoin="ProductionOrder.id == foreign(OperationalRiskSignal.production_order_id)",
        foreign_keys="OperationalRiskSignal.production_order_id",
    )


class ProductionOperation(Base, IdentityMixin, TimestampMixin, DictMixin):
    """Operation within a production order."""

    __tablename__ = "production_operations"
    __table_args__ = (
        UniqueConstraint("production_order_id", "sequence_number"),
        Index("ix_production_operations_workstation_status", "workstation_id", "status"),
    )

    production_order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    operation_code: Mapped[str] = mapped_column(String(60), nullable=False)
    operation_name: Mapped[str] = mapped_column(String(120), nullable=False)
    sequence_number: Mapped[int] = mapped_column(nullable=False)
    planned_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    required_headcount: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planned")

    production_order: Mapped[ProductionOrder] = relationship(
        "ProductionOrder",
        back_populates="operations",
        primaryjoin="foreign(ProductionOperation.production_order_id) == ProductionOrder.id",
        foreign_keys=[production_order_id],
    )
    workstation: Mapped[Workstation] = relationship(
        "Workstation",
        back_populates="operations",
        primaryjoin="foreign(ProductionOperation.workstation_id) == Workstation.id",
        foreign_keys=[workstation_id],
    )
    qualification_requirements: Mapped[list[OperationQualificationRequirement]] = relationship(
        "OperationQualificationRequirement",
        back_populates="production_operation",
        primaryjoin="ProductionOperation.id == foreign(OperationQualificationRequirement.production_operation_id)",
        foreign_keys="OperationQualificationRequirement.production_operation_id",
        cascade="all, delete-orphan",
    )


class OperationQualificationRequirement(Base, IdentityMixin, TimestampMixin, DictMixin):
    __tablename__ = "operation_qualification_requirements"
    __table_args__ = (
        Index("ix_operation_qualification_requirements_operation_status", "production_operation_id", "status"),
    )

    production_operation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    requirement_type: Mapped[str] = mapped_column(String(40), nullable=False)
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    equipment_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    min_proficiency_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    must_be_validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    min_authorization_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    min_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    production_operation: Mapped[ProductionOperation] = relationship(
        "ProductionOperation",
        back_populates="qualification_requirements",
        primaryjoin="foreign(OperationQualificationRequirement.production_operation_id) == ProductionOperation.id",
        foreign_keys=[production_operation_id],
    )


__all__ = ["OperationQualificationRequirement", "ProductionOperation", "ProductionOrder"]
