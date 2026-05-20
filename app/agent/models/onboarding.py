"""Agent runtime onboarding case model."""

from __future__ import annotations

from sqlalchemy import Boolean, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin


class OnboardingCase(Base, IdentityMixin, TimestampMixin, DictMixin):
    """Lightweight agent-owned onboarding state for multi-turn sessions."""

    __tablename__ = "agent_onboarding_cases"
    __table_args__ = (
        UniqueConstraint("session_id", "user_tag", "intent"),
        Index("ix_agent_onboarding_cases_user_active", "user_tag", "is_active"),
        Index("ix_agent_onboarding_cases_session_active", "session_id", "is_active"),
    )

    session_id: Mapped[str] = mapped_column(String(80), nullable=False)
    user_tag: Mapped[str] = mapped_column(String(80), nullable=False)
    intent: Mapped[str] = mapped_column(String(40), nullable=False, default="worker_onboarding")
    worker_id: Mapped[int | None] = mapped_column(nullable=True)
    worker_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    worker_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    hire_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    organization_unit_id: Mapped[int | None] = mapped_column(nullable=True)
    production_line_id: Mapped[int | None] = mapped_column(nullable=True)
    production_team_id: Mapped[int | None] = mapped_column(nullable=True)
    role_title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_workstation_id: Mapped[int | None] = mapped_column(nullable=True)
    collected_fields_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_fields_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    pending_actions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_actions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_flags_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    latest_eligibility_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_agent_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


__all__ = ["OnboardingCase"]
