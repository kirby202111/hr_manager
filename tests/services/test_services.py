"""Comprehensive pytest unit tests for all service modules."""

from datetime import UTC, date, datetime, time, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.agent_memory import MemoryCreate, MemoryUpdate, ReminderCreate
from app.schemas.attendance import AttendanceCheckIn, AttendanceCheckOut
from app.schemas.org_unit import DepartmentCreate, DepartmentUpdate
from app.schemas.worker import WorkerCreate, WorkerUpdate
from app.schemas.worker_skill import EmployeeSkillCreate, EmployeeSkillUpdate
from app.schemas.leave import LeaveApproval, LeaveCreate, LeaveUpdate
from app.schemas.payroll import PayrollCreate, PayrollUpdate
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberCreate,
    ProjectMemberUpdate,
    ProjectSkillRequirementCreate,
    ProjectSkillRequirementUpdate,
    ProjectTimesheetCreate,
    ProjectTimesheetUpdate,
    ProjectUpdate,
)
from app.schemas.skill_definition import SkillCatalogCreate, SkillCatalogUpdate
from app.services import (
    agent_memory,
    attendance,
    knowledge_base,
    leave,
    org_unit as department,
    payroll,
    project,
    skill_definition as skill_catalog,
    worker as employee,
    worker_skill as employee_skill,
)

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 1. Worker Service
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestWorkerService:
    def test_list_workers_empty(self):
        result = employee.list_workers()
        assert result.total == 0
        assert result.employees == []

    def test_list_workers_with_data(self, sample_employee):
        result = employee.list_workers()
        assert result.total == 1
        assert result.employees[0].name == "寮犱笁"
        assert result.employees[0].department_name == "宸ョ▼閮?

    def test_get_worker(self, sample_employee):
        result = employee.get_worker(sample_employee["id"])
        assert result.id == sample_employee["id"]
        assert result.name == "寮犱笁"
        assert result.department_name == "宸ョ▼閮?

    def test_get_employee_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            employee.get_worker(9999)
        assert exc_info.value.status_code == 404
        assert "9999 not found" in exc_info.value.detail

    def test_create_worker(self, sample_department):
        emp_in = WorkerCreate(name="鏉庡洓", department_id=sample_department["id"], salary=12000.0)
        result = employee.create_worker(emp_in)
        assert result.name == "鏉庡洓"
        assert result.department_name == "宸ョ▼閮?
        assert result.salary == 12000.0

    def test_create_worker_no_department(self):
        emp_in = WorkerCreate(name="鐜嬩簲", salary=10000.0)
        result = employee.create_worker(emp_in)
        assert result.name == "鐜嬩簲"
        assert result.department_id is None
        assert result.department_name is None

    def test_create_worker_invalid_department(self):
        emp_in = WorkerCreate(name="璧靛叚", department_id=9999, salary=10000.0)
        with pytest.raises(HTTPException) as exc_info:
            employee.create_worker(emp_in)
        assert exc_info.value.status_code == 400
        assert "9999 not found" in exc_info.value.detail

    def test_update_worker(self, sample_employee, sample_department):
        emp_in = WorkerUpdate(name="寮犱笁涓?)
        result = employee.update_worker(sample_employee["id"], emp_in)
        assert result.name == "寮犱笁涓?

    def test_update_worker_not_found(self):
        emp_in = WorkerUpdate(name="Nobody")
        with pytest.raises(HTTPException) as exc_info:
            employee.update_worker(9999, emp_in)
        assert exc_info.value.status_code == 404

    def test_update_worker_invalid_department(self, sample_employee):
        emp_in = WorkerUpdate(department_id=9999)
        with pytest.raises(HTTPException) as exc_info:
            employee.update_worker(sample_employee["id"], emp_in)
        assert exc_info.value.status_code == 400
        assert "9999 not found" in exc_info.value.detail

    def test_delete_worker(self, sample_employee):
        result = employee.delete_worker(sample_employee["id"])
        assert "deleted" in result["message"]
        with pytest.raises(HTTPException) as exc_info:
            employee.get_worker(sample_employee["id"])
        assert exc_info.value.status_code == 404

    def test_delete_worker_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            employee.delete_worker(9999)
        assert exc_info.value.status_code == 404


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 2. Department Service
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestDepartmentService:
    def test_list_departments_empty(self):
        result = department.list_departments()
        assert result.total == 0
        assert result.departments == []

    def test_list_departments_with_employee_count(self, sample_department, sample_employee):
        result = department.list_departments()
        assert result.total == 1
        assert result.departments[0].employee_count == 1

    def test_get_department(self, sample_department):
        result = department.get_department(sample_department["id"])
        assert result.name == "宸ョ▼閮?
        assert result.employee_count == 0

    def test_get_department_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            department.get_department(9999)
        assert exc_info.value.status_code == 404
        assert "9999 not found" in exc_info.value.detail

    def test_create_department(self):
        dept_in = DepartmentCreate(name="甯傚満閮?, description="甯傚満钀ラ攢", manager="鏉庣粡鐞?)
        result = department.create_department(dept_in)
        assert result.name == "甯傚満閮?
        assert result.employee_count == 0

    def test_create_department_duplicate_name(self, sample_department):
        dept_in = DepartmentCreate(name="宸ョ▼閮?)
        with pytest.raises(HTTPException) as exc_info:
            department.create_department(dept_in)
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    def test_update_department(self, sample_department):
        dept_in = DepartmentUpdate(description="鐮斿彂閮ㄩ棬V2")
        result = department.update_department(sample_department["id"], dept_in)
        assert result.description == "鐮斿彂閮ㄩ棬V2"

    def test_update_department_not_found(self):
        dept_in = DepartmentUpdate(name="涓嶅瓨鍦?)
        with pytest.raises(HTTPException) as exc_info:
            department.update_department(9999, dept_in)
        assert exc_info.value.status_code == 404

    def test_update_department_duplicate_name(self, sample_department):
        # Create another department first
        dept_in = DepartmentCreate(name="甯傚満閮?)
        department.create_department(dept_in)
        # Try to rename 宸ョ▼閮?to 甯傚満閮?
        dup_in = DepartmentUpdate(name="甯傚満閮?)
        with pytest.raises(HTTPException) as exc_info:
            department.update_department(sample_department["id"], dup_in)
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    def test_update_department_same_name_ok(self, sample_department):
        dept_in = DepartmentUpdate(name="宸ョ▼閮?, description="鏇存柊鎻忚堪")
        result = department.update_department(sample_department["id"], dept_in)
        assert result.description == "鏇存柊鎻忚堪"

    def test_delete_department(self, sample_department):
        result = department.delete_department(sample_department["id"])
        assert "deleted" in result["message"]

    def test_delete_department_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            department.delete_department(9999)
        assert exc_info.value.status_code == 404

    def test_delete_department_with_employees(self, sample_department, sample_employee):
        with pytest.raises(HTTPException) as exc_info:
            department.delete_department(sample_department["id"])
        assert exc_info.value.status_code == 400
        assert "Cannot delete" in exc_info.value.detail

    def test_get_department_workers(self, sample_department, sample_employee):
        result = department.get_department_workers(sample_department["id"])
        assert len(result) == 1
        assert result[0].name == "寮犱笁"

    def test_get_department_workers_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            department.get_department_workers(9999)
        assert exc_info.value.status_code == 404


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 3. Attendance Service
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestAttendanceService:
    def test_check_in(self, sample_employee):
        data = AttendanceCheckIn(
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            check_in=time(8, 30),
        )
        result = attendance.check_in(data)
        assert result.employee_id == sample_employee["id"]
        assert result.status == "normal"
        assert result.employee_name == "寮犱笁"
        assert result.work_hours is None

    def test_check_in_late(self, sample_employee):
        data = AttendanceCheckIn(
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            check_in=time(9, 30),
        )
        result = attendance.check_in(data)
        assert result.status == "late"

    def test_check_in_employee_not_found(self):
        data = AttendanceCheckIn(
            employee_id=9999,
            date=date(2026, 5, 10),
            check_in=time(8, 30),
        )
        with pytest.raises(HTTPException) as exc_info:
            attendance.check_in(data)
        assert exc_info.value.status_code == 404

    def test_check_in_duplicate(self, sample_employee):
        data = AttendanceCheckIn(
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            check_in=time(8, 30),
        )
        attendance.check_in(data)
        with pytest.raises(HTTPException) as exc_info:
            attendance.check_in(data)
        assert exc_info.value.status_code == 400
        assert "already checked in" in exc_info.value.detail

    def test_check_out(self, sample_employee):
        data_in = AttendanceCheckIn(
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            check_in=time(8, 30),
        )
        record = attendance.check_in(data_in)
        data_out = AttendanceCheckOut(check_out=time(18, 0))
        result = attendance.check_out(record.id, data_out)
        assert result.check_out == time(18, 0)
        assert result.work_hours == 9.5
        assert result.status == "normal"

    def test_check_out_early_leave(self, sample_employee):
        data_in = AttendanceCheckIn(
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            check_in=time(8, 30),
        )
        record = attendance.check_in(data_in)
        data_out = AttendanceCheckOut(check_out=time(17, 0))
        result = attendance.check_out(record.id, data_out)
        assert result.status == "early_leave"
        assert result.work_hours == 8.5

    def test_check_out_not_found(self):
        data_out = AttendanceCheckOut(check_out=time(18, 0))
        with pytest.raises(HTTPException) as exc_info:
            attendance.check_out(9999, data_out)
        assert exc_info.value.status_code == 404

    def test_check_out_already_checked_out(self, sample_attendance):
        # sample_attendance has no check_out, but let's add one
        data_out = AttendanceCheckOut(check_out=time(18, 0))
        attendance.check_out(sample_attendance["id"], data_out)
        # Now try again
        data_out2 = AttendanceCheckOut(check_out=time(19, 0))
        with pytest.raises(HTTPException) as exc_info:
            attendance.check_out(sample_attendance["id"], data_out2)
        assert exc_info.value.status_code == 400
        assert "Already checked out" in exc_info.value.detail

    def test_list_attendance(self, sample_attendance):
        result = attendance.list_attendance()
        assert result.total == 1

    def test_get_attendance(self, sample_attendance):
        result = attendance.get_attendance(sample_attendance["id"])
        assert result.id == sample_attendance["id"]
        assert result.employee_name == "寮犱笁"

    def test_get_attendance_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            attendance.get_attendance(9999)
        assert exc_info.value.status_code == 404

    def test_get_employee_attendance(self, sample_employee, sample_attendance):
        result = attendance.get_employee_attendance(sample_employee["id"])
        assert len(result) == 1

    def test_get_employee_attendance_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            attendance.get_employee_attendance(9999)
        assert exc_info.value.status_code == 404

    def test_get_employee_stats(self, sample_employee):
        # Create two attendance records
        attendance.check_in(
            AttendanceCheckIn(
                employee_id=sample_employee["id"],
                date=date(2026, 5, 1),
                check_in=time(8, 30),
            )
        )
        attendance.check_in(
            AttendanceCheckIn(
                employee_id=sample_employee["id"],
                date=date(2026, 5, 2),
                check_in=time(9, 30),
            )
        )
        result = attendance.get_employee_stats(sample_employee["id"], date(2026, 5, 1), date(2026, 5, 3))
        assert result.total_work_days == 3
        assert result.actual_work_days == 2
        assert result.normal_days == 1
        assert result.late_days == 1
        assert result.absent_days == 1

    def test_get_employee_stats_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            attendance.get_employee_stats(9999, date(2026, 5, 1), date(2026, 5, 3))
        assert exc_info.value.status_code == 404

    def test_calculate_work_hours(self):
        hours = attendance._calculate_work_hours(time(8, 30), time(18, 0))
        assert hours == 9.5

    def test_calculate_work_hours_short(self):
        hours = attendance._calculate_work_hours(time(9, 0), time(10, 0))
        assert hours == 1.0


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 4. Leave Service
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestLeaveService:
    def test_create_leave(self, sample_employee):
        data = LeaveCreate(
            employee_id=sample_employee["id"],
            leave_type="annual",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 3),
            reason="浼戝亣",
        )
        result = leave.create_leave(data)
        assert result.employee_name == "寮犱笁"
        assert result.leave_type == "annual"
        assert result.leave_type_name == "骞村亣"
        assert result.days == 3
        assert result.status == "pending"

    def test_create_leave_employee_not_found(self):
        data = LeaveCreate(
            employee_id=9999,
            leave_type="annual",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 3),
        )
        with pytest.raises(HTTPException) as exc_info:
            leave.create_leave(data)
        assert exc_info.value.status_code == 404

    def test_create_leave_end_before_start(self, sample_employee):
        data = LeaveCreate(
            employee_id=sample_employee["id"],
            leave_type="annual",
            start_date=date(2026, 6, 5),
            end_date=date(2026, 6, 3),
        )
        with pytest.raises(HTTPException) as exc_info:
            leave.create_leave(data)
        assert exc_info.value.status_code == 400
        assert "end_date must be >= start_date" in exc_info.value.detail

    def test_create_leave_invalid_type(self, sample_employee):
        data = LeaveCreate(
            employee_id=sample_employee["id"],
            leave_type="invalid_type",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 3),
        )
        with pytest.raises(HTTPException) as exc_info:
            leave.create_leave(data)
        assert exc_info.value.status_code == 400
        assert "Invalid leave_type" in exc_info.value.detail

    def test_create_leave_date_overlap(self, sample_employee):
        # Create an approved leave first
        data1 = LeaveCreate(
            employee_id=sample_employee["id"],
            leave_type="annual",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
        )
        leave1 = leave.create_leave(data1)
        # Approve it
        approval = LeaveApproval(approver="缁忕悊")
        leave.approve_leave(leave1.id, approval)
        # Try to create overlapping leave
        data2 = LeaveCreate(
            employee_id=sample_employee["id"],
            leave_type="sick",
            start_date=date(2026, 6, 3),
            end_date=date(2026, 6, 7),
        )
        with pytest.raises(HTTPException) as exc_info:
            leave.create_leave(data2)
        assert exc_info.value.status_code == 400
        assert "overlap" in exc_info.value.detail

    def test_create_leave_insufficient_balance(self, sample_employee):
        # Annual balance is 10 days. Use 8 first, then try 3 more
        data1 = LeaveCreate(
            employee_id=sample_employee["id"],
            leave_type="annual",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 8),
        )
        leave1 = leave.create_leave(data1)
        approval = LeaveApproval(approver="缁忕悊")
        leave.approve_leave(leave1.id, approval)
        # Now try 3 more annual (only 2 remaining)
        data2 = LeaveCreate(
            employee_id=sample_employee["id"],
            leave_type="annual",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 3),
        )
        with pytest.raises(HTTPException) as exc_info:
            leave.create_leave(data2)
        assert exc_info.value.status_code == 400
        assert "Insufficient" in exc_info.value.detail

    def test_list_leaves(self, sample_leave):
        result = leave.list_leaves()
        assert result.total == 1

    def test_get_leave(self, sample_leave):
        result = leave.get_leave(sample_leave["id"])
        assert result.id == sample_leave["id"]

    def test_get_leave_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            leave.get_leave(9999)
        assert exc_info.value.status_code == 404

    def test_update_leave(self, sample_leave):
        data = LeaveUpdate(end_date=date(2026, 5, 14))
        result = leave.update_leave(sample_leave["id"], data)
        assert result.days == 5  # May 10-14 inclusive

    def test_update_leave_not_found(self):
        data = LeaveUpdate(reason="test")
        with pytest.raises(HTTPException) as exc_info:
            leave.update_leave(9999, data)
        assert exc_info.value.status_code == 404

    def test_update_leave_not_pending(self, sample_leave):
        approval = LeaveApproval(approver="缁忕悊")
        leave.approve_leave(sample_leave["id"], approval)
        data = LeaveUpdate(reason="update after approval")
        with pytest.raises(HTTPException) as exc_info:
            leave.update_leave(sample_leave["id"], data)
        assert exc_info.value.status_code == 400
        assert "Only pending" in exc_info.value.detail

    def test_update_leave_end_before_start(self, sample_leave):
        data = LeaveUpdate(end_date=date(2026, 5, 8))
        with pytest.raises(HTTPException) as exc_info:
            leave.update_leave(sample_leave["id"], data)
        assert exc_info.value.status_code == 400
        assert "end_date must be >= start_date" in exc_info.value.detail

    def test_approve_leave(self, sample_leave):
        approval = LeaveApproval(approver="寮犵粡鐞?, comment="鍚屾剰")
        result = leave.approve_leave(sample_leave["id"], approval)
        assert result.status == "approved"
        assert result.approver == "寮犵粡鐞?

    def test_approve_leave_not_found(self):
        approval = LeaveApproval(approver="缁忕悊")
        with pytest.raises(HTTPException) as exc_info:
            leave.approve_leave(9999, approval)
        assert exc_info.value.status_code == 404

    def test_approve_leave_not_pending(self, sample_leave):
        approval = LeaveApproval(approver="缁忕悊")
        leave.approve_leave(sample_leave["id"], approval)
        with pytest.raises(HTTPException) as exc_info:
            leave.approve_leave(sample_leave["id"], approval)
        assert exc_info.value.status_code == 400
        assert "Only pending" in exc_info.value.detail

    def test_reject_leave(self, sample_leave):
        approval = LeaveApproval(approver="寮犵粡鐞?)
        result = leave.reject_leave(sample_leave["id"], approval)
        assert result.status == "rejected"

    def test_reject_leave_not_found(self):
        approval = LeaveApproval(approver="缁忕悊")
        with pytest.raises(HTTPException) as exc_info:
            leave.reject_leave(9999, approval)
        assert exc_info.value.status_code == 404

    def test_reject_leave_not_pending(self, sample_leave):
        approval = LeaveApproval(approver="缁忕悊")
        leave.approve_leave(sample_leave["id"], approval)
        with pytest.raises(HTTPException) as exc_info:
            leave.reject_leave(sample_leave["id"], approval)
        assert exc_info.value.status_code == 400

    def test_cancel_leave(self, sample_leave):
        result = leave.cancel_leave(sample_leave["id"])
        assert "cancelled" in result["message"]

    def test_cancel_leave_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            leave.cancel_leave(9999)
        assert exc_info.value.status_code == 404

    def test_cancel_leave_not_pending(self, sample_leave):
        approval = LeaveApproval(approver="缁忕悊")
        leave.approve_leave(sample_leave["id"], approval)
        with pytest.raises(HTTPException) as exc_info:
            leave.cancel_leave(sample_leave["id"])
        assert exc_info.value.status_code == 400

    def test_get_leave_balance(self, sample_employee):
        result = leave.get_leave_balance(sample_employee["id"])
        assert result.annual_total == 10
        assert result.annual_remaining == 10
        assert result.sick_total == 15
        assert result.personal_total == 5

    def test_get_leave_balance_after_usage(self, sample_employee):
        data = LeaveCreate(
            employee_id=sample_employee["id"],
            leave_type="annual",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 3),
        )
        leave1 = leave.create_leave(data)
        approval = LeaveApproval(approver="缁忕悊")
        leave.approve_leave(leave1.id, approval)
        result = leave.get_leave_balance(sample_employee["id"])
        assert result.annual_used == 3
        assert result.annual_remaining == 7

    def test_get_leave_balance_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            leave.get_leave_balance(9999)
        assert exc_info.value.status_code == 404

    def test_calculate_days(self):
        days = leave._calculate_days(date(2026, 5, 10), date(2026, 5, 12))
        assert days == 3

    def test_other_leave_type_no_balance_check(self, sample_employee):
        data = LeaveCreate(
            employee_id=sample_employee["id"],
            leave_type="other",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 20),
        )
        result = leave.create_leave(data)
        assert result.leave_type == "other"
        assert result.leave_type_name == "鍏朵粬"


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 5. Payroll Service
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestPayrollService:
    def test_create_payroll(self, sample_employee):
        data = PayrollCreate(
            employee_id=sample_employee["id"],
            month="2026-05",
            base_salary=15000.0,
            bonuses=1000.0,
            deductions=500.0,
        )
        result = payroll.create_payroll(data)
        assert result.employee_name == "寮犱笁"
        assert result.net_salary == 15500.0  # 15000 + 1000 - 500
        assert result.status == "draft"

    def test_create_payroll_employee_not_found(self):
        data = PayrollCreate(
            employee_id=9999,
            month="2026-05",
            base_salary=10000.0,
        )
        with pytest.raises(HTTPException) as exc_info:
            payroll.create_payroll(data)
        assert exc_info.value.status_code == 404

    def test_create_payroll_invalid_month_format(self, sample_employee):
        data = PayrollCreate(
            employee_id=sample_employee["id"],
            month="2026/05",
            base_salary=10000.0,
        )
        with pytest.raises(HTTPException) as exc_info:
            payroll.create_payroll(data)
        assert exc_info.value.status_code == 400
        assert "YYYY-MM" in exc_info.value.detail

    def test_create_payroll_duplicate(self, sample_employee):
        data = PayrollCreate(
            employee_id=sample_employee["id"],
            month="2026-05",
            base_salary=15000.0,
        )
        payroll.create_payroll(data)
        with pytest.raises(HTTPException) as exc_info:
            payroll.create_payroll(data)
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    def test_generate_monthly_payroll(self, sample_employee):
        results = payroll.generate_monthly_payroll("2026-06")
        assert len(results) == 1
        assert results[0].employee_id == sample_employee["id"]
        assert results[0].status == "draft"

    def test_generate_monthly_payroll_skips_existing(self, sample_payroll):
        results = payroll.generate_monthly_payroll("2026-05")
        # sample_payroll already exists for 2026-05
        assert len(results) == 0

    def test_list_payrolls(self, sample_payroll):
        result = payroll.list_payrolls()
        assert result.total == 1

    def test_get_payroll(self, sample_payroll):
        result = payroll.get_payroll(sample_payroll["id"])
        assert result.id == sample_payroll["id"]

    def test_get_payroll_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            payroll.get_payroll(9999)
        assert exc_info.value.status_code == 404

    def test_update_payroll(self, sample_payroll):
        data = PayrollUpdate(bonuses=2000.0, deductions=1000.0)
        result = payroll.update_payroll(sample_payroll["id"], data)
        assert result.bonuses == 2000.0
        assert result.net_salary == 16000.0  # 15000 + 2000 - 1000

    def test_update_payroll_not_found(self):
        data = PayrollUpdate(bonuses=100.0)
        with pytest.raises(HTTPException) as exc_info:
            payroll.update_payroll(9999, data)
        assert exc_info.value.status_code == 404

    def test_update_payroll_not_draft(self, sample_payroll):
        payroll.pay_payroll(sample_payroll["id"])
        data = PayrollUpdate(bonuses=100.0)
        with pytest.raises(HTTPException) as exc_info:
            payroll.update_payroll(sample_payroll["id"], data)
        assert exc_info.value.status_code == 400
        assert "Only draft" in exc_info.value.detail

    def test_pay_payroll(self, sample_payroll):
        result = payroll.pay_payroll(sample_payroll["id"])
        assert result.status == "paid"
        assert result.payment_date == date.today()

    def test_pay_payroll_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            payroll.pay_payroll(9999)
        assert exc_info.value.status_code == 404

    def test_pay_payroll_not_draft(self, sample_payroll):
        payroll.pay_payroll(sample_payroll["id"])
        with pytest.raises(HTTPException) as exc_info:
            payroll.pay_payroll(sample_payroll["id"])
        assert exc_info.value.status_code == 400
        assert "Only draft" in exc_info.value.detail

    def test_get_employee_payrolls(self, sample_employee, sample_payroll):
        result = payroll.get_employee_payrolls(sample_employee["id"])
        assert len(result) == 1

    def test_get_employee_payrolls_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            payroll.get_employee_payrolls(9999)
        assert exc_info.value.status_code == 404

    def test_get_payslip(self, sample_payroll):
        result = payroll.get_payslip(sample_payroll["id"])
        assert result.payroll.id == sample_payroll["id"]
        assert result.attendance_summary is not None
        assert result.leave_summary is not None

    def test_get_payslip_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            payroll.get_payslip(9999)
        assert exc_info.value.status_code == 404

    def test_calculate_net_salary(self):
        assert payroll._calculate_net_salary(10000, 500, 200) == 10300.0
        assert payroll._calculate_net_salary(10000, 0, 0) == 10000.0

    def test_parse_month(self):
        y, m = payroll._parse_month("2026-05")
        assert y == 2026
        assert m == 5

    def test_parse_month_invalid(self):
        with pytest.raises(HTTPException) as exc_info:
            payroll._parse_month("invalid")
        assert exc_info.value.status_code == 400


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 6. Worker Skill Service
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestEmployeeSkillService:
    def test_list_skills_empty(self):
        result = employee_skill.list_skills()
        assert result.total == 0

    def test_list_skills(self, sample_employee_skill):
        result = employee_skill.list_skills()
        assert result.total == 1
        assert result.skills[0].employee_name == "寮犱笁"
        assert result.skills[0].skill_category == "缂栫▼"

    def test_list_skills_by_employee(self, sample_employee, sample_employee_skill):
        result = employee_skill.list_skills_by_employee(sample_employee["id"])
        assert result.total == 1

    def test_list_skills_by_employee_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            employee_skill.list_skills_by_employee(9999)
        assert exc_info.value.status_code == 404

    def test_list_workers_by_skill(self, sample_employee_skill):
        result = employee_skill.list_workers_by_skill("Python")
        assert result.total == 1

    def test_get_skill(self, sample_employee_skill):
        result = employee_skill.get_skill(sample_employee_skill["id"])
        assert result.id == sample_employee_skill["id"]

    def test_get_skill_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            employee_skill.get_skill(9999)
        assert exc_info.value.status_code == 404

    def test_create_skill(self, sample_employee, sample_skill_catalog):
        skill_in = EmployeeSkillCreate(
            employee_id=sample_employee["id"],
            skill_name="Python",
            skill_id=sample_skill_catalog["id"],
            proficiency_level="intermediate",
            years_of_experience=2.0,
        )
        result = employee_skill.create_skill(skill_in)
        assert result.proficiency_level == "intermediate"
        assert result.employee_name == "寮犱笁"

    def test_create_skill_employee_not_found(self, sample_skill_catalog):
        skill_in = EmployeeSkillCreate(
            employee_id=9999,
            skill_name="Python",
            skill_id=sample_skill_catalog["id"],
            proficiency_level="beginner",
        )
        with pytest.raises(HTTPException) as exc_info:
            employee_skill.create_skill(skill_in)
        assert exc_info.value.status_code == 400
        assert "涓嶅瓨鍦? in exc_info.value.detail

    def test_create_skill_invalid_proficiency(self, sample_employee):
        skill_in = EmployeeSkillCreate(
            employee_id=sample_employee["id"],
            skill_name="Python",
            proficiency_level="guru",
        )
        with pytest.raises(HTTPException) as exc_info:
            employee_skill.create_skill(skill_in)
        assert exc_info.value.status_code == 400
        assert "鏃犳晥鐨勭啛缁冪▼搴? in exc_info.value.detail

    def test_create_skill_invalid_catalog(self, sample_employee):
        skill_in = EmployeeSkillCreate(
            employee_id=sample_employee["id"],
            skill_name="Python",
            skill_id=9999,
            proficiency_level="beginner",
        )
        with pytest.raises(HTTPException) as exc_info:
            employee_skill.create_skill(skill_in)
        assert exc_info.value.status_code == 400
        assert "鎶€鑳界洰褰? in exc_info.value.detail

    def test_update_skill(self, sample_employee_skill):
        skill_in = EmployeeSkillUpdate(proficiency_level="expert", years_of_experience=8.0)
        result = employee_skill.update_skill(sample_employee_skill["id"], skill_in)
        assert result.proficiency_level == "expert"

    def test_update_skill_not_found(self):
        skill_in = EmployeeSkillUpdate(proficiency_level="expert")
        with pytest.raises(HTTPException) as exc_info:
            employee_skill.update_skill(9999, skill_in)
        assert exc_info.value.status_code == 404
        assert "鎶€鑳借褰? in exc_info.value.detail

    def test_update_skill_invalid_proficiency(self, sample_employee_skill):
        skill_in = EmployeeSkillUpdate(proficiency_level="invalid")
        with pytest.raises(HTTPException) as exc_info:
            employee_skill.update_skill(sample_employee_skill["id"], skill_in)
        assert exc_info.value.status_code == 400
        assert "鏃犳晥鐨勭啛缁冪▼搴? in exc_info.value.detail

    def test_update_skill_invalid_catalog(self, sample_employee_skill):
        skill_in = EmployeeSkillUpdate(skill_id=9999)
        with pytest.raises(HTTPException) as exc_info:
            employee_skill.update_skill(sample_employee_skill["id"], skill_in)
        assert exc_info.value.status_code == 400
        assert "鎶€鑳界洰褰? in exc_info.value.detail

    def test_delete_skill(self, sample_employee_skill):
        result = employee_skill.delete_skill(sample_employee_skill["id"])
        assert "宸插垹闄? in result["message"]

    def test_delete_skill_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            employee_skill.delete_skill(9999)
        assert exc_info.value.status_code == 404


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 7. Skill Catalog Service
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestSkillCatalogService:
    def test_list_skills_empty(self):
        result = skill_catalog.list_skills()
        assert result.total == 0

    def test_list_skills(self, sample_skill_catalog):
        result = skill_catalog.list_skills()
        assert result.total == 1
        assert result.skills[0].name == "Python"

    def test_list_skills_filter_category(self, sample_skill_catalog):
        # Create another skill in different category
        skill_in = SkillCatalogCreate(name="Java", category="缂栫▼", description="Java璇█")
        skill_catalog.create_skill(skill_in)
        skill_in2 = SkillCatalogCreate(name="Excel", category="鍔炲叕", description="琛ㄦ牸宸ュ叿")
        skill_catalog.create_skill(skill_in2)

        result = skill_catalog.list_skills(category="鍔炲叕")
        assert result.total == 1
        assert result.skills[0].name == "Excel"

    def test_get_skill(self, sample_skill_catalog):
        result = skill_catalog.get_skill(sample_skill_catalog["id"])
        assert result.name == "Python"
        assert result.employee_count == 0

    def test_get_skill_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            skill_catalog.get_skill(9999)
        assert exc_info.value.status_code == 404
        assert "鎶€鑳界洰褰? in exc_info.value.detail

    def test_create_skill(self):
        skill_in = SkillCatalogCreate(name="JavaScript", category="缂栫▼", description="JS璇█")
        result = skill_catalog.create_skill(skill_in)
        assert result.name == "JavaScript"

    def test_create_skill_duplicate_name(self, sample_skill_catalog):
        skill_in = SkillCatalogCreate(name="Python")
        with pytest.raises(HTTPException) as exc_info:
            skill_catalog.create_skill(skill_in)
        assert exc_info.value.status_code == 400
        assert "宸插瓨鍦? in exc_info.value.detail

    def test_update_skill(self, sample_skill_catalog):
        skill_in = SkillCatalogUpdate(description="Python 3.x")
        result = skill_catalog.update_skill(sample_skill_catalog["id"], skill_in)
        assert result.description == "Python 3.x"

    def test_update_skill_not_found(self):
        skill_in = SkillCatalogUpdate(name="涓嶅瓨鍦?)
        with pytest.raises(HTTPException) as exc_info:
            skill_catalog.update_skill(9999, skill_in)
        assert exc_info.value.status_code == 404

    def test_update_skill_duplicate_name(self, sample_skill_catalog):
        skill_in = SkillCatalogCreate(name="Java", category="缂栫▼")
        skill_catalog.create_skill(skill_in)
        dup_in = SkillCatalogUpdate(name="Java")
        with pytest.raises(HTTPException) as exc_info:
            skill_catalog.update_skill(sample_skill_catalog["id"], dup_in)
        assert exc_info.value.status_code == 400
        assert "宸插瓨鍦? in exc_info.value.detail

    def test_update_skill_same_name_ok(self, sample_skill_catalog):
        skill_in = SkillCatalogUpdate(name="Python", description="Updated")
        result = skill_catalog.update_skill(sample_skill_catalog["id"], skill_in)
        assert result.description == "Updated"

    def test_delete_skill(self, sample_skill_catalog):
        result = skill_catalog.delete_skill(sample_skill_catalog["id"])
        assert "宸插垹闄? in result["message"]

    def test_delete_skill_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            skill_catalog.delete_skill(9999)
        assert exc_info.value.status_code == 404

    def test_delete_skill_in_use_by_employee(self, sample_employee_skill, sample_skill_catalog):
        with pytest.raises(HTTPException) as exc_info:
            skill_catalog.delete_skill(sample_skill_catalog["id"])
        assert exc_info.value.status_code == 400
        assert "姝ｅ湪琚娇鐢? in exc_info.value.detail


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 8. Project Service
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestProjectService:
    def test_list_projects_empty(self):
        result = project.list_projects()
        assert result.total == 0

    def test_list_projects(self, sample_project):
        result = project.list_projects()
        assert result.total == 1
        assert result.projects[0].name == "HR绯荤粺V2"

    def test_list_projects_filter_status(self, sample_project):
        result = project.list_projects(status="active")
        assert result.total == 0
        result2 = project.list_projects(status="planning")
        assert result2.total == 1

    def test_get_project(self, sample_project):
        result = project.get_project(sample_project["id"])
        assert result.name == "HR绯荤粺V2"

    def test_get_project_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            project.get_project(9999)
        assert exc_info.value.status_code == 404
        assert "椤圭洰" in exc_info.value.detail

    def test_create_project(self):
        proj_in = ProjectCreate(
            name="鏂伴」鐩?,
            status="planning",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        result = project.create_project(proj_in)
        assert result.name == "鏂伴」鐩?
        assert result.skill_requirement_count == 0
        assert result.member_count == 0

    def test_create_project_invalid_status(self):
        proj_in = ProjectCreate(name="鍧忛」鐩?, status="invalid")
        with pytest.raises(HTTPException) as exc_info:
            project.create_project(proj_in)
        assert exc_info.value.status_code == 400
        assert "鏃犳晥鐨勯」鐩姸鎬? in exc_info.value.detail

    def test_create_project_end_before_start(self):
        proj_in = ProjectCreate(
            name="鍧忛」鐩?,
            status="planning",
            start_date=date(2026, 12, 31),
            end_date=date(2026, 1, 1),
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_project(proj_in)
        assert exc_info.value.status_code == 400
        assert "缁撴潫鏃ユ湡涓嶈兘鏃╀簬寮€濮嬫棩鏈? in exc_info.value.detail

    def test_update_project(self, sample_project):
        proj_in = ProjectUpdate(name="HR绯荤粺V3")
        result = project.update_project(sample_project["id"], proj_in)
        assert result.name == "HR绯荤粺V3"

    def test_update_project_not_found(self):
        proj_in = ProjectUpdate(name="涓嶅瓨鍦?)
        with pytest.raises(HTTPException) as exc_info:
            project.update_project(9999, proj_in)
        assert exc_info.value.status_code == 404

    def test_update_project_invalid_status(self, sample_project):
        proj_in = ProjectUpdate(status="invalid")
        with pytest.raises(HTTPException) as exc_info:
            project.update_project(sample_project["id"], proj_in)
        assert exc_info.value.status_code == 400
        assert "鏃犳晥鐨勯」鐩姸鎬? in exc_info.value.detail

    def test_delete_project(self, sample_project):
        result = project.delete_project(sample_project["id"])
        assert "宸插垹闄? in result["message"]

    def test_delete_project_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            project.delete_project(9999)
        assert exc_info.value.status_code == 404

    def test_delete_project_active(self, sample_project):
        # Set project to active
        project.update_project(sample_project["id"], ProjectUpdate(status="active"))
        with pytest.raises(HTTPException) as exc_info:
            project.delete_project(sample_project["id"])
        assert exc_info.value.status_code == 400
        assert "娲昏穬椤圭洰鏃犳硶鍒犻櫎" in exc_info.value.detail


class TestProjectSkillRequirement:
    def test_list_requirements_empty(self, sample_project):
        result = project.list_skill_requirements(sample_project["id"])
        assert result.total == 0

    def test_list_requirements_project_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            project.list_skill_requirements(9999)
        assert exc_info.value.status_code == 404

    def test_create_requirement(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        result = project.create_skill_requirement(sample_project["id"], req_in)
        assert result.skill_name == "Python"
        assert result.project_id == sample_project["id"]

    def test_create_requirement_project_not_found(self, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_skill_requirement(9999, req_in)
        assert exc_info.value.status_code == 404

    def test_create_requirement_invalid_catalog(self, sample_project):
        req_in = ProjectSkillRequirementCreate(
            skill_id=9999,
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_skill_requirement(sample_project["id"], req_in)
        assert exc_info.value.status_code == 400
        assert "鎶€鑳界洰褰? in exc_info.value.detail

    def test_create_requirement_invalid_proficiency(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="guru",
            person_days=20.0,
            headcount=2,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_skill_requirement(sample_project["id"], req_in)
        assert exc_info.value.status_code == 400
        assert "鏃犳晥鐨勭啛缁冪▼搴? in exc_info.value.detail

    def test_create_requirement_person_days_zero(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=0,
            headcount=2,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_skill_requirement(sample_project["id"], req_in)
        assert exc_info.value.status_code == 400
        assert "宸ユ椂棰勭畻蹇呴』澶т簬0" in exc_info.value.detail

    def test_create_requirement_headcount_zero(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=0,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_skill_requirement(sample_project["id"], req_in)
        assert exc_info.value.status_code == 400
        assert "鎵€闇€浜烘暟蹇呴』澶т簬0" in exc_info.value.detail

    def test_create_requirement_duplicate(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        project.create_skill_requirement(sample_project["id"], req_in)
        with pytest.raises(HTTPException) as exc_info:
            project.create_skill_requirement(sample_project["id"], req_in)
        assert exc_info.value.status_code == 400
        assert "宸插瓨鍦ㄨ鎶€鑳介渶姹? in exc_info.value.detail

    def test_update_requirement(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        req = project.create_skill_requirement(sample_project["id"], req_in)
        update_in = ProjectSkillRequirementUpdate(person_days=30.0)
        result = project.update_skill_requirement(sample_project["id"], req.id, update_in)
        assert result.person_days == 30.0

    def test_update_requirement_not_found(self, sample_project):
        update_in = ProjectSkillRequirementUpdate(person_days=30.0)
        with pytest.raises(HTTPException) as exc_info:
            project.update_skill_requirement(sample_project["id"], 9999, update_in)
        assert exc_info.value.status_code == 404

    def test_update_requirement_invalid_proficiency(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        req = project.create_skill_requirement(sample_project["id"], req_in)
        update_in = ProjectSkillRequirementUpdate(required_proficiency="guru")
        with pytest.raises(HTTPException) as exc_info:
            project.update_skill_requirement(sample_project["id"], req.id, update_in)
        assert exc_info.value.status_code == 400

    def test_update_requirement_person_days_zero(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        req = project.create_skill_requirement(sample_project["id"], req_in)
        update_in = ProjectSkillRequirementUpdate(person_days=0)
        with pytest.raises(HTTPException) as exc_info:
            project.update_skill_requirement(sample_project["id"], req.id, update_in)
        assert exc_info.value.status_code == 400

    def test_update_requirement_headcount_zero(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        req = project.create_skill_requirement(sample_project["id"], req_in)
        update_in = ProjectSkillRequirementUpdate(headcount=0)
        with pytest.raises(HTTPException) as exc_info:
            project.update_skill_requirement(sample_project["id"], req.id, update_in)
        assert exc_info.value.status_code == 400

    def test_delete_requirement(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        req = project.create_skill_requirement(sample_project["id"], req_in)
        result = project.delete_skill_requirement(sample_project["id"], req.id)
        assert "宸插垹闄? in result["message"]

    def test_delete_requirement_not_found(self, sample_project):
        with pytest.raises(HTTPException) as exc_info:
            project.delete_skill_requirement(sample_project["id"], 9999)
        assert exc_info.value.status_code == 404


class TestProjectMember:
    def test_list_members_empty(self, sample_project):
        result = project.list_members(sample_project["id"])
        assert result.total == 0

    def test_list_members_project_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            project.list_members(9999)
        assert exc_info.value.status_code == 404

    def test_create_member(self, sample_project, sample_employee):
        member_in = ProjectMemberCreate(
            employee_id=sample_employee["id"],
            role="寮€鍙?,
            assigned_date=date(2026, 1, 15),
        )
        result = project.create_member(sample_project["id"], member_in)
        assert result.employee_name == "寮犱笁"
        assert result.role == "寮€鍙?

    def test_create_member_project_not_found(self, sample_employee):
        member_in = ProjectMemberCreate(
            employee_id=sample_employee["id"],
            role="寮€鍙?,
            assigned_date=date(2026, 1, 15),
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_member(9999, member_in)
        assert exc_info.value.status_code == 404

    def test_create_member_employee_not_found(self, sample_project):
        member_in = ProjectMemberCreate(
            employee_id=9999,
            role="寮€鍙?,
            assigned_date=date(2026, 1, 15),
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_member(sample_project["id"], member_in)
        assert exc_info.value.status_code == 400
        assert "鍛樺伐" in exc_info.value.detail

    def test_create_member_duplicate(self, sample_project, sample_employee):
        member_in = ProjectMemberCreate(
            employee_id=sample_employee["id"],
            role="寮€鍙?,
            assigned_date=date(2026, 1, 15),
        )
        project.create_member(sample_project["id"], member_in)
        with pytest.raises(HTTPException) as exc_info:
            project.create_member(sample_project["id"], member_in)
        assert exc_info.value.status_code == 400
        assert "宸插湪姝ら」鐩腑" in exc_info.value.detail

    def test_update_member(self, sample_project, sample_employee):
        member_in = ProjectMemberCreate(
            employee_id=sample_employee["id"],
            role="寮€鍙?,
            assigned_date=date(2026, 1, 15),
        )
        member = project.create_member(sample_project["id"], member_in)
        update_in = ProjectMemberUpdate(role="娴嬭瘯")
        result = project.update_member(sample_project["id"], member.id, update_in)
        assert result.role == "娴嬭瘯"

    def test_update_member_not_found(self, sample_project):
        update_in = ProjectMemberUpdate(role="娴嬭瘯")
        with pytest.raises(HTTPException) as exc_info:
            project.update_member(sample_project["id"], 9999, update_in)
        assert exc_info.value.status_code == 404

    def test_delete_member(self, sample_project, sample_employee):
        member_in = ProjectMemberCreate(
            employee_id=sample_employee["id"],
            role="寮€鍙?,
            assigned_date=date(2026, 1, 15),
        )
        member = project.create_member(sample_project["id"], member_in)
        result = project.delete_member(sample_project["id"], member.id)
        assert "宸茬Щ闄? in result["message"]

    def test_delete_member_not_found(self, sample_project):
        with pytest.raises(HTTPException) as exc_info:
            project.delete_member(sample_project["id"], 9999)
        assert exc_info.value.status_code == 404


class TestProjectTimesheet:
    def _setup_project_with_member_and_req(self, sample_project, sample_employee, sample_skill_catalog):
        """Helper: add a requirement and a member to the project."""
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        req = project.create_skill_requirement(sample_project["id"], req_in)
        member_in = ProjectMemberCreate(
            employee_id=sample_employee["id"],
            role="寮€鍙?,
            assigned_date=date(2026, 1, 15),
        )
        project.create_member(sample_project["id"], member_in)
        return req

    def test_list_timesheets_empty(self, sample_project):
        result = project.list_timesheets(sample_project["id"])
        assert result.total == 0

    def test_list_timesheets_project_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            project.list_timesheets(9999)
        assert exc_info.value.status_code == 404

    def test_create_timesheet(self, sample_project, sample_employee, sample_skill_catalog):
        req = self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=8.0,
            description="寮€鍙戝伐浣?,
        )
        result = project.create_timesheet(sample_project["id"], ts_in)
        assert result.employee_name == "寮犱笁"
        assert result.skill_name == "Python"
        assert result.hours == 8.0

    def test_create_timesheet_project_not_found(self):
        ts_in = ProjectTimesheetCreate(
            requirement_id=1,
            employee_id=1,
            date=date(2026, 5, 10),
            hours=8.0,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_timesheet(9999, ts_in)
        assert exc_info.value.status_code == 404

    def test_create_timesheet_requirement_not_in_project(self, sample_project, sample_employee, sample_skill_catalog):
        self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        # Create another project with a different requirement
        proj2 = project.create_project(ProjectCreate(name="椤圭洰2", status="planning"))
        req2 = project.create_skill_requirement(
            proj2.id,
            ProjectSkillRequirementCreate(
                skill_id=sample_skill_catalog["id"],
                required_proficiency="advanced",
                person_days=10.0,
                headcount=1,
            ),
        )
        ts_in = ProjectTimesheetCreate(
            requirement_id=req2.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=8.0,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_timesheet(sample_project["id"], ts_in)
        assert exc_info.value.status_code == 400
        assert "涓嶅睘浜庤椤圭洰" in exc_info.value.detail

    def test_create_timesheet_employee_not_found(self, sample_project, sample_skill_catalog):
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        req = project.create_skill_requirement(sample_project["id"], req_in)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=9999,
            date=date(2026, 5, 10),
            hours=8.0,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_timesheet(sample_project["id"], ts_in)
        assert exc_info.value.status_code == 400
        assert "鍛樺伐" in exc_info.value.detail

    def test_create_timesheet_not_member(self, sample_project, sample_skill_catalog):
        # Create another employee but don't add as member
        from app.repositories import worker as emp_repo

        emp2 = emp_repo.create_worker({"name": "鏉庡洓", "salary": 10000.0})
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        req = project.create_skill_requirement(sample_project["id"], req_in)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=emp2["id"],
            date=date(2026, 5, 10),
            hours=8.0,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_timesheet(sample_project["id"], ts_in)
        assert exc_info.value.status_code == 400
        assert "涓嶆槸椤圭洰鎴愬憳" in exc_info.value.detail

    def test_create_timesheet_hours_zero(self, sample_project, sample_employee, sample_skill_catalog):
        req = self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=0,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_timesheet(sample_project["id"], ts_in)
        assert exc_info.value.status_code == 400
        assert "宸ユ椂蹇呴』澶т簬0" in exc_info.value.detail

    def test_create_timesheet_future_date(self, sample_project, sample_employee, sample_skill_catalog):
        req = self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        future = date.today() + timedelta(days=30)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=future,
            hours=8.0,
        )
        with pytest.raises(HTTPException) as exc_info:
            project.create_timesheet(sample_project["id"], ts_in)
        assert exc_info.value.status_code == 400
        assert "涓嶈兘鍦ㄦ湭鏉? in exc_info.value.detail

    def test_update_timesheet(self, sample_project, sample_employee, sample_skill_catalog):
        req = self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=8.0,
        )
        ts = project.create_timesheet(sample_project["id"], ts_in)
        update_in = ProjectTimesheetUpdate(hours=6.0)
        result = project.update_timesheet(sample_project["id"], ts.id, update_in)
        assert result.hours == 6.0

    def test_update_timesheet_not_found(self, sample_project):
        update_in = ProjectTimesheetUpdate(hours=6.0)
        with pytest.raises(HTTPException) as exc_info:
            project.update_timesheet(sample_project["id"], 9999, update_in)
        assert exc_info.value.status_code == 404

    def test_update_timesheet_invalid_requirement(self, sample_project, sample_employee, sample_skill_catalog):
        req = self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=8.0,
        )
        ts = project.create_timesheet(sample_project["id"], ts_in)
        # Create another project and requirement
        proj2 = project.create_project(ProjectCreate(name="椤圭洰2", status="planning"))
        req2 = project.create_skill_requirement(
            proj2.id,
            ProjectSkillRequirementCreate(
                skill_id=sample_skill_catalog["id"],
                required_proficiency="advanced",
                person_days=10.0,
                headcount=1,
            ),
        )
        update_in = ProjectTimesheetUpdate(requirement_id=req2.id)
        with pytest.raises(HTTPException) as exc_info:
            project.update_timesheet(sample_project["id"], ts.id, update_in)
        assert exc_info.value.status_code == 400
        assert "涓嶅睘浜庤椤圭洰" in exc_info.value.detail

    def test_update_timesheet_not_member(self, sample_project, sample_employee, sample_skill_catalog):
        req = self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=8.0,
        )
        ts = project.create_timesheet(sample_project["id"], ts_in)
        # Try to change to a non-member employee
        from app.repositories import worker as emp_repo

        emp2 = emp_repo.create_worker({"name": "鏉庡洓", "salary": 10000.0})
        update_in = ProjectTimesheetUpdate(employee_id=emp2["id"])
        with pytest.raises(HTTPException) as exc_info:
            project.update_timesheet(sample_project["id"], ts.id, update_in)
        assert exc_info.value.status_code == 400
        assert "涓嶆槸椤圭洰鎴愬憳" in exc_info.value.detail

    def test_update_timesheet_hours_zero(self, sample_project, sample_employee, sample_skill_catalog):
        req = self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=8.0,
        )
        ts = project.create_timesheet(sample_project["id"], ts_in)
        update_in = ProjectTimesheetUpdate(hours=0)
        with pytest.raises(HTTPException) as exc_info:
            project.update_timesheet(sample_project["id"], ts.id, update_in)
        assert exc_info.value.status_code == 400

    def test_update_timesheet_future_date(self, sample_project, sample_employee, sample_skill_catalog):
        req = self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=8.0,
        )
        ts = project.create_timesheet(sample_project["id"], ts_in)
        future = date.today() + timedelta(days=30)
        update_in = ProjectTimesheetUpdate(date=future)
        with pytest.raises(HTTPException) as exc_info:
            project.update_timesheet(sample_project["id"], ts.id, update_in)
        assert exc_info.value.status_code == 400

    def test_delete_timesheet(self, sample_project, sample_employee, sample_skill_catalog):
        req = self._setup_project_with_member_and_req(sample_project, sample_employee, sample_skill_catalog)
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=8.0,
        )
        ts = project.create_timesheet(sample_project["id"], ts_in)
        result = project.delete_timesheet(sample_project["id"], ts.id)
        assert "宸插垹闄? in result["message"]

    def test_delete_timesheet_not_found(self, sample_project):
        with pytest.raises(HTTPException) as exc_info:
            project.delete_timesheet(sample_project["id"], 9999)
        assert exc_info.value.status_code == 404


class TestProjectProgress:
    def test_get_project_progress_empty(self, sample_project):
        result = project.get_project_progress(sample_project["id"])
        assert result.overall_progress == 0.0
        assert result.total_budget_person_days == 0.0

    def test_get_project_progress_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            project.get_project_progress(9999)
        assert exc_info.value.status_code == 404

    def test_get_project_progress_with_data(self, sample_project, sample_employee, sample_skill_catalog):
        # Setup requirement and member
        req_in = ProjectSkillRequirementCreate(
            skill_id=sample_skill_catalog["id"],
            required_proficiency="advanced",
            person_days=20.0,
            headcount=2,
        )
        req = project.create_skill_requirement(sample_project["id"], req_in)
        member_in = ProjectMemberCreate(
            employee_id=sample_employee["id"],
            role="寮€鍙?,
            assigned_date=date(2026, 1, 15),
        )
        project.create_member(sample_project["id"], member_in)
        # Add a timesheet
        ts_in = ProjectTimesheetCreate(
            requirement_id=req.id,
            employee_id=sample_employee["id"],
            date=date(2026, 5, 10),
            hours=8.0,
        )
        project.create_timesheet(sample_project["id"], ts_in)

        result = project.get_project_progress(sample_project["id"])
        assert result.total_budget_person_days == 20.0
        assert result.total_used_person_days == 1.0  # 8 hours / 8
        assert len(result.by_requirement) == 1
        assert len(result.by_member) == 1


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 9. Agent Memory Service
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestAgentMemoryService:
    def test_save_memory(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            user_tag="user1",
            memory_type="fact",
            category="general",
            subject="test subject",
            content="test content",
            source="agent_observed",
        )
        result = agent_memory.save_memory(mem_in)
        assert result.memory_type == "fact"
        assert result.is_active is True

    def test_save_memory_invalid_type(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            memory_type="invalid",
            category="general",
            subject="test",
            content="test",
        )
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.save_memory(mem_in)
        assert exc_info.value.status_code == 400
        assert "鏃犳晥鐨勮蹇嗙被鍨? in exc_info.value.detail

    def test_save_memory_invalid_category(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            memory_type="fact",
            category="invalid",
            subject="test",
            content="test",
        )
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.save_memory(mem_in)
        assert exc_info.value.status_code == 400
        assert "鏃犳晥鐨勪笟鍔″垎绫? in exc_info.value.detail

    def test_save_memory_invalid_source(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            memory_type="fact",
            category="general",
            subject="test",
            content="test",
            source="invalid",
        )
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.save_memory(mem_in)
        assert exc_info.value.status_code == 400
        assert "鏃犳晥鐨勬潵婧? in exc_info.value.detail

    def test_save_memory_preference_dedup(self):
        mem_in1 = MemoryCreate(
            session_id="sess1",
            user_tag="user1",
            memory_type="preference",
            category="general",
            subject="theme",
            content="dark mode",
            source="user_instructed",
        )
        result1 = agent_memory.save_memory(mem_in1)
        # Save same preference again - should update, not create new
        mem_in2 = MemoryCreate(
            session_id="sess1",
            user_tag="user1",
            memory_type="preference",
            category="general",
            subject="theme",
            content="light mode",
            source="user_instructed",
        )
        result2 = agent_memory.save_memory(mem_in2)
        assert result2.id == result1.id
        assert result2.content == "light mode"

    def test_recall_memories_by_user_tag(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            user_tag="user1",
            memory_type="fact",
            category="general",
            subject="test subject",
            content="test content",
        )
        agent_memory.save_memory(mem_in)
        result = agent_memory.recall_memories("user1")
        assert result.total == 1

    def test_recall_memories_by_subject(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            user_tag="user1",
            memory_type="fact",
            category="general",
            subject="unique subject xyz",
            content="test content",
        )
        agent_memory.save_memory(mem_in)
        result = agent_memory.recall_memories("user1", subject="unique subject xyz")
        assert result.total == 1

    def test_recall_memories_by_keyword(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            user_tag="user1",
            memory_type="fact",
            category="general",
            subject="test",
            content="important keyword banana",
        )
        agent_memory.save_memory(mem_in)
        result = agent_memory.recall_memories("user1", keyword="banana")
        assert result.total == 1

    def test_recall_memories_invalid_type(self):
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.recall_memories("user1", memory_type="invalid")
        assert exc_info.value.status_code == 400

    def test_recall_memories_invalid_category(self):
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.recall_memories("user1", category="invalid")
        assert exc_info.value.status_code == 400

    def test_get_memory(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            memory_type="fact",
            category="general",
            subject="test",
            content="content",
        )
        saved = agent_memory.save_memory(mem_in)
        result = agent_memory.get_memory(saved.id)
        assert result.id == saved.id

    def test_get_memory_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.get_memory(9999)
        assert exc_info.value.status_code == 404

    def test_update_memory(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            memory_type="fact",
            category="general",
            subject="test",
            content="original",
        )
        saved = agent_memory.save_memory(mem_in)
        update_in = MemoryUpdate(content="updated content", importance=5)
        result = agent_memory.update_memory(saved.id, update_in)
        assert result.content == "updated content"
        assert result.importance == 5

    def test_update_memory_not_found(self):
        update_in = MemoryUpdate(content="nope")
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.update_memory(9999, update_in)
        assert exc_info.value.status_code == 404

    def test_delete_memory(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            memory_type="fact",
            category="general",
            subject="test",
            content="content",
        )
        saved = agent_memory.save_memory(mem_in)
        result = agent_memory.delete_memory(saved.id)
        assert "宸插垹闄? in result["message"]

    def test_delete_memory_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.delete_memory(9999)
        assert exc_info.value.status_code == 404

    def test_create_reminder(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            user_tag="user1",
            memory_type="reminder",
            category="general",
            subject="test",
            content="remember this",
        )
        saved = agent_memory.save_memory(mem_in)
        reminder_in = ReminderCreate(
            reminder_type="one_time",
            trigger_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
        )
        result = agent_memory.create_reminder(saved.id, reminder_in)
        assert result.memory_id == saved.id
        assert result.reminder_type == "one_time"
        assert result.triggered is False

    def test_create_reminder_memory_not_found(self):
        reminder_in = ReminderCreate(
            trigger_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
        )
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.create_reminder(9999, reminder_in)
        assert exc_info.value.status_code == 404

    def test_create_reminder_invalid_type(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            memory_type="reminder",
            category="general",
            subject="test",
            content="remember this",
        )
        saved = agent_memory.save_memory(mem_in)
        reminder_in = ReminderCreate(
            reminder_type="invalid",
            trigger_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
        )
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.create_reminder(saved.id, reminder_in)
        assert exc_info.value.status_code == 400
        assert "鏃犳晥鐨勬彁閱掔被鍨? in exc_info.value.detail

    def test_check_pending_reminders(self):
        # Create memory with user_tag and a reminder in the past
        mem_in = MemoryCreate(
            session_id="sess1",
            user_tag="user1",
            memory_type="reminder",
            category="general",
            subject="test",
            content="remember this",
        )
        saved = agent_memory.save_memory(mem_in)
        past = datetime(2020, 1, 1, 10, 0, tzinfo=UTC)
        reminder_in = ReminderCreate(
            reminder_type="one_time",
            trigger_at=past,
        )
        agent_memory.create_reminder(saved.id, reminder_in)
        result = agent_memory.check_pending_reminders("user1")
        assert result.total == 1
        assert result.reminders[0].triggered is True

    def test_check_pending_reminders_none(self):
        result = agent_memory.check_pending_reminders("nobody")
        assert result.total == 0

    def test_dismiss_reminder(self):
        mem_in = MemoryCreate(
            session_id="sess1",
            memory_type="reminder",
            category="general",
            subject="test",
            content="remember this",
        )
        saved = agent_memory.save_memory(mem_in)
        reminder_in = ReminderCreate(
            trigger_at=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
        )
        reminder = agent_memory.create_reminder(saved.id, reminder_in)
        result = agent_memory.dismiss_reminder(reminder.id)
        assert "宸插垹闄? in result["message"]

    def test_dismiss_reminder_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            agent_memory.dismiss_reminder(9999)
        assert exc_info.value.status_code == 404

    def test_cleanup_expired(self):
        # Create an active memory with expires_at in the past
        mem_in = MemoryCreate(
            session_id="sess1",
            memory_type="fact",
            category="general",
            subject="test",
            content="expires",
            expires_at=datetime(2020, 1, 1, tzinfo=UTC),
        )
        agent_memory.save_memory(mem_in)
        result = agent_memory.cleanup_expired()
        assert "宸叉竻鐞? in result["message"]


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# 10. Knowledge Base Service (with mocks)
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?


class TestKnowledgeBaseService:
    @patch("app.services.knowledge_base.chunk_text")
    @patch("app.services.knowledge_base.get_store")
    def test_add_document_from_text(self, mock_get_store, mock_chunk_text):
        mock_store = MagicMock()
        mock_store.add_document.return_value = 3
        mock_get_store.return_value = mock_store
        mock_chunk_text.return_value = ["chunk1", "chunk2", "chunk3"]

        result = knowledge_base.add_document_from_text(title="Test Doc", content="Hello world", source="test_source")
        assert result["chunk_count"] == 3
        assert result["title"] == "Test Doc"
        assert result["total_chars"] == 11
        mock_chunk_text.assert_called_once_with("Hello world")
        mock_store.add_document.assert_called_once()

    @patch("app.services.knowledge_base.chunk_text")
    @patch("app.services.knowledge_base.get_store")
    def test_add_document_from_text_no_source(self, mock_get_store, mock_chunk_text):
        mock_store = MagicMock()
        mock_store.add_document.return_value = 1
        mock_get_store.return_value = mock_store
        mock_chunk_text.return_value = ["chunk1"]

        result = knowledge_base.add_document_from_text(title="My Title", content="Content")
        # When no source, title is used as source
        assert result["source"] == "My Title"

    @patch("app.services.knowledge_base.add_document_from_text")
    def test_add_document_from_file(self, mock_add_from_text):
        mock_add_from_text.return_value = {
            "doc_id": "abc123",
            "source": "test.txt",
            "title": "test",
            "chunk_count": 1,
            "total_chars": 10,
        }
        # Use a file that exists
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("Hello world content")
            tmp_path = f.name
        try:
            result = knowledge_base.add_document_from_file(tmp_path)
            assert result["chunk_count"] == 1
        finally:
            os.unlink(tmp_path)

    def test_add_document_from_file_not_found(self):
        result = knowledge_base.add_document_from_file("/nonexistent/path/file.txt")
        assert "error" in result
        assert "not found" in result["error"].lower() or "File not found" in result["error"]

    @patch("app.services.knowledge_base.get_store")
    def test_search_documents(self, mock_get_store):
        mock_store = MagicMock()
        mock_result = MagicMock()
        mock_result.text = "found text"
        mock_result.score = 0.95
        mock_result.metadata = {"source": "doc1", "doc_id": "abc", "chunk_index": 0}
        mock_store.search.return_value = [mock_result]
        mock_get_store.return_value = mock_store

        result = knowledge_base.search_documents("query", top_k=5)
        assert result["total_results"] == 1
        assert result["results"][0]["text"] == "found text"
        assert result["results"][0]["score"] == 0.95

    @patch("app.services.knowledge_base.get_store")
    def test_list_documents(self, mock_get_store):
        mock_store = MagicMock()
        mock_store.list_documents.return_value = [{"doc_id": "abc", "source": "test"}]
        mock_store.get_chunk_count.return_value = 5
        mock_get_store.return_value = mock_store

        result = knowledge_base.list_documents()
        assert result["total_documents"] == 1
        assert result["total_chunks"] == 5

    @patch("app.services.knowledge_base.get_store")
    def test_delete_document(self, mock_get_store):
        mock_store = MagicMock()
        mock_store.delete_document.return_value = 3
        mock_get_store.return_value = mock_store

        result = knowledge_base.delete_document("doc_id_123")
        assert result["chunks_deleted"] == 3

    @patch("app.services.knowledge_base.get_store")
    def test_delete_document_not_found(self, mock_get_store):
        mock_store = MagicMock()
        mock_store.delete_document.return_value = 0
        mock_get_store.return_value = mock_store

        result = knowledge_base.delete_document("nonexistent")
        assert "error" in result
        assert "not found" in result["error"].lower() or "not found" in result["error"]

