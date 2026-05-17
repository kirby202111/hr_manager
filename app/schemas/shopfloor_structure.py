from datetime import datetime

from pydantic import BaseModel


class ProductionLineCreate(BaseModel):
    name: str
    department_id: int
    supervisor_employee_id: int | None = None
    status: str = "active"
    description: str | None = None


class ProductionLineUpdate(BaseModel):
    name: str | None = None
    department_id: int | None = None
    supervisor_employee_id: int | None = None
    status: str | None = None
    description: str | None = None


class ProductionLineResponse(ProductionLineCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class ProductionTeamCreate(BaseModel):
    name: str
    line_id: int
    leader_employee_id: int | None = None
    shift_type: str = "day"
    status: str = "active"


class ProductionTeamUpdate(BaseModel):
    name: str | None = None
    line_id: int | None = None
    leader_employee_id: int | None = None
    shift_type: str | None = None
    status: str | None = None


class ProductionTeamResponse(ProductionTeamCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class WorkstationCreate(BaseModel):
    line_id: int
    code: str
    name: str
    risk_level: str = "low"
    status: str = "active"


class WorkstationUpdate(BaseModel):
    line_id: int | None = None
    code: str | None = None
    name: str | None = None
    risk_level: str | None = None
    status: str | None = None


class WorkstationResponse(WorkstationCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class WorkstationRequiredSkillCreate(BaseModel):
    skill_id: int
    required_proficiency: str = "intermediate"


class WorkstationRequiredSkillResponse(WorkstationRequiredSkillCreate):
    id: int
    workstation_id: int
    created_at: datetime


class WorkstationRequiredCertificationCreate(BaseModel):
    certification_id: int
    required: bool = True


class WorkstationRequiredCertificationResponse(WorkstationRequiredCertificationCreate):
    id: int
    workstation_id: int
    created_at: datetime


class WorkstationEquipmentRequirementCreate(BaseModel):
    equipment_code: str
    required_authorization_level: str = "operator"


class WorkstationEquipmentRequirementResponse(WorkstationEquipmentRequirementCreate):
    id: int
    workstation_id: int
    created_at: datetime
