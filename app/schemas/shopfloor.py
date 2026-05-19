"""Shopfloor schemas."""

from datetime import datetime

from pydantic import BaseModel


class ProductionLineCreate(BaseModel):
    organization_unit_id: int
    code: str
    name: str
    supervisor_worker_id: int | None = None
    status: str = "active"
    description: str | None = None


class ProductionLineUpdate(BaseModel):
    organization_unit_id: int | None = None
    code: str | None = None
    name: str | None = None
    supervisor_worker_id: int | None = None
    status: str | None = None
    description: str | None = None


class ProductionLineResponse(BaseModel):
    id: int
    organization_unit_id: int
    code: str
    name: str
    supervisor_worker_id: int | None = None
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductionLineListResponse(BaseModel):
    production_lines: list[ProductionLineResponse]
    total: int


class ProductionTeamCreate(BaseModel):
    production_line_id: int
    code: str
    name: str
    leader_worker_id: int | None = None
    shift_pattern: str | None = None
    status: str = "active"
    description: str | None = None


class ProductionTeamUpdate(BaseModel):
    production_line_id: int | None = None
    code: str | None = None
    name: str | None = None
    leader_worker_id: int | None = None
    shift_pattern: str | None = None
    status: str | None = None
    description: str | None = None


class ProductionTeamResponse(BaseModel):
    id: int
    production_line_id: int
    code: str
    name: str
    leader_worker_id: int | None = None
    shift_pattern: str | None = None
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductionTeamListResponse(BaseModel):
    production_teams: list[ProductionTeamResponse]
    total: int


class WorkstationCreate(BaseModel):
    production_line_id: int
    code: str
    name: str
    workstation_type: str
    risk_level: str
    status: str = "active"
    description: str | None = None


class WorkstationUpdate(BaseModel):
    production_line_id: int | None = None
    code: str | None = None
    name: str | None = None
    workstation_type: str | None = None
    risk_level: str | None = None
    status: str | None = None
    description: str | None = None


class WorkstationResponse(BaseModel):
    id: int
    production_line_id: int
    code: str
    name: str
    workstation_type: str
    risk_level: str
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkstationListResponse(BaseModel):
    workstations: list[WorkstationResponse]
    total: int


class WorkstationSkillRequirementCreate(BaseModel):
    skill_id: int
    min_proficiency_level: str
    must_be_validated: bool = False
    is_mandatory: bool = True
    status: str = "active"
    description: str | None = None


class WorkstationSkillRequirementUpdate(BaseModel):
    skill_id: int | None = None
    min_proficiency_level: str | None = None
    must_be_validated: bool | None = None
    is_mandatory: bool | None = None
    status: str | None = None
    description: str | None = None


class WorkstationSkillRequirementResponse(BaseModel):
    id: int
    workstation_id: int
    skill_id: int
    min_proficiency_level: str
    must_be_validated: bool
    is_mandatory: bool
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkstationSkillRequirementListResponse(BaseModel):
    requirements: list[WorkstationSkillRequirementResponse]
    total: int


class WorkstationCertificationRequirementCreate(BaseModel):
    certification_id: int
    is_mandatory: bool = True
    grace_days: int = 0
    status: str = "active"
    description: str | None = None


class WorkstationCertificationRequirementUpdate(BaseModel):
    certification_id: int | None = None
    is_mandatory: bool | None = None
    grace_days: int | None = None
    status: str | None = None
    description: str | None = None


class WorkstationCertificationRequirementResponse(BaseModel):
    id: int
    workstation_id: int
    certification_id: int
    is_mandatory: bool
    grace_days: int
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkstationCertificationRequirementListResponse(BaseModel):
    requirements: list[WorkstationCertificationRequirementResponse]
    total: int


class WorkstationTrainingRequirementCreate(BaseModel):
    safety_training_id: int
    is_mandatory: bool = True
    min_score: float | None = None
    status: str = "active"
    description: str | None = None


class WorkstationTrainingRequirementUpdate(BaseModel):
    safety_training_id: int | None = None
    is_mandatory: bool | None = None
    min_score: float | None = None
    status: str | None = None
    description: str | None = None


class WorkstationTrainingRequirementResponse(BaseModel):
    id: int
    workstation_id: int
    safety_training_id: int
    is_mandatory: bool
    min_score: float | None = None
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkstationTrainingRequirementListResponse(BaseModel):
    requirements: list[WorkstationTrainingRequirementResponse]
    total: int


class WorkstationEquipmentRequirementCreate(BaseModel):
    equipment_code: str
    min_authorization_level: str
    is_mandatory: bool = True
    status: str = "active"
    description: str | None = None


class WorkstationEquipmentRequirementUpdate(BaseModel):
    equipment_code: str | None = None
    min_authorization_level: str | None = None
    is_mandatory: bool | None = None
    status: str | None = None
    description: str | None = None


class WorkstationEquipmentRequirementResponse(BaseModel):
    id: int
    workstation_id: int
    equipment_code: str
    min_authorization_level: str
    is_mandatory: bool
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkstationEquipmentRequirementListResponse(BaseModel):
    requirements: list[WorkstationEquipmentRequirementResponse]
    total: int


__all__ = [
    "ProductionLineCreate",
    "ProductionLineListResponse",
    "ProductionLineResponse",
    "ProductionLineUpdate",
    "ProductionTeamCreate",
    "ProductionTeamListResponse",
    "ProductionTeamResponse",
    "ProductionTeamUpdate",
    "WorkstationCreate",
    "WorkstationCertificationRequirementCreate",
    "WorkstationCertificationRequirementListResponse",
    "WorkstationCertificationRequirementResponse",
    "WorkstationCertificationRequirementUpdate",
    "WorkstationEquipmentRequirementCreate",
    "WorkstationEquipmentRequirementListResponse",
    "WorkstationEquipmentRequirementResponse",
    "WorkstationEquipmentRequirementUpdate",
    "WorkstationListResponse",
    "WorkstationResponse",
    "WorkstationSkillRequirementCreate",
    "WorkstationSkillRequirementListResponse",
    "WorkstationSkillRequirementResponse",
    "WorkstationSkillRequirementUpdate",
    "WorkstationTrainingRequirementCreate",
    "WorkstationTrainingRequirementListResponse",
    "WorkstationTrainingRequirementResponse",
    "WorkstationTrainingRequirementUpdate",
    "WorkstationUpdate",
]
