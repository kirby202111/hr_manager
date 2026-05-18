"""人员主数据与任职归属模型。"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.attendance import AttendanceRecord, LeaveRequest, PayrollRecord
    from app.models.capability import WorkerSkill
    from app.models.organization import OrganizationUnit
    from app.models.qualification import EquipmentAuthorization, WorkerCertification, WorkerSafetyTraining
    from app.models.risk import OperationalRiskSignal
    from app.models.shopfloor import ProductionLine, ProductionTeam
    from app.models.staffing import ShiftAssignment


class Worker(Base, IdentityMixin, TimestampMixin, DictMixin):
    """人员主档，承载现场运营里的核心员工信息。"""

    __tablename__ = "workers"

    worker_code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    organization_unit_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    exit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    base_salary: Mapped[float | None] = mapped_column(Float, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 人员是多个业务链路的汇聚点：组织、能力、资质、排班、履约、项目、风险。
    organization_unit: Mapped[OrganizationUnit | None] = relationship(
        "OrganizationUnit",
        back_populates="workers",
        primaryjoin="foreign(Worker.organization_unit_id) == OrganizationUnit.id",
        foreign_keys=[organization_unit_id],
    )
    managed_units: Mapped[list[OrganizationUnit]] = relationship(
        "OrganizationUnit",
        back_populates="manager",
        primaryjoin="Worker.id == foreign(OrganizationUnit.manager_worker_id)",
        foreign_keys="OrganizationUnit.manager_worker_id",
    )
    assignments: Mapped[list[WorkerAssignment]] = relationship(
        "WorkerAssignment",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(WorkerAssignment.worker_id)",
        foreign_keys="WorkerAssignment.worker_id",
        cascade="all, delete-orphan",
    )
    skills: Mapped[list[WorkerSkill]] = relationship(
        "WorkerSkill",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(WorkerSkill.worker_id)",
        foreign_keys="WorkerSkill.worker_id",
        cascade="all, delete-orphan",
    )
    certifications: Mapped[list[WorkerCertification]] = relationship(
        "WorkerCertification",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(WorkerCertification.worker_id)",
        foreign_keys="WorkerCertification.worker_id",
        cascade="all, delete-orphan",
    )
    safety_trainings: Mapped[list[WorkerSafetyTraining]] = relationship(
        "WorkerSafetyTraining",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(WorkerSafetyTraining.worker_id)",
        foreign_keys="WorkerSafetyTraining.worker_id",
        cascade="all, delete-orphan",
    )
    equipment_authorizations: Mapped[list[EquipmentAuthorization]] = relationship(
        "EquipmentAuthorization",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(EquipmentAuthorization.worker_id)",
        foreign_keys="EquipmentAuthorization.worker_id",
        cascade="all, delete-orphan",
    )
    shift_assignments: Mapped[list[ShiftAssignment]] = relationship(
        "ShiftAssignment",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(ShiftAssignment.worker_id)",
        foreign_keys="ShiftAssignment.worker_id",
        cascade="all, delete-orphan",
    )
    attendance_records: Mapped[list[AttendanceRecord]] = relationship(
        "AttendanceRecord",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(AttendanceRecord.worker_id)",
        foreign_keys="AttendanceRecord.worker_id",
        cascade="all, delete-orphan",
    )
    leave_requests: Mapped[list[LeaveRequest]] = relationship(
        "LeaveRequest",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(LeaveRequest.worker_id)",
        foreign_keys="LeaveRequest.worker_id",
        cascade="all, delete-orphan",
    )
    payroll_records: Mapped[list[PayrollRecord]] = relationship(
        "PayrollRecord",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(PayrollRecord.worker_id)",
        foreign_keys="PayrollRecord.worker_id",
        cascade="all, delete-orphan",
    )
    raised_risk_signals: Mapped[list[OperationalRiskSignal]] = relationship(
        "OperationalRiskSignal",
        back_populates="worker",
        primaryjoin="Worker.id == foreign(OperationalRiskSignal.worker_id)",
        foreign_keys="OperationalRiskSignal.worker_id",
    )
    supervised_lines: Mapped[list[ProductionLine]] = relationship(
        "ProductionLine",
        back_populates="supervisor",
        primaryjoin="Worker.id == foreign(ProductionLine.supervisor_worker_id)",
        foreign_keys="ProductionLine.supervisor_worker_id",
    )
    led_teams: Mapped[list[ProductionTeam]] = relationship(
        "ProductionTeam",
        back_populates="leader",
        primaryjoin="Worker.id == foreign(ProductionTeam.leader_worker_id)",
        foreign_keys="ProductionTeam.leader_worker_id",
    )


class WorkerAssignment(Base, IdentityMixin, TimestampMixin, DictMixin):
    """人员在组织、产线、班组上的任职/归属记录。"""

    __tablename__ = "worker_assignments"
    __table_args__ = (
        Index("ix_worker_assignments_worker_status", "worker_id", "status"),
        Index("ix_worker_assignments_line_team", "production_line_id", "production_team_id"),
    )

    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    organization_unit_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    production_line_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    production_team_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    role_title: Mapped[str] = mapped_column(String(100), nullable=False)
    assignment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="assignments",
        primaryjoin="foreign(WorkerAssignment.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )
    organization_unit: Mapped[OrganizationUnit | None] = relationship(
        "OrganizationUnit",
        back_populates="worker_assignments",
        primaryjoin="foreign(WorkerAssignment.organization_unit_id) == OrganizationUnit.id",
        foreign_keys=[organization_unit_id],
    )
    production_line: Mapped[ProductionLine | None] = relationship(
        "ProductionLine",
        back_populates="worker_assignments",
        primaryjoin="foreign(WorkerAssignment.production_line_id) == ProductionLine.id",
        foreign_keys=[production_line_id],
    )
    production_team: Mapped[ProductionTeam | None] = relationship(
        "ProductionTeam",
        back_populates="worker_assignments",
        primaryjoin="foreign(WorkerAssignment.production_team_id) == ProductionTeam.id",
        foreign_keys=[production_team_id],
    )


__all__ = ["Worker", "WorkerAssignment"]
