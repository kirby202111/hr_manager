from app.agent.protocol import AgentTool, Skill, _safe
from app.services import employee_skill as skill_service
from app.schemas.employee_skill import EmployeeSkillCreate, EmployeeSkillUpdate


skill = Skill(
    name="skill_management",
    description="员工技能的查询与管理",
    applicability="用户询问员工技能、技能熟练度、技能认证，或需要新增、修改、删除员工技能时使用",
    tools=[
        AgentTool(
            name="query_skills",
            description="查询所有员工技能记录",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: _safe(skill_service.list_skills),
        ),
        AgentTool(
            name="query_skill",
            description="根据技能记录ID查询单条技能详情",
            parameters={
                "type": "object",
                "properties": {"skill_id": {"type": "integer", "description": "技能记录ID"}},
                "required": ["skill_id"],
            },
            fn=lambda skill_id: _safe(skill_service.get_skill, skill_id),
        ),
        AgentTool(
            name="query_employee_skills",
            description="查询指定员工的所有技能",
            parameters={
                "type": "object",
                "properties": {"employee_id": {"type": "integer", "description": "员工ID"}},
                "required": ["employee_id"],
            },
            fn=lambda employee_id: _safe(skill_service.list_skills_by_employee, employee_id),
        ),
        AgentTool(
            name="create_skill",
            description="为员工添加技能，需要提供员工ID、技能名称和熟练程度(beginner/intermediate/advanced/expert)",
            parameters={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "员工ID"},
                    "skill_name": {"type": "string", "description": "技能名称"},
                    "proficiency_level": {
                        "type": "string",
                        "description": "熟练程度：beginner(入门)/intermediate(中级)/advanced(高级)/expert(专家)",
                        "enum": ["beginner", "intermediate", "advanced", "expert"],
                    },
                    "years_of_experience": {"type": "number", "description": "使用该技能的年限（可选）"},
                    "certification": {"type": "string", "description": "相关认证（可选）"},
                },
                "required": ["employee_id", "skill_name", "proficiency_level"],
            },
            fn=lambda employee_id, skill_name, proficiency_level,
                years_of_experience=None, certification=None: _safe(
                skill_service.create_skill,
                EmployeeSkillCreate(
                    employee_id=employee_id,
                    skill_name=skill_name,
                    proficiency_level=proficiency_level,
                    years_of_experience=years_of_experience,
                    certification=certification,
                ),
            ),
        ),
        AgentTool(
            name="update_skill",
            description="更新员工技能信息，只需提供要修改的字段",
            parameters={
                "type": "object",
                "properties": {
                    "skill_id": {"type": "integer", "description": "技能记录ID"},
                    "skill_name": {"type": "string", "description": "技能名称（可选）"},
                    "proficiency_level": {
                        "type": "string",
                        "description": "熟练程度（可选）：beginner/intermediate/advanced/expert",
                        "enum": ["beginner", "intermediate", "advanced", "expert"],
                    },
                    "years_of_experience": {"type": "number", "description": "使用年限（可选）"},
                    "certification": {"type": "string", "description": "相关认证（可选）"},
                },
                "required": ["skill_id"],
            },
            fn=lambda skill_id, skill_name=None, proficiency_level=None,
                years_of_experience=None, certification=None: _safe(
                skill_service.update_skill,
                skill_id,
                EmployeeSkillUpdate(
                    skill_name=skill_name,
                    proficiency_level=proficiency_level,
                    years_of_experience=years_of_experience,
                    certification=certification,
                ),
            ),
        ),
        AgentTool(
            name="delete_skill",
            description="删除指定技能记录",
            parameters={
                "type": "object",
                "properties": {"skill_id": {"type": "integer", "description": "技能记录ID"}},
                "required": ["skill_id"],
            },
            fn=lambda skill_id: _safe(skill_service.delete_skill, skill_id),
        ),
    ],
)
