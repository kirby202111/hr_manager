from app.agent.protocol import AgentTool, Skill, _safe
from app.services import performance as performance_service
from app.schemas.performance import PerformanceReviewCreate


skill = Skill(
    name="performance_management",
    description="绩效评审与考核管理",
    applicability="用户询问绩效评分、考核周期，或需要提交绩效评审时使用",
    tools=[
        AgentTool(
            name="query_performance_reviews",
            description="查询绩效评审记录，可按员工ID和考核周期ID筛选",
            parameters={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "员工ID（可选）"},
                    "cycle_id": {"type": "integer", "description": "考核周期ID（可选）"},
                },
                "required": [],
            },
            fn=lambda employee_id=None, cycle_id=None: _safe(
                performance_service.list_reviews, employee_id, cycle_id
            ),
        ),
        AgentTool(
            name="query_employee_performance",
            description="查询员工的绩效摘要，包含平均评分、评审次数、最新评分、评分分布",
            parameters={
                "type": "object",
                "properties": {"employee_id": {"type": "integer", "description": "员工ID"}},
                "required": ["employee_id"],
            },
            fn=lambda employee_id: _safe(performance_service.get_employee_summary, employee_id),
        ),
        AgentTool(
            name="query_performance_cycles",
            description="查询所有绩效考核周期列表",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: _safe(performance_service.list_cycles),
        ),
        AgentTool(
            name="create_performance_review",
            description="提交绩效评审评分",
            parameters={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "员工ID"},
                    "cycle_id": {"type": "integer", "description": "考核周期ID"},
                    "rating": {"type": "number", "description": "评分，1.0-5.0"},
                    "reviewer": {"type": "string", "description": "评审人姓名"},
                    "comments": {"type": "string", "description": "评审意见（可选）"},
                },
                "required": ["employee_id", "cycle_id", "rating", "reviewer"],
            },
            fn=lambda employee_id, cycle_id, rating, reviewer, comments=None: _safe(
                performance_service.create_review,
                PerformanceReviewCreate(
                    employee_id=employee_id,
                    cycle_id=cycle_id,
                    rating=rating,
                    reviewer=reviewer,
                    comments=comments,
                ),
            ),
        ),
    ],
)
