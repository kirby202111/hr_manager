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


__all__ = [
    "CertificationCreate",
    "CertificationListResponse",
    "CertificationResponse",
    "CertificationUpdate",
    "EquipmentAuthorizationCreate",
    "EquipmentAuthorizationListResponse",
    "EquipmentAuthorizationResponse",
    "EquipmentAuthorizationUpdate",
    "SafetyTrainingCreate",
    "SafetyTrainingListResponse",
    "SafetyTrainingResponse",
    "SafetyTrainingUpdate",
    "WorkerCertificationCreate",
    "WorkerCertificationListResponse",
    "WorkerCertificationResponse",
    "WorkerCertificationUpdate",
    "WorkerSafetyTrainingCreate",
    "WorkerSafetyTrainingListResponse",
    "WorkerSafetyTrainingResponse",
    "WorkerSafetyTrainingUpdate",
]
