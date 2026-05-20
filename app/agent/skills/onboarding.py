"""Onboarding-focused agent tools."""

from __future__ import annotations

from datetime import date

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.agent.schemas.onboarding import OnboardingCasePatch
from app.agent.services import onboarding as onboarding_service
from app.schemas.capability import WorkerSkillCreate
from app.schemas.qualification import (
    EquipmentAuthorizationCreate,
    WorkerCertificationCreate,
    WorkerSafetyTrainingCreate,
)
from app.schemas.workforce import (
    WorkerAssignmentCreate,
    WorkerAssignmentUpdate,
    WorkerCreate,
    WorkerUpdate,
)
from app.services.capability import worker_skill as worker_skill_service
from app.services.qualification import (
    eligibility as eligibility_service,
    equipment_authorization as authorization_service,
    worker_certification as certification_service,
    worker_safety_training as training_service,
)
from app.services.workforce import worker as worker_service
from app.services.workforce import worker_assignment as worker_assignment_service


def _create_worker_profile(
    worker_code: str,
    full_name: str,
    employment_type: str,
    status: str = "active",
    organization_unit_id: int | None = None,
    hire_date: str | None = None,
    exit_date: str | None = None,
    base_salary: float | None = None,
    phone_number: str | None = None,
    notes: str | None = None,
):
    return safe_call(
        worker_service.create_worker,
        WorkerCreate(
            worker_code=worker_code,
            full_name=full_name,
            employment_type=employment_type,
            status=status,
            organization_unit_id=organization_unit_id,
            hire_date=hire_date,
            exit_date=exit_date,
            base_salary=base_salary,
            phone_number=phone_number,
            notes=notes,
        ),
    )


def _update_worker_profile(
    worker_id: int,
    confirm: bool = False,
    worker_code: str | None = None,
    full_name: str | None = None,
    employment_type: str | None = None,
    status: str | None = None,
    organization_unit_id: int | None = None,
    hire_date: str | None = None,
    exit_date: str | None = None,
    base_salary: float | None = None,
    phone_number: str | None = None,
    notes: str | None = None,
):
    if not confirm:
        return {"error": "confirmation_required", "message": "Updating an existing worker requires user confirmation."}
    return safe_call(
        worker_service.update_worker,
        worker_id,
        WorkerUpdate(
            worker_code=worker_code,
            full_name=full_name,
            employment_type=employment_type,
            status=status,
            organization_unit_id=organization_unit_id,
            hire_date=hire_date,
            exit_date=exit_date,
            base_salary=base_salary,
            phone_number=phone_number,
            notes=notes,
        ),
    )


def _create_primary_assignment(
    worker_id: int,
    organization_unit_id: int | None,
    production_line_id: int | None,
    role_title: str,
    assignment_type: str,
    start_date: str,
    production_team_id: int | None = None,
    status: str = "active",
    end_date: str | None = None,
    is_primary: bool = True,
    notes: str | None = None,
):
    return safe_call(
        worker_assignment_service.create_worker_assignment,
        WorkerAssignmentCreate(
            worker_id=worker_id,
            organization_unit_id=organization_unit_id,
            production_line_id=production_line_id,
            production_team_id=production_team_id,
            role_title=role_title,
            assignment_type=assignment_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            is_primary=is_primary,
            notes=notes,
        ),
    )


def _update_primary_assignment(
    worker_assignment_id: int,
    confirm: bool = False,
    worker_id: int | None = None,
    organization_unit_id: int | None = None,
    production_line_id: int | None = None,
    production_team_id: int | None = None,
    role_title: str | None = None,
    assignment_type: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    is_primary: bool | None = None,
    notes: str | None = None,
):
    if not confirm:
        return {
            "error": "confirmation_required",
            "message": "Updating an existing assignment requires user confirmation.",
        }
    return safe_call(
        worker_assignment_service.update_worker_assignment,
        worker_assignment_id,
        WorkerAssignmentUpdate(
            worker_id=worker_id,
            organization_unit_id=organization_unit_id,
            production_line_id=production_line_id,
            production_team_id=production_team_id,
            role_title=role_title,
            assignment_type=assignment_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            is_primary=is_primary,
            notes=notes,
        ),
    )


