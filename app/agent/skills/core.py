from app.agent.protocol import AgentTool, Skill, _safe
from app.services import employee as employee_service
from app.services import department as department_service
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


skill = Skill(
    name="employee_management",
    description="员工与部门的基础查询和管理",
    applicability="用户询问员工信息、部门信息，或需要创建、修改、删除员工/部门时使用",
    tools=[
        AgentTool(
            name="query_employees",
            description="查询所有员工列表，返回员工ID、姓名、部门、薪资等信息",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: _safe(employee_service.list_employees),
        ),
        AgentTool(
            name="query_employee",
            description="根据员工ID查询单个员工的详细信息",
            parameters={
                "type": "object",
                "properties": {"employee_id": {"type": "integer", "description": "员工ID"}},
                "required": ["employee_id"],
            },
            fn=lambda employee_id: _safe(employee_service.get_employee, employee_id),
        ),
        AgentTool(
            name="query_departments",
            description="查询所有部门列表，返回部门ID、名称、人数等信息",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: _safe(department_service.list_departments),
        ),
        AgentTool(
            name="query_department",
            description="根据部门ID查询部门详情，包括部门人数",
            parameters={
                "type": "object",
                "properties": {"department_id": {"type": "integer", "description": "部门ID"}},
                "required": ["department_id"],
            },
            fn=lambda department_id: _safe(department_service.get_department, department_id),
        ),
        AgentTool(
            name="query_department_employees",
            description="查询指定部门下的所有员工",
            parameters={
                "type": "object",
                "properties": {"department_id": {"type": "integer", "description": "部门ID"}},
                "required": ["department_id"],
            },
            fn=lambda department_id: _safe(department_service.get_department_employees, department_id),
        ),
        AgentTool(
            name="create_employee",
            description="创建新员工，需要提供姓名和薪资",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "员工姓名"},
                    "department_id": {"type": "integer", "description": "部门ID（可选）"},
                    "salary": {"type": "number", "description": "月薪"},
                },
                "required": ["name", "salary"],
            },
            fn=lambda name, salary, department_id=None: _safe(
                employee_service.create_employee,
                EmployeeCreate(name=name, department_id=department_id, salary=salary),
            ),
        ),
        AgentTool(
            name="update_employee",
            description="更新员工信息，只需提供要修改的字段",
            parameters={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "员工ID"},
                    "name": {"type": "string", "description": "新姓名（可选）"},
                    "department_id": {"type": "integer", "description": "新部门ID（可选）"},
                    "salary": {"type": "number", "description": "新月薪（可选）"},
                },
                "required": ["employee_id"],
            },
            fn=lambda employee_id, name=None, department_id=None, salary=None: _safe(
                employee_service.update_employee,
                employee_id,
                EmployeeUpdate(name=name, department_id=department_id, salary=salary),
            ),
        ),
        AgentTool(
            name="delete_employee",
            description="删除指定员工",
            parameters={
                "type": "object",
                "properties": {"employee_id": {"type": "integer", "description": "员工ID"}},
                "required": ["employee_id"],
            },
            fn=lambda employee_id: _safe(employee_service.delete_employee, employee_id),
        ),
    ],
)
