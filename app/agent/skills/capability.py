"""Capability-related agent tools."""

from __future__ import annotations

from pydantic import BaseModel

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.schemas.capability import SkillCreate, SkillUpdate, WorkerSkillCreate, WorkerSkillUpdate
from app.services.capability import skill as skill_service
from app.services.capability import worker_skill as worker_skill_service


class ListSkillsInput(BaseModel):
    category: str | None = None
    status: str | None = None


class GetSkillInput(BaseModel):
    skill_id: int


class UpdateSkillInput(SkillUpdate):
    skill_id: int


class DeleteSkillInput(BaseModel):
    skill_id: int


class ListWorkerSkillsInput(BaseModel):
    worker_id: int | None = None
    skill_id: int | None = None
    proficiency_level: str | None = None
    validated: bool | None = None


class GetWorkerSkillInput(BaseModel):
    worker_skill_id: int


class UpdateWorkerSkillInput(WorkerSkillUpdate):
    worker_skill_id: int


class DeleteWorkerSkillInput(BaseModel):
    worker_skill_id: int


def _create_skill(**kwargs):
    return safe_call(skill_service.create_skill, SkillCreate(**kwargs))


def _update_skill(skill_id: int, **kwargs):
    return safe_call(skill_service.update_skill, skill_id, SkillUpdate(**kwargs))


def _create_worker_skill(**kwargs):
    return safe_call(worker_skill_service.create_worker_skill, WorkerSkillCreate(**kwargs))


def _update_worker_skill(worker_skill_id: int, **kwargs):
    return safe_call(worker_skill_service.update_worker_skill, worker_skill_id, WorkerSkillUpdate(**kwargs))


skill = AgentSkill(
    name="capability",
    description="Manage skill definitions and worker skill profiles.",
    applicability="Use for skill catalogs, worker capability lookups, and skill matrix updates.",
    keywords=("skill", "capability", "proficiency", "validated", "技能", "能力", "熟练度"),
    tools=[
        AgentTool(
            name="list_skills",
            description="List skill definitions with optional category or status filters.",
            parameters=ListSkillsInput.model_json_schema(),
            fn=lambda category=None, status=None: safe_call(skill_service.list_skills, category, status),
        ),
        AgentTool(
            name="get_skill",
            description="Get one skill definition by ID.",
            parameters=GetSkillInput.model_json_schema(),
            fn=lambda skill_id: safe_call(skill_service.get_skill, skill_id),
        ),
        AgentTool(
            name="create_skill",
            description="Create a new skill definition.",
            parameters=SkillCreate.model_json_schema(),
            fn=_create_skill,
        ),
        AgentTool(
            name="update_skill",
            description="Update an existing skill definition.",
            parameters=UpdateSkillInput.model_json_schema(),
            fn=lambda skill_id, **kwargs: _update_skill(skill_id, **kwargs),
        ),
        AgentTool(
            name="delete_skill",
            description="Delete one skill definition by ID.",
            parameters=DeleteSkillInput.model_json_schema(),
            fn=lambda skill_id: safe_call(skill_service.delete_skill, skill_id),
        ),
        AgentTool(
            name="list_worker_skills",
            description="List worker skill records with optional worker, skill, level, or validation filters.",
            parameters=ListWorkerSkillsInput.model_json_schema(),
            fn=lambda worker_id=None, skill_id=None, proficiency_level=None, validated=None: safe_call(
                worker_skill_service.list_worker_skills,
                worker_id,
                skill_id,
                proficiency_level,
                validated,
            ),
        ),
        AgentTool(
            name="get_worker_skill",
            description="Get one worker skill record by ID.",
            parameters=GetWorkerSkillInput.model_json_schema(),
            fn=lambda worker_skill_id: safe_call(worker_skill_service.get_worker_skill, worker_skill_id),
        ),
        AgentTool(
            name="create_worker_skill",
            description="Create a new worker skill record.",
            parameters=WorkerSkillCreate.model_json_schema(),
            fn=_create_worker_skill,
        ),
        AgentTool(
            name="update_worker_skill",
            description="Update an existing worker skill record.",
            parameters=UpdateWorkerSkillInput.model_json_schema(),
            fn=lambda worker_skill_id, **kwargs: _update_worker_skill(worker_skill_id, **kwargs),
        ),
        AgentTool(
            name="delete_worker_skill",
            description="Delete one worker skill record by ID.",
            parameters=DeleteWorkerSkillInput.model_json_schema(),
            fn=lambda worker_skill_id: safe_call(worker_skill_service.delete_worker_skill, worker_skill_id),
        ),
    ],
)

__all__ = ["skill"]
