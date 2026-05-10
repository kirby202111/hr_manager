from datetime import date as date_type

from app.agent.protocol import AgentTool, Skill, _safe
from app.services import leave as leave_service
from app.schemas.leave import LeaveCreate, LeaveApproval


skill = Skill(
    name="leave_management",
    description="请假申请与审批管理",
    applicability="用户询问请假记录、假期余额，或需要提交、审批、驳回请假申请时使用",
    tools=[
        AgentTool(
            name="query_leaves",
            description="查询请假记录，可按员工ID和状态筛选",
            parameters={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "员工ID（可选）"},
                    "status": {"type": "string", "description": "状态：pending/approved/rejected/cancelled（可选）"},
                },
                "required": [],
            },
            fn=lambda employee_id=None, status=None: _safe(
                leave_service.list_leaves, employee_id, status
            ),
        ),
        AgentTool(
            name="query_leave_balance",
            description="查询员工的请假余额（年假、病假、事假的总额、已用、剩余）",
            parameters={
                "type": "object",
                "properties": {"employee_id": {"type": "integer", "description": "员工ID"}},
                "required": ["employee_id"],
            },
            fn=lambda employee_id: _safe(leave_service.get_leave_balance, employee_id),
        ),
        AgentTool(
            name="create_leave",
            description="提交请假申请",
            parameters={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "员工ID"},
                    "leave_type": {"type": "string", "description": "请假类型：sick(病假)/annual(年假)/personal(事假)/other(其他)"},
                    "start_date": {"type": "string", "description": "起始日期，格式YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "结束日期，格式YYYY-MM-DD"},
                    "reason": {"type": "string", "description": "请假原因（可选）"},
                },
                "required": ["employee_id", "leave_type", "start_date", "end_date"],
            },
            fn=lambda employee_id, leave_type, start_date, end_date, reason=None: _safe(
                leave_service.create_leave,
                LeaveCreate(
                    employee_id=employee_id,
                    leave_type=leave_type,
                    start_date=date_type.fromisoformat(start_date),
                    end_date=date_type.fromisoformat(end_date),
                    reason=reason,
                ),
            ),
        ),
        AgentTool(
            name="approve_leave",
            description="审批通过请假申请",
            parameters={
                "type": "object",
                "properties": {
                    "leave_id": {"type": "integer", "description": "请假记录ID"},
                    "approver": {"type": "string", "description": "审批人姓名"},
                    "comment": {"type": "string", "description": "审批意见（可选）"},
                },
                "required": ["leave_id", "approver"],
            },
            fn=lambda leave_id, approver, comment=None: _safe(
                leave_service.approve_leave,
                leave_id,
                LeaveApproval(approver=approver, comment=comment),
            ),
        ),
        AgentTool(
            name="reject_leave",
            description="驳回请假申请",
            parameters={
                "type": "object",
                "properties": {
                    "leave_id": {"type": "integer", "description": "请假记录ID"},
                    "approver": {"type": "string", "description": "审批人姓名"},
                    "comment": {"type": "string", "description": "驳回原因（可选）"},
                },
                "required": ["leave_id", "approver"],
            },
            fn=lambda leave_id, approver, comment=None: _safe(
                leave_service.reject_leave,
                leave_id,
                LeaveApproval(approver=approver, comment=comment),
            ),
        ),
    ],
)
