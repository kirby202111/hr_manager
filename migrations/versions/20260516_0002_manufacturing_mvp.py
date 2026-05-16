"""manufacturing mvp schema

Revision ID: 20260516_0002
Revises: 20260515_0001
Create Date: 2026-05-16
"""
# ruff: noqa: E501

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260516_0002"
down_revision = "20260515_0001"
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "production_lines",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("supervisor_employee_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_production_lines_department_id", "production_lines", ["department_id"])
    op.create_table(
        "production_teams",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("line_id", sa.Integer(), nullable=False),
        sa.Column("leader_employee_id", sa.Integer(), nullable=True),
        sa.Column("shift_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_production_teams_line_id", "production_teams", ["line_id"])
    op.create_table(
        "workstations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("line_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("line_id", "code", name="uq_workstations_line_code"),
    )
    op.create_index("ix_workstations_line_id", "workstations", ["line_id"])
    op.create_table("workstation_required_skills", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("workstation_id", sa.Integer(), nullable=False), sa.Column("skill_id", sa.Integer(), nullable=False), sa.Column("required_proficiency", sa.String(length=20), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_workstation_required_skills_workstation_id", "workstation_required_skills", ["workstation_id"])
    op.create_table("workstation_required_certifications", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("workstation_id", sa.Integer(), nullable=False), sa.Column("certification_id", sa.Integer(), nullable=False), sa.Column("required", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_workstation_required_certifications_workstation_id", "workstation_required_certifications", ["workstation_id"])
    op.create_table("workstation_equipment_requirements", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("workstation_id", sa.Integer(), nullable=False), sa.Column("equipment_code", sa.String(length=100), nullable=False), sa.Column("required_authorization_level", sa.String(length=20), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_workstation_equipment_requirements_workstation_id", "workstation_equipment_requirements", ["workstation_id"])
    op.create_table("employee_team_assignments", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("employee_id", sa.Integer(), nullable=False), sa.Column("team_id", sa.Integer(), nullable=False), sa.Column("line_id", sa.Integer(), nullable=False), sa.Column("start_date", sa.Date(), nullable=False), sa.Column("end_date", sa.Date(), nullable=True), sa.Column("is_primary", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_employee_team_assignments_employee_id", "employee_team_assignments", ["employee_id"])
    op.create_table("employee_production_profiles", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("employee_id", sa.Integer(), nullable=False), sa.Column("worker_type", sa.String(length=30), nullable=False), sa.Column("production_status", sa.String(length=20), nullable=False), sa.Column("can_support_lines", sa.Text(), nullable=False), sa.Column("notes", sa.String(), nullable=True), *_timestamps(), sa.UniqueConstraint("employee_id", name="uq_employee_production_profiles_employee_id"))
    op.create_table("certifications", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("category", sa.String(length=30), nullable=False), sa.Column("required_training_hours", sa.Float(), nullable=False), sa.Column("validity_months", sa.Integer(), nullable=True), sa.Column("description", sa.String(), nullable=True), *_timestamps())
    op.create_table("employee_certifications", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("employee_id", sa.Integer(), nullable=False), sa.Column("certification_id", sa.Integer(), nullable=False), sa.Column("issued_at", sa.Date(), nullable=False), sa.Column("expires_at", sa.Date(), nullable=True), sa.Column("status", sa.String(length=20), nullable=False), sa.Column("evidence", sa.String(), nullable=True), *_timestamps())
    op.create_index("ix_employee_certifications_employee_id", "employee_certifications", ["employee_id"])
    op.create_table("equipment_authorizations", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("employee_id", sa.Integer(), nullable=False), sa.Column("equipment_code", sa.String(length=100), nullable=False), sa.Column("authorization_level", sa.String(length=20), nullable=False), sa.Column("issued_at", sa.Date(), nullable=False), sa.Column("expires_at", sa.Date(), nullable=True), sa.Column("status", sa.String(length=20), nullable=False), *_timestamps())
    op.create_index("ix_equipment_authorizations_employee_id", "equipment_authorizations", ["employee_id"])
    op.create_table("safety_trainings", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("title", sa.String(length=150), nullable=False), sa.Column("category", sa.String(length=30), nullable=False), sa.Column("required_for_certification_id", sa.Integer(), nullable=True), sa.Column("validity_months", sa.Integer(), nullable=True), sa.Column("description", sa.String(), nullable=True), *_timestamps())
    op.create_table("employee_safety_records", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("employee_id", sa.Integer(), nullable=False), sa.Column("training_id", sa.Integer(), nullable=False), sa.Column("completed_at", sa.Date(), nullable=False), sa.Column("score", sa.Float(), nullable=True), sa.Column("expires_at", sa.Date(), nullable=True), sa.Column("status", sa.String(length=20), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_employee_safety_records_employee_id", "employee_safety_records", ["employee_id"])
    op.create_table("production_orders", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("order_no", sa.String(length=100), nullable=False), sa.Column("product_name", sa.String(length=150), nullable=False), sa.Column("line_id", sa.Integer(), nullable=True), sa.Column("planned_quantity", sa.Integer(), nullable=False), sa.Column("planned_start_date", sa.Date(), nullable=True), sa.Column("planned_end_date", sa.Date(), nullable=True), sa.Column("status", sa.String(length=20), nullable=False), sa.Column("priority", sa.String(length=20), nullable=False), sa.Column("description", sa.String(), nullable=True), *_timestamps(), sa.UniqueConstraint("order_no", name="uq_production_orders_order_no"))
    op.create_table("production_order_operations", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("order_id", sa.Integer(), nullable=False), sa.Column("workstation_id", sa.Integer(), nullable=False), sa.Column("process_code", sa.String(length=100), nullable=False), sa.Column("sequence", sa.Integer(), nullable=False), sa.Column("planned_hours", sa.Float(), nullable=True), sa.Column("required_headcount", sa.Integer(), nullable=False), sa.Column("status", sa.String(length=20), nullable=False), *_timestamps())
    op.create_index("ix_production_order_operations_order_id", "production_order_operations", ["order_id"])
    op.create_table("shift_definitions", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("code", sa.String(length=50), nullable=False), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("start_time", sa.Time(), nullable=False), sa.Column("end_time", sa.Time(), nullable=False), sa.Column("shift_type", sa.String(length=20), nullable=False), sa.Column("allowance_rate", sa.Float(), nullable=False), *_timestamps(), sa.UniqueConstraint("code", name="uq_shift_definitions_code"))
    op.create_table("production_shift_plans", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("order_id", sa.Integer(), nullable=True), sa.Column("line_id", sa.Integer(), nullable=False), sa.Column("shift_id", sa.Integer(), nullable=False), sa.Column("work_date", sa.Date(), nullable=False), sa.Column("required_headcount", sa.Integer(), nullable=False), sa.Column("status", sa.String(length=20), nullable=False), sa.Column("created_by", sa.String(length=100), nullable=True), *_timestamps())
    op.create_index("ix_production_shift_plans_line_date_shift", "production_shift_plans", ["line_id", "work_date", "shift_id"])
    op.create_table("employee_shift_assignments", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("plan_id", sa.Integer(), nullable=False), sa.Column("employee_id", sa.Integer(), nullable=False), sa.Column("workstation_id", sa.Integer(), nullable=False), sa.Column("assignment_type", sa.String(length=20), nullable=False), sa.Column("status", sa.String(length=20), nullable=False), *_timestamps())
    op.create_index("ix_employee_shift_assignments_plan_employee", "employee_shift_assignments", ["plan_id", "employee_id"])
    op.create_table("production_risk_signals", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("order_id", sa.Integer(), nullable=True), sa.Column("employee_id", sa.Integer(), nullable=True), sa.Column("line_id", sa.Integer(), nullable=True), sa.Column("workstation_id", sa.Integer(), nullable=True), sa.Column("shift_assignment_id", sa.Integer(), nullable=True), sa.Column("signal_type", sa.String(length=60), nullable=False), sa.Column("severity", sa.String(length=20), nullable=False), sa.Column("evidence", sa.Text(), nullable=False), sa.Column("status", sa.String(length=20), nullable=False), sa.Column("detected_by", sa.String(length=20), nullable=False), *_timestamps())
    op.create_index("ix_production_risk_signals_status", "production_risk_signals", ["status"])
    op.create_table("production_risk_reviews", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("risk_signal_id", sa.Integer(), nullable=False), sa.Column("reviewer", sa.String(length=100), nullable=False), sa.Column("conclusion", sa.String(), nullable=False), sa.Column("action_suggestion", sa.String(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_production_risk_reviews_risk_signal_id", "production_risk_reviews", ["risk_signal_id"])


def downgrade() -> None:
    for table_name in [
        "production_risk_reviews",
        "production_risk_signals",
        "employee_shift_assignments",
        "production_shift_plans",
        "shift_definitions",
        "production_order_operations",
        "production_orders",
        "employee_safety_records",
        "safety_trainings",
        "equipment_authorizations",
        "employee_certifications",
        "certifications",
        "employee_production_profiles",
        "employee_team_assignments",
        "workstation_equipment_requirements",
        "workstation_required_certifications",
        "workstation_required_skills",
        "workstations",
        "production_teams",
        "production_lines",
    ]:
        op.drop_table(table_name)
