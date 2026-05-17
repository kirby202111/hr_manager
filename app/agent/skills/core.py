from app.agent.protocol import AgentTool, Skill, _safe
from app.schemas.worker import WorkerCreate, WorkerUpdate
from app.services import org_unit as department_service
from app.services import worker as worker_service

skill = Skill(
    name="worker_management",
    description="员工与部门的基础查询和管理",
    applicability="用户需要查询员工信息、部门信息，或创建、修改、删除员工/部门时使用",
    tools=[
        AgentTool(
            name="query_workers",
            description="查询所有员工列表，返回员工 ID、姓名、部门、薪资等信息",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: _safe(worker_service.list_workers),
        ),
        AgentTool(
            name="query_worker",
            description="根据员工 ID 查询单个员工的详细信息",
            parameters={
                "type": "object",
                "properties": {"worker_id": {"type": "integer", "description": "员工 ID"}},
                "required": ["worker_id"],
            },
            fn=lambda worker_id: _safe(worker_service.get_worker, worker_id),
        ),
        AgentTool(
            name="query_departments",
            description="查询所有部门列表，返回部门 ID、名称、人数等信息",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: _safe(department_service.list_departments),
        ),
        AgentTool(
            name="query_department",
            description="根据部门 ID 查询部门详情，包括部门人数",
            parameters={
                "type": "object",
                "properties": {"department_id": {"type": "integer", "description": "部门 ID"}},
                "required": ["department_id"],
            },
            fn=lambda department_id: _safe(department_service.get_department, department_id),
        ),
        AgentTool(
            name="query_department_workers",
            description="查询指定部门下的所有员工",
            parameters={
                "type": "object",
                "properties": {"department_id": {"type": "integer", "description": "部门 ID"}},
                "required": ["department_id"],
            },
            fn=lambda department_id: _safe(department_service.get_department_workers, department_id),
        ),
        AgentTool(
            name="create_worker",
            description="创建新员工，需要提供姓名和薪资",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "员工姓名"},
                    "department_id": {"type": "integer", "description": "部门 ID（可选）"},
                    "salary": {"type": "number", "description": "月薪"},
                },
                "required": ["name", "salary"],
            },
            fn=lambda name, salary, department_id=None: _safe(
                worker_service.create_worker,
                WorkerCreate(name=name, department_id=department_id, salary=salary),
            ),
        ),
        AgentTool(
            name="update_worker",
            description="更新员工信息，只需要提供要修改的字段",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer", "description": "员工 ID"},
                    "name": {"type": "string", "description": "新姓名（可选）"},
                    "department_id": {"type": "integer", "description": "新部门 ID（可选）"},
                    "salary": {"type": "number", "description": "新月薪（可选）"},
                },
                "required": ["worker_id"],
            },
            fn=lambda worker_id, name=None, department_id=None, salary=None: _safe(
                worker_service.update_worker,
                worker_id,
                WorkerUpdate(name=name, department_id=department_id, salary=salary),
            ),
        ),
        AgentTool(
            name="delete_worker",
            description="删除指定员工",
            parameters={
                "type": "object",
                "properties": {"worker_id": {"type": "integer", "description": "员工 ID"}},
                "required": ["worker_id"],
            },
            fn=lambda worker_id: _safe(worker_service.delete_worker, worker_id),
        ),
    ],
)
