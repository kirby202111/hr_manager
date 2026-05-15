from app.agent.protocol import AgentTool, Skill, _safe
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberCreate,
    ProjectSkillRequirementCreate,
    ProjectTimesheetCreate,
    ProjectUpdate,
)
from app.schemas.skill_catalog import SkillCatalogCreate
from app.services import project as project_service
from app.services import skill_catalog as catalog_service

skill = Skill(
    name="project_management",
    description="项目与技能目录管理",
    applicability="用户询问项目信息、项目技能需求、项目成员分配、项目工时与进度，或需要管理技能目录时使用",
    tools=[
        # ── 技能目录 ───────────────────────────────────────────
        AgentTool(
            name="query_skill_catalog",
            description="查询技能目录，可按分类筛选",
            parameters={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "技能分类（可选）"},
                },
                "required": [],
            },
            fn=lambda category=None: _safe(catalog_service.list_skills, category),
        ),
        AgentTool(
            name="create_skill_catalog_entry",
            description="在技能目录中新增技能",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "技能名称"},
                    "category": {"type": "string", "description": "技能分类（可选）"},
                    "description": {"type": "string", "description": "技能描述（可选）"},
                },
                "required": ["name"],
            },
            fn=lambda name, category=None, description=None: _safe(
                catalog_service.create_skill,
                SkillCatalogCreate(name=name, category=category, description=description),
            ),
        ),
        # ── 项目 ───────────────────────────────────────────────
        AgentTool(
            name="query_projects",
            description="查询所有项目，可按状态筛选(planning/active/completed)",
            parameters={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "项目状态筛选（可选）",
                        "enum": ["planning", "active", "completed"],
                    },
                },
                "required": [],
            },
            fn=lambda status=None: _safe(project_service.list_projects, status),
        ),
        AgentTool(
            name="query_project",
            description="根据ID查询项目详情",
            parameters={
                "type": "object",
                "properties": {"project_id": {"type": "integer", "description": "项目ID"}},
                "required": ["project_id"],
            },
            fn=lambda project_id: _safe(project_service.get_project, project_id),
        ),
        AgentTool(
            name="create_project",
            description="新建项目",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "项目名称"},
                    "description": {"type": "string", "description": "项目描述（可选）"},
                    "status": {
                        "type": "string",
                        "description": "项目状态（默认planning）",
                        "enum": ["planning", "active", "completed"],
                    },
                    "start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD（可选）"},
                    "end_date": {"type": "string", "description": "结束日期 YYYY-MM-DD（可选）"},
                },
                "required": ["name"],
            },
            fn=lambda name, description=None, status="planning", start_date=None, end_date=None: _safe(
                project_service.create_project,
                ProjectCreate(
                    name=name,
                    description=description,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                ),
            ),
        ),
        AgentTool(
            name="update_project",
            description="更新项目信息",
            parameters={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "项目ID"},
                    "name": {"type": "string", "description": "项目名称（可选）"},
                    "description": {"type": "string", "description": "项目描述（可选）"},
                    "status": {
                        "type": "string",
                        "description": "项目状态（可选）",
                        "enum": ["planning", "active", "completed"],
                    },
                    "start_date": {"type": "string", "description": "开始日期（可选）"},
                    "end_date": {"type": "string", "description": "结束日期（可选）"},
                },
                "required": ["project_id"],
            },
            fn=lambda project_id, name=None, description=None, status=None, start_date=None, end_date=None: _safe(
                project_service.update_project,
                project_id,
                ProjectUpdate(
                    name=name,
                    description=description,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                ),
            ),
        ),
        # ── 项目技能需求 ───────────────────────────────────────
        AgentTool(
            name="query_project_skill_requirements",
            description="查询项目的技能需求列表",
            parameters={
                "type": "object",
                "properties": {"project_id": {"type": "integer", "description": "项目ID"}},
                "required": ["project_id"],
            },
            fn=lambda project_id: _safe(project_service.list_skill_requirements, project_id),
        ),
        AgentTool(
            name="add_project_skill_requirement",
            description="为项目添加技能需求，需要指定技能目录ID、熟练程度、工时预算(人天)和所需人数",
            parameters={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "项目ID"},
                    "skill_id": {"type": "integer", "description": "技能目录ID"},
                    "required_proficiency": {
                        "type": "string",
                        "description": "所需熟练程度：beginner/intermediate/advanced/expert",
                        "enum": ["beginner", "intermediate", "advanced", "expert"],
                    },
                    "person_days": {"type": "number", "description": "工时预算（人天）"},
                    "headcount": {"type": "integer", "description": "所需人数"},
                },
                "required": ["project_id", "skill_id", "required_proficiency", "person_days", "headcount"],
            },
            fn=lambda project_id, skill_id, required_proficiency, person_days, headcount: _safe(
                project_service.create_skill_requirement,
                project_id,
                ProjectSkillRequirementCreate(
                    skill_id=skill_id,
                    required_proficiency=required_proficiency,
                    person_days=person_days,
                    headcount=headcount,
                ),
            ),
        ),
        # ── 项目成员 ───────────────────────────────────────────
        AgentTool(
            name="query_project_members",
            description="查询项目成员列表",
            parameters={
                "type": "object",
                "properties": {"project_id": {"type": "integer", "description": "项目ID"}},
                "required": ["project_id"],
            },
            fn=lambda project_id: _safe(project_service.list_members, project_id),
        ),
        AgentTool(
            name="add_project_member",
            description="为项目分配成员",
            parameters={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "项目ID"},
                    "employee_id": {"type": "integer", "description": "员工ID"},
                    "role": {"type": "string", "description": "项目角色"},
                    "assigned_date": {"type": "string", "description": "分配日期 YYYY-MM-DD"},
                },
                "required": ["project_id", "employee_id", "role", "assigned_date"],
            },
            fn=lambda project_id, employee_id, role, assigned_date: _safe(
                project_service.create_member,
                project_id,
                ProjectMemberCreate(employee_id=employee_id, role=role, assigned_date=assigned_date),
            ),
        ),
        # ── 项目工时 ───────────────────────────────────────────
        AgentTool(
            name="query_project_timesheets",
            description="查询项目工时记录，可按员工或技能需求筛选",
            parameters={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "项目ID"},
                    "employee_id": {"type": "integer", "description": "员工ID（可选）"},
                    "requirement_id": {"type": "integer", "description": "技能需求ID（可选）"},
                },
                "required": ["project_id"],
            },
            fn=lambda project_id, employee_id=None, requirement_id=None: _safe(
                project_service.list_timesheets,
                project_id,
                employee_id,
                requirement_id,
            ),
        ),
        AgentTool(
            name="add_project_timesheet",
            description="为项目添加工时记录",
            parameters={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "项目ID"},
                    "requirement_id": {"type": "integer", "description": "技能需求ID"},
                    "employee_id": {"type": "integer", "description": "员工ID"},
                    "date": {"type": "string", "description": "工作日期 YYYY-MM-DD"},
                    "hours": {"type": "number", "description": "当日投入时长（小时）"},
                    "description": {"type": "string", "description": "工作内容（可选）"},
                },
                "required": ["project_id", "requirement_id", "employee_id", "date", "hours"],
            },
            fn=lambda project_id, requirement_id, employee_id, date, hours, description=None: _safe(
                project_service.create_timesheet,
                project_id,
                ProjectTimesheetCreate(
                    requirement_id=requirement_id,
                    employee_id=employee_id,
                    date=date,
                    hours=hours,
                    description=description,
                ),
            ),
        ),
        # ── 项目进度 ───────────────────────────────────────────
        AgentTool(
            name="query_project_progress",
            description="查询项目进度汇总，包含按技能需求和按成员的工时消耗",
            parameters={
                "type": "object",
                "properties": {"project_id": {"type": "integer", "description": "项目ID"}},
                "required": ["project_id"],
            },
            fn=lambda project_id: _safe(project_service.get_project_progress, project_id),
        ),
    ],
)
