from app.agent.protocol import Skill, _safe
from app.schemas.employee import EmployeeCreate
from app.services import employee as employee_service
from app.services import leave as leave_service


def onboard_employee(name: str = "", salary: float = 0, department_id: int | None = None, **kwargs) -> dict:
    """办理新员工入职：创建员工 -> 查询初始假期余额"""
    if not name or not salary:
        return {"error": "入职需要提供员工姓名和薪资"}

    employee = _safe(
        employee_service.create_employee,
        EmployeeCreate(name=name, department_id=department_id, salary=salary),
    )
    if "error" in employee:
        return {"error": f"创建员工失败: {employee['error']}"}

    employee_id = employee["id"]
    steps = [{"step": "create_employee", "status": "success", "data": employee}]

    balance = _safe(leave_service.get_leave_balance, employee_id)
    if "error" not in balance:
        steps.append({"step": "query_leave_balance", "status": "success", "data": balance})
    else:
        steps.append({"step": "query_leave_balance", "status": "skipped", "reason": balance["error"]})

    return {
        "message": f"员工 {name} 入职成功",
        "employee_id": employee_id,
        "steps": steps,
    }


skill = Skill(
    name="employee_onboarding",
    description="新员工入职流程",
    applicability="用户需要办理新员工入职、注册新员工、设置新员工信息时使用",
    tools=[],
    workflows={
        "onboard_employee": onboard_employee,
    },
)
