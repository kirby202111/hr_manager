from __future__ import annotations

from unittest.mock import MagicMock, patch

# 鈹€鈹€ Skill definitions 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€


class TestCoreSkill:
    def test_skill_metadata(self):
        from app.agent.skills.core import skill

        assert skill.name == "worker_management"
        assert skill.description
        assert skill.applicability
        assert len(skill.tools) > 0
        assert skill.enabled is True

    def test_tool_names(self):
        from app.agent.skills.core import skill

        names = [t.name for t in skill.tools]
        assert "query_workers" in names
        assert "query_worker" in names
        assert "create_worker" in names
        assert "update_worker" in names
        assert "delete_worker" in names

    def test_tool_openai_format(self):
        from app.agent.skills.core import skill

        for tool in skill.tools:
            fmt = tool.to_openai_tool()
            assert fmt["type"] == "function"
            assert "name" in fmt["function"]
            assert "parameters" in fmt["function"]


class TestEmployeeSkillSkill:
    def test_skill_metadata(self):
        from app.agent.skills.employee_skill import skill

        assert skill.name == "skill_management"
        assert len(skill.tools) > 0

    def test_tool_names(self):
        from app.agent.skills.employee_skill import skill

        names = [t.name for t in skill.tools]
        assert "query_skills" in names or "query_worker_skills" in names


class TestOnboardingSkill:
    def test_skill_metadata(self):
        from app.agent.skills.onboarding import skill

        assert skill.name == "worker_onboarding"
        assert len(skill.tools) == 0
        assert "onboard_employee" in skill.workflows

    @patch("app.agent.skills.onboarding.employee_service")
    @patch("app.agent.skills.onboarding.leave_service")
    def test_onboard_employee_success(self, mock_leave, mock_emp):
        from app.agent.skills.onboarding import onboard_employee

        mock_emp.create_worker.return_value = MagicMock(
            model_dump=lambda: {
                "id": 1,
                "name": "寮犱笁",
                "salary": 10000,
                "department_id": None,
                "department_name": None,
            },
        )
        mock_leave.get_leave_balance.return_value = MagicMock(
            model_dump=lambda: {"employee_id": 1, "annual_remaining": 10},
        )
        result = onboard_employee(name="寮犱笁", salary=10000)
        assert "error" not in result or result.get("employee_id") == 1

    def test_onboard_employee_missing_params(self):
        from app.agent.skills.onboarding import onboard_employee

        result = onboard_employee(name="", salary=0)
        assert "error" in result


class TestLeaveSkill:
    def test_skill_metadata(self):
        from app.agent.skills.leave import skill

        assert skill.name == "leave_management"
        assert len(skill.tools) > 0

    def test_tool_names(self):
        from app.agent.skills.leave import skill

        names = [t.name for t in skill.tools]
        assert "query_leaves" in names or "create_leave" in names


class TestAttendanceSkill:
    def test_skill_metadata(self):
        from app.agent.skills.attendance import skill

        assert skill.name == "attendance_management"
        assert len(skill.tools) > 0


class TestPayrollSkill:
    def test_skill_metadata(self):
        from app.agent.skills.payroll import skill

        assert skill.name == "payroll_processing"
        assert len(skill.tools) > 0