def _record_worker_skill(
    worker_id: int,
    skill_id: int,
    proficiency_level: str,
    years_of_experience: float | None = None,
    validated: bool = False,
    notes: str | None = None,
):
    return safe_call(
        worker_skill_service.create_worker_skill,
        WorkerSkillCreate(
            worker_id=worker_id,
            skill_id=skill_id,
            proficiency_level=proficiency_level,
            years_of_experience=years_of_experience,
            validated=validated,
            notes=notes,
        ),
    )


def _record_worker_certification(
    worker_id: int,
    certification_id: int,
    issued_at: str,
    certification_number: str | None = None,
    expires_at: str | None = None,
    status: str = "valid",
    evidence_uri: str | None = None,
):
    return safe_call(
        certification_service.create_worker_certification,
        WorkerCertificationCreate(
            worker_id=worker_id,
            certification_id=certification_id,
            certification_number=certification_number,
            issued_at=issued_at,
            expires_at=expires_at,
            status=status,
            evidence_uri=evidence_uri,
        ),
    )


def _record_worker_training(
    worker_id: int,
    safety_training_id: int,
    completed_at: str,
    expires_at: str | None = None,
    score: float | None = None,
    status: str = "valid",
):
    return safe_call(
        training_service.create_worker_safety_training,
        WorkerSafetyTrainingCreate(
            worker_id=worker_id,
            safety_training_id=safety_training_id,
            completed_at=completed_at,
            expires_at=expires_at,
            score=score,
            status=status,
        ),
    )


def _record_equipment_authorization(
    worker_id: int,
    equipment_code: str,
    authorization_level: str,
    issued_at: str,
    expires_at: str | None = None,
    status: str = "valid",
    evidence_uri: str | None = None,
):
    return safe_call(
        authorization_service.create_equipment_authorization,
        EquipmentAuthorizationCreate(
            worker_id=worker_id,
            equipment_code=equipment_code,
            authorization_level=authorization_level,
            issued_at=issued_at,
            expires_at=expires_at,
            status=status,
            evidence_uri=evidence_uri,
        ),
    )


def _check_worker_workstation_eligibility(
    worker_id: int,
    workstation_id: int,
    work_date: str | None = None,
    production_operation_id: int | None = None,
    persist_snapshot: bool = True,
):
    effective_work_date = work_date or date.today().isoformat()
    return safe_call(
        eligibility_service.evaluate_worker_eligibility,
        worker_id=worker_id,
        workstation_id=workstation_id,
        work_date=date.fromisoformat(effective_work_date),
        production_operation_id=production_operation_id,
        persist_snapshot=persist_snapshot,
        source_context="agent_onboarding",
    )


def _save_onboarding_case(
    session_id: str,
    user_tag: str,
    worker_id: int | None = None,
    worker_code: str | None = None,
    worker_name: str | None = None,
    employment_type: str | None = None,
    hire_date: str | None = None,
    organization_unit_id: int | None = None,
    production_line_id: int | None = None,
    production_team_id: int | None = None,
    role_title: str | None = None,
    target_workstation_id: int | None = None,
    collected_fields: list[str] | None = None,
    missing_fields: list[str] | None = None,
    pending_actions: list[str] | None = None,
    completed_actions: list[str] | None = None,
    risk_flags: list[str] | None = None,
    latest_eligibility: dict | None = None,
    last_agent_summary: str | None = None,
    is_active: bool | None = None,
):
    return safe_call(
        onboarding_service.upsert_case,
        session_id,
        user_tag,
        OnboardingCasePatch(
            worker_id=worker_id,
            worker_code=worker_code,
            worker_name=worker_name,
            employment_type=employment_type,
            hire_date=hire_date,
            organization_unit_id=organization_unit_id,
            production_line_id=production_line_id,
            production_team_id=production_team_id,
            role_title=role_title,
            target_workstation_id=target_workstation_id,
            collected_fields=collected_fields,
            missing_fields=missing_fields,
            pending_actions=pending_actions,
            completed_actions=completed_actions,
            risk_flags=risk_flags,
            latest_eligibility=latest_eligibility,
            last_agent_summary=last_agent_summary,
            is_active=is_active,
        ),
    )


