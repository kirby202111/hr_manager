"""Qualification-related agent tools."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.schemas.qualification import (
    CertificationCreate,
    CertificationUpdate,
    EligibilityCheckRequest,
    EquipmentAuthorizationCreate,
    EquipmentAuthorizationUpdate,
    SafetyTrainingCreate,
    SafetyTrainingUpdate,
    WorkerCertificationCreate,
    WorkerCertificationUpdate,
    WorkerSafetyTrainingCreate,
    WorkerSafetyTrainingUpdate,
)
from app.services.qualification import certification as certification_service
from app.services.qualification import eligibility as eligibility_service
from app.services.qualification import equipment_authorization as equipment_authorization_service
from app.services.qualification import safety_training as safety_training_service
from app.services.qualification import worker_certification as worker_certification_service
from app.services.qualification import worker_safety_training as worker_safety_training_service


class ListCertificationsInput(BaseModel):
    category: str | None = None


class GetCertificationInput(BaseModel):
    certification_id: int


class UpdateCertificationInput(CertificationUpdate):
    certification_id: int


class DeleteCertificationInput(BaseModel):
    certification_id: int


class ListSafetyTrainingsInput(BaseModel):
    category: str | None = None


class GetSafetyTrainingInput(BaseModel):
    safety_training_id: int


class UpdateSafetyTrainingInput(SafetyTrainingUpdate):
    safety_training_id: int


class DeleteSafetyTrainingInput(BaseModel):
    safety_training_id: int


class ListWorkerCertificationsInput(BaseModel):
    worker_id: int | None = None
    certification_id: int | None = None
    status: str | None = None


class GetWorkerCertificationInput(BaseModel):
    worker_certification_id: int


class UpdateWorkerCertificationInput(WorkerCertificationUpdate):
    worker_certification_id: int


class DeleteWorkerCertificationInput(BaseModel):
    worker_certification_id: int


class ListWorkerSafetyTrainingsInput(BaseModel):
    worker_id: int | None = None
    safety_training_id: int | None = None
    status: str | None = None


class GetWorkerSafetyTrainingInput(BaseModel):
    worker_safety_training_id: int


class UpdateWorkerSafetyTrainingInput(WorkerSafetyTrainingUpdate):
    worker_safety_training_id: int


class DeleteWorkerSafetyTrainingInput(BaseModel):
    worker_safety_training_id: int


class ListEquipmentAuthorizationsInput(BaseModel):
    worker_id: int | None = None
    equipment_code: str | None = None
    status: str | None = None


class GetEquipmentAuthorizationInput(BaseModel):
    equipment_authorization_id: int


class UpdateEquipmentAuthorizationInput(EquipmentAuthorizationUpdate):
    equipment_authorization_id: int


class DeleteEquipmentAuthorizationInput(BaseModel):
    equipment_authorization_id: int


class ListEligibilitySnapshotsInput(BaseModel):
    worker_id: int
    workstation_id: int | None = None
    shift_plan_id: int | None = None
    status: str | None = None
    work_date_from: date | None = None
    work_date_to: date | None = None


class GetEligibilitySnapshotInput(BaseModel):
    worker_id: int
    snapshot_id: int


def _create_certification(**kwargs):
    return safe_call(certification_service.create_certification, CertificationCreate(**kwargs))


def _update_certification(certification_id: int, **kwargs):
    return safe_call(certification_service.update_certification, certification_id, CertificationUpdate(**kwargs))


def _create_safety_training(**kwargs):
    return safe_call(safety_training_service.create_safety_training, SafetyTrainingCreate(**kwargs))


def _update_safety_training(safety_training_id: int, **kwargs):
    return safe_call(safety_training_service.update_safety_training, safety_training_id, SafetyTrainingUpdate(**kwargs))


def _create_worker_certification(**kwargs):
    return safe_call(worker_certification_service.create_worker_certification, WorkerCertificationCreate(**kwargs))


def _update_worker_certification(worker_certification_id: int, **kwargs):
    return safe_call(
        worker_certification_service.update_worker_certification,
        worker_certification_id,
        WorkerCertificationUpdate(**kwargs),
    )


def _create_worker_safety_training(**kwargs):
    return safe_call(
        worker_safety_training_service.create_worker_safety_training,
        WorkerSafetyTrainingCreate(**kwargs),
    )


def _update_worker_safety_training(worker_safety_training_id: int, **kwargs):
    return safe_call(
        worker_safety_training_service.update_worker_safety_training,
        worker_safety_training_id,
        WorkerSafetyTrainingUpdate(**kwargs),
    )


def _create_equipment_authorization(**kwargs):
    return safe_call(
        equipment_authorization_service.create_equipment_authorization,
        EquipmentAuthorizationCreate(**kwargs),
    )


def _update_equipment_authorization(equipment_authorization_id: int, **kwargs):
    return safe_call(
        equipment_authorization_service.update_equipment_authorization,
        equipment_authorization_id,
        EquipmentAuthorizationUpdate(**kwargs),
    )


def _check_worker_eligibility(**kwargs):
    payload = EligibilityCheckRequest(**kwargs)
    return safe_call(
        eligibility_service.evaluate_worker_eligibility,
        worker_id=payload.worker_id,
        workstation_id=payload.workstation_id,
        work_date=payload.work_date,
        production_operation_id=payload.production_operation_id,
        persist_snapshot=payload.persist_snapshot,
        source_context="agent_check",
    )


def _list_worker_eligibility_snapshots(
    worker_id: int,
    workstation_id: int | None = None,
    shift_plan_id: int | None = None,
    status: str | None = None,
    work_date_from: date | None = None,
    work_date_to: date | None = None,
):
    return safe_call(
        eligibility_service.list_worker_eligibility_snapshots,
        worker_id,
        workstation_id,
        shift_plan_id,
        status,
        work_date_from,
        work_date_to,
    )


skill = AgentSkill(
    name="qualification",
    description="Manage qualifications and evaluate worker eligibility.",
    applicability="Use for certifications, trainings, authorizations, and go/no-go eligibility checks.",
    keywords=(
        "qualification",
        "certification",
        "training",
        "authorization",
        "eligibility",
        "资质",
        "证书",
        "培训",
        "授权",
        "资格",
    ),
    tools=[
        AgentTool(
            name="list_certifications",
            description="List certification definitions with an optional category filter.",
            parameters=ListCertificationsInput.model_json_schema(),
            fn=lambda category=None: safe_call(certification_service.list_certifications, category),
        ),
        AgentTool(
            name="get_certification",
            description="Get one certification definition by ID.",
            parameters=GetCertificationInput.model_json_schema(),
            fn=lambda certification_id: safe_call(certification_service.get_certification, certification_id),
        ),
        AgentTool(
            name="create_certification",
            description="Create a new certification definition.",
            parameters=CertificationCreate.model_json_schema(),
            fn=_create_certification,
        ),
        AgentTool(
            name="update_certification",
            description="Update an existing certification definition.",
            parameters=UpdateCertificationInput.model_json_schema(),
            fn=lambda certification_id, **kwargs: _update_certification(certification_id, **kwargs),
        ),
        AgentTool(
            name="delete_certification",
            description="Delete one certification definition by ID.",
            parameters=DeleteCertificationInput.model_json_schema(),
            fn=lambda certification_id: safe_call(certification_service.delete_certification, certification_id),
        ),
        AgentTool(
            name="list_safety_trainings",
            description="List safety training definitions with an optional category filter.",
            parameters=ListSafetyTrainingsInput.model_json_schema(),
            fn=lambda category=None: safe_call(safety_training_service.list_safety_trainings, category),
        ),
        AgentTool(
            name="get_safety_training",
            description="Get one safety training definition by ID.",
            parameters=GetSafetyTrainingInput.model_json_schema(),
            fn=lambda safety_training_id: safe_call(safety_training_service.get_safety_training, safety_training_id),
        ),
        AgentTool(
            name="create_safety_training",
            description="Create a new safety training definition.",
            parameters=SafetyTrainingCreate.model_json_schema(),
            fn=_create_safety_training,
        ),
        AgentTool(
            name="update_safety_training",
            description="Update an existing safety training definition.",
            parameters=UpdateSafetyTrainingInput.model_json_schema(),
            fn=lambda safety_training_id, **kwargs: _update_safety_training(safety_training_id, **kwargs),
        ),
        AgentTool(
            name="delete_safety_training",
            description="Delete one safety training definition by ID.",
            parameters=DeleteSafetyTrainingInput.model_json_schema(),
            fn=lambda safety_training_id: safe_call(
                safety_training_service.delete_safety_training,
                safety_training_id,
            ),
        ),
        AgentTool(
            name="list_worker_certifications",
            description="List worker certification records with optional worker, certification, or status filters.",
            parameters=ListWorkerCertificationsInput.model_json_schema(),
            fn=lambda worker_id=None, certification_id=None, status=None: safe_call(
                worker_certification_service.list_worker_certifications,
                worker_id,
                certification_id,
                status,
            ),
        ),
        AgentTool(
            name="get_worker_certification",
            description="Get one worker certification record by ID.",
            parameters=GetWorkerCertificationInput.model_json_schema(),
            fn=lambda worker_certification_id: safe_call(
                worker_certification_service.get_worker_certification,
                worker_certification_id,
            ),
        ),
        AgentTool(
            name="create_worker_certification",
            description="Create a new worker certification record.",
            parameters=WorkerCertificationCreate.model_json_schema(),
            fn=_create_worker_certification,
        ),
        AgentTool(
            name="update_worker_certification",
            description="Update an existing worker certification record.",
            parameters=UpdateWorkerCertificationInput.model_json_schema(),
            fn=lambda worker_certification_id, **kwargs: _update_worker_certification(
                worker_certification_id,
                **kwargs,
            ),
        ),
        AgentTool(
            name="delete_worker_certification",
            description="Delete one worker certification record by ID.",
            parameters=DeleteWorkerCertificationInput.model_json_schema(),
            fn=lambda worker_certification_id: safe_call(
                worker_certification_service.delete_worker_certification,
                worker_certification_id,
            ),
        ),
        AgentTool(
            name="list_worker_safety_trainings",
            description="List worker safety training records with optional worker, training, or status filters.",
            parameters=ListWorkerSafetyTrainingsInput.model_json_schema(),
            fn=lambda worker_id=None, safety_training_id=None, status=None: safe_call(
                worker_safety_training_service.list_worker_safety_trainings,
                worker_id,
                safety_training_id,
                status,
            ),
        ),
        AgentTool(
            name="get_worker_safety_training",
            description="Get one worker safety training record by ID.",
            parameters=GetWorkerSafetyTrainingInput.model_json_schema(),
            fn=lambda worker_safety_training_id: safe_call(
                worker_safety_training_service.get_worker_safety_training,
                worker_safety_training_id,
            ),
        ),
        AgentTool(
            name="create_worker_safety_training",
            description="Create a new worker safety training record.",
            parameters=WorkerSafetyTrainingCreate.model_json_schema(),
            fn=_create_worker_safety_training,
        ),
        AgentTool(
            name="update_worker_safety_training",
            description="Update an existing worker safety training record.",
            parameters=UpdateWorkerSafetyTrainingInput.model_json_schema(),
            fn=lambda worker_safety_training_id, **kwargs: _update_worker_safety_training(
                worker_safety_training_id,
                **kwargs,
            ),
        ),
        AgentTool(
            name="delete_worker_safety_training",
            description="Delete one worker safety training record by ID.",
            parameters=DeleteWorkerSafetyTrainingInput.model_json_schema(),
            fn=lambda worker_safety_training_id: safe_call(
                worker_safety_training_service.delete_worker_safety_training,
                worker_safety_training_id,
            ),
        ),
        AgentTool(
            name="list_equipment_authorizations",
            description="List equipment authorizations with optional worker, equipment code, or status filters.",
            parameters=ListEquipmentAuthorizationsInput.model_json_schema(),
            fn=lambda worker_id=None, equipment_code=None, status=None: safe_call(
                equipment_authorization_service.list_equipment_authorizations,
                worker_id,
                equipment_code,
                status,
            ),
        ),
        AgentTool(
            name="get_equipment_authorization",
            description="Get one equipment authorization record by ID.",
            parameters=GetEquipmentAuthorizationInput.model_json_schema(),
            fn=lambda equipment_authorization_id: safe_call(
                equipment_authorization_service.get_equipment_authorization,
                equipment_authorization_id,
            ),
        ),
        AgentTool(
            name="create_equipment_authorization",
            description="Create a new equipment authorization record.",
            parameters=EquipmentAuthorizationCreate.model_json_schema(),
            fn=_create_equipment_authorization,
        ),
        AgentTool(
            name="update_equipment_authorization",
            description="Update an existing equipment authorization record.",
            parameters=UpdateEquipmentAuthorizationInput.model_json_schema(),
            fn=lambda equipment_authorization_id, **kwargs: _update_equipment_authorization(
                equipment_authorization_id,
                **kwargs,
            ),
        ),
        AgentTool(
            name="delete_equipment_authorization",
            description="Delete one equipment authorization record by ID.",
            parameters=DeleteEquipmentAuthorizationInput.model_json_schema(),
            fn=lambda equipment_authorization_id: safe_call(
                equipment_authorization_service.delete_equipment_authorization,
                equipment_authorization_id,
            ),
        ),
        AgentTool(
            name="check_worker_eligibility",
            description=(
                "Evaluate whether a worker is eligible for a workstation "
                "or production operation on a work date."
            ),
            parameters=EligibilityCheckRequest.model_json_schema(),
            fn=_check_worker_eligibility,
        ),
        AgentTool(
            name="list_worker_eligibility_snapshots",
            description="List saved eligibility snapshots for one worker.",
            parameters=ListEligibilitySnapshotsInput.model_json_schema(),
            fn=_list_worker_eligibility_snapshots,
        ),
        AgentTool(
            name="get_worker_eligibility_snapshot",
            description="Get one eligibility snapshot for one worker by snapshot ID.",
            parameters=GetEligibilitySnapshotInput.model_json_schema(),
            fn=lambda worker_id, snapshot_id: safe_call(
                eligibility_service.get_worker_eligibility_snapshot,
                worker_id,
                snapshot_id,
            ),
        ),
    ],
)

__all__ = ["skill"]
