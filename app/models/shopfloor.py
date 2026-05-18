"""Shopfloor domain models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.organization import OrganizationUnit
    from app.models.production import ProductionOperation, ProductionOrder
    from app.models.qualification import (
        WorkstationCertificationRequirement,
        WorkstationEquipmentRequirement,
        WorkstationSkillRequirement,
    )
    from app.models.risk import OperationalRiskSignal
    from app.models.staffing import ShiftAssignment, ShiftPlan
    from app.models.workforce import Worker, WorkerAssignment


class ProductionLine(Base, IdentityMixin, TimestampMixin, DictMixin):
    __tablename__ = "production_lines"
    __table_args__ = (UniqueConstraint("organization_unit_id", "code"),)

    organization_unit_id: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    supervisor_worker_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

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


__all__ = ["ProductionLine", "ProductionTeam", "Workstation"]
