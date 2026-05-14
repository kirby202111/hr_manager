"""Unit tests for all SQLAlchemy ORM models.

Each model is tested for:
- Creating an instance with all fields set and verifying to_dict() output
- Nullable fields correctly accept None and appear as None in to_dict()
- Non-nullable fields hold their assigned values
"""

from datetime import UTC, date, datetime, time

from app import database as db_mod
from app.models.agent_memory import (
    AgentMemory,
    ConversationMessage,
    MemoryReminder,
)
from app.models.attendance import Attendance
from app.models.department import Department

# ── Model imports ──────────────────────────────────────────────
from app.models.employee import Employee
from app.models.employee_skill import EmployeeSkill
from app.models.leave import Leave
from app.models.payroll import Payroll
from app.models.project import (
    Project,
    ProjectMember,
    ProjectSkillRequirement,
    ProjectTimesheet,
)
from app.models.skill_catalog import SkillCatalog

# ── Helpers ────────────────────────────────────────────────────


def _add_and_refresh(obj):
    """Persist an ORM object, commit, refresh, and return it."""
    session = db_mod.SessionLocal()
    try:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    finally:
        session.close()


# ==============================================================
# Employee
# ==============================================================


class TestEmployee:
    def test_create_with_all_fields(self):
        emp = Employee(name="张三", department_id=1, salary=15000.0)
        persisted = _add_and_refresh(emp)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {"id", "name", "department_id", "salary"}
        assert d["id"] is not None
        assert d["name"] == "张三"
        assert d["department_id"] == 1
        assert d["salary"] == 15000.0

    def test_nullable_department_id_is_none(self):
        emp = Employee(name="李四", department_id=None, salary=8000.0)
        persisted = _add_and_refresh(emp)
        d = persisted.to_dict()

        assert d["department_id"] is None
        assert d["name"] == "李四"
        assert d["salary"] == 8000.0

    def test_query_by_id(self):
        emp = Employee(name="王五", department_id=2, salary=20000.0)
        persisted = _add_and_refresh(emp)

        session = db_mod.SessionLocal()
        try:
            found = session.get(Employee, persisted.id)
            assert found is not None
            assert found.to_dict()["name"] == "王五"
        finally:
            session.close()


# ==============================================================
# Department
# ==============================================================


class TestDepartment:
    def test_create_with_all_fields(self):
        dept = Department(name="工程部", description="研发部门", manager="张经理")
        persisted = _add_and_refresh(dept)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {"id", "name", "description", "manager"}
        assert d["id"] is not None
        assert d["name"] == "工程部"
        assert d["description"] == "研发部门"
        assert d["manager"] == "张经理"

    def test_nullable_fields_are_none(self):
        dept = Department(name="市场部", description=None, manager=None)
        persisted = _add_and_refresh(dept)
        d = persisted.to_dict()

        assert d["description"] is None
        assert d["manager"] is None
        assert d["name"] == "市场部"


# ==============================================================
# Attendance
# ==============================================================


class TestAttendance:
    def test_create_with_all_fields(self):
        att = Attendance(
            employee_id=1,
            date=date(2026, 5, 1),
            check_in=time(8, 30),
            check_out=time(17, 30),
            status="normal",
            work_hours=8.0,
        )
        persisted = _add_and_refresh(att)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "employee_id",
            "date",
            "check_in",
            "check_out",
            "status",
            "work_hours",
        }
        assert d["id"] is not None
        assert d["employee_id"] == 1
        assert d["date"] == date(2026, 5, 1)
        assert d["check_in"] == time(8, 30)
        assert d["check_out"] == time(17, 30)
        assert d["status"] == "normal"
        assert d["work_hours"] == 8.0

    def test_nullable_fields_are_none(self):
        att = Attendance(
            employee_id=2,
            date=date(2026, 5, 2),
            check_in=time(9, 0),
            check_out=None,
            status="normal",
            work_hours=None,
        )
        persisted = _add_and_refresh(att)
        d = persisted.to_dict()

        assert d["check_out"] is None
        assert d["work_hours"] is None


# ==============================================================
# Leave
# ==============================================================


