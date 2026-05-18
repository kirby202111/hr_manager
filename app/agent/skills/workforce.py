"""Workforce-related agent tools."""

from __future__ import annotations

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.services.workforce import worker as worker_service
from app.services.workforce import worker_assignment as assignment_service


def _list_worker_assignments(
    worker_id=None,
    organization_unit_id=None,
    production_line_id=None,
    production_team_id=None,
    status=None,
):
    return safe_call(
        assignment_service.list_worker_assignments,
        worker_id,
        organization_unit_id,
        production_line_id,
        production_team_id,
        status,
    )


skill = AgentSkill(
    name="workforce",
    description="Query workforce master data and current worker assignments.",
    applicability="Use for employee lookup, worker status, organization placement, and assignment history.",
    keywords=("worker", "employee", "staff", "assignment", "人员", "员工", "班组", "分配"),
    tools=[
        AgentTool(
            name="list_workers",
            description="List workers with optional organization, employment type, and status filters.",
            parameters={
                "type": "object",
                "properties": {
                    "organization_unit_id": {"type": "integer"},
                    "employment_type": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
            fn=lambda organization_unit_id=None, employment_type=None, status=None: safe_call(
                worker_service.list_workers,
                organization_unit_id,
                employment_type,
                status,
            ),
        ),
        AgentTool(
            name="get_worker",
            description="Get one worker by id.",
            parameters={
                "type": "object",
                "properties": {"worker_id": {"type": "integer"}},
                "required": ["worker_id"],
            },
            fn=lambda worker_id: safe_call(worker_service.get_worker, worker_id),
        ),
        AgentTool(
            name="list_worker_assignments",
            description="List worker assignment records with optional filters.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "organization_unit_id": {"type": "integer"},
                    "production_line_id": {"type": "integer"},
                    "production_team_id": {"type": "integer"},
                    "status": {"type": "string"},
                },
            },
            fn=_list_worker_assignments,
        ),
    ],
)

__all__ = ["skill"]
