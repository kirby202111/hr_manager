"""Qualification schemas."""

from datetime import date, datetime

from pydantic import BaseModel


class CertificationCreate(BaseModel):
    name: str
    code: str
    category: str
    validity_months: int | None = None
    issuing_authority: str | None = None
    description: str | None = None


class CertificationUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    category: str | None = None
    validity_months: int | None = None
    issuing_authority: str | None = None
    description: str | None = None


class CertificationResponse(BaseModel):
    id: int
    name: str
    code: str
    category: str
    validity_months: int | None = None
    issuing_authority: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class CertificationListResponse(BaseModel):
    certifications: list[CertificationResponse]
    total: int


class WorkerCertificationCreate(BaseModel):
    worker_id: int
    certification_id: int
    certification_number: str | None = None
    issued_at: date
    expires_at: date | None = None
    status: str = "valid"
    evidence_uri: str | None = None


class WorkerCertificationUpdate(BaseModel):
    worker_id: int | None = None
    certification_id: int | None = None
    certification_number: str | None = None
    issued_at: date | None = None
    expires_at: date | None = None
    status: str | None = None
    evidence_uri: str | None = None


class WorkerCertificationResponse(BaseModel):
    id: int
    worker_id: int
    certification_id: int
    certification_number: str | None = None
    issued_at: date
    expires_at: date | None = None
    status: str
    evidence_uri: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkerCertificationListResponse(BaseModel):
    worker_certifications: list[WorkerCertificationResponse]
    total: int


class SafetyTrainingCreate(BaseModel):
    title: str
    code: str
    category: str
    skill_id: int | None = None
    required_certification_id: int | None = None
    validity_months: int | None = None
    required_hours: float | None = None
    description: str | None = None


class SafetyTrainingUpdate(BaseModel):
    title: str | None = None
    code: str | None = None
    category: str | None = None
    skill_id: int | None = None
    required_certification_id: int | None = None
    validity_months: int | None = None
    required_hours: float | None = None
    description: str | None = None


class SafetyTrainingResponse(BaseModel):
    id: int
    title: str
    code: str
    category: str
    skill_id: int | None = None
    required_certification_id: int | None = None
    validity_months: int | None = None
    required_hours: float | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class SafetyTrainingListResponse(BaseModel):
    safety_trainings: list[SafetyTrainingResponse]
    total: int


class WorkerSafetyTrainingCreate(BaseModel):
    worker_id: int
    safety_training_id: int
    completed_at: date
    expires_at: date | None = None
    score: float | None = None
    status: str = "valid"


class WorkerSafetyTrainingUpdate(BaseModel):
    worker_id: int | None = None
    safety_training_id: int | None = None
    completed_at: date | None = None
    expires_at: date | None = None
    score: float | None = None
    status: str | None = None


class WorkerSafetyTrainingResponse(BaseModel):
    id: int
    worker_id: int
    safety_training_id: int
    completed_at: date
    expires_at: date | None = None
    score: float | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class WorkerSafetyTrainingListResponse(BaseModel):
    worker_safety_trainings: list[WorkerSafetyTrainingResponse]
    total: int


class EquipmentAuthorizationCreate(BaseModel):
    worker_id: int
    equipment_code: str
    authorization_level: str
    issued_at: date
    expires_at: date | None = None
    status: str = "valid"
    evidence_uri: str | None = None


class EquipmentAuthorizationUpdate(BaseModel):
    worker_id: int | None = None
    equipment_code: str | None = None
    authorization_level: str | None = None
    issued_at: date | None = None
    expires_at: date | None = None
    status: str | None = None
    evidence_uri: str | None = None


class EquipmentAuthorizationResponse(BaseModel):
    id: int
    worker_id: int
    equipment_code: str
    authorization_level: str
    issued_at: date
    expires_at: date | None = None
    status: str
    evidence_uri: str | None = None
    created_at: datetime
    updated_at: datetime


class EquipmentAuthorizationListResponse(BaseModel):
    equipment_authorizations: list[EquipmentAuthorizationResponse]
    total: int


class EligibilityCheckRequest(BaseModel):
    worker_id: int
    workstation_id: int
    work_date: date
    production_operation_id: int | None = None
    persist_snapshot: bool = True


class EligibilityDetailResponse(BaseModel):
    dimension: str
    requirement_type: str
    reference_id: int | None = None
    reference_code: str | None = None
    reference_name: str | None = None
    status: str
    reason_code: str
    message: str
    actual_value: str | None = None
    expected_value: str | None = None
    severity: str


class WorkerEligibilityEvaluationResponse(BaseModel):
    status: str
    summary_reason: str
    snapshot_id: int | None = None
    worker_id: int
    workstation_id: int
    production_operation_id: int | None = None
    shift_plan_id: int | None = None
    shift_assignment_id: int | None = None
    work_date: date
    details: list[EligibilityDetailResponse]
    checked_at: datetime


class WorkerEligibilitySnapshotResponse(BaseModel):
    id: int
    worker_id: int
    workstation_id: int
    production_operation_id: int | None = None
    shift_plan_id: int | None = None
    shift_assignment_id: int | None = None
    work_date: date
    status: str
    summary_reason: str
    detail_json: list[dict]
    checked_at: datetime
    checked_by: str
    rule_version: str
    source_context: str
    created_at: datetime
    updated_at: datetime


class WorkerEligibilitySnapshotListResponse(BaseModel):
    snapshots: list[WorkerEligibilitySnapshotResponse]
    total: int


__all__ = [
    "CertificationCreate",
    "CertificationListResponse",
    "CertificationResponse",
    "CertificationUpdate",
    "EquipmentAuthorizationCreate",
    "EquipmentAuthorizationListResponse",
    "EquipmentAuthorizationResponse",
    "EquipmentAuthorizationUpdate",
    "EligibilityCheckRequest",
    "EligibilityDetailResponse",
    "SafetyTrainingCreate",
    "SafetyTrainingListResponse",
    "SafetyTrainingResponse",
    "SafetyTrainingUpdate",
    "WorkerEligibilityEvaluationResponse",
    "WorkerEligibilitySnapshotListResponse",
    "WorkerEligibilitySnapshotResponse",
    "WorkerCertificationCreate",
    "WorkerCertificationListResponse",
    "WorkerCertificationResponse",
    "WorkerCertificationUpdate",
    "WorkerSafetyTrainingCreate",
    "WorkerSafetyTrainingListResponse",
    "WorkerSafetyTrainingResponse",
    "WorkerSafetyTrainingUpdate",
]
