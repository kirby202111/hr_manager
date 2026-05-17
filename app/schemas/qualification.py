"""资质域 Schema，覆盖证书、安全培训与设备授权。"""

from datetime import date, datetime

from pydantic import BaseModel


class CertificationCreate(BaseModel):
    """证书目录创建输入。"""

    name: str
    code: str
    category: str
    validity_months: int | None = None
    issuing_authority: str | None = None
    description: str | None = None


class CertificationUpdate(BaseModel):
    """证书目录部分更新输入。"""

    name: str | None = None
    code: str | None = None
    category: str | None = None
    validity_months: int | None = None
    issuing_authority: str | None = None
    description: str | None = None


class CertificationResponse(BaseModel):
    """证书目录标准响应。"""

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
    """证书目录列表响应。"""

    certifications: list[CertificationResponse]
    total: int


class WorkerCertificationCreate(BaseModel):
    """人员持证记录创建输入。"""

    worker_id: int
    certification_id: int
    certification_number: str | None = None
    issued_at: date
    expires_at: date | None = None
    status: str = "valid"
    evidence_uri: str | None = None


class WorkerCertificationUpdate(BaseModel):
    """人员持证记录部分更新输入。"""

    worker_id: int | None = None
    certification_id: int | None = None
    certification_number: str | None = None
    issued_at: date | None = None
    expires_at: date | None = None
    status: str | None = None
    evidence_uri: str | None = None


class WorkerCertificationResponse(BaseModel):
    """人员持证记录标准响应。"""

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
    """人员持证记录列表响应。"""

    worker_certifications: list[WorkerCertificationResponse]
    total: int


class SafetyTrainingCreate(BaseModel):
    """安全培训目录创建输入。"""

    title: str
    code: str
    category: str
    skill_id: int | None = None
    required_certification_id: int | None = None
    validity_months: int | None = None
    required_hours: float | None = None
    description: str | None = None


class SafetyTrainingUpdate(BaseModel):
    """安全培训目录部分更新输入。"""

    title: str | None = None
    code: str | None = None
    category: str | None = None
    skill_id: int | None = None
    required_certification_id: int | None = None
    validity_months: int | None = None
    required_hours: float | None = None
    description: str | None = None


class SafetyTrainingResponse(BaseModel):
    """安全培训目录标准响应。"""

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
    """安全培训目录列表响应。"""

    safety_trainings: list[SafetyTrainingResponse]
    total: int


class WorkerSafetyTrainingCreate(BaseModel):
    """人员安全培训完成记录创建输入。"""

    worker_id: int
    safety_training_id: int
    completed_at: date
    expires_at: date | None = None
    score: float | None = None
    status: str = "valid"


class WorkerSafetyTrainingUpdate(BaseModel):
    """人员安全培训完成记录部分更新输入。"""

    worker_id: int | None = None
    safety_training_id: int | None = None
    completed_at: date | None = None
    expires_at: date | None = None
    score: float | None = None
    status: str | None = None


class WorkerSafetyTrainingResponse(BaseModel):
    """人员安全培训完成记录标准响应。"""

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
    """人员安全培训完成记录列表响应。"""

    worker_safety_trainings: list[WorkerSafetyTrainingResponse]
    total: int


class EquipmentAuthorizationCreate(BaseModel):
    """设备操作授权记录创建输入。"""

    worker_id: int
    equipment_code: str
    authorization_level: str
    issued_at: date
    expires_at: date | None = None
    status: str = "valid"
    evidence_uri: str | None = None


class EquipmentAuthorizationUpdate(BaseModel):
    """设备操作授权记录部分更新输入。"""

    worker_id: int | None = None
    equipment_code: str | None = None
    authorization_level: str | None = None
    issued_at: date | None = None
    expires_at: date | None = None
    status: str | None = None
    evidence_uri: str | None = None


class EquipmentAuthorizationResponse(BaseModel):
    """设备操作授权记录标准响应。"""

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
    """设备操作授权记录列表响应。"""

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
