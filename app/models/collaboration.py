"""协同域模型，覆盖项目、成员、技能需求和工时。"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.capability import Skill
    from app.models.workforce import Worker


class Project(Base, IdentityMixin, TimestampMixin, DictMixin):
    """项目主档。"""

    __tablename__ = "projects"

    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    members: Mapped[list[ProjectMember]] = relationship(
        "ProjectMember",
        back_populates="project",
        primaryjoin="Project.id == foreign(ProjectMember.project_id)",
        foreign_keys="ProjectMember.project_id",
        cascade="all, delete-orphan",
    )
    skill_requirements: Mapped[list[ProjectSkillRequirement]] = relationship(
        "ProjectSkillRequirement",
        back_populates="project",
        primaryjoin="Project.id == foreign(ProjectSkillRequirement.project_id)",
        foreign_keys="ProjectSkillRequirement.project_id",
        cascade="all, delete-orphan",
    )
    timesheet_entries: Mapped[list[ProjectTimesheetEntry]] = relationship(
        "ProjectTimesheetEntry",
        back_populates="project",
        primaryjoin="Project.id == foreign(ProjectTimesheetEntry.project_id)",
        foreign_keys="ProjectTimesheetEntry.project_id",
        cascade="all, delete-orphan",
    )


class ProjectMember(Base, IdentityMixin, TimestampMixin, DictMixin):
    """项目成员记录。"""

    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "worker_id"),
        Index("ix_project_members_project_worker", "project_id", "worker_id"),
    )

    project_id: Mapped[int] = mapped_column(Integer, nullable=False)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    assigned_date: Mapped[date] = mapped_column(Date, nullable=False)
    allocation_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    project: Mapped[Project] = relationship(
        "Project",
        back_populates="members",
        primaryjoin="foreign(ProjectMember.project_id) == Project.id",
        foreign_keys=[project_id],
    )
    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="project_memberships",
        primaryjoin="foreign(ProjectMember.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )


class ProjectSkillRequirement(Base, IdentityMixin, TimestampMixin, DictMixin):
    """项目技能需求。"""

    __tablename__ = "project_skill_requirements"
    __table_args__ = (
        UniqueConstraint("project_id", "skill_id"),
        Index("ix_project_skill_requirements_project_skill", "project_id", "skill_id"),
    )

    project_id: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, nullable=False)
    required_proficiency: Mapped[str] = mapped_column(String(20), nullable=False)
    person_days: Mapped[float] = mapped_column(Float, nullable=False)
    headcount: Mapped[int] = mapped_column(nullable=False)

    project: Mapped[Project] = relationship(
        "Project",
        back_populates="skill_requirements",
        primaryjoin="foreign(ProjectSkillRequirement.project_id) == Project.id",
        foreign_keys=[project_id],
    )
    skill: Mapped[Skill] = relationship(
        "Skill",
        back_populates="project_requirements",
        primaryjoin="foreign(ProjectSkillRequirement.skill_id) == Skill.id",
        foreign_keys=[skill_id],
    )
    timesheet_entries: Mapped[list[ProjectTimesheetEntry]] = relationship(
        "ProjectTimesheetEntry",
        back_populates="project_skill_requirement",
        primaryjoin="ProjectSkillRequirement.id == foreign(ProjectTimesheetEntry.project_skill_requirement_id)",
        foreign_keys="ProjectTimesheetEntry.project_skill_requirement_id",
    )


class ProjectTimesheetEntry(Base, IdentityMixin, TimestampMixin, DictMixin):
    """项目工时填报记录。"""

    __tablename__ = "project_timesheet_entries"
    __table_args__ = (
        Index("ix_project_timesheet_entries_project_worker_work_date", "project_id", "worker_id", "work_date"),
        Index("ix_project_timesheet_entries_requirement_id", "project_skill_requirement_id"),
    )

    project_id: Mapped[int] = mapped_column(Integer, nullable=False)
    project_skill_requirement_id: Mapped[int] = mapped_column(Integer, nullable=False)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[Project] = relationship(
        "Project",
        back_populates="timesheet_entries",
        primaryjoin="foreign(ProjectTimesheetEntry.project_id) == Project.id",
        foreign_keys=[project_id],
    )
    project_skill_requirement: Mapped[ProjectSkillRequirement] = relationship(
        "ProjectSkillRequirement",
        back_populates="timesheet_entries",
        primaryjoin="foreign(ProjectTimesheetEntry.project_skill_requirement_id) == ProjectSkillRequirement.id",
        foreign_keys=[project_skill_requirement_id],
    )
    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="project_timesheet_entries",
        primaryjoin="foreign(ProjectTimesheetEntry.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )


__all__ = [
    "Project",
    "ProjectMember",
    "ProjectSkillRequirement",
    "ProjectTimesheetEntry",
]
