from datetime import date, datetime

from pydantic import BaseModel


class CertificationCreate(BaseModel):
    name: str
    category: str = "safety"
    required_training_hours: float = 0
    validity_months: int | None = None
    description: str | None = None


class CertificationUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    required_training_hours: float | None = None
    validity_months: int | None = None
    description: str | None = None


class CertificationResponse(CertificationCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class EmployeeCertificationCreate(BaseModel):
    employee_id: int
    certification_id: int
    issued_at: date
    expires_at: date | None = None
    status: str = "valid"
    evidence: str | None = None


class EmployeeCertificationUpdate(BaseModel):
    issued_at: date | None = None
    expires_at: date | None = None
    status: str | None = None
    evidence: str | None = None


class EmployeeCertificationResponse(EmployeeCertificationCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class EquipmentAuthorizationCreate(BaseModel):
    employee_id: int
    equipment_code: str
    authorization_level: str = "operator"
    issued_at: date
    expires_at: date | None = None
    status: str = "valid"


class EquipmentAuthorizationUpdate(BaseModel):
    authorization_level: str | None = None
    issued_at: date | None = None
    expires_at: date | None = None
    status: str | None = None


class EquipmentAuthorizationResponse(EquipmentAuthorizationCreate):
    id: int
    created_at: datetime
    updated_at: datetime
