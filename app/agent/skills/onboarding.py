from app.agent.protocol import Skill, _safe
from app.schemas.worker import WorkerCreate
from app.services import leave as leave_service
from app.services import worker as worker_service


def onboard_worker(name: str = "", salary: float = 0, department_id: int | None = None, **kwargs) -> dict:
    """办理新员工入职：创建员工 -> 查询初始假期余额。"""
    if not name or not salary:
        return {"error": "入职需要提供员工姓名和薪资"}

    worker = _safe(
        worker_service.create_worker,
        WorkerCreate(name=name, department_id=department_id, salary=salary),
    )
    if "error" in worker:
        return {"error": f"创建员工失败: {worker['error']}"}

    worker_id = worker["id"]
    steps = [{"step": "create_worker", "status": "success", "data": worker}]

    balance = _safe(leave_service.get_leave_balance, worker_id)
    if "error" not in balance:
        steps.append({"step": "query_leave_balance", "status": "success", "data": balance})
    else:
        steps.append({"step": "query_leave_balance", "status": "skipped", "reason": balance["error"]})

    return {
        "message": f"员工 {name} 入职成功",
        "worker_id": worker_id,
        "steps": steps,
    }


skill = Skill(
    name="worker_onboarding",
    description="新员工入职流程",
    applicability="用户需要办理新员工入职、注册新员工、设置新员工信息时使用",
    tools=[],
    workflows={
        "onboard_worker": onboard_worker,
    },
)