class TestLeave:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        approved = datetime(2026, 5, 9, 10, 0, 0)
        leave = Leave(
            employee_id=1,
            leave_type="annual",
            leave_type_name="年假",
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 12),
            days=3,
            reason="家庭事务",
            status="approved",
            approver="张经理",
            approved_at=approved,
            created_at=now,
        )
        persisted = _add_and_refresh(leave)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "employee_id",
            "leave_type",
            "leave_type_name",
            "start_date",
            "end_date",
            "days",
            "reason",
            "status",
            "approver",
            "approved_at",
            "created_at",
        }
        assert d["id"] is not None
        assert d["employee_id"] == 1
        assert d["leave_type"] == "annual"
        assert d["leave_type_name"] == "年假"
        assert d["start_date"] == date(2026, 5, 10)
        assert d["end_date"] == date(2026, 5, 12)
        assert d["days"] == 3
        assert d["reason"] == "家庭事务"
        assert d["status"] == "approved"
        assert d["approver"] == "张经理"
        assert d["approved_at"] == approved
        assert d["created_at"] is not None

    def test_nullable_fields_are_none(self):
        now = datetime.now(UTC)
        leave = Leave(
            employee_id=2,
            leave_type="sick",
            leave_type_name="病假",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 2),
            days=2,
            reason=None,
            status="pending",
            approver=None,
            approved_at=None,
            created_at=now,
        )
        persisted = _add_and_refresh(leave)
        d = persisted.to_dict()

        assert d["reason"] is None
        assert d["approver"] is None
        assert d["approved_at"] is None


# ==============================================================
# Payroll
# ==============================================================


class TestPayroll:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        payroll = Payroll(
            employee_id=1,
            month="2026-05",
            base_salary=15000.0,
            bonuses=2000.0,
            deductions=500.0,
            net_salary=16500.0,
            status="paid",
            payment_date=date(2026, 5, 10),
            created_at=now,
        )
        persisted = _add_and_refresh(payroll)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "employee_id",
            "month",
            "base_salary",
            "bonuses",
            "deductions",
            "net_salary",
            "status",
            "payment_date",
            "created_at",
        }
        assert d["id"] is not None
        assert d["employee_id"] == 1
        assert d["month"] == "2026-05"
        assert d["base_salary"] == 15000.0
        assert d["bonuses"] == 2000.0
        assert d["deductions"] == 500.0
        assert d["net_salary"] == 16500.0
        assert d["status"] == "paid"
        assert d["payment_date"] == date(2026, 5, 10)
        assert d["created_at"] is not None

    def test_default_values_and_nullable_payment_date(self):
        now = datetime.now(UTC)
        payroll = Payroll(
            employee_id=2,
            month="2026-06",
            base_salary=12000.0,
            net_salary=12000.0,
            status="draft",
            payment_date=None,
            created_at=now,
        )
        persisted = _add_and_refresh(payroll)
        d = persisted.to_dict()

        # bonuses and deductions have server defaults of 0
        assert d["bonuses"] == 0
        assert d["deductions"] == 0
        assert d["payment_date"] is None


# ==============================================================
# Project
# ==============================================================


class TestProject:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        proj = Project(
            name="HR系统V2",
            description="HR管理系统升级",
            status="planning",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            created_at=now,
        )
        persisted = _add_and_refresh(proj)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "name",
            "description",
            "status",
            "start_date",
            "end_date",
            "created_at",
        }
        assert d["id"] is not None
        assert d["name"] == "HR系统V2"
        assert d["description"] == "HR管理系统升级"
        assert d["status"] == "planning"
        assert d["start_date"] == date(2026, 1, 1)
        assert d["end_date"] == date(2026, 12, 31)
        assert d["created_at"] is not None

    def test_nullable_fields_are_none(self):
        now = datetime.now(UTC)
        proj = Project(
            name="快速项目",
            description=None,
            status="active",
            start_date=None,
            end_date=None,
            created_at=now,
        )
        persisted = _add_and_refresh(proj)
        d = persisted.to_dict()

        assert d["description"] is None
        assert d["start_date"] is None
        assert d["end_date"] is None


# ==============================================================
# ProjectSkillRequirement
# ==============================================================


class TestProjectSkillRequirement:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        req = ProjectSkillRequirement(
            project_id=1,
            skill_id=10,
            required_proficiency="advanced",
            person_days=20.0,
            headcount=3,
            created_at=now,
        )
        persisted = _add_and_refresh(req)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "project_id",
            "skill_id",
            "required_proficiency",
            "person_days",
            "headcount",
            "created_at",
        }
        assert d["id"] is not None
        assert d["project_id"] == 1
        assert d["skill_id"] == 10
        assert d["required_proficiency"] == "advanced"
        assert d["person_days"] == 20.0
        assert d["headcount"] == 3
        assert d["created_at"] is not None