class TestAnalyticsSkill:
    def test_skill_metadata(self):
        from app.agent.skills.analytics import skill

        assert skill.name == "analytics"
        assert len(skill.tools) == 3

    def test_tool_names(self):
        from app.agent.skills.analytics import skill

        names = [t.name for t in skill.tools]
        assert "analyze_department_salary_distribution" in names
        assert "analyze_attendance_anomalies" in names
        assert "analyze_leave_trends" in names

    @patch("app.agent.skills.analytics.department_service")
    @patch("app.agent.skills.analytics.employee_repo")
    def test_analyze_department_salary(self, mock_emp_repo, mock_dept_service):
        from app.agent.skills.analytics import _analyze_department_salary

        mock_dept_service.list_departments.return_value = MagicMock(
            departments=[MagicMock(id=1, name="宸ョ▼閮?)],
        )
        mock_emp_repo.get_workers_by_department.return_value = [
            {"salary": 15000},
            {"salary": 20000},
        ]
        result = _analyze_department_salary()
        assert "departments" in result
        assert result["departments"][0]["avg_salary"] == 17500


class TestKnowledgeBaseSkill:
    def test_skill_metadata(self):
        from app.agent.skills.knowledge_base import skill

        assert skill.name == "knowledge_base"
        assert len(skill.tools) > 0

    def test_tool_names(self):
        from app.agent.skills.knowledge_base import skill

        names = [t.name for t in skill.tools]
        assert "search_knowledge_base" in names


class TestProjectSkill:
    def test_skill_metadata(self):
        from app.agent.skills.project import skill

        assert skill.name == "project_management"
        assert len(skill.tools) > 0


class TestMemorySkill:
    def test_skill_metadata(self):
        from app.agent.skills.memory import skill

        assert skill.name == "memory"
        assert len(skill.tools) > 0

    def test_tool_names(self):
        from app.agent.skills.memory import skill

        names = [t.name for t in skill.tools]
        assert "recall_memories" in names
        assert "save_memory" in names
        assert "check_reminders" in names
        assert "set_reminder" in names
        assert "delete_memory" in names

    @patch("app.agent.skills.memory.memory_service")
    def test_recall_memories_tool_calls_service(self, mock_service):
        from app.agent.skills.memory import skill

        mock_service.recall_memories.return_value = MagicMock(
            model_dump=lambda: {"memories": [], "total": 0},
        )
        recall_tool = skill.get_tool_map()["recall_memories"]
        recall_tool.fn(user_tag="test_user")
        mock_service.recall_memories.assert_called_once()

    @patch("app.agent.skills.memory.memory_service")
    def test_save_memory_tool_constructs_schema(self, mock_service):
        from app.agent.skills.memory import skill

        mock_service.save_memory.return_value = MagicMock(
            model_dump=lambda: {"id": 1, "content": "test"},
        )
        save_tool = skill.get_tool_map()["save_memory"]
        save_tool.fn(
            user_tag="test_user",
            memory_type="fact",
            category="general",
            subject="test",
            content="娴嬭瘯鍐呭",
        )
        mock_service.save_memory.assert_called_once()

    @patch("app.agent.skills.memory.memory_service")
    def test_save_memory_error_handling(self, mock_service):
        from fastapi import HTTPException

        from app.agent.skills.memory import skill as mem_skill

        mock_service.save_memory.side_effect = HTTPException(status_code=400, detail="bad")
        save_tool = mem_skill.get_tool_map()["save_memory"]
        result = save_tool.fn(
            user_tag="test",
            memory_type="invalid",
            category="general",
            subject="test",
            content="test",
        )
        assert "error" in result


# 鈹€鈹€ Skill registration 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€


class TestSkillRegistration:
    def test_register_all_skills(self):
        from app.agent.skill_registry import SkillRegistry
        from app.agent.skills import register_all_skills

        registry = SkillRegistry()
        register_all_skills(registry)
        skills = registry.list_skills()
        skill_names = [s["name"] for s in skills]
        assert "worker_management" in skill_names
        assert "skill_management" in skill_names
        assert "leave_management" in skill_names
        assert "attendance_management" in skill_names
        assert "payroll_processing" in skill_names
        assert "analytics" in skill_names
        assert "knowledge_base" in skill_names
        assert "project_management" in skill_names
        assert "memory" in skill_names
        assert "worker_onboarding" in skill_names
        assert len(skills) == 10

    def test_all_skills_have_tools_or_workflows(self):
        from app.agent.skill_registry import SkillRegistry
        from app.agent.skills import register_all_skills

        registry = SkillRegistry()
        register_all_skills(registry)
        for skill_info in registry.list_skills():
            assert skill_info["tool_count"] > 0 or skill_info["workflow_count"] > 0

    def test_no_duplicate_tool_names(self):
        from app.agent.skill_registry import SkillRegistry
        from app.agent.skills import register_all_skills

        registry = SkillRegistry()
        register_all_skills(registry)
        all_tools = registry.get_all_tools()
        names = [t.name for t in all_tools]
        assert len(names) == len(set(names)), f"Duplicate tool names: {set(n for n in names if names.count(n) > 1)}"

