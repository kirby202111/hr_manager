"""Attendance-related agent tools."""

from __future__ import annotations

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.services.attendance import attendance_record as attendance_service
from app.services.attendance import leave_request as leave_service
from app.services.attendance import payroll_record as payroll_service

skill = AgentSkill(
    name="attendance",
    description="Query attendance, leave, and payroll records.",
    applicability="Use for time tracking, leave history, attendance anomalies, and payroll status checks.",
    keywords=("attendance", "leave", "payroll", "考勤", "请假", "薪资", "工资"),
    tools=[
        AgentTool(
            name="list_attendance_records",
            description="List attendance records with optional worker, work_date, and status filters.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "work_date": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
            fn=lambda worker_id=None, work_date=None, status=None: safe_call(
                attendance_service.list_attendance_records,
                worker_id,
                work_date,
                status,
            ),
        ),
        AgentTool(
            name="list_leave_requests",
            description="List leave requests with optional worker, status, type, and date-range filters.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "status": {"type": "string"},
                    "leave_type": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                },
            },
            fn=lambda worker_id=None, status=None, leave_type=None, start_date=None, end_date=None: safe_call(
                leave_service.list_leave_requests,
                worker_id,
                status,
                leave_type,
                start_date,
                end_date,
            ),
        ),
        AgentTool(
            name="list_payroll_records",
            description="List payroll records with optional worker, pay period, and status filters.",
            parameters={
                "type": "object",
                "properties": {
                    "worker_id": {"type": "integer"},
                    "pay_period": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
            fn=lambda worker_id=None, pay_period=None, status=None: safe_call(
                payroll_service.list_payroll_records,
                worker_id,
                pay_period,
                status,
            ),
        ),
    ],
)

__all__ = ["skill"]