# ==============================================================
# ProjectMember
# ==============================================================


class TestProjectMember:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        member = ProjectMember(
            project_id=1,
            employee_id=5,
            role="开发工程师",
            assigned_date=date(2026, 3, 15),
            created_at=now,
        )
        persisted = _add_and_refresh(member)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "project_id",
            "employee_id",
            "role",
            "assigned_date",
            "created_at",
        }
        assert d["id"] is not None
        assert d["project_id"] == 1
        assert d["employee_id"] == 5
        assert d["role"] == "开发工程师"
        assert d["assigned_date"] == date(2026, 3, 15)
        assert d["created_at"] is not None


# ==============================================================
# ProjectTimesheet
# ==============================================================


class TestProjectTimesheet:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        ts = ProjectTimesheet(
            project_id=1,
            requirement_id=10,
            employee_id=5,
            date=date(2026, 5, 13),
            hours=6.5,
            description="后端API开发",
            created_at=now,
        )
        persisted = _add_and_refresh(ts)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "project_id",
            "requirement_id",
            "employee_id",
            "date",
            "hours",
            "description",
            "created_at",
        }
        assert d["id"] is not None
        assert d["project_id"] == 1
        assert d["requirement_id"] == 10
        assert d["employee_id"] == 5
        assert d["date"] == date(2026, 5, 13)
        assert d["hours"] == 6.5
        assert d["description"] == "后端API开发"
        assert d["created_at"] is not None

    def test_nullable_description_is_none(self):
        now = datetime.now(UTC)
        ts = ProjectTimesheet(
            project_id=2,
            requirement_id=11,
            employee_id=6,
            date=date(2026, 5, 14),
            hours=4.0,
            description=None,
            created_at=now,
        )
        persisted = _add_and_refresh(ts)
        d = persisted.to_dict()

        assert d["description"] is None


# ==============================================================
# EmployeeSkill
# ==============================================================


class TestEmployeeSkill:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        skill = EmployeeSkill(
            employee_id=1,
            skill_name="Python",
            skill_id=10,
            proficiency_level="advanced",
            years_of_experience=5.0,
            certification="PCEP",
            created_at=now,
        )
        persisted = _add_and_refresh(skill)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "employee_id",
            "skill_name",
            "skill_id",
            "proficiency_level",
            "years_of_experience",
            "certification",
            "created_at",
        }
        assert d["id"] is not None
        assert d["employee_id"] == 1
        assert d["skill_name"] == "Python"
        assert d["skill_id"] == 10
        assert d["proficiency_level"] == "advanced"
        assert d["years_of_experience"] == 5.0
        assert d["certification"] == "PCEP"
        assert d["created_at"] is not None

    def test_nullable_fields_are_none(self):
        now = datetime.now(UTC)
        skill = EmployeeSkill(
            employee_id=2,
            skill_name="Java",
            skill_id=None,
            proficiency_level="intermediate",
            years_of_experience=None,
            certification=None,
            created_at=now,
        )
        persisted = _add_and_refresh(skill)
        d = persisted.to_dict()

        assert d["skill_id"] is None
        assert d["years_of_experience"] is None
        assert d["certification"] is None


# ==============================================================
# SkillCatalog
# ==============================================================


class TestSkillCatalog:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        catalog = SkillCatalog(
            name="Python",
            category="编程",
            description="Python编程语言",
            created_at=now,
        )
        persisted = _add_and_refresh(catalog)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {"id", "name", "category", "description", "created_at"}
        assert d["id"] is not None
        assert d["name"] == "Python"
        assert d["category"] == "编程"
        assert d["description"] == "Python编程语言"
        assert d["created_at"] is not None

    def test_nullable_fields_are_none(self):
        now = datetime.now(UTC)
        catalog = SkillCatalog(
            name="Docker",
            category=None,
            description=None,
            created_at=now,
        )
        persisted = _add_and_refresh(catalog)
        d = persisted.to_dict()

        assert d["category"] is None
        assert d["description"] is None


# ==============================================================
# AgentMemory
# ==============================================================


