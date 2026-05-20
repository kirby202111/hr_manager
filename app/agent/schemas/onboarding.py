"""Schemas for agent onboarding runtime state."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OnboardingCasePatch(BaseModel):
    """Patch payload for onboarding case updates."""

    worker_id: int | None = None
    worker_code: str | None = None
    worker_name: str | None = None
    employment_type: str | None = None
    hire_date: str | None = None
    organization_unit_id: int | None = None
    production_line_id: int | None = None
    production_team_id: int | None = None
    role_title: str | None = None
    target_workstation_id: int | None = None
    collected_fields: list[str] | None = None
    missing_fields: list[str] | None = None
    pending_actions: list[str] | None = None
    completed_actions: list[str] | None = None
    risk_flags: list[str] | None = None
    latest_eligibility: dict[str, Any] | None = None
    last_agent_summary: str | None = None
    is_active: bool | None = None


class OnboardingCaseResponse(BaseModel):
    """Stored onboarding case response."""

    id: int
    session_id: str
    user_tag: str
    intent: str
    worker_id: int | None = None
    worker_code: str | None = None
    worker_name: str | None = None
    employment_type: str | None = None
    hire_date: str | None = None
    organization_unit_id: int | None = None
    organization_unit_name: str | None = None
    production_line_id: int | None = None
    production_line_name: str | None = None
    production_team_id: int | None = None
    production_team_name: str | None = None
    role_title: str | None = None
    target_workstation_id: int | None = None
    target_workstation_name: str | None = None
    collected_fields: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    pending_actions: list[str] = Field(default_factory=list)
    completed_actions: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    latest_eligibility: dict[str, Any] | None = None
    last_agent_summary: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SessionStateResponse(BaseModel):
    """Session-level agent state surfaced to the frontend."""

    session_id: str
    onboarding_case: OnboardingCaseResponse | None = None


__all__ = ["OnboardingCasePatch", "OnboardingCaseResponse", "SessionStateResponse"]
