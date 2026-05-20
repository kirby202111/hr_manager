"""Operations and staffing agent tools."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.schemas.production import (
    ProductionOperationCreate,
    ProductionOperationUpdate,
    ProductionOrderCreate,
    ProductionOrderUpdate,
)
from app.schemas.shopfloor import (
    ProductionLineCreate,
    ProductionLineUpdate,
    WorkstationCreate,
    WorkstationUpdate,
)
from app.schemas.staffing import (
    ShiftAssignmentCreate,
    ShiftAssignmentUpdate,
    ShiftPlanCreate,
    ShiftPlanUpdate,
    ShiftTemplateCreate,
    ShiftTemplateUpdate,
)
from app.services.production import production_operation as production_operation_service
from app.services.production import production_order as production_order_service
from app.services.shopfloor import production_line as production_line_service
from app.services.shopfloor import workstation as workstation_service
from app.services.staffing import shift_assignment as shift_assignment_service
from app.services.staffing import shift_plan as shift_plan_service
from app.services.staffing import shift_template as shift_template_service


class ListProductionLinesInput(BaseModel):
    organization_unit_id: int | None = None
    code: str | None = None
    status: str | None = None


class GetProductionLineInput(BaseModel):
    production_line_id: int


class UpdateProductionLineInput(ProductionLineUpdate):
    production_line_id: int


class DeleteProductionLineInput(BaseModel):
    production_line_id: int


class ListWorkstationsInput(BaseModel):
    production_line_id: int | None = None
    code: str | None = None
    status: str | None = None


class GetWorkstationInput(BaseModel):
    workstation_id: int


class UpdateWorkstationInput(WorkstationUpdate):
    workstation_id: int


class DeleteWorkstationInput(BaseModel):
    workstation_id: int


class ListProductionOrdersInput(BaseModel):
    production_line_id: int | None = None
    order_number: str | None = None
    status: str | None = None


class GetProductionOrderInput(BaseModel):
    production_order_id: int


class UpdateProductionOrderInput(ProductionOrderUpdate):
    production_order_id: int


class DeleteProductionOrderInput(BaseModel):
    production_order_id: int


class ListProductionOperationsInput(BaseModel):
    production_order_id: int | None = None
    workstation_id: int | None = None
    status: str | None = None


class GetProductionOperationInput(BaseModel):
    production_operation_id: int


class UpdateProductionOperationInput(ProductionOperationUpdate):
    production_operation_id: int


class DeleteProductionOperationInput(BaseModel):
    production_operation_id: int


class ListShiftTemplatesInput(BaseModel):
    code: str | None = None
    shift_type: str | None = None
    status: str | None = None


class GetShiftTemplateInput(BaseModel):
    shift_template_id: int


class UpdateShiftTemplateInput(ShiftTemplateUpdate):
    shift_template_id: int


class DeleteShiftTemplateInput(BaseModel):
    shift_template_id: int


class ListShiftPlansInput(BaseModel):
    production_line_id: int | None = None
    shift_template_id: int | None = None
    work_date: date | None = None
    status: str | None = None
    production_order_id: int | None = None


class GetShiftPlanInput(BaseModel):
    shift_plan_id: int


class UpdateShiftPlanInput(ShiftPlanUpdate):
    shift_plan_id: int


class DeleteShiftPlanInput(BaseModel):
    shift_plan_id: int


class ListShiftAssignmentsInput(BaseModel):
    shift_plan_id: int | None = None
    worker_id: int | None = None
    workstation_id: int | None = None
    status: str | None = None


class GetShiftAssignmentInput(BaseModel):
    shift_assignment_id: int


class UpdateShiftAssignmentInput(ShiftAssignmentUpdate):
    shift_assignment_id: int


class DeleteShiftAssignmentInput(BaseModel):
    shift_assignment_id: int


def _create_production_line(**kwargs):
    return safe_call(production_line_service.create_production_line, ProductionLineCreate(**kwargs))


def _update_production_line(production_line_id: int, **kwargs):
    return safe_call(
        production_line_service.update_production_line,
        production_line_id,
        ProductionLineUpdate(**kwargs),
    )


def _create_workstation(**kwargs):
    return safe_call(workstation_service.create_workstation, WorkstationCreate(**kwargs))


def _update_workstation(workstation_id: int, **kwargs):
    return safe_call(workstation_service.update_workstation, workstation_id, WorkstationUpdate(**kwargs))


def _create_production_order(**kwargs):
    return safe_call(production_order_service.create_production_order, ProductionOrderCreate(**kwargs))


def _update_production_order(production_order_id: int, **kwargs):
    return safe_call(
        production_order_service.update_production_order,
        production_order_id,
        ProductionOrderUpdate(**kwargs),
    )


def _create_production_operation(**kwargs):
    return safe_call(
        production_operation_service.create_production_operation,
        ProductionOperationCreate(**kwargs),
    )


def _update_production_operation(production_operation_id: int, **kwargs):
    return safe_call(
        production_operation_service.update_production_operation,
        production_operation_id,
        ProductionOperationUpdate(**kwargs),
    )


def _create_shift_template(**kwargs):
    return safe_call(shift_template_service.create_shift_template, ShiftTemplateCreate(**kwargs))


def _update_shift_template(shift_template_id: int, **kwargs):
    return safe_call(shift_template_service.update_shift_template, shift_template_id, ShiftTemplateUpdate(**kwargs))


def _create_shift_plan(**kwargs):
    return safe_call(shift_plan_service.create_shift_plan, ShiftPlanCreate(**kwargs))


def _update_shift_plan(shift_plan_id: int, **kwargs):
    return safe_call(shift_plan_service.update_shift_plan, shift_plan_id, ShiftPlanUpdate(**kwargs))


def _list_shift_plans(
    production_line_id: int | None = None,
    shift_template_id: int | None = None,
    work_date: date | None = None,
    status: str | None = None,
    production_order_id: int | None = None,
):
    return safe_call(
        shift_plan_service.list_shift_plans,
        production_line_id,
        shift_template_id,
        work_date,
        status,
        production_order_id,
    )


def _create_shift_assignment(**kwargs):
    return safe_call(shift_assignment_service.create_shift_assignment, ShiftAssignmentCreate(**kwargs))


def _update_shift_assignment(shift_assignment_id: int, **kwargs):
    return safe_call(
        shift_assignment_service.update_shift_assignment,
        shift_assignment_id,
        ShiftAssignmentUpdate(**kwargs),
    )


skill = AgentSkill(
    name="operations",
    description="Manage shopfloor, production, and staffing records.",
    applicability="Use for production lines, workstations, orders, operations, shift plans, and assignments.",
    keywords=(
        "production",
        "workstation",
        "shift",
        "staffing",
        "operation",
        "line",
        "工位",
        "排班",
        "产线",
        "工序",
        "订单",
    ),
    tools=[
        AgentTool(
            name="list_production_lines",
            description="List production lines with optional organization, code, or status filters.",
            parameters=ListProductionLinesInput.model_json_schema(),
            fn=lambda organization_unit_id=None, code=None, status=None: safe_call(
                production_line_service.list_production_lines,
                organization_unit_id,
                code,
                status,
            ),
        ),
        AgentTool(
            name="get_production_line",
            description="Get one production line by ID.",
            parameters=GetProductionLineInput.model_json_schema(),
            fn=lambda production_line_id: safe_call(production_line_service.get_production_line, production_line_id),
        ),
        AgentTool(
            name="create_production_line",
            description="Create a new production line.",
            parameters=ProductionLineCreate.model_json_schema(),
            fn=_create_production_line,
        ),
        AgentTool(
            name="update_production_line",
            description="Update an existing production line.",
            parameters=UpdateProductionLineInput.model_json_schema(),
            fn=lambda production_line_id, **kwargs: _update_production_line(production_line_id, **kwargs),
        ),
        AgentTool(
            name="delete_production_line",
            description="Delete one production line by ID.",
            parameters=DeleteProductionLineInput.model_json_schema(),
            fn=lambda production_line_id: safe_call(production_line_service.delete_production_line, production_line_id),
        ),
        AgentTool(
            name="list_workstations",
            description="List workstations with optional line, code, or status filters.",
            parameters=ListWorkstationsInput.model_json_schema(),
            fn=lambda production_line_id=None, code=None, status=None: safe_call(
                workstation_service.list_workstations,
                production_line_id,
                code,
                status,
            ),
        ),
        AgentTool(
            name="get_workstation",
            description="Get one workstation by ID.",
            parameters=GetWorkstationInput.model_json_schema(),
            fn=lambda workstation_id: safe_call(workstation_service.get_workstation, workstation_id),
        ),
        AgentTool(
            name="create_workstation",
            description="Create a new workstation.",
            parameters=WorkstationCreate.model_json_schema(),
            fn=_create_workstation,
        ),
        AgentTool(
            name="update_workstation",
            description="Update an existing workstation.",
            parameters=UpdateWorkstationInput.model_json_schema(),
            fn=lambda workstation_id, **kwargs: _update_workstation(workstation_id, **kwargs),
        ),
        AgentTool(
            name="delete_workstation",
            description="Delete one workstation by ID.",
            parameters=DeleteWorkstationInput.model_json_schema(),
            fn=lambda workstation_id: safe_call(workstation_service.delete_workstation, workstation_id),
        ),
        AgentTool(
            name="list_production_orders",
            description="List production orders with optional line, order number, or status filters.",
            parameters=ListProductionOrdersInput.model_json_schema(),
            fn=lambda production_line_id=None, order_number=None, status=None: safe_call(
                production_order_service.list_production_orders,
                production_line_id,
                order_number,
                status,
            ),
        ),
        AgentTool(
            name="get_production_order",
            description="Get one production order by ID.",
            parameters=GetProductionOrderInput.model_json_schema(),
            fn=lambda production_order_id: safe_call(
                production_order_service.get_production_order,
                production_order_id,
            ),
        ),
        AgentTool(
            name="create_production_order",
            description="Create a new production order.",
            parameters=ProductionOrderCreate.model_json_schema(),
            fn=_create_production_order,
        ),
        AgentTool(
            name="update_production_order",
            description="Update an existing production order.",
            parameters=UpdateProductionOrderInput.model_json_schema(),
            fn=lambda production_order_id, **kwargs: _update_production_order(production_order_id, **kwargs),
        ),
        AgentTool(
            name="delete_production_order",
            description="Delete one production order by ID.",
            parameters=DeleteProductionOrderInput.model_json_schema(),
            fn=lambda production_order_id: safe_call(
                production_order_service.delete_production_order,
                production_order_id,
            ),
        ),
        AgentTool(
            name="list_production_operations",
            description="List production operations with optional order, workstation, or status filters.",
            parameters=ListProductionOperationsInput.model_json_schema(),
            fn=lambda production_order_id=None, workstation_id=None, status=None: safe_call(
                production_operation_service.list_production_operations,
                production_order_id,
                workstation_id,
                status,
            ),
        ),
        AgentTool(
            name="get_production_operation",
            description="Get one production operation by ID.",
            parameters=GetProductionOperationInput.model_json_schema(),
            fn=lambda production_operation_id: safe_call(
                production_operation_service.get_production_operation,
                production_operation_id,
            ),
        ),
        AgentTool(
            name="create_production_operation",
            description="Create a new production operation.",
            parameters=ProductionOperationCreate.model_json_schema(),
            fn=_create_production_operation,
        ),
        AgentTool(
            name="update_production_operation",
            description="Update an existing production operation.",
            parameters=UpdateProductionOperationInput.model_json_schema(),
            fn=lambda production_operation_id, **kwargs: _update_production_operation(
                production_operation_id,
                **kwargs,
            ),
        ),
        AgentTool(
            name="delete_production_operation",
            description="Delete one production operation by ID.",
            parameters=DeleteProductionOperationInput.model_json_schema(),
            fn=lambda production_operation_id: safe_call(
                production_operation_service.delete_production_operation,
                production_operation_id,
            ),
        ),
        AgentTool(
            name="list_shift_templates",
            description="List shift templates with optional code, type, or status filters.",
            parameters=ListShiftTemplatesInput.model_json_schema(),
            fn=lambda code=None, shift_type=None, status=None: safe_call(
                shift_template_service.list_shift_templates,
                code,
                shift_type,
                status,
            ),
        ),
        AgentTool(
            name="get_shift_template",
            description="Get one shift template by ID.",
            parameters=GetShiftTemplateInput.model_json_schema(),
            fn=lambda shift_template_id: safe_call(shift_template_service.get_shift_template, shift_template_id),
        ),
        AgentTool(
            name="create_shift_template",
            description="Create a new shift template.",
            parameters=ShiftTemplateCreate.model_json_schema(),
            fn=_create_shift_template,
        ),
        AgentTool(
            name="update_shift_template",
            description="Update an existing shift template.",
            parameters=UpdateShiftTemplateInput.model_json_schema(),
            fn=lambda shift_template_id, **kwargs: _update_shift_template(shift_template_id, **kwargs),
        ),
        AgentTool(
            name="delete_shift_template",
            description="Delete one shift template by ID.",
            parameters=DeleteShiftTemplateInput.model_json_schema(),
            fn=lambda shift_template_id: safe_call(
                shift_template_service.delete_shift_template,
                shift_template_id,
            ),
        ),
        AgentTool(
            name="list_shift_plans",
            description="List shift plans with optional line, template, date, status, or production order filters.",
            parameters=ListShiftPlansInput.model_json_schema(),
            fn=_list_shift_plans,
        ),
        AgentTool(
            name="get_shift_plan",
            description="Get one shift plan by ID.",
            parameters=GetShiftPlanInput.model_json_schema(),
            fn=lambda shift_plan_id: safe_call(shift_plan_service.get_shift_plan, shift_plan_id),
        ),
        AgentTool(
            name="create_shift_plan",
            description="Create a new shift plan.",
            parameters=ShiftPlanCreate.model_json_schema(),
            fn=_create_shift_plan,
        ),
        AgentTool(
            name="update_shift_plan",
            description="Update an existing shift plan.",
            parameters=UpdateShiftPlanInput.model_json_schema(),
            fn=lambda shift_plan_id, **kwargs: _update_shift_plan(shift_plan_id, **kwargs),
        ),
        AgentTool(
            name="delete_shift_plan",
            description="Delete one shift plan by ID.",
            parameters=DeleteShiftPlanInput.model_json_schema(),
            fn=lambda shift_plan_id: safe_call(shift_plan_service.delete_shift_plan, shift_plan_id),
        ),
        AgentTool(
            name="list_shift_assignments",
            description="List shift assignments with optional plan, worker, workstation, or status filters.",
            parameters=ListShiftAssignmentsInput.model_json_schema(),
            fn=lambda shift_plan_id=None, worker_id=None, workstation_id=None, status=None: safe_call(
                shift_assignment_service.list_shift_assignments,
                shift_plan_id,
                worker_id,
                workstation_id,
                status,
            ),
        ),
        AgentTool(
            name="get_shift_assignment",
            description="Get one shift assignment by ID.",
            parameters=GetShiftAssignmentInput.model_json_schema(),
            fn=lambda shift_assignment_id: safe_call(
                shift_assignment_service.get_shift_assignment,
                shift_assignment_id,
            ),
        ),
        AgentTool(
            name="create_shift_assignment",
            description="Create a new shift assignment. Eligibility validation runs automatically.",
            parameters=ShiftAssignmentCreate.model_json_schema(),
            fn=_create_shift_assignment,
        ),
        AgentTool(
            name="update_shift_assignment",
            description="Update an existing shift assignment. Eligibility validation runs automatically.",
            parameters=UpdateShiftAssignmentInput.model_json_schema(),
            fn=lambda shift_assignment_id, **kwargs: _update_shift_assignment(shift_assignment_id, **kwargs),
        ),
        AgentTool(
            name="delete_shift_assignment",
            description="Delete one shift assignment by ID.",
            parameters=DeleteShiftAssignmentInput.model_json_schema(),
            fn=lambda shift_assignment_id: safe_call(
                shift_assignment_service.delete_shift_assignment,
                shift_assignment_id,
            ),
        ),
    ],
)

__all__ = ["skill"]
