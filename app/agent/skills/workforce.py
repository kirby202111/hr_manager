"""Workforce-related agent tools."""

from __future__ import annotations

from pydantic import BaseModel

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.schemas.workforce import (
    WorkerAssignmentCreate,
    WorkerAssignmentUpdate,
    WorkerCreate,
    WorkerUpdate,
)
from app.services.workforce import worker as worker_service
from app.services.workforce import worker_assignment as worker_assignment_service


class ListWorkersInput(BaseModel):
    organization_unit_id: int | None = None
    employment_type: str | None = None
    status: str | None = None


class GetWorkerInput(BaseModel):
    worker_id: int


class UpdateWorkerInput(WorkerUpdate):
    worker_id: int


class DeleteWorkerInput(BaseModel):
    worker_id: int


class ListWorkerAssignmentsInput(BaseModel):
    worker_id: int | None = None
    organization_unit_id: int | None = None
    production_line_id: int | None = None
    production_team_id: int | None = None
    status: str | None = None


class GetWorkerAssignmentInput(BaseModel):
    worker_assignment_id: int


class UpdateWorkerAssignmentInput(WorkerAssignmentUpdate):
    worker_assignment_id: int


class DeleteWorkerAssignmentInput(BaseModel):
    worker_assignment_id: int


def _create_worker(**kwargs):
    return safe_call(worker_service.create_worker, WorkerCreate(**kwargs))


def _update_worker(worker_id: int, **kwargs):
    return safe_call(worker_service.update_worker, worker_id, WorkerUpdate(**kwargs))


def _create_worker_assignment(**kwargs):
    return safe_call(worker_assignment_service.create_worker_assignment, WorkerAssignmentCreate(**kwargs))


def _update_worker_assignment(worker_assignment_id: int, **kwargs):
    return safe_call(
        worker_assignment_service.update_worker_assignment,
        worker_assignment_id,
        WorkerAssignmentUpdate(**kwargs),
    )


def _list_worker_assignments(
    worker_id: int | None = None,
    organization_unit_id: int | None = None,
    production_line_id: int | None = None,
    production_team_id: int | None = None,
    status: str | None = None,
):
    return safe_call(
        worker_assignment_service.list_worker_assignments,
        worker_id,
        organization_unit_id,
        production_line_id,
        production_team_id,
        status,
    )


skill = AgentSkill(
    name="workforce",
    description="Manage workers and their assignments.",
    applicability="Use for employee master data, current assignments, and staffing ownership lookups.",
    keywords=("worker", "employee", "staff", "assignment", "人员", "员工", "任职", "归属", "班组"),
    tools=[
        AgentTool(
            name="list_workers",
            description="List workers with optional organization, employment, or status filters.",
            parameters=ListWorkersInput.model_json_schema(),
            fn=lambda organization_unit_id=None, employment_type=None, status=None: safe_call(
                worker_service.list_workers,
                organization_unit_id,
                employment_type,
                status,
            ),
        ),
        AgentTool(
            name="get_worker",
            description="Get one worker by ID.",
            parameters=GetWorkerInput.model_json_schema(),
            fn=lambda worker_id: safe_call(worker_service.get_worker, worker_id),
        ),
        AgentTool(
            name="create_worker",
            description="Create a new worker record.",
            parameters=WorkerCreate.model_json_schema(),
            fn=_create_worker,
        ),
        AgentTool(
            name="update_worker",
            description="Update an existing worker record.",
            parameters=UpdateWorkerInput.model_json_schema(),
            fn=lambda worker_id, **kwargs: _update_worker(worker_id, **kwargs),
        ),
        AgentTool(
            name="delete_worker",
            description="Delete one worker by ID.",
            parameters=DeleteWorkerInput.model_json_schema(),
            fn=lambda worker_id: safe_call(worker_service.delete_worker, worker_id),
        ),
        AgentTool(
            name="list_worker_assignments",
            description="List worker assignments with optional worker, line, team, or status filters.",
            parameters=ListWorkerAssignmentsInput.model_json_schema(),
            fn=_list_worker_assignments,
        ),
        AgentTool(
            name="get_worker_assignment",
            description="Get one worker assignment by ID.",
            parameters=GetWorkerAssignmentInput.model_json_schema(),
            fn=lambda worker_assignment_id: safe_call(
                worker_assignment_service.get_worker_assignment,
                worker_assignment_id,
            ),
        ),
        AgentTool(
            name="create_worker_assignment",
            description="Create a new worker assignment record.",
            parameters=WorkerAssignmentCreate.model_json_schema(),
            fn=_create_worker_assignment,
        ),
        AgentTool(
            name="update_worker_assignment",
            description="Update an existing worker assignment record.",
            parameters=UpdateWorkerAssignmentInput.model_json_schema(),
            fn=lambda worker_assignment_id, **kwargs: _update_worker_assignment(
                worker_assignment_id,
                **kwargs,
            ),
        ),
        AgentTool(
            name="delete_worker_assignment",
            description="Delete one worker assignment by ID.",
            parameters=DeleteWorkerAssignmentInput.model_json_schema(),
            fn=lambda worker_assignment_id: safe_call(
                worker_assignment_service.delete_worker_assignment,
                worker_assignment_id,
            ),
        ),
    ],
)

__all__ = ["skill"]