class TestAgentMemory:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        expires = datetime(2027, 1, 1, 0, 0, 0)
        mem = AgentMemory(
            session_id="sess-001",
            user_tag="user-42",
            memory_type="fact",
            category="偏好",
            subject="工作时间",
            content="用户偏好上午开会",
            source="chat",
            importance=5,
            expires_at=expires,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        persisted = _add_and_refresh(mem)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "session_id",
            "user_tag",
            "memory_type",
            "category",
            "subject",
            "content",
            "source",
            "importance",
            "expires_at",
            "is_active",
            "created_at",
            "updated_at",
        }
        assert d["id"] is not None
        assert d["session_id"] == "sess-001"
        assert d["user_tag"] == "user-42"
        assert d["memory_type"] == "fact"
        assert d["category"] == "偏好"
        assert d["subject"] == "工作时间"
        assert d["content"] == "用户偏好上午开会"
        assert d["source"] == "chat"
        assert d["importance"] == 5
        assert d["expires_at"] == expires
        assert d["is_active"] is True
        assert d["created_at"] is not None
        assert d["updated_at"] is not None

    def test_default_values_and_nullable_fields(self):
        now = datetime.now(UTC)
        mem = AgentMemory(
            session_id="sess-002",
            user_tag=None,
            memory_type="note",
            category="项目",
            subject="进度",
            content="项目即将完成",
            source="tool",
            expires_at=None,
            created_at=now,
            updated_at=now,
        )
        persisted = _add_and_refresh(mem)
        d = persisted.to_dict()

        # importance defaults to 3, is_active defaults to True
        assert d["importance"] == 3
        assert d["is_active"] is True
        # nullable fields
        assert d["user_tag"] is None
        assert d["expires_at"] is None


# ==============================================================
# MemoryReminder
# ==============================================================


class TestMemoryReminder:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        trigger = datetime(2026, 6, 1, 9, 0, 0)
        reminder = MemoryReminder(
            memory_id=1,
            reminder_type="one_time",
            trigger_at=trigger,
            recurrence_rule="FREQ=DAILY",
            triggered=True,
            trigger_count=2,
            created_at=now,
        )
        persisted = _add_and_refresh(reminder)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "memory_id",
            "reminder_type",
            "trigger_at",
            "recurrence_rule",
            "triggered",
            "trigger_count",
            "created_at",
        }
        assert d["id"] is not None
        assert d["memory_id"] == 1
        assert d["reminder_type"] == "one_time"
        assert d["trigger_at"] == trigger
        assert d["recurrence_rule"] == "FREQ=DAILY"
        assert d["triggered"] is True
        assert d["trigger_count"] == 2
        assert d["created_at"] is not None

    def test_default_values_and_nullable_recurrence_rule(self):
        now = datetime.now(UTC)
        trigger = datetime(2026, 7, 1, 9, 0, 0)
        reminder = MemoryReminder(
            memory_id=2,
            reminder_type="recurring",
            trigger_at=trigger,
            recurrence_rule=None,
            created_at=now,
        )
        persisted = _add_and_refresh(reminder)
        d = persisted.to_dict()

        # triggered defaults to False, trigger_count defaults to 0
        assert d["triggered"] is False
        assert d["trigger_count"] == 0
        assert d["recurrence_rule"] is None


# ==============================================================
# ConversationMessage
# ==============================================================


class TestConversationMessage:
    def test_create_with_all_fields(self):
        now = datetime.now(UTC)
        msg = ConversationMessage(
            session_id="sess-100",
            role="assistant",
            content="你好，有什么可以帮助你？",
            tool_call_id="call-abc",
            tool_calls='[{"id":"call-abc","type":"function"}]',
            reasoning_content="思考过程...",
            created_at=now,
        )
        persisted = _add_and_refresh(msg)
        d = persisted.to_dict()

        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "id",
            "session_id",
            "role",
            "content",
            "tool_call_id",
            "tool_calls",
            "reasoning_content",
            "created_at",
        }
        assert d["id"] is not None
        assert d["session_id"] == "sess-100"
        assert d["role"] == "assistant"
        assert d["content"] == "你好，有什么可以帮助你？"
        assert d["tool_call_id"] == "call-abc"
        assert d["tool_calls"] == '[{"id":"call-abc","type":"function"}]'
        assert d["reasoning_content"] == "思考过程..."
        assert d["created_at"] is not None

    def test_nullable_fields_are_none(self):
        now = datetime.now(UTC)
        msg = ConversationMessage(
            session_id="sess-101",
            role="user",
            content=None,
            tool_call_id=None,
            tool_calls=None,
            reasoning_content=None,
            created_at=now,
        )
        persisted = _add_and_refresh(msg)
        d = persisted.to_dict()

        assert d["content"] is None
        assert d["tool_call_id"] is None
        assert d["tool_calls"] is None
        assert d["reasoning_content"] is None
