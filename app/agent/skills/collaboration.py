"""Collaboration-related agent tools."""

from __future__ import annotations

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.services.collaboration import project as project_service

skill = AgentSkill(
    name="collaboration",
    description="Query project collaboration records.",
    applicability="Use for project lookup, progress context, and coordination-related conversations.",
    keywords=("project", "collaboration", "项目", "协作"),
    tools=[
        AgentTool(
            name="list_projects",
            description="List projects with optional status filtering.",
            parameters={
                "type": "object",
                "properties": {"status": {"type": "string"}},
            },
            fn=lambda status=None: safe_call(project_service.list_projects, status),
        ),
        AgentTool(
            name="get_project",
            description="Get one project by id.",
            parameters={
                "type": "object",
                "properties": {"project_id": {"type": "integer"}},
                "required": ["project_id"],
            },
            fn=lambda project_id: safe_call(project_service.get_project, project_id),
        ),
    ],
)

__all__ = ["skill"]
