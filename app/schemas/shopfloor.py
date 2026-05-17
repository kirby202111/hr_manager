"""生产现场域 Schema，覆盖产线、工位、工单与风险信号。"""

from datetime import date, datetime

from pydantic import BaseModel


class ProductionLineCreate(BaseModel):
    """产线创建输入。"""

    organization_unit_id: int
    code: str
    name: str
    supervisor_worker_id: int | None = None
    status: str = "active"
    description: str | None = None


class ProductionLineUpdate(BaseModel):
    """产线部分更新输入。"""

    organization_unit_id: int | None = None
    code: str | None = None
    name: str | None = None
    supervisor_worker_id: int | None = None
    status: str | None = None
    description: str | None = None


class ProductionLineResponse(BaseModel):
    """产线标准响应。"""

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
    """产线列表响应。"""

    production_lines: list[ProductionLineResponse]
    total: int


class ProductionTeamCreate(BaseModel):
    """班组创建输入。"""

    production_line_id: int
    code: str
    name: str
    leader_worker_id: int | None = None
    shift_pattern: str | None = None
    status: str = "active"
    description: str | None = None


class ProductionTeamUpdate(BaseModel):
    """班组部分更新输入。"""

    production_line_id: int | None = None
    code: str | None = None
    name: str | None = None
    leader_worker_id: int | None = None
    shift_pattern: str | None = None
    status: str | None = None
    description: str | None = None


class ProductionTeamResponse(BaseModel):
    """班组标准响应。"""

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
    """班组列表响应。"""

    production_teams: list[ProductionTeamResponse]
    total: int


class WorkstationCreate(BaseModel):
    """工位创建输入。"""

    production_line_id: int
    code: str
    name: str
    workstation_type: str
    risk_level: str
    status: str = "active"
    description: str | None = None


class WorkstationUpdate(BaseModel):
    """工位部分更新输入。"""

    production_line_id: int | None = None
    code: str | None = None
    name: str | None = None
    workstation_type: str | None = None
    risk_level: str | None = None
    status: str | None = None
    description: str | None = None


class WorkstationResponse(BaseModel):
    """工位标准响应。"""

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
    """工位列表响应。"""

    workstations: list[WorkstationResponse]
    total: int


class WorkstationSkillRequirementCreate(BaseModel):
    """工位技能要求创建输入。"""

    workstation_id: int
    skill_id: int
    required_proficiency: str
    mandatory: bool = True


class WorkstationSkillRequirementUpdate(BaseModel):
    """工位技能要求部分更新输入。"""

    workstation_id: int | None = None
    skill_id: int | None = None
    required_proficiency: str | None = None
    mandatory: bool | None = None


class WorkstationSkillRequirementResponse(BaseModel):
    """工位技能要求标准响应。"""

    id: int
    workstation_id: int
    skill_id: int
    required_proficiency: str
    mandatory: bool
    created_at: datetime
    updated_at: datetime


class WorkstationSkillRequirementListResponse(BaseModel):
    """工位技能要求列表响应。"""

    workstation_skill_requirements: list[WorkstationSkillRequirementResponse]
    total: int


class WorkstationCertificationRequirementCreate(BaseModel):
    """工位证书要求创建输入。"""

    workstation_id: int
    certification_id: int
    mandatory: bool = True


class WorkstationCertificationRequirementUpdate(BaseModel):
    """工位证书要求部分更新输入。"""

    workstation_id: int | None = None
    certification_id: int | None = None
    mandatory: bool | None = None


class WorkstationCertificationRequirementResponse(BaseModel):
    """工位证书要求标准响应。"""

    id: int
    workstation_id: int
    certification_id: int
    mandatory: bool
    created_at: datetime
    updated_at: datetime


class WorkstationCertificationRequirementListResponse(BaseModel):
    """工位证书要求列表响应。"""

    workstation_certification_requirements: list[WorkstationCertificationRequirementResponse]
    total: int


class WorkstationEquipmentRequirementCreate(BaseModel):
    """工位设备授权要求创建输入。"""

    workstation_id: int
    equipment_code: str
    required_authorization_level: str
    mandatory: bool = True


class WorkstationEquipmentRequirementUpdate(BaseModel):
    """工位设备授权要求部分更新输入。"""

    workstation_id: int | None = None
    equipment_code: str | None = None
    required_authorization_level: str | None = None
    mandatory: bool | None = None


class WorkstationEquipmentRequirementResponse(BaseModel):
    """工位设备授权要求标准响应。"""

    id: int
    workstation_id: int
    equipment_code: str
    required_authorization_level: str
    mandatory: bool
    created_at: datetime
    updated_at: datetime


class WorkstationEquipmentRequirementListResponse(BaseModel):
    """工位设备授权要求列表响应。"""

    workstation_equipment_requirements: list[WorkstationEquipmentRequirementResponse]
    total: int


class ProductionOrderCreate(BaseModel):
    """生产工单创建输入。"""

    order_number: str
    production_line_id: int | None = None
    product_code: str
    product_name: str
    planned_quantity: int
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    priority: str
    status: str = "planned"
    description: str | None = None


