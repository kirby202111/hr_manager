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
    "WorkstationListResponse",
    "WorkstationResponse",
    "WorkstationUpdate",
]
