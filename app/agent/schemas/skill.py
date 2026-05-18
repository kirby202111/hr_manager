"""Agent skill schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SkillResponse(BaseModel):
    """Skill descriptor exposed to frontend."""

    name: str
    description: str
    applicability: str
    enabled: bool


class SkillListResponse(BaseModel):
    """Collection of runtime skills."""

    skills: list[SkillResponse]


__all__ = ["SkillListResponse", "SkillResponse"]
