"""Attendance-related agent tools."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.schemas.attendance import (
    AttendanceRecordCreate,
    AttendanceRecordUpdate,
    LeaveRequestCreate,
    LeaveRequestUpdate,
    PayrollRecordCreate,
    PayrollRecordUpdate,
)
from app.services.attendance import attendance_record as attendance_record_service
from app.services.attendance import leave_request as leave_request_service
from app.services.attendance import payroll_record as payroll_record_service


class ListAttendanceRecordsInput(BaseModel):
    worker_id: int | None = None
    work_date: date | None = None
    status: str | None = None


class GetAttendanceRecordInput(BaseModel):
    attendance_record_id: int


class UpdateAttendanceRecordInput(AttendanceRecordUpdate):
    attendance_record_id: int


class DeleteAttendanceRecordInput(BaseModel):
    attendance_record_id: int


class ListLeaveRequestsInput(BaseModel):
    worker_id: int | None = None
    status: str | None = None
    leave_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class GetLeaveRequestInput(BaseModel):
    leave_request_id: int


class UpdateLeaveRequestInput(LeaveRequestUpdate):
    leave_request_id: int


class DeleteLeaveRequestInput(BaseModel):
    leave_request_id: int


class ListPayrollRecordsInput(BaseModel):
    worker_id: int | None = None
    pay_period: str | None = None
    status: str | None = None


class GetPayrollRecordInput(BaseModel):
    payroll_record_id: int


class UpdatePayrollRecordInput(PayrollRecordUpdate):
    payroll_record_id: int


class DeletePayrollRecordInput(BaseModel):
    payroll_record_id: int


def _create_attendance_record(**kwargs):
    return safe_call(attendance_record_service.create_attendance_record, AttendanceRecordCreate(**kwargs))


def _update_attendance_record(attendance_record_id: int, **kwargs):
    return safe_call(
        attendance_record_service.update_attendance_record,
        attendance_record_id,
        AttendanceRecordUpdate(**kwargs),
    )


def _create_leave_request(**kwargs):
    return safe_call(leave_request_service.create_leave_request, LeaveRequestCreate(**kwargs))


def _update_leave_request(leave_request_id: int, **kwargs):
    return safe_call(leave_request_service.update_leave_request, leave_request_id, LeaveRequestUpdate(**kwargs))


def _create_payroll_record(**kwargs):
    return safe_call(payroll_record_service.create_payroll_record, PayrollRecordCreate(**kwargs))


def _update_payroll_record(payroll_record_id: int, **kwargs):
    return safe_call(
        payroll_record_service.update_payroll_record,
        payroll_record_id,
        PayrollRecordUpdate(**kwargs),
    )


skill = AgentSkill(
    name="attendance",
    description="Manage attendance, leave, and payroll records.",
    applicability="Use for daily attendance checks, leave tracking, and payroll lookups.",
    keywords=("attendance", "leave", "payroll", "absence", "考勤", "请假", "薪资", "出勤"),
    tools=[
        AgentTool(
            name="list_attendance_records",
            description="List attendance records with optional worker, date, or status filters.",
            parameters=ListAttendanceRecordsInput.model_json_schema(),
            fn=lambda worker_id=None, work_date=None, status=None: safe_call(
                attendance_record_service.list_attendance_records,
                worker_id,
                work_date,
                status,
            ),
        ),
        AgentTool(
            name="get_attendance_record",
            description="Get one attendance record by ID.",
            parameters=GetAttendanceRecordInput.model_json_schema(),
            fn=lambda attendance_record_id: safe_call(
                attendance_record_service.get_attendance_record,
                attendance_record_id,
            ),
        ),
        AgentTool(
            name="create_attendance_record",
            description="Create a new attendance record.",
            parameters=AttendanceRecordCreate.model_json_schema(),
            fn=_create_attendance_record,
        ),
        AgentTool(
            name="update_attendance_record",
            description="Update an existing attendance record.",
            parameters=UpdateAttendanceRecordInput.model_json_schema(),
            fn=lambda attendance_record_id, **kwargs: _update_attendance_record(attendance_record_id, **kwargs),
        ),
        AgentTool(
            name="delete_attendance_record",
            description="Delete one attendance record by ID.",
            parameters=DeleteAttendanceRecordInput.model_json_schema(),
            fn=lambda attendance_record_id: safe_call(
                attendance_record_service.delete_attendance_record,
                attendance_record_id,
            ),
        ),
        AgentTool(
            name="list_leave_requests",
            description="List leave requests with optional worker, type, status, or date filters.",
            parameters=ListLeaveRequestsInput.model_json_schema(),
            fn=lambda worker_id=None, status=None, leave_type=None, start_date=None, end_date=None: safe_call(
                leave_request_service.list_leave_requests,
                worker_id,
                status,
                leave_type,
                start_date,
                end_date,
            ),
        ),
        AgentTool(
            name="get_leave_request",
            description="Get one leave request by ID.",
            parameters=GetLeaveRequestInput.model_json_schema(),
            fn=lambda leave_request_id: safe_call(leave_request_service.get_leave_request, leave_request_id),
        ),
        AgentTool(
            name="create_leave_request",
            description="Create a new leave request.",
            parameters=LeaveRequestCreate.model_json_schema(),
            fn=_create_leave_request,
        ),
        AgentTool(
            name="update_leave_request",
            description="Update an existing leave request.",
            parameters=UpdateLeaveRequestInput.model_json_schema(),
            fn=lambda leave_request_id, **kwargs: _update_leave_request(leave_request_id, **kwargs),
        ),
        AgentTool(
            name="delete_leave_request",
            description="Delete one leave request by ID.",
            parameters=DeleteLeaveRequestInput.model_json_schema(),
            fn=lambda leave_request_id: safe_call(leave_request_service.delete_leave_request, leave_request_id),
        ),
        AgentTool(
            name="list_payroll_records",
            description="List payroll records with optional worker, pay period, or status filters.",
            parameters=ListPayrollRecordsInput.model_json_schema(),
            fn=lambda worker_id=None, pay_period=None, status=None: safe_call(
                payroll_record_service.list_payroll_records,
                worker_id,
                pay_period,
                status,
            ),
        ),
        AgentTool(
            name="get_payroll_record",
            description="Get one payroll record by ID.",
            parameters=GetPayrollRecordInput.model_json_schema(),
            fn=lambda payroll_record_id: safe_call(payroll_record_service.get_payroll_record, payroll_record_id),
        ),
        AgentTool(
            name="create_payroll_record",
            description="Create a new payroll record.",
            parameters=PayrollRecordCreate.model_json_schema(),
            fn=_create_payroll_record,
        ),
        AgentTool(
            name="update_payroll_record",
            description="Update an existing payroll record.",
            parameters=UpdatePayrollRecordInput.model_json_schema(),
            fn=lambda payroll_record_id, **kwargs: _update_payroll_record(payroll_record_id, **kwargs),
        ),
        AgentTool(
            name="delete_payroll_record",
            description="Delete one payroll record by ID.",
            parameters=DeletePayrollRecordInput.model_json_schema(),
            fn=lambda payroll_record_id: safe_call(
                payroll_record_service.delete_payroll_record,
                payroll_record_id,
            ),
        ),
    ],
)

__all__ = ["skill"]
