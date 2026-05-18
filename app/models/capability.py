"""能力域模型，描述技能目录与人员技能。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.qualification import SafetyTraining, WorkstationSkillRequirement
    from app.models.workforce import Worker


class Skill(Base, IdentityMixin, TimestampMixin, DictMixin):
    """技能目录主数据。"""

    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    worker_skills: Mapped[list[WorkerSkill]] = relationship(
        "WorkerSkill",
        back_populates="skill",
        primaryjoin="Skill.id == foreign(WorkerSkill.skill_id)",
        foreign_keys="WorkerSkill.skill_id",
        cascade="all, delete-orphan",
    )
    workstation_requirements: Mapped[list[WorkstationSkillRequirement]] = relationship(
        "WorkstationSkillRequirement",
        back_populates="skill",
        primaryjoin="Skill.id == foreign(WorkstationSkillRequirement.skill_id)",
        foreign_keys="WorkstationSkillRequirement.skill_id",
        cascade="all, delete-orphan",
    )
    safety_trainings: Mapped[list[SafetyTraining]] = relationship(
        "SafetyTraining",
        back_populates="skill",
        primaryjoin="Skill.id == foreign(SafetyTraining.skill_id)",
        foreign_keys="SafetyTraining.skill_id",
    )


class WorkerSkill(Base, IdentityMixin, TimestampMixin, DictMixin):
    """人员技能画像，表达技能熟练度与经验。"""

    __tablename__ = "worker_skills"
    __table_args__ = (
        UniqueConstraint("worker_id", "skill_id"),
        Index("ix_worker_skills_worker_proficiency", "worker_id", "proficiency_level"),
    )

    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, nullable=False)
    proficiency_level: Mapped[str] = mapped_column(String(20), nullable=False)
    years_of_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="skills",
        primaryjoin="foreign(WorkerSkill.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )
    skill: Mapped[Skill] = relationship(
        "Skill",
        back_populates="worker_skills",
        primaryjoin="foreign(WorkerSkill.skill_id) == Skill.id",
        foreign_keys=[skill_id],
    )


__all__ = ["Skill", "WorkerSkill"]