class ProductionOrderUpdate(BaseModel):
    """生产工单部分更新输入。"""

    order_number: str | None = None
    production_line_id: int | None = None
    product_code: str | None = None
    product_name: str | None = None
    planned_quantity: int | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    priority: str | None = None
    status: str | None = None
    description: str | None = None


class ProductionOrderResponse(BaseModel):
    """生产工单标准响应。"""

    id: int
    order_number: str
    production_line_id: int | None = None
    product_code: str
    product_name: str
    planned_quantity: int
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    priority: str
    status: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductionOrderListResponse(BaseModel):
    """生产工单列表响应。"""

    production_orders: list[ProductionOrderResponse]
    total: int


class ProductionOperationCreate(BaseModel):
    """工单工序创建输入。"""

    production_order_id: int
    workstation_id: int
    operation_code: str
    operation_name: str
    sequence_number: int
    planned_hours: float | None = None
    required_headcount: int
    status: str = "planned"


class ProductionOperationUpdate(BaseModel):
    """工单工序部分更新输入。"""

    production_order_id: int | None = None
    workstation_id: int | None = None
    operation_code: str | None = None
    operation_name: str | None = None
    sequence_number: int | None = None
    planned_hours: float | None = None
    required_headcount: int | None = None
    status: str | None = None


class ProductionOperationResponse(BaseModel):
    """工单工序标准响应。"""

    id: int
    production_order_id: int
    workstation_id: int
    operation_code: str
    operation_name: str
    sequence_number: int
    planned_hours: float | None = None
    required_headcount: int
    status: str
    created_at: datetime
    updated_at: datetime


class ProductionOperationListResponse(BaseModel):
    """工单工序列表响应。"""

    production_operations: list[ProductionOperationResponse]
    total: int


class OperationalRiskSignalCreate(BaseModel):
    """风险信号创建输入。"""

    production_order_id: int | None = None
    worker_id: int | None = None
    production_line_id: int | None = None
    workstation_id: int | None = None
    shift_assignment_id: int | None = None
    signal_type: str
    severity: str
    status: str = "open"
    detected_by: str
    evidence: str


class OperationalRiskSignalUpdate(BaseModel):
    """风险信号部分更新输入。"""

    production_order_id: int | None = None
    worker_id: int | None = None
    production_line_id: int | None = None
    workstation_id: int | None = None
    shift_assignment_id: int | None = None
    signal_type: str | None = None
    severity: str | None = None
    status: str | None = None
    detected_by: str | None = None
    evidence: str | None = None


class OperationalRiskSignalResponse(BaseModel):
    """风险信号标准响应。"""

    id: int
    production_order_id: int | None = None
    worker_id: int | None = None
    production_line_id: int | None = None
    workstation_id: int | None = None
    shift_assignment_id: int | None = None
    signal_type: str
    severity: str
    status: str
    detected_by: str
    evidence: str
    created_at: datetime
    updated_at: datetime


class OperationalRiskSignalListResponse(BaseModel):
    """风险信号列表响应。"""

    operational_risk_signals: list[OperationalRiskSignalResponse]
    total: int


class OperationalRiskReviewCreate(BaseModel):
    """风险复核记录创建输入。"""

    risk_signal_id: int
    reviewer_name: str
    conclusion: str
    action_suggestion: str
    review_status: str = "completed"


class OperationalRiskReviewUpdate(BaseModel):
    """风险复核记录部分更新输入。"""

    risk_signal_id: int | None = None
    reviewer_name: str | None = None
    conclusion: str | None = None
    action_suggestion: str | None = None
    review_status: str | None = None


class OperationalRiskReviewResponse(BaseModel):
    """风险复核记录标准响应。"""

    id: int
    risk_signal_id: int
    reviewer_name: str
    conclusion: str
    action_suggestion: str
    review_status: str
    created_at: datetime
    updated_at: datetime


class OperationalRiskReviewListResponse(BaseModel):
    """风险复核记录列表响应。"""

    operational_risk_reviews: list[OperationalRiskReviewResponse]
    total: int


__all__ = [
    "OperationalRiskReviewCreate",
    "OperationalRiskReviewListResponse",
    "OperationalRiskReviewResponse",
    "OperationalRiskReviewUpdate",
    "OperationalRiskSignalCreate",
    "OperationalRiskSignalListResponse",
    "OperationalRiskSignalResponse",
    "OperationalRiskSignalUpdate",
    "ProductionLineCreate",
    "ProductionLineListResponse",
    "ProductionLineResponse",
    "ProductionLineUpdate",
    "ProductionOperationCreate",
    "ProductionOperationListResponse",
    "ProductionOperationResponse",
    "ProductionOperationUpdate",
    "ProductionOrderCreate",
    "ProductionOrderListResponse",
    "ProductionOrderResponse",
    "ProductionOrderUpdate",
    "ProductionTeamCreate",
    "ProductionTeamListResponse",
    "ProductionTeamResponse",
    "ProductionTeamUpdate",
    "WorkstationCertificationRequirementCreate",
    "WorkstationCertificationRequirementListResponse",
    "WorkstationCertificationRequirementResponse",
    "WorkstationCertificationRequirementUpdate",
    "WorkstationCreate",
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
    "WorkstationUpdate",
]
