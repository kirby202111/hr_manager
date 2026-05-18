"""生产现场域模型，覆盖产线、班组、工位、工单和风险。"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.capability import Skill
    from app.models.organization import OrganizationUnit
    from app.models.qualification import Certification
    from app.models.staffing import ShiftAssignment, ShiftPlan
    from app.models.workforce import Worker, WorkerAssignment


class ProductionLine(Base, IdentityMixin, TimestampMixin, DictMixin):
    """产线主档，是排班、工位和工单的现场载体。"""

    __tablename__ = "production_lines"
    __table_args__ = (UniqueConstraint("organization_unit_id", "code"),)

    organization_unit_id: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    supervisor_worker_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 产线同时连接组织归属、负责人、工位、工单、排班和风险。
    organization_unit: Mapped[OrganizationUnit] = relationship(
        "OrganizationUnit",
        back_populates="production_lines",
        primaryjoin="foreign(ProductionLine.organization_unit_id) == OrganizationUnit.id",
        foreign_keys=[organization_unit_id],
    )
    supervisor: Mapped[Worker | None] = relationship(
        "Worker",
        back_populates="supervised_lines",
        primaryjoin="foreign(ProductionLine.supervisor_worker_id) == Worker.id",
        foreign_keys=[supervisor_worker_id],
    )
    teams: Mapped[list[ProductionTeam]] = relationship(
        "ProductionTeam",
        back_populates="production_line",
        primaryjoin="ProductionLine.id == foreign(ProductionTeam.production_line_id)",
        foreign_keys="ProductionTeam.production_line_id",
        cascade="all, delete-orphan",
    )
    workstations: Mapped[list[Workstation]] = relationship(
        "Workstation",
        back_populates="production_line",
        primaryjoin="ProductionLine.id == foreign(Workstation.production_line_id)",
        foreign_keys="Workstation.production_line_id",
        cascade="all, delete-orphan",
    )
    worker_assignments: Mapped[list[WorkerAssignment]] = relationship(
        "WorkerAssignment",
        back_populates="production_line",
        primaryjoin="ProductionLine.id == foreign(WorkerAssignment.production_line_id)",
        foreign_keys="WorkerAssignment.production_line_id",
    )
    shift_plans: Mapped[list[ShiftPlan]] = relationship(
        "ShiftPlan",
        back_populates="production_line",
        primaryjoin="ProductionLine.id == foreign(ShiftPlan.production_line_id)",
        foreign_keys="ShiftPlan.production_line_id",
        cascade="all, delete-orphan",
    )
    production_orders: Mapped[list[ProductionOrder]] = relationship(
        "ProductionOrder",
        back_populates="production_line",
        primaryjoin="ProductionLine.id == foreign(ProductionOrder.production_line_id)",
        foreign_keys="ProductionOrder.production_line_id",
    )
    risk_signals: Mapped[list[OperationalRiskSignal]] = relationship(
        "OperationalRiskSignal",
        back_populates="production_line",
        primaryjoin="ProductionLine.id == foreign(OperationalRiskSignal.production_line_id)",
        foreign_keys="OperationalRiskSignal.production_line_id",
    )


class ProductionTeam(Base, IdentityMixin, TimestampMixin, DictMixin):
    """班组主档，用于表达产线下的执行单元。"""

    __tablename__ = "production_teams"
    __table_args__ = (UniqueConstraint("production_line_id", "code"),)

    production_line_id: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    leader_worker_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shift_pattern: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    production_line: Mapped[ProductionLine] = relationship(
        "ProductionLine",
        back_populates="teams",
        primaryjoin="foreign(ProductionTeam.production_line_id) == ProductionLine.id",
        foreign_keys=[production_line_id],
    )
    leader: Mapped[Worker | None] = relationship(
        "Worker",
        back_populates="led_teams",
        primaryjoin="foreign(ProductionTeam.leader_worker_id) == Worker.id",
        foreign_keys=[leader_worker_id],
    )
    worker_assignments: Mapped[list[WorkerAssignment]] = relationship(
        "WorkerAssignment",
        back_populates="production_team",
        primaryjoin="ProductionTeam.id == foreign(WorkerAssignment.production_team_id)",
        foreign_keys="WorkerAssignment.production_team_id",
    )


class Workstation(Base, IdentityMixin, TimestampMixin, DictMixin):
    """工位主档，承接能力要求、资格要求和实际分配。"""

    __tablename__ = "workstations"
    __table_args__ = (
        UniqueConstraint("production_line_id", "code"),
        Index("ix_workstations_line_status", "production_line_id", "status"),
    )

    production_line_id: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    workstation_type: Mapped[str] = mapped_column(String(40), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    production_line: Mapped[ProductionLine] = relationship(
        "ProductionLine",
        back_populates="workstations",
        primaryjoin="foreign(Workstation.production_line_id) == ProductionLine.id",
        foreign_keys=[production_line_id],
    )
    skill_requirements: Mapped[list[WorkstationSkillRequirement]] = relationship(
        "WorkstationSkillRequirement",
        back_populates="workstation",
        primaryjoin="Workstation.id == foreign(WorkstationSkillRequirement.workstation_id)",
        foreign_keys="WorkstationSkillRequirement.workstation_id",
        cascade="all, delete-orphan",
    )
    certification_requirements: Mapped[list[WorkstationCertificationRequirement]] = relationship(
        "WorkstationCertificationRequirement",
        back_populates="workstation",
        primaryjoin="Workstation.id == foreign(WorkstationCertificationRequirement.workstation_id)",
        foreign_keys="WorkstationCertificationRequirement.workstation_id",
        cascade="all, delete-orphan",
    )
    equipment_requirements: Mapped[list[WorkstationEquipmentRequirement]] = relationship(
        "WorkstationEquipmentRequirement",
        back_populates="workstation",
        primaryjoin="Workstation.id == foreign(WorkstationEquipmentRequirement.workstation_id)",
        foreign_keys="WorkstationEquipmentRequirement.workstation_id",
        cascade="all, delete-orphan",
    )
    operations: Mapped[list[ProductionOperation]] = relationship(
        "ProductionOperation",
        back_populates="workstation",
        primaryjoin="Workstation.id == foreign(ProductionOperation.workstation_id)",
        foreign_keys="ProductionOperation.workstation_id",
    )
    shift_assignments: Mapped[list[ShiftAssignment]] = relationship(
        "ShiftAssignment",
        back_populates="workstation",
        primaryjoin="Workstation.id == foreign(ShiftAssignment.workstation_id)",
        foreign_keys="ShiftAssignment.workstation_id",
    )
    risk_signals: Mapped[list[OperationalRiskSignal]] = relationship(
        "OperationalRiskSignal",
        back_populates="workstation",
        primaryjoin="Workstation.id == foreign(OperationalRiskSignal.workstation_id)",
        foreign_keys="OperationalRiskSignal.workstation_id",
    )


class WorkstationSkillRequirement(Base, IdentityMixin, TimestampMixin, DictMixin):
    """工位技能要求。"""

    __tablename__ = "workstation_skill_requirements"
    __table_args__ = (UniqueConstraint("workstation_id", "skill_id"),)

    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, nullable=False)
    required_proficiency: Mapped[str] = mapped_column(String(20), nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    workstation: Mapped[Workstation] = relationship(
        "Workstation",
        back_populates="skill_requirements",
        primaryjoin="foreign(WorkstationSkillRequirement.workstation_id) == Workstation.id",
        foreign_keys=[workstation_id],
    )
    skill: Mapped[Skill] = relationship(
        "Skill",
        back_populates="workstation_requirements",
        primaryjoin="foreign(WorkstationSkillRequirement.skill_id) == Skill.id",
        foreign_keys=[skill_id],
    )


class WorkstationCertificationRequirement(Base, IdentityMixin, TimestampMixin, DictMixin):
    """工位证书要求。"""

    __tablename__ = "workstation_certification_requirements"
    __table_args__ = (UniqueConstraint("workstation_id", "certification_id"),)

    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    certification_id: Mapped[int] = mapped_column(Integer, nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    workstation: Mapped[Workstation] = relationship(
        "Workstation",
        back_populates="certification_requirements",
        primaryjoin="foreign(WorkstationCertificationRequirement.workstation_id) == Workstation.id",
        foreign_keys=[workstation_id],
    )
    certification: Mapped[Certification] = relationship(
        "Certification",
        back_populates="workstation_requirements",
        primaryjoin="foreign(WorkstationCertificationRequirement.certification_id) == Certification.id",
        foreign_keys=[certification_id],
    )


class WorkstationEquipmentRequirement(Base, IdentityMixin, TimestampMixin, DictMixin):
    """工位设备授权要求。"""

    __tablename__ = "workstation_equipment_requirements"
    __table_args__ = (UniqueConstraint("workstation_id", "equipment_code"),)

    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    equipment_code: Mapped[str] = mapped_column(String(100), nullable=False)
    required_authorization_level: Mapped[str] = mapped_column(String(20), nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    workstation: Mapped[Workstation] = relationship(
        "Workstation",
        back_populates="equipment_requirements",
        primaryjoin="foreign(WorkstationEquipmentRequirement.workstation_id) == Workstation.id",
        foreign_keys=[workstation_id],
    )


class ProductionOrder(Base, IdentityMixin, TimestampMixin, DictMixin):
    """生产工单主档。"""

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
    """工单下的工序/工步。"""

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


class OperationalRiskSignal(Base, IdentityMixin, TimestampMixin, DictMixin):
    """现场风险信号，可挂接到人、线、工位、排班或工单。"""

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
    """风险信号的复核与处置建议。"""

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


__all__ = [
    "OperationalRiskReview",
    "OperationalRiskSignal",
    "ProductionLine",
    "ProductionOperation",
    "ProductionOrder",
    "ProductionTeam",
    "Workstation",
    "WorkstationCertificationRequirement",
    "WorkstationEquipmentRequirement",
    "WorkstationSkillRequirement",
]
