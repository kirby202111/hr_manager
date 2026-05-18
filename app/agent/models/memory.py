"""Agent runtime memory models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin


class AgentMemory(Base, IdentityMixin, TimestampMixin, DictMixin):
    """Agent long-term memory entry."""

    __tablename__ = "agent_memories"
    __table_args__ = (
        Index("ix_agent_memories_user_created", "user_tag", "created_at"),
        Index("ix_agent_memories_subject", "subject"),
        Index("ix_agent_memories_active_expires", "is_active", "expires_at"),
    )

    session_id: Mapped[str] = mapped_column(String(80), nullable=False)
    user_tag: Mapped[str | None] = mapped_column(String(80), nullable=True)
    memory_type: Mapped[str] = mapped_column(String(30), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    importance: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # No database foreign key is used; relationship is expressed explicitly.
    reminders: Mapped[list[MemoryReminder]] = relationship(
        "MemoryReminder",
        back_populates="memory",
        primaryjoin="foreign(MemoryReminder.memory_id) == AgentMemory.id",
        foreign_keys="MemoryReminder.memory_id",
        cascade="all, delete-orphan",
    )


class MemoryReminder(Base, IdentityMixin, DictMixin):
    """Reminder task attached to an agent memory entry."""

    __tablename__ = "memory_reminders"
    __table_args__ = (
        Index("ix_memory_reminders_memory_id", "memory_id"),
        Index("ix_memory_reminders_trigger_status", "trigger_at", "triggered"),
    )

    memory_id: Mapped[int] = mapped_column(Integer, nullable=False)
    reminder_type: Mapped[str] = mapped_column(String(20), nullable=False)
    trigger_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(120), nullable=True)
    triggered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    memory: Mapped[AgentMemory] = relationship(
        "AgentMemory",
        back_populates="reminders",
        primaryjoin=lambda: foreign(MemoryReminder.memory_id) == AgentMemory.id,
        foreign_keys=lambda: [MemoryReminder.memory_id],
    )


__all__ = ["AgentMemory", "MemoryReminder"]
