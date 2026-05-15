"""baseline schema without foreign keys

Revision ID: 20260515_0001
Revises:
Create Date: 2026-05-15
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260515_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("manager", sa.String(), nullable=True),
        sa.UniqueConstraint("name", name="uq_departments_name"),
    )
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("salary", sa.Float(), nullable=False),
    )
    op.create_index("ix_employees_department_id", "employees", ["department_id"])
    op.create_table(
        "attendance",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("check_in", sa.Time(), nullable=False),
        sa.Column("check_out", sa.Time(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("work_hours", sa.Float(), nullable=True),
        sa.UniqueConstraint("employee_id", "date", name="uq_attendance_employee_date"),
    )
    op.create_index("ix_attendance_employee_date", "attendance", ["employee_id", "date"])
    op.create_table(
        "leaves",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("leave_type", sa.String(), nullable=False),
        sa.Column("leave_type_name", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("days", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("approver", sa.String(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_leaves_employee_status_dates", "leaves", ["employee_id", "status", "start_date", "end_date"])
    op.create_table(
        "payrolls",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.String(), nullable=False),
        sa.Column("base_salary", sa.Float(), nullable=False),
        sa.Column("bonuses", sa.Float(), nullable=False, server_default="0"),
        sa.Column("deductions", sa.Float(), nullable=False, server_default="0"),
        sa.Column("net_salary", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("employee_id", "month", name="uq_payrolls_employee_month"),
    )
    op.create_index("ix_payrolls_employee_month", "payrolls", ["employee_id", "month"])
    op.create_table(
        "skill_catalogs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "employee_skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("skill_name", sa.String(length=100), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=True),
        sa.Column("proficiency_level", sa.String(length=20), nullable=False),
        sa.Column("years_of_experience", sa.Float(), nullable=True),
        sa.Column("certification", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("employee_id", "skill_name", name="uq_employee_skills_employee_skill_name"),
    )
    op.create_index("ix_employee_skills_employee_id", "employee_skills", ["employee_id"])
    op.create_index("ix_employee_skills_skill_id", "employee_skills", ["skill_id"])
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_table(
        "project_skill_requirements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("required_proficiency", sa.String(length=20), nullable=False),
        sa.Column("person_days", sa.Float(), nullable=False),
        sa.Column("headcount", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("project_id", "skill_id", name="uq_project_requirements_project_skill"),
    )
    op.create_index("ix_project_requirements_project_id", "project_skill_requirements", ["project_id"])
    op.create_index("ix_project_requirements_skill_id", "project_skill_requirements", ["skill_id"])
    op.create_table(
        "project_members",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("assigned_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("project_id", "employee_id", name="uq_project_members_project_employee"),
    )
    op.create_index("ix_project_members_project_id", "project_members", ["project_id"])
    op.create_index("ix_project_members_employee_id", "project_members", ["employee_id"])
    op.create_table(
        "project_timesheets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("requirement_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("hours", sa.Float(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_project_timesheets_project_employee_date",
        "project_timesheets",
        ["project_id", "employee_id", "date"],
    )
    op.create_index("ix_project_timesheets_requirement_id", "project_timesheets", ["requirement_id"])
    op.create_table(
        "agent_memories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(length=100), nullable=False),
        sa.Column("user_tag", sa.String(length=100), nullable=True),
        sa.Column("memory_type", sa.String(length=30), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("subject", sa.String(length=200), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("importance", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "memory_reminders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("memory_id", sa.Integer(), nullable=False),
        sa.Column("reminder_type", sa.String(length=20), nullable=False),
        sa.Column("trigger_at", sa.DateTime(), nullable=False),
        sa.Column("recurrence_rule", sa.String(length=100), nullable=True),
        sa.Column("triggered", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("trigger_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(length=100), nullable=False),
        sa.Column("user_tag", sa.String(length=100), nullable=False, server_default="default"),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column("tool_call_id", sa.String(length=100), nullable=True),
        sa.Column("tool_calls", sa.String(), nullable=True),
        sa.Column("reasoning_content", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_conversation_messages_session_id", "conversation_messages", ["session_id"])
    op.create_index("ix_conversation_messages_user_tag", "conversation_messages", ["user_tag"])


def downgrade() -> None:
    for table_name in [
        "conversation_messages",
        "memory_reminders",
        "agent_memories",
        "project_timesheets",
        "project_members",
        "project_skill_requirements",
        "projects",
        "employee_skills",
        "skill_catalogs",
        "payrolls",
        "leaves",
        "attendance",
        "employees",
        "departments",
    ]:
        op.drop_table(table_name)
