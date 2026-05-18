"""Qualification domain models."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.capability import Skill
    from app.models.shopfloor import Workstation
    from app.models.workforce import Worker


class Certification(Base, IdentityMixin, TimestampMixin, DictMixin):
    __tablename__ = "certifications"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    validity_months: Mapped[int | None] = mapped_column(nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    worker_certifications: Mapped[list[WorkerCertification]] = relationship(
        "WorkerCertification",
        back_populates="certification",
        primaryjoin="Certification.id == foreign(WorkerCertification.certification_id)",
        foreign_keys="WorkerCertification.certification_id",
        cascade="all, delete-orphan",
    )
    workstation_requirements: Mapped[list[WorkstationCertificationRequirement]] = relationship(
        "WorkstationCertificationRequirement",
        back_populates="certification",
        primaryjoin="Certification.id == foreign(WorkstationCertificationRequirement.certification_id)",
        foreign_keys="WorkstationCertificationRequirement.certification_id",
        cascade="all, delete-orphan",
    )
    safety_trainings: Mapped[list[SafetyTraining]] = relationship(
        "SafetyTraining",
        back_populates="required_certification",
        primaryjoin="Certification.id == foreign(SafetyTraining.required_certification_id)",
        foreign_keys="SafetyTraining.required_certification_id",
    )


class WorkerCertification(Base, IdentityMixin, TimestampMixin, DictMixin):
    __tablename__ = "worker_certifications"
    __table_args__ = (
        UniqueConstraint("worker_id", "certification_id"),
        Index("ix_worker_certifications_status_expires_at", "status", "expires_at"),
    )

    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    certification_id: Mapped[int] = mapped_column(Integer, nullable=False)
    certification_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    issued_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="valid")
    evidence_uri: Mapped[str | None] = mapped_column(String(255), nullable=True)

    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="certifications",
        primaryjoin="foreign(WorkerCertification.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )
    certification: Mapped[Certification] = relationship(
        "Certification",
        back_populates="worker_certifications",
        primaryjoin="foreign(WorkerCertification.certification_id) == Certification.id",
        foreign_keys=[certification_id],
    )


class SafetyTraining(Base, IdentityMixin, TimestampMixin, DictMixin):
    __tablename__ = "safety_trainings"

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    skill_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    required_certification_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validity_months: Mapped[int | None] = mapped_column(nullable=True)
    required_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    skill: Mapped[Skill | None] = relationship(
        "Skill",
        back_populates="safety_trainings",
        primaryjoin="foreign(SafetyTraining.skill_id) == Skill.id",
        foreign_keys=[skill_id],
    )
    required_certification: Mapped[Certification | None] = relationship(
        "Certification",
        back_populates="safety_trainings",
        primaryjoin="foreign(SafetyTraining.required_certification_id) == Certification.id",
        foreign_keys=[required_certification_id],
    )
    worker_records: Mapped[list[WorkerSafetyTraining]] = relationship(
        "WorkerSafetyTraining",
        back_populates="safety_training",
        primaryjoin="SafetyTraining.id == foreign(WorkerSafetyTraining.safety_training_id)",
        foreign_keys="WorkerSafetyTraining.safety_training_id",
        cascade="all, delete-orphan",
    )


class WorkerSafetyTraining(Base, IdentityMixin, TimestampMixin, DictMixin):
    __tablename__ = "worker_safety_trainings"
    __table_args__ = (
        UniqueConstraint("worker_id", "safety_training_id"),
        Index("ix_worker_safety_trainings_status", "status"),
    )

    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    safety_training_id: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="valid")

    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="safety_trainings",
        primaryjoin="foreign(WorkerSafetyTraining.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )
    safety_training: Mapped[SafetyTraining] = relationship(
        "SafetyTraining",
        back_populates="worker_records",
        primaryjoin="foreign(WorkerSafetyTraining.safety_training_id) == SafetyTraining.id",
        foreign_keys=[safety_training_id],
    )


class EquipmentAuthorization(Base, IdentityMixin, TimestampMixin, DictMixin):
    __tablename__ = "equipment_authorizations"
    __table_args__ = (
        UniqueConstraint("worker_id", "equipment_code"),
        Index("ix_equipment_authorizations_status_expires_at", "status", "expires_at"),
    )

    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    equipment_code: Mapped[str] = mapped_column(String(100), nullable=False)
    authorization_level: Mapped[str] = mapped_column(String(20), nullable=False)
    issued_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="valid")
    evidence_uri: Mapped[str | None] = mapped_column(String(255), nullable=True)

    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="equipment_authorizations",
        primaryjoin="foreign(EquipmentAuthorization.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )


class WorkstationSkillRequirement(Base, IdentityMixin, TimestampMixin, DictMixin):
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


__all__ = [
    "Certification",
    "EquipmentAuthorization",
    "SafetyTraining",
    "WorkerCertification",
    "WorkerSafetyTraining",
    "WorkstationCertificationRequirement",
    "WorkstationEquipmentRequirement",
    "WorkstationSkillRequirement",
]
