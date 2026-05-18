"""Capability-related agent tools."""

from __future__ import annotations

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.services.capability import skill as skill_service
from app.services.capability import worker_skill as worker_skill_service

skill = AgentSkill(
    name="capability",
    description="Query capability catalogs and worker skill matrices.",
    applicability="Use for skill catalog lookup, qualification matching, and worker capability inspection.",
    keywords=("skill", "capability", "qualification", "技能", "能力", "资质"),
    tools=[
        AgentTool(
            name="list_skills_catalog",
            description="List skill catalog records with optional category and status filters.",
            parameters={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
            fn=lambda category=None, status=None: safe_call(skill_service.list_skills, category, status),
        ),
        AgentTool(
            name="get_skill_detail",
            description="Get one skill by id.",
            parameters={
                "type": "object",
                "properties": {"skill_id": {"type": "integer"}},
                "required": ["skill_id"],
            },
            fn=lambda skill_id: safe_call(skill_service.get_skill, skill_id),
        ),
        AgentTool(
            name="list_worker_skills",
            description="List worker skill records with optional worker, skill, proficiency, and validation filters.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "skill_id": {"type": "integer"},
                    "proficiency_level": {"type": "string"},
                    "validated": {"type": "boolean"},
                },
            },
            fn=lambda worker_id=None, skill_id=None, proficiency_level=None, validated=None: safe_call(
                worker_skill_service.list_worker_skills,
                worker_id,
                skill_id,
                proficiency_level,
                validated,
            ),
        ),
    ],
)

__all__ = ["skill"]