skill = AgentSkill(
    name="onboarding",
    description="Create, qualify, and review factory-worker onboarding readiness through chat.",
    applicability="Use for new worker onboarding, workstation readiness, qualification gaps, and placement decisions.",
    keywords=("入职", "新员工", "新工人", "办理上岗", "安排到某工位", "补培训后上岗", "onboarding", "new hire"),
    tools=[
        AgentTool(
            name="find_worker_candidates",
            description="Search likely worker matches before creating or updating a worker profile.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_code": {"type": "string"},
                    "full_name": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            },
            fn=lambda worker_code=None, full_name=None, phone_number=None, limit=5: safe_call(
                onboarding_service.find_worker_candidates,
                worker_code,
                full_name,
                phone_number,
                limit,
            ),
        ),
        AgentTool(
            name="create_worker_profile",
            description="Create a new worker profile when no duplicate worker exists.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_code": {"type": "string"},
                    "full_name": {"type": "string"},
                    "employment_type": {"type": "string"},
                    "status": {"type": "string"},
                    "organization_unit_id": {"type": "integer"},
                    "hire_date": {"type": "string"},
                    "exit_date": {"type": "string"},
                    "base_salary": {"type": "number"},
                    "phone_number": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["worker_code", "full_name", "employment_type"],
            },
            fn=_create_worker_profile,
        ),
        AgentTool(
            name="update_worker_profile",
            description="Update an existing worker profile after explicit user confirmation.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "confirm": {"type": "boolean"},
                    "worker_code": {"type": "string"},
                    "full_name": {"type": "string"},
                    "employment_type": {"type": "string"},
                    "status": {"type": "string"},
                    "organization_unit_id": {"type": "integer"},
                    "hire_date": {"type": "string"},
                    "exit_date": {"type": "string"},
                    "base_salary": {"type": "number"},
                    "phone_number": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["worker_id"],
            },
            fn=_update_worker_profile,
        ),
        AgentTool(
            name="create_primary_assignment",
            description="Create a worker's primary organization, line, and team assignment for onboarding.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "organization_unit_id": {"type": "integer"},
                    "production_line_id": {"type": "integer"},
                    "production_team_id": {"type": "integer"},
                    "role_title": {"type": "string"},
                    "assignment_type": {"type": "string"},
                    "status": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "is_primary": {"type": "boolean"},
                    "notes": {"type": "string"},
                },
                "required": ["worker_id", "role_title", "assignment_type", "start_date"],
            },
            fn=_create_primary_assignment,
        ),
        AgentTool(
            name="update_primary_assignment",
            description="Update an existing assignment only after explicit user confirmation.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_assignment_id": {"type": "integer"},
                    "confirm": {"type": "boolean"},
                    "worker_id": {"type": "integer"},
                    "organization_unit_id": {"type": "integer"},
                    "production_line_id": {"type": "integer"},
                    "production_team_id": {"type": "integer"},
                    "role_title": {"type": "string"},
                    "assignment_type": {"type": "string"},
                    "status": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "is_primary": {"type": "boolean"},
                    "notes": {"type": "string"},
                },
                "required": ["worker_assignment_id"],
            },
            fn=_update_primary_assignment,
        ),
        AgentTool(
            name="list_shopfloor_targets",
            description="List organization units, lines, teams, and workstations that match a natural-language target.",
            parameters={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"},
                    "organization_unit_id": {"type": "integer"},
                    "production_line_id": {"type": "integer"},
                    "production_team_id": {"type": "integer"},
                    "workstation_id": {"type": "integer"},
                },
            },
            fn=lambda keyword=None, organization_unit_id=None, production_line_id=None, production_team_id=None, workstation_id=None: (
                safe_call(
                    onboarding_service.list_shopfloor_targets,
                    keyword,
                    organization_unit_id,
                    production_line_id,
                    production_team_id,
                    workstation_id,
                )
            ),
        ),
        AgentTool(
            name="get_workstation_requirements",
            description="Get the skill, certification, training, and equipment requirements for a workstation.",
            parameters={
                "type": "object",
                "properties": {
                    "workstation_id": {"type": "integer"},
                    "production_operation_id": {"type": "integer"},
                },
                "required": ["workstation_id"],
            },
            fn=lambda workstation_id, production_operation_id=None: safe_call(
                onboarding_service.get_workstation_requirements,
                workstation_id,
                production_operation_id,
            ),
        ),
        AgentTool(
            name="get_worker_qualification_summary",
            description=(
                "Summarize a worker's existing skills, certifications, trainings, "
                "and equipment authorizations."
            ),
            parameters={
                "type": "object",
                "properties": {"worker_id": {"type": "integer"}},
                "required": ["worker_id"],
            },
            fn=lambda worker_id: safe_call(onboarding_service.get_worker_qualification_summary, worker_id),
        ),
        AgentTool(
            name="record_worker_skill",
            description="Record a new worker skill needed for workstation eligibility.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "skill_id": {"type": "integer"},
                    "proficiency_level": {"type": "string"},
                    "years_of_experience": {"type": "number"},
                    "validated": {"type": "boolean"},
                    "notes": {"type": "string"},
                },
                "required": ["worker_id", "skill_id", "proficiency_level"],
            },
            fn=_record_worker_skill,
        ),
        AgentTool(
            name="record_worker_certification",
            description="Record a worker certification needed for onboarding readiness.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "certification_id": {"type": "integer"},
                    "certification_number": {"type": "string"},
                    "issued_at": {"type": "string"},
                    "expires_at": {"type": "string"},
                    "status": {"type": "string"},
                    "evidence_uri": {"type": "string"},
                },
                "required": ["worker_id", "certification_id", "issued_at"],
            },
            fn=_record_worker_certification,
        ),
        AgentTool(
            name="record_worker_training",
            description="Record a worker safety training result needed for onboarding readiness.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "safety_training_id": {"type": "integer"},
                    "completed_at": {"type": "string"},
                    "expires_at": {"type": "string"},
                    "score": {"type": "number"},
                    "status": {"type": "string"},
                },
                "required": ["worker_id", "safety_training_id", "completed_at"],
            },
            fn=_record_worker_training,
        ),
        AgentTool(
            name="record_equipment_authorization",
            description="Record a worker equipment authorization needed for onboarding readiness.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "equipment_code": {"type": "string"},
                    "authorization_level": {"type": "string"},
                    "issued_at": {"type": "string"},
                    "expires_at": {"type": "string"},
                    "status": {"type": "string"},
                    "evidence_uri": {"type": "string"},
                },
                "required": ["worker_id", "equipment_code", "authorization_level", "issued_at"],
            },
            fn=_record_equipment_authorization,
        ),
        AgentTool(
            name="check_worker_workstation_eligibility",
            description="Run the final workstation eligibility check for a worker.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "workstation_id": {"type": "integer"},
                    "work_date": {"type": "string"},
                    "production_operation_id": {"type": "integer"},
                    "persist_snapshot": {"type": "boolean"},
                },
                "required": ["worker_id", "workstation_id"],
            },
            fn=_check_worker_workstation_eligibility,
        ),
        AgentTool(
            name="load_onboarding_case",
            description="Load the current onboarding case for this chat session.",
            parameters={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "user_tag": {"type": "string"},
                },
                "required": ["session_id", "user_tag"],
            },
            fn=lambda session_id, user_tag: safe_call(onboarding_service.get_active_case, session_id, user_tag),
        ),
        AgentTool(
            name="save_onboarding_case",
            description="Save the latest onboarding case summary, missing items, and progress for this session.",
            parameters={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "user_tag": {"type": "string"},
                    "worker_id": {"type": "integer"},
                    "worker_code": {"type": "string"},
                    "worker_name": {"type": "string"},
                    "employment_type": {"type": "string"},
                    "hire_date": {"type": "string"},
                    "organization_unit_id": {"type": "integer"},
                    "production_line_id": {"type": "integer"},
                    "production_team_id": {"type": "integer"},
                    "role_title": {"type": "string"},
                    "target_workstation_id": {"type": "integer"},
                    "collected_fields": {"type": "array", "items": {"type": "string"}},
                    "missing_fields": {"type": "array", "items": {"type": "string"}},
                    "pending_actions": {"type": "array", "items": {"type": "string"}},
                    "completed_actions": {"type": "array", "items": {"type": "string"}},
                    "risk_flags": {"type": "array", "items": {"type": "string"}},
                    "latest_eligibility": {"type": "object"},
                    "last_agent_summary": {"type": "string"},
                    "is_active": {"type": "boolean"},
                },
                "required": ["session_id", "user_tag"],
            },
            fn=_save_onboarding_case,
        ),
        AgentTool(
            name="clear_onboarding_case",
            description=(
                "Clear the onboarding case for this chat session when the onboarding task is done "
                "or restarted."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "user_tag": {"type": "string"},
                },
                "required": ["session_id", "user_tag"],
            },
            fn=lambda session_id, user_tag: safe_call(onboarding_service.reset_case, session_id, user_tag),
        ),
    ],
)

__all__ = ["skill"]
