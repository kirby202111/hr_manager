from app.agent.protocol import AgentTool, Skill, _safe
from app.services import payroll as payroll_service

skill = Skill(
    name="payroll_processing",
    description="薪资查询、生成与发放管理",
    applicability="用户询问薪资、工资条，或需要生成、发放薪资时使用",
    tools=[
        AgentTool(
            name="query_payrolls",
            description="查询薪资记录，可按员工ID、月份、状态筛选",
            parameters={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "员工ID（可选）"},
                    "month": {"type": "string", "description": "月份，格式YYYY-MM（可选）"},
                    "status": {"type": "string", "description": "状态：draft/paid（可选）"},
                },
                "required": [],
            },
            fn=lambda employee_id=None, month=None, status=None: _safe(
                payroll_service.list_payrolls, employee_id, month, status
            ),
        ),
        AgentTool(
            name="query_payslip",
            description="查询薪资条详情，包含考勤摘要、请假摘要、扣款明细、奖金明细",
            parameters={
                "type": "object",
                "properties": {"payroll_id": {"type": "integer", "description": "薪资记录ID"}},
                "required": ["payroll_id"],
            },
            fn=lambda payroll_id: _safe(payroll_service.get_payslip, payroll_id),
        ),
        AgentTool(
            name="generate_monthly_payroll",
            description="为所有员工生成指定月份的薪资，自动计算考勤扣款和请假扣款",
            parameters={
                "type": "object",
                "properties": {"month": {"type": "string", "description": "月份，格式YYYY-MM"}},
                "required": ["month"],
            },
            fn=lambda month: _safe(payroll_service.generate_monthly_payroll, month),
        ),
        AgentTool(
            name="pay_payroll",
            description="将薪资记录标记为已支付",
            parameters={
                "type": "object",
                "properties": {"payroll_id": {"type": "integer", "description": "薪资记录ID"}},
                "required": ["payroll_id"],
            },
            fn=lambda payroll_id: _safe(payroll_service.pay_payroll, payroll_id),
        ),
    ],
)
