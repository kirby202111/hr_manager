"""排班域模型，覆盖班次模板、排班计划和分配明细。"""

from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, Index, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.production import ProductionOrder
    from app.models.risk import OperationalRiskSignal
    from app.models.shopfloor import ProductionLine, Workstation
    from app.models.workforce import Worker


class ShiftTemplate(Base, IdentityMixin, TimestampMixin, DictMixin):
    """班次模板，定义时段和津贴规则。"""

    __tablename__ = "shift_templates"

    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    shift_type: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    allowance_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    shift_plans: Mapped[list[ShiftPlan]] = relationship(
        "ShiftPlan",
        back_populates="shift_template",
        primaryjoin="ShiftTemplate.id == foreign(ShiftPlan.shift_template_id)",
        foreign_keys="ShiftPlan.shift_template_id",
        cascade="all, delete-orphan",
    )


class ShiftPlan(Base, IdentityMixin, TimestampMixin, DictMixin):
    """某产线某日某班次的人力计划。"""

    __tablename__ = "shift_plans"
    __table_args__ = (
        UniqueConstraint("production_line_id", "work_date", "shift_template_id"),
        Index(
            "ix_shift_plans_line_work_date_shift_template_id",
            "production_line_id",
            "work_date",
            "shift_template_id",
        ),
    )

    production_order_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    production_line_id: Mapped[int] = mapped_column(Integer, nullable=False)
    shift_template_id: Mapped[int] = mapped_column(Integer, nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    required_headcount: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planned")
    created_by: Mapped[str | None] = mapped_column(String(120), nullable=True)

    production_order: Mapped[ProductionOrder | None] = relationship(
        "ProductionOrder",
        back_populates="shift_plans",
        primaryjoin="foreign(ShiftPlan.production_order_id) == ProductionOrder.id",
        foreign_keys=[production_order_id],
    )
    production_line: Mapped[ProductionLine] = relationship(
        "ProductionLine",
        back_populates="shift_plans",
        primaryjoin="foreign(ShiftPlan.production_line_id) == ProductionLine.id",
        foreign_keys=[production_line_id],
    )
    shift_template: Mapped[ShiftTemplate] = relationship(
        "ShiftTemplate",
        back_populates="shift_plans",
        primaryjoin="foreign(ShiftPlan.shift_template_id) == ShiftTemplate.id",
        foreign_keys=[shift_template_id],
    )
    assignments: Mapped[list[ShiftAssignment]] = relationship(
        "ShiftAssignment",
        back_populates="shift_plan",
        primaryjoin="ShiftPlan.id == foreign(ShiftAssignment.shift_plan_id)",
        foreign_keys="ShiftAssignment.shift_plan_id",
        cascade="all, delete-orphan",
    )


class ShiftAssignment(Base, IdentityMixin, TimestampMixin, DictMixin):
    """排班分配明细，落到具体人员和工位。"""

    __tablename__ = "shift_assignments"
    __table_args__ = (
        UniqueConstraint("shift_plan_id", "worker_id", "workstation_id"),
        Index("ix_shift_assignments_worker_status", "worker_id", "status"),
    )

    shift_plan_id: Mapped[int] = mapped_column(Integer, nullable=False)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    assignment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")
    assigned_role: Mapped[str | None] = mapped_column(String(100), nullable=True)

    shift_plan: Mapped[ShiftPlan] = relationship(
        "ShiftPlan",
        back_populates="assignments",
        primaryjoin="foreign(ShiftAssignment.shift_plan_id) == ShiftPlan.id",
        foreign_keys=[shift_plan_id],
    )
    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="shift_assignments",
        primaryjoin="foreign(ShiftAssignment.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )
    workstation: Mapped[Workstation] = relationship(
        "Workstation",
        back_populates="shift_assignments",
        primaryjoin="foreign(ShiftAssignment.workstation_id) == Workstation.id",
        foreign_keys=[workstation_id],
    )
    risk_signals: Mapped[list[OperationalRiskSignal]] = relationship(
        "OperationalRiskSignal",
        back_populates="shift_assignment",
        primaryjoin="ShiftAssignment.id == foreign(OperationalRiskSignal.shift_assignment_id)",
        foreign_keys="OperationalRiskSignal.shift_assignment_id",
    )


__all__ = ["ShiftAssignment", "ShiftPlan", "ShiftTemplate"]
