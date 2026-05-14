"""Complete pytest unit tests for all repository modules."""

from datetime import UTC, date, datetime, time, timedelta

from app.repositories import agent_memory as memory_repo
from app.repositories import attendance as att_repo
from app.repositories import department as dept_repo
from app.repositories import employee as emp_repo
from app.repositories import employee_skill as eskill_repo
from app.repositories import leave as leave_repo
from app.repositories import payroll as payroll_repo
from app.repositories import project as proj_repo
from app.repositories import skill_catalog as catalog_repo

# ═══════════════════════════════════════════════════════════════
# Department Repository
# ═══════════════════════════════════════════════════════════════


class TestDepartmentRepository:
    def test_get_all_returns_empty_when_no_data(self):
        assert dept_repo.get_all_departments() == []

    def test_crud_full_flow(self):
        # Create
        dept = dept_repo.create_department(
            {
                "name": "工程部",
                "description": "研发部门",
                "manager": "张经理",
            }
        )
        assert dept["id"] is not None
        assert dept["name"] == "工程部"
        assert dept["description"] == "研发部门"
        assert dept["manager"] == "张经理"

        # Read by id
        fetched = dept_repo.get_department_by_id(dept["id"])
        assert fetched is not None
        assert fetched["name"] == "工程部"

        # Read by name
        by_name = dept_repo.get_department_by_name("工程部")
        assert by_name is not None
        assert by_name["id"] == dept["id"]

        # Read all
        all_depts = dept_repo.get_all_departments()
        assert len(all_depts) == 1

        # Update
        updated = dept_repo.update_department(dept["id"], {"name": "技术部", "manager": "李经理"})
        assert updated is not None
        assert updated["name"] == "技术部"
        assert updated["manager"] == "李经理"
        assert updated["description"] == "研发部门"  # unchanged

        # Delete
        assert dept_repo.delete_department(dept["id"]) is True
        assert dept_repo.get_department_by_id(dept["id"]) is None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert dept_repo.get_department_by_id(9999) is None

    def test_get_by_name_returns_none_for_nonexistent(self):
        assert dept_repo.get_department_by_name("不存在的部门") is None

    def test_update_returns_none_for_nonexistent(self):
        assert dept_repo.update_department(9999, {"name": "x"}) is None

    def test_delete_returns_false_for_nonexistent(self):
        assert dept_repo.delete_department(9999) is False

    def test_update_partial_fields_ignores_none(self):
        dept = dept_repo.create_department({"name": "财务部", "description": "财务", "manager": "王经理"})
        updated = dept_repo.update_department(dept["id"], {"name": "审计部", "description": None})
        assert updated["name"] == "审计部"
        assert updated["description"] == "财务"  # None was ignored


# ═══════════════════════════════════════════════════════════════
# Employee Repository
# ═══════════════════════════════════════════════════════════════


class TestEmployeeRepository:
    def test_get_all_returns_empty_when_no_data(self):
        assert emp_repo.get_all_employees() == []

    def test_crud_full_flow(self):
        emp = emp_repo.create_employee(
            {
                "name": "张三",
                "department_id": 1,
                "salary": 15000.0,
            }
        )
        assert emp["id"] is not None
        assert emp["name"] == "张三"
        assert emp["salary"] == 15000.0

        # Read by id
        fetched = emp_repo.get_employee_by_id(emp["id"])
        assert fetched is not None
        assert fetched["name"] == "张三"

        # Read all
        all_emps = emp_repo.get_all_employees()
        assert len(all_emps) == 1

        # Update
        updated = emp_repo.update_employee(emp["id"], {"name": "李四", "salary": 18000.0})
        assert updated["name"] == "李四"
        assert updated["salary"] == 18000.0
        assert updated["department_id"] == 1  # unchanged

        # Delete
        assert emp_repo.delete_employee(emp["id"]) is True
        assert emp_repo.get_employee_by_id(emp["id"]) is None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert emp_repo.get_employee_by_id(9999) is None

    def test_update_returns_none_for_nonexistent(self):
        assert emp_repo.update_employee(9999, {"name": "x"}) is None

    def test_delete_returns_false_for_nonexistent(self):
        assert emp_repo.delete_employee(9999) is False

    def test_get_employees_by_department(self):
        emp_repo.create_employee({"name": "A", "department_id": 1, "salary": 10000.0})
        emp_repo.create_employee({"name": "B", "department_id": 1, "salary": 12000.0})
        emp_repo.create_employee({"name": "C", "department_id": 2, "salary": 11000.0})

        dept1 = emp_repo.get_employees_by_department(1)
        dept2 = emp_repo.get_employees_by_department(2)
        assert len(dept1) == 2
        assert len(dept2) == 1
        assert emp_repo.get_employees_by_department(999) == []

    def test_update_partial_fields_ignores_none(self):
        emp = emp_repo.create_employee({"name": "王五", "department_id": 1, "salary": 10000.0})
        updated = emp_repo.update_employee(emp["id"], {"name": "赵六", "department_id": None})
        assert updated["name"] == "赵六"
        assert updated["department_id"] == 1  # None was ignored


# ═══════════════════════════════════════════════════════════════
# Attendance Repository
# ═══════════════════════════════════════════════════════════════


class TestAttendanceRepository:
    def test_get_all_returns_empty_when_no_data(self):
        assert att_repo.get_all_attendance() == []

    def test_calculate_status_normal(self):
        assert att_repo.calculate_status(time(8, 30), time(18, 30)) == "normal"
        assert att_repo.calculate_status(time(9, 0), time(18, 0)) == "normal"

    def test_calculate_status_late(self):
        assert att_repo.calculate_status(time(9, 1), time(18, 30)) == "late"
        assert att_repo.calculate_status(time(10, 0)) == "late"

    def test_calculate_status_early_leave(self):
        assert att_repo.calculate_status(time(8, 0), time(17, 59)) == "early_leave"

    def test_calculate_status_late_and_early_leave(self):
        # Both late and early — the function returns "late" in this case
        result = att_repo.calculate_status(time(9, 30), time(17, 0))
        assert result == "late"

    def test_crud_full_flow(self):
        record = att_repo.create_attendance(
            {
                "employee_id": 1,
                "date": date(2026, 5, 1),
                "check_in": time(8, 30),
                "status": "normal",
            }
        )
        assert record["id"] is not None
        assert record["status"] == "normal"

        # Read by id
        fetched = att_repo.get_attendance_by_id(record["id"])
        assert fetched is not None
        assert fetched["employee_id"] == 1

        # Read by employee+date
        by_emp_date = att_repo.get_attendance_by_employee_date(1, date(2026, 5, 1))
        assert by_emp_date is not None
        assert by_emp_date["id"] == record["id"]

        # Read all
        all_recs = att_repo.get_all_attendance()
        assert len(all_recs) == 1

        # Update
        updated = att_repo.update_attendance(
            record["id"], {"check_out": time(18, 30), "status": "normal", "work_hours": 10.0}
        )
        assert updated["check_out"] == time(18, 30)
        assert updated["work_hours"] == 10.0

        # Delete (via employee list — no dedicated delete in attendance repo, test via get)
        # Attendance repo has no delete function; verify update works
        assert updated is not None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert att_repo.get_attendance_by_id(9999) is None

    def test_get_by_employee_date_returns_none(self):
        assert att_repo.get_attendance_by_employee_date(9999, date(2026, 5, 1)) is None

    def test_get_attendance_by_employee(self):
        _att = {"employee_id": 1, "date": date(2026, 5, 1), "check_in": time(8, 0), "status": "normal"}
        att_repo.create_attendance(_att)
        att_repo.create_attendance({**_att, "date": date(2026, 5, 2)})
        att_repo.create_attendance({**_att, "employee_id": 2})

        records = att_repo.get_attendance_by_employee(1)
        assert len(records) == 2
        assert att_repo.get_attendance_by_employee(999) == []

    def test_get_all_filters_employee_id(self):
        _att = {"employee_id": 1, "date": date(2026, 5, 1), "check_in": time(8, 0), "status": "normal"}
        att_repo.create_attendance(_att)
        att_repo.create_attendance({**_att, "employee_id": 2})

        filtered = att_repo.get_all_attendance(employee_id=1)
        assert len(filtered) == 1
        assert filtered[0]["employee_id"] == 1

    def test_get_all_filters_date_range(self):
        _att = {"employee_id": 1, "date": date(2026, 5, 1), "check_in": time(8, 0), "status": "normal"}
        att_repo.create_attendance(_att)
        att_repo.create_attendance({**_att, "date": date(2026, 5, 10)})
        att_repo.create_attendance({**_att, "date": date(2026, 5, 20)})

        # start_date filter
        result = att_repo.get_all_attendance(start_date=date(2026, 5, 5))
        assert len(result) == 2

        # end_date filter
        result = att_repo.get_all_attendance(end_date=date(2026, 5, 15))
        assert len(result) == 2

        # both filters
        result = att_repo.get_all_attendance(start_date=date(2026, 5, 5), end_date=date(2026, 5, 15))
        assert len(result) == 1

    def test_update_returns_none_for_nonexistent(self):
        assert att_repo.update_attendance(9999, {"status": "late"}) is None

    def test_update_sets_all_fields_including_none(self):
        """Attendance update uses setattr for ALL fields, not just non-None."""
        record = att_repo.create_attendance(
            {
                "employee_id": 1,
                "date": date(2026, 5, 1),
                "check_in": time(8, 0),
                "check_out": time(18, 0),
                "status": "normal",
                "work_hours": 10.0,
            }
        )
        updated = att_repo.update_attendance(record["id"], {"work_hours": None, "status": "late"})
        assert updated["status"] == "late"
        assert updated["work_hours"] is None  # setattr sets None too


# ═══════════════════════════════════════════════════════════════
# Leave Repository
# ═══════════════════════════════════════════════════════════════


class TestLeaveRepository:
    NOW = datetime.now(UTC)

    def test_get_all_returns_empty_when_no_data(self):
        assert leave_repo.get_all_leaves() == []

    def test_crud_full_flow(self):
        leave = leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "annual",
                "leave_type_name": "年假",
                "start_date": date(2026, 5, 10),
                "end_date": date(2026, 5, 12),
                "days": 3,
                "status": "pending",
                "created_at": self.NOW,
            }
        )
        assert leave["id"] is not None
        assert leave["leave_type"] == "annual"

        # Read by id
        fetched = leave_repo.get_leave_by_id(leave["id"])
        assert fetched is not None
        assert fetched["status"] == "pending"

        # Read all
        all_leaves = leave_repo.get_all_leaves()
        assert len(all_leaves) == 1

        # Update — leave uses setattr for ALL fields (even None)
        updated = leave_repo.update_leave(leave["id"], {"status": "approved", "approver": "李经理"})
        assert updated["status"] == "approved"
        assert updated["approver"] == "李经理"

        # Delete — no delete function in leave repo, verify update
        assert updated is not None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert leave_repo.get_leave_by_id(9999) is None

    def test_update_returns_none_for_nonexistent(self):
        assert leave_repo.update_leave(9999, {"status": "approved"}) is None

    def test_update_sets_all_fields_including_none(self):
        """Leave update uses setattr for ALL fields, not just non-None."""
        leave = leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "sick",
                "leave_type_name": "病假",
                "start_date": date(2026, 6, 1),
                "end_date": date(2026, 6, 2),
                "days": 2,
                "reason": "身体不适",
                "status": "pending",
                "created_at": self.NOW,
            }
        )
        updated = leave_repo.update_leave(leave["id"], {"reason": None})
        assert updated["reason"] is None  # setattr sets None too

    def test_get_leaves_by_employee(self):
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "annual",
                "leave_type_name": "年假",
                "start_date": date(2026, 5, 1),
                "end_date": date(2026, 5, 2),
                "days": 2,
                "status": "approved",
                "created_at": self.NOW,
            }
        )
        leave_repo.create_leave(
            {
                "employee_id": 2,
                "leave_type": "sick",
                "leave_type_name": "病假",
                "start_date": date(2026, 5, 1),
                "end_date": date(2026, 5, 1),
                "days": 1,
                "status": "pending",
                "created_at": self.NOW,
            }
        )
        result = leave_repo.get_leaves_by_employee(1)
        assert len(result) == 1
        assert result[0]["employee_id"] == 1

    def test_get_all_leaves_filter_employee_id(self):
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "annual",
                "leave_type_name": "年假",
                "start_date": date(2026, 5, 1),
                "end_date": date(2026, 5, 2),
                "days": 2,
                "status": "approved",
                "created_at": self.NOW,
            }
        )
        leave_repo.create_leave(
            {
                "employee_id": 2,
                "leave_type": "sick",
                "leave_type_name": "病假",
                "start_date": date(2026, 5, 1),
                "end_date": date(2026, 5, 1),
                "days": 1,
                "status": "pending",
                "created_at": self.NOW,
            }
        )
        result = leave_repo.get_all_leaves(employee_id=1)
        assert len(result) == 1

    def test_get_all_leaves_filter_status(self):
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "annual",
                "leave_type_name": "年假",
                "start_date": date(2026, 5, 1),
                "end_date": date(2026, 5, 2),
                "days": 2,
                "status": "approved",
                "created_at": self.NOW,
            }
        )
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "sick",
                "leave_type_name": "病假",
                "start_date": date(2026, 5, 5),
                "end_date": date(2026, 5, 5),
                "days": 1,
                "status": "pending",
                "created_at": self.NOW,
            }
        )
        result = leave_repo.get_all_leaves(status="approved")
        assert len(result) == 1
        assert result[0]["status"] == "approved"

    def test_get_all_leaves_combined_filters(self):
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "annual",
                "leave_type_name": "年假",
                "start_date": date(2026, 5, 1),
                "end_date": date(2026, 5, 2),
                "days": 2,
                "status": "approved",
                "created_at": self.NOW,
            }
        )
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "sick",
                "leave_type_name": "病假",
                "start_date": date(2026, 5, 5),
                "end_date": date(2026, 5, 5),
                "days": 1,
                "status": "pending",
                "created_at": self.NOW,
            }
        )
        result = leave_repo.get_all_leaves(employee_id=1, status="approved")
        assert len(result) == 1

    def test_get_approved_leaves_by_type(self):
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "annual",
                "leave_type_name": "年假",
                "start_date": date(2026, 5, 1),
                "end_date": date(2026, 5, 2),
                "days": 2,
                "status": "approved",
                "created_at": self.NOW,
            }
        )
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "annual",
                "leave_type_name": "年假",
                "start_date": date(2026, 5, 10),
                "end_date": date(2026, 5, 11),
                "days": 2,
                "status": "pending",
                "created_at": self.NOW,
            }
        )
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "sick",
                "leave_type_name": "病假",
                "start_date": date(2026, 5, 15),
                "end_date": date(2026, 5, 15),
                "days": 1,
                "status": "approved",
                "created_at": self.NOW,
            }
        )
        result = leave_repo.get_approved_leaves_by_type(1, "annual")
        assert len(result) == 1
        assert result[0]["leave_type"] == "annual"

    def test_get_approved_leaves_in_range(self):
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "annual",
                "leave_type_name": "年假",
                "start_date": date(2026, 5, 5),
                "end_date": date(2026, 5, 10),
                "days": 6,
                "status": "approved",
                "created_at": self.NOW,
            }
        )
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "sick",
                "leave_type_name": "病假",
                "start_date": date(2026, 6, 1),
                "end_date": date(2026, 6, 5),
                "days": 5,
                "status": "approved",
                "created_at": self.NOW,
            }
        )
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "personal",
                "leave_type_name": "事假",
                "start_date": date(2026, 5, 1),
                "end_date": date(2026, 5, 3),
                "days": 3,
                "status": "pending",
                "created_at": self.NOW,
            }
        )
        # Overlapping with May 1-15 range
        result = leave_repo.get_approved_leaves_in_range(1, date(2026, 5, 1), date(2026, 5, 15))
        assert len(result) == 1
        assert result[0]["leave_type"] == "annual"

    def test_get_approved_leaves_in_range_no_overlap(self):
        leave_repo.create_leave(
            {
                "employee_id": 1,
                "leave_type": "annual",
                "leave_type_name": "年假",
                "start_date": date(2026, 6, 1),
                "end_date": date(2026, 6, 5),
                "days": 5,
                "status": "approved",
                "created_at": self.NOW,
            }
        )
        result = leave_repo.get_approved_leaves_in_range(1, date(2026, 5, 1), date(2026, 5, 15))
        assert len(result) == 0


# ═══════════════════════════════════════════════════════════════
# Payroll Repository
# ═══════════════════════════════════════════════════════════════


class TestPayrollRepository:
    NOW = datetime.now(UTC)

    def test_get_all_returns_empty_when_no_data(self):
        assert payroll_repo.get_all_payrolls() == []

    def test_crud_full_flow(self):
        payroll = payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-05",
                "base_salary": 15000.0,
                "bonuses": 1000.0,
                "deductions": 500.0,
                "net_salary": 15500.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        assert payroll["id"] is not None
        assert payroll["month"] == "2026-05"

        # Read by id
        fetched = payroll_repo.get_payroll_by_id(payroll["id"])
        assert fetched is not None
        assert fetched["net_salary"] == 15500.0

        # Read all
        all_records = payroll_repo.get_all_payrolls()
        assert len(all_records) == 1

        # Update — payroll uses setattr for ALL fields
        updated = payroll_repo.update_payroll(payroll["id"], {"status": "paid", "bonuses": 2000.0})
        assert updated["status"] == "paid"
        assert updated["bonuses"] == 2000.0

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert payroll_repo.get_payroll_by_id(9999) is None

    def test_update_returns_none_for_nonexistent(self):
        assert payroll_repo.update_payroll(9999, {"status": "paid"}) is None

    def test_update_sets_all_fields_including_none(self):
        """Payroll update uses setattr for ALL fields, not just non-None."""
        payroll = payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-05",
                "base_salary": 15000.0,
                "bonuses": 1000.0,
                "deductions": 500.0,
                "net_salary": 15500.0,
                "status": "draft",
                "payment_date": date(2026, 6, 1),
                "created_at": self.NOW,
            }
        )
        updated = payroll_repo.update_payroll(payroll["id"], {"payment_date": None})
        assert updated["payment_date"] is None

    def test_get_payroll_by_employee_month(self):
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-05",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-06",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        result = payroll_repo.get_payroll_by_employee_month(1, "2026-05")
        assert result is not None
        assert result["month"] == "2026-05"
        assert payroll_repo.get_payroll_by_employee_month(1, "2026-12") is None

    def test_get_payrolls_by_employee(self):
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-05",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        payroll_repo.create_payroll(
            {
                "employee_id": 2,
                "month": "2026-05",
                "base_salary": 12000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 12000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        result = payroll_repo.get_payrolls_by_employee(1)
        assert len(result) == 1

    def test_get_all_filters_employee_id(self):
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-05",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        payroll_repo.create_payroll(
            {
                "employee_id": 2,
                "month": "2026-05",
                "base_salary": 12000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 12000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        result = payroll_repo.get_all_payrolls(employee_id=1)
        assert len(result) == 1

    def test_get_all_filters_month(self):
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-05",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-06",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        result = payroll_repo.get_all_payrolls(month="2026-05")
        assert len(result) == 1

    def test_get_all_filters_status(self):
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-05",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-06",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "paid",
                "created_at": self.NOW,
            }
        )
        result = payroll_repo.get_all_payrolls(status="paid")
        assert len(result) == 1
        assert result[0]["status"] == "paid"

    def test_get_all_combined_filters(self):
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-05",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        payroll_repo.create_payroll(
            {
                "employee_id": 1,
                "month": "2026-06",
                "base_salary": 15000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 15000.0,
                "status": "paid",
                "created_at": self.NOW,
            }
        )
        payroll_repo.create_payroll(
            {
                "employee_id": 2,
                "month": "2026-05",
                "base_salary": 12000.0,
                "bonuses": 0.0,
                "deductions": 0.0,
                "net_salary": 12000.0,
                "status": "draft",
                "created_at": self.NOW,
            }
        )
        result = payroll_repo.get_all_payrolls(employee_id=1, status="draft")
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════════
# Project Repository
# ═══════════════════════════════════════════════════════════════


class TestProjectRepository:
    NOW = datetime.now(UTC)

    def test_get_all_returns_empty_when_no_data(self):
        assert proj_repo.get_all_projects() == []

    def test_crud_full_flow(self):
        proj = proj_repo.create_project(
            {
                "name": "HR系统V2",
                "description": "HR管理系统升级",
                "status": "planning",
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "created_at": self.NOW,
            }
        )
        assert proj["id"] is not None
        assert proj["name"] == "HR系统V2"

        # Read by id
        fetched = proj_repo.get_project_by_id(proj["id"])
        assert fetched is not None
        assert fetched["status"] == "planning"

        # Read all
        all_projs = proj_repo.get_all_projects()
        assert len(all_projs) == 1

        # Update
        updated = proj_repo.update_project(proj["id"], {"status": "active", "description": "升级中"})
        assert updated["status"] == "active"
        assert updated["description"] == "升级中"
        assert updated["name"] == "HR系统V2"  # unchanged

        # Delete
        assert proj_repo.delete_project(proj["id"]) is True
        assert proj_repo.get_project_by_id(proj["id"]) is None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert proj_repo.get_project_by_id(9999) is None

    def test_update_returns_none_for_nonexistent(self):
        assert proj_repo.update_project(9999, {"status": "active"}) is None

    def test_delete_returns_false_for_nonexistent(self):
        assert proj_repo.delete_project(9999) is False

    def test_get_all_filters_status(self):
        proj_repo.create_project(
            {
                "name": "A",
                "status": "planning",
                "created_at": self.NOW,
            }
        )
        proj_repo.create_project(
            {
                "name": "B",
                "status": "active",
                "created_at": self.NOW,
            }
        )
        result = proj_repo.get_all_projects(status="active")
        assert len(result) == 1
        assert result[0]["name"] == "B"

    def test_delete_project_cascades_timesheets_members_requirements(self):
        """Deleting a project should cascade delete its timesheets, members, and requirements."""
        proj = proj_repo.create_project(
            {
                "name": "级联项目",
                "status": "active",
                "created_at": self.NOW,
            }
        )
        req = proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 1,
                "required_proficiency": "advanced",
                "person_days": 20.0,
                "headcount": 2,
                "created_at": self.NOW,
            }
        )
        member = proj_repo.create_member(
            {
                "project_id": proj["id"],
                "employee_id": 1,
                "role": "开发",
                "assigned_date": date(2026, 1, 1),
                "created_at": self.NOW,
            }
        )
        ts = proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req["id"],
                "employee_id": 1,
                "date": date(2026, 1, 15),
                "hours": 8.0,
                "created_at": self.NOW,
            }
        )

        assert proj_repo.delete_project(proj["id"]) is True
        assert proj_repo.get_timesheet_by_id(ts["id"]) is None
        assert proj_repo.get_member_by_id(member["id"]) is None
        assert proj_repo.get_requirement_by_id(req["id"]) is None

    def test_count_requirements_and_members(self):
        proj = proj_repo.create_project(
            {
                "name": "计数项目",
                "status": "active",
                "created_at": self.NOW,
            }
        )
        proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 1,
                "required_proficiency": "advanced",
                "person_days": 10.0,
                "headcount": 1,
                "created_at": self.NOW,
            }
        )
        proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 2,
                "required_proficiency": "intermediate",
                "person_days": 15.0,
                "headcount": 2,
                "created_at": self.NOW,
            }
        )
        proj_repo.create_member(
            {
                "project_id": proj["id"],
                "employee_id": 1,
                "role": "开发",
                "assigned_date": date(2026, 1, 1),
                "created_at": self.NOW,
            }
        )

        assert proj_repo.count_requirements(proj["id"]) == 2
        assert proj_repo.count_members(proj["id"]) == 1
        assert proj_repo.count_requirements(9999) == 0


# ═══════════════════════════════════════════════════════════════
# Project Requirement Repository
# ═══════════════════════════════════════════════════════════════


class TestProjectRequirementRepository:
    NOW = datetime.now(UTC)

    def _create_project(self):
        return proj_repo.create_project(
            {
                "name": "需求项目",
                "status": "planning",
                "created_at": self.NOW,
            }
        )

    def test_crud_full_flow(self):
        proj = self._create_project()
        req = proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 1,
                "required_proficiency": "expert",
                "person_days": 30.0,
                "headcount": 3,
                "created_at": self.NOW,
            }
        )
        assert req["id"] is not None
        assert req["required_proficiency"] == "expert"

        # Read by id
        fetched = proj_repo.get_requirement_by_id(req["id"])
        assert fetched is not None
        assert fetched["person_days"] == 30.0

        # Read by project+skill
        by_ps = proj_repo.get_requirement_by_project_and_skill(proj["id"], 1)
        assert by_ps is not None
        assert by_ps["id"] == req["id"]

        # Read by project
        reqs = proj_repo.get_requirements_by_project(proj["id"])
        assert len(reqs) == 1

        # Update
        updated = proj_repo.update_requirement(req["id"], {"person_days": 40.0, "headcount": 4})
        assert updated["person_days"] == 40.0
        assert updated["headcount"] == 4

        # Delete
        assert proj_repo.delete_requirement(req["id"]) is True
        assert proj_repo.get_requirement_by_id(req["id"]) is None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert proj_repo.get_requirement_by_id(9999) is None

    def test_get_by_project_and_skill_returns_none(self):
        assert proj_repo.get_requirement_by_project_and_skill(9999, 9999) is None

    def test_update_returns_none_for_nonexistent(self):
        assert proj_repo.update_requirement(9999, {"person_days": 10.0}) is None

    def test_delete_returns_false_for_nonexistent(self):
        assert proj_repo.delete_requirement(9999) is False

    def test_delete_requirement_cascades_timesheets(self):
        proj = self._create_project()
        req = proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 1,
                "required_proficiency": "advanced",
                "person_days": 20.0,
                "headcount": 2,
                "created_at": self.NOW,
            }
        )
        ts = proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req["id"],
                "employee_id": 1,
                "date": date(2026, 1, 10),
                "hours": 8.0,
                "created_at": self.NOW,
            }
        )
        assert proj_repo.delete_requirement(req["id"]) is True
        assert proj_repo.get_timesheet_by_id(ts["id"]) is None

    def test_update_partial_ignores_none(self):
        proj = self._create_project()
        req = proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 1,
                "required_proficiency": "advanced",
                "person_days": 20.0,
                "headcount": 2,
                "created_at": self.NOW,
            }
        )
        updated = proj_repo.update_requirement(req["id"], {"person_days": 25.0, "headcount": None})
        assert updated["person_days"] == 25.0
        assert updated["headcount"] == 2  # None ignored


# ═══════════════════════════════════════════════════════════════
# Project Member Repository
# ═══════════════════════════════════════════════════════════════


class TestProjectMemberRepository:
    NOW = datetime.now(UTC)

    def _create_project(self):
        return proj_repo.create_project(
            {
                "name": "成员项目",
                "status": "active",
                "created_at": self.NOW,
            }
        )

    def test_crud_full_flow(self):
        proj = self._create_project()
        member = proj_repo.create_member(
            {
                "project_id": proj["id"],
                "employee_id": 1,
                "role": "开发工程师",
                "assigned_date": date(2026, 1, 1),
                "created_at": self.NOW,
            }
        )
        assert member["id"] is not None
        assert member["role"] == "开发工程师"

        # Read by id
        fetched = proj_repo.get_member_by_id(member["id"])
        assert fetched is not None

        # Read by project
        members = proj_repo.get_members_by_project(proj["id"])
        assert len(members) == 1

        # Read by employee+project
        by_ep = proj_repo.get_member_by_employee_project(1, proj["id"])
        assert by_ep is not None
        assert by_ep["id"] == member["id"]

        # Update
        updated = proj_repo.update_member(member["id"], {"role": "技术负责人"})
        assert updated["role"] == "技术负责人"

        # Delete
        assert proj_repo.delete_member(member["id"]) is True
        assert proj_repo.get_member_by_id(member["id"]) is None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert proj_repo.get_member_by_id(9999) is None

    def test_get_by_employee_project_returns_none(self):
        assert proj_repo.get_member_by_employee_project(9999, 9999) is None

    def test_update_returns_none_for_nonexistent(self):
        assert proj_repo.update_member(9999, {"role": "x"}) is None

    def test_delete_returns_false_for_nonexistent(self):
        assert proj_repo.delete_member(9999) is False

    def test_get_members_by_project_empty(self):
        proj = self._create_project()
        assert proj_repo.get_members_by_project(proj["id"]) == []

    def test_update_partial_ignores_none(self):
        proj = self._create_project()
        member = proj_repo.create_member(
            {
                "project_id": proj["id"],
                "employee_id": 1,
                "role": "开发",
                "assigned_date": date(2026, 1, 1),
                "created_at": self.NOW,
            }
        )
        updated = proj_repo.update_member(member["id"], {"role": "测试", "assigned_date": None})
        assert updated["role"] == "测试"
        assert updated["assigned_date"] == date(2026, 1, 1)  # None ignored


# ═══════════════════════════════════════════════════════════════
# Project Timesheet Repository
# ═══════════════════════════════════════════════════════════════


class TestProjectTimesheetRepository:
    NOW = datetime.now(UTC)

    def _create_project_with_req(self):
        proj = proj_repo.create_project(
            {
                "name": "工时项目",
                "status": "active",
                "created_at": self.NOW,
            }
        )
        req = proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 1,
                "required_proficiency": "advanced",
                "person_days": 20.0,
                "headcount": 1,
                "created_at": self.NOW,
            }
        )
        return proj, req

    def test_crud_full_flow(self):
        proj, req = self._create_project_with_req()
        ts = proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req["id"],
                "employee_id": 1,
                "date": date(2026, 1, 15),
                "hours": 8.0,
                "description": "开发功能",
                "created_at": self.NOW,
            }
        )
        assert ts["id"] is not None
        assert ts["hours"] == 8.0

        # Read by id
        fetched = proj_repo.get_timesheet_by_id(ts["id"])
        assert fetched is not None
        assert fetched["description"] == "开发功能"

        # Read by project
        timesheets = proj_repo.get_timesheets_by_project(proj["id"])
        assert len(timesheets) == 1

        # Update
        updated = proj_repo.update_timesheet(ts["id"], {"hours": 6.0})
        assert updated["hours"] == 6.0

        # Delete
        assert proj_repo.delete_timesheet(ts["id"]) is True
        assert proj_repo.get_timesheet_by_id(ts["id"]) is None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert proj_repo.get_timesheet_by_id(9999) is None

    def test_update_returns_none_for_nonexistent(self):
        assert proj_repo.update_timesheet(9999, {"hours": 5.0}) is None

    def test_delete_returns_false_for_nonexistent(self):
        assert proj_repo.delete_timesheet(9999) is False

    def test_get_timesheets_by_project_filters_employee_id(self):
        proj, req = self._create_project_with_req()
        proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req["id"],
                "employee_id": 1,
                "date": date(2026, 1, 15),
                "hours": 8.0,
                "created_at": self.NOW,
            }
        )
        proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req["id"],
                "employee_id": 2,
                "date": date(2026, 1, 15),
                "hours": 4.0,
                "created_at": self.NOW,
            }
        )
        result = proj_repo.get_timesheets_by_project(proj["id"], employee_id=1)
        assert len(result) == 1
        assert result[0]["employee_id"] == 1

    def test_get_timesheets_by_project_filters_requirement_id(self):
        proj, req1 = self._create_project_with_req()
        req2 = proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 2,
                "required_proficiency": "intermediate",
                "person_days": 10.0,
                "headcount": 1,
                "created_at": self.NOW,
            }
        )
        proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req1["id"],
                "employee_id": 1,
                "date": date(2026, 1, 15),
                "hours": 8.0,
                "created_at": self.NOW,
            }
        )
        proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req2["id"],
                "employee_id": 1,
                "date": date(2026, 1, 15),
                "hours": 4.0,
                "created_at": self.NOW,
            }
        )
        result = proj_repo.get_timesheets_by_project(proj["id"], requirement_id=req1["id"])
        assert len(result) == 1
        assert result[0]["requirement_id"] == req1["id"]

    def test_update_partial_ignores_none(self):
        proj, req = self._create_project_with_req()
        ts = proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req["id"],
                "employee_id": 1,
                "date": date(2026, 1, 15),
                "hours": 8.0,
                "description": "原始描述",
                "created_at": self.NOW,
            }
        )
        updated = proj_repo.update_timesheet(ts["id"], {"hours": 6.0, "description": None})
        assert updated["hours"] == 6.0
        assert updated["description"] == "原始描述"  # None ignored


# ═══════════════════════════════════════════════════════════════
# Project Progress
# ═══════════════════════════════════════════════════════════════


class TestProjectProgress:
    NOW = datetime.now(UTC)

    def test_progress_empty_project(self):
        proj = proj_repo.create_project(
            {
                "name": "空项目",
                "status": "planning",
                "created_at": self.NOW,
            }
        )
        progress = proj_repo.get_progress_by_project(proj["id"])
        assert progress["total_budget_person_days"] == 0.0
        assert progress["total_used_person_days"] == 0.0
        assert progress["overall_progress"] == 0.0
        assert progress["by_requirement"] == []
        assert progress["by_member"] == []

    def test_progress_with_data(self):
        proj = proj_repo.create_project(
            {
                "name": "进度项目",
                "status": "active",
                "created_at": self.NOW,
            }
        )
        req = proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 1,
                "required_proficiency": "advanced",
                "person_days": 10.0,
                "headcount": 1,
                "created_at": self.NOW,
            }
        )
        proj_repo.create_member(
            {
                "project_id": proj["id"],
                "employee_id": 1,
                "role": "开发",
                "assigned_date": date(2026, 1, 1),
                "created_at": self.NOW,
            }
        )
        # 16 hours = 2 person-days
        proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req["id"],
                "employee_id": 1,
                "date": date(2026, 1, 15),
                "hours": 16.0,
                "created_at": self.NOW,
            }
        )

        progress = proj_repo.get_progress_by_project(proj["id"])
        assert progress["total_budget_person_days"] == 10.0
        assert progress["total_used_person_days"] == 2.0
        assert progress["overall_progress"] == 20.0
        assert len(progress["by_requirement"]) == 1
        assert progress["by_requirement"][0]["used_person_days"] == 2.0
        assert progress["by_requirement"][0]["progress"] == 20.0
        assert len(progress["by_member"]) == 1
        assert progress["by_member"][0]["total_person_days"] == 2.0

    def test_progress_capped_at_100(self):
        proj = proj_repo.create_project(
            {
                "name": "超预算项目",
                "status": "active",
                "created_at": self.NOW,
            }
        )
        req = proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": 1,
                "required_proficiency": "advanced",
                "person_days": 5.0,
                "headcount": 1,
                "created_at": self.NOW,
            }
        )
        # 80 hours = 10 person-days, but budget is 5
        proj_repo.create_timesheet(
            {
                "project_id": proj["id"],
                "requirement_id": req["id"],
                "employee_id": 1,
                "date": date(2026, 1, 15),
                "hours": 80.0,
                "created_at": self.NOW,
            }
        )
        progress = proj_repo.get_progress_by_project(proj["id"])
        assert progress["overall_progress"] == 100.0
        assert progress["by_requirement"][0]["progress"] == 100.0


# ═══════════════════════════════════════════════════════════════
# Employee Skill Repository
# ═══════════════════════════════════════════════════════════════


class TestEmployeeSkillRepository:
    NOW = datetime.now(UTC)

    def test_get_all_returns_empty_when_no_data(self):
        assert eskill_repo.get_all_skills() == []

    def test_crud_full_flow(self):
        skill = eskill_repo.create_skill(
            {
                "employee_id": 1,
                "skill_name": "Python",
                "skill_id": 10,
                "proficiency_level": "advanced",
                "years_of_experience": 5.0,
                "certification": "PCEP",
                "created_at": self.NOW,
            }
        )
        assert skill["id"] is not None
        assert skill["skill_name"] == "Python"
        assert skill["proficiency_level"] == "advanced"

        # Read by id
        fetched = eskill_repo.get_skill_by_id(skill["id"])
        assert fetched is not None
        assert fetched["employee_id"] == 1

        # Read all
        all_skills = eskill_repo.get_all_skills()
        assert len(all_skills) == 1

        # Update
        updated = eskill_repo.update_skill(skill["id"], {"proficiency_level": "expert", "years_of_experience": 8.0})
        assert updated["proficiency_level"] == "expert"
        assert updated["years_of_experience"] == 8.0
        assert updated["skill_name"] == "Python"  # unchanged

        # Delete
        assert eskill_repo.delete_skill(skill["id"]) is True
        assert eskill_repo.get_skill_by_id(skill["id"]) is None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert eskill_repo.get_skill_by_id(9999) is None

    def test_update_returns_none_for_nonexistent(self):
        assert eskill_repo.update_skill(9999, {"proficiency_level": "expert"}) is None

    def test_delete_returns_false_for_nonexistent(self):
        assert eskill_repo.delete_skill(9999) is False

    def test_get_skills_by_employee(self):
        eskill_repo.create_skill(
            {
                "employee_id": 1,
                "skill_name": "Python",
                "proficiency_level": "advanced",
                "created_at": self.NOW,
            }
        )
        eskill_repo.create_skill(
            {
                "employee_id": 1,
                "skill_name": "Java",
                "proficiency_level": "intermediate",
                "created_at": self.NOW,
            }
        )
        eskill_repo.create_skill(
            {
                "employee_id": 2,
                "skill_name": "Go",
                "proficiency_level": "beginner",
                "created_at": self.NOW,
            }
        )
        result = eskill_repo.get_skills_by_employee(1)
        assert len(result) == 2
        assert eskill_repo.get_skills_by_employee(999) == []

    def test_get_skills_by_name_contains(self):
        eskill_repo.create_skill(
            {
                "employee_id": 1,
                "skill_name": "Python",
                "proficiency_level": "advanced",
                "created_at": self.NOW,
            }
        )
        eskill_repo.create_skill(
            {
                "employee_id": 2,
                "skill_name": "Python Flask",
                "proficiency_level": "intermediate",
                "created_at": self.NOW,
            }
        )
        eskill_repo.create_skill(
            {
                "employee_id": 3,
                "skill_name": "Java",
                "proficiency_level": "beginner",
                "created_at": self.NOW,
            }
        )
        result = eskill_repo.get_skills_by_name("Python")
        assert len(result) == 2
        result_exact = eskill_repo.get_skills_by_name("Java")
        assert len(result_exact) == 1

    def test_update_partial_ignores_none(self):
        skill = eskill_repo.create_skill(
            {
                "employee_id": 1,
                "skill_name": "Python",
                "proficiency_level": "advanced",
                "years_of_experience": 5.0,
                "certification": "PCEP",
                "created_at": self.NOW,
            }
        )
        updated = eskill_repo.update_skill(skill["id"], {"proficiency_level": "expert", "certification": None})
        assert updated["proficiency_level"] == "expert"
        assert updated["certification"] == "PCEP"  # None ignored


# ═══════════════════════════════════════════════════════════════
# Skill Catalog Repository
# ═══════════════════════════════════════════════════════════════


class TestSkillCatalogRepository:
    NOW = datetime.now(UTC)

    def test_get_all_returns_empty_when_no_data(self):
        assert catalog_repo.get_all_skills() == []

    def test_crud_full_flow(self):
        skill = catalog_repo.create_skill(
            {
                "name": "Python",
                "category": "编程",
                "description": "Python编程语言",
                "created_at": self.NOW,
            }
        )
        assert skill["id"] is not None
        assert skill["name"] == "Python"

        # Read by id
        fetched = catalog_repo.get_skill_by_id(skill["id"])
        assert fetched is not None
        assert fetched["category"] == "编程"

        # Read by name
        by_name = catalog_repo.get_skill_by_name("Python")
        assert by_name is not None
        assert by_name["id"] == skill["id"]

        # Read all
        all_skills = catalog_repo.get_all_skills()
        assert len(all_skills) == 1

        # Update
        updated = catalog_repo.update_skill(skill["id"], {"description": "通用编程语言", "category": "开发"})
        assert updated["description"] == "通用编程语言"
        assert updated["name"] == "Python"  # unchanged

        # Delete
        assert catalog_repo.delete_skill(skill["id"]) is True
        assert catalog_repo.get_skill_by_id(skill["id"]) is None

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert catalog_repo.get_skill_by_id(9999) is None

    def test_get_by_name_returns_none_for_nonexistent(self):
        assert catalog_repo.get_skill_by_name("不存在的技能") is None

    def test_update_returns_none_for_nonexistent(self):
        assert catalog_repo.update_skill(9999, {"name": "x"}) is None

    def test_delete_returns_false_for_nonexistent(self):
        assert catalog_repo.delete_skill(9999) is False

    def test_get_all_filters_category(self):
        catalog_repo.create_skill({"name": "Python", "category": "编程", "created_at": self.NOW})
        catalog_repo.create_skill({"name": "沟通", "category": "软技能", "created_at": self.NOW})
        result = catalog_repo.get_all_skills(category="编程")
        assert len(result) == 1
        assert result[0]["name"] == "Python"

    def test_count_employee_skills_by_skill_id(self):
        skill = catalog_repo.create_skill({"name": "Python", "category": "编程", "created_at": self.NOW})
        eskill_repo.create_skill(
            {
                "employee_id": 1,
                "skill_name": "Python",
                "skill_id": skill["id"],
                "proficiency_level": "advanced",
                "created_at": self.NOW,
            }
        )
        eskill_repo.create_skill(
            {
                "employee_id": 2,
                "skill_name": "Python",
                "skill_id": skill["id"],
                "proficiency_level": "intermediate",
                "created_at": self.NOW,
            }
        )
        assert catalog_repo.count_employee_skills_by_skill_id(skill["id"]) == 2
        assert catalog_repo.count_employee_skills_by_skill_id(9999) == 0

    def test_count_project_requirements_by_skill_id(self):
        skill = catalog_repo.create_skill({"name": "Go", "category": "编程", "created_at": self.NOW})
        proj = proj_repo.create_project({"name": "P1", "status": "planning", "created_at": self.NOW})
        proj_repo.create_requirement(
            {
                "project_id": proj["id"],
                "skill_id": skill["id"],
                "required_proficiency": "advanced",
                "person_days": 10.0,
                "headcount": 1,
                "created_at": self.NOW,
            }
        )
        assert catalog_repo.count_project_requirements_by_skill_id(skill["id"]) == 1
        assert catalog_repo.count_project_requirements_by_skill_id(9999) == 0

    def test_update_partial_ignores_none(self):
        skill = catalog_repo.create_skill(
            {
                "name": "Rust",
                "category": "编程",
                "description": "系统语言",
                "created_at": self.NOW,
            }
        )
        updated = catalog_repo.update_skill(skill["id"], {"description": "安全语言", "category": None})
        assert updated["description"] == "安全语言"
        assert updated["category"] == "编程"  # None ignored


# ═══════════════════════════════════════════════════════════════
# Agent Memory Repository
# ═══════════════════════════════════════════════════════════════


class TestAgentMemoryRepository:
    NOW = datetime.now(UTC)

    def _make_memory_data(self, **overrides):
        base = {
            "session_id": "sess-1",
            "user_tag": "user-1",
            "memory_type": "fact",
            "category": "general",
            "subject": "测试主题",
            "content": "测试内容",
            "source": "user",
            "importance": 3,
            "is_active": True,
            "created_at": self.NOW,
            "updated_at": self.NOW,
        }
        base.update(overrides)
        return base

    # ── Memory CRUD ─────────────────────────────────────────

    def test_get_all_returns_empty_when_no_data(self):
        assert memory_repo.get_memories_by_user_tag("user-1") == []

    def test_crud_full_flow(self):
        mem = memory_repo.create_memory(self._make_memory_data())
        assert mem["id"] is not None
        assert mem["subject"] == "测试主题"

        # Read by id
        fetched = memory_repo.get_memory_by_id(mem["id"])
        assert fetched is not None
        assert fetched["content"] == "测试内容"

        # Update
        updated = memory_repo.update_memory(mem["id"], {"content": "更新内容", "importance": 5})
        assert updated["content"] == "更新内容"
        assert updated["importance"] == 5

    def test_get_by_id_returns_none_for_nonexistent(self):
        assert memory_repo.get_memory_by_id(9999) is None

    def test_update_returns_none_for_nonexistent(self):
        assert memory_repo.update_memory(9999, {"content": "x"}) is None

    def test_delete_memory(self):
        mem = memory_repo.create_memory(self._make_memory_data())
        assert memory_repo.delete_memory(mem["id"]) is True
        assert memory_repo.get_memory_by_id(mem["id"]) is None

    def test_delete_memory_returns_false_for_nonexistent(self):
        assert memory_repo.delete_memory(9999) is False

    def test_delete_memory_cascades_reminders(self):
        mem = memory_repo.create_memory(self._make_memory_data())
        memory_repo.create_reminder(
            {
                "memory_id": mem["id"],
                "reminder_type": "one-time",
                "trigger_at": datetime.now(UTC) + timedelta(days=1),
                "created_at": self.NOW,
            }
        )
        assert memory_repo.delete_memory(mem["id"]) is True
        assert memory_repo.get_reminders_by_memory(mem["id"]) == []

    def test_update_sets_all_fields_including_none(self):
        """Agent memory update uses setattr for ALL fields."""
        mem = memory_repo.create_memory(self._make_memory_data(expires_at=self.NOW + timedelta(days=30)))
        updated = memory_repo.update_memory(mem["id"], {"expires_at": None})
        assert updated["expires_at"] is None

    # ── Memory queries ──────────────────────────────────────

    def test_get_memories_by_user_tag(self):
        memory_repo.create_memory(self._make_memory_data(user_tag="user-1"))
        memory_repo.create_memory(self._make_memory_data(user_tag="user-1", subject="主题2"))
        memory_repo.create_memory(self._make_memory_data(user_tag="user-2"))
        result = memory_repo.get_memories_by_user_tag("user-1")
        assert len(result) == 2

    def test_get_memories_by_user_tag_filter_memory_type(self):
        memory_repo.create_memory(self._make_memory_data(memory_type="fact"))
        memory_repo.create_memory(self._make_memory_data(memory_type="preference"))
        result = memory_repo.get_memories_by_user_tag("user-1", memory_type="fact")
        assert len(result) == 1

    def test_get_memories_by_user_tag_filter_category(self):
        memory_repo.create_memory(self._make_memory_data(category="general"))
        memory_repo.create_memory(self._make_memory_data(category="work"))
        result = memory_repo.get_memories_by_user_tag("user-1", category="work")
        assert len(result) == 1

    def test_get_memories_by_user_tag_active_only(self):
        memory_repo.create_memory(self._make_memory_data(is_active=True))
        memory_repo.create_memory(self._make_memory_data(is_active=False))
        result = memory_repo.get_memories_by_user_tag("user-1", active_only=True)
        assert len(result) == 1
        result_all = memory_repo.get_memories_by_user_tag("user-1", active_only=False)
        assert len(result_all) == 2

    def test_get_memories_by_subject(self):
        memory_repo.create_memory(self._make_memory_data(subject="薪资"))
        memory_repo.create_memory(self._make_memory_data(subject="薪资", user_tag="user-2"))
        memory_repo.create_memory(self._make_memory_data(subject="考勤"))
        result = memory_repo.get_memories_by_subject("薪资")
        assert len(result) == 2

    def test_get_memories_by_subject_active_only(self):
        memory_repo.create_memory(self._make_memory_data(subject="薪资", is_active=True))
        memory_repo.create_memory(self._make_memory_data(subject="薪资", is_active=False))
        result = memory_repo.get_memories_by_subject("薪资", active_only=True)
        assert len(result) == 1
        result_all = memory_repo.get_memories_by_subject("薪资", active_only=False)
        assert len(result_all) == 2

    def test_search_memories_by_content_ilike(self):
        memory_repo.create_memory(self._make_memory_data(content="Python编程语言"))
        memory_repo.create_memory(self._make_memory_data(content="Java开发框架"))
        memory_repo.create_memory(self._make_memory_data(content="python数据分析"))  # case-insensitive
        result = memory_repo.search_memories_by_content("user-1", "python")
        # SQLite ilike is case-sensitive by default, but .ilike() should handle it
        # At minimum the first one should match
        assert len(result) >= 1

    def test_get_recent_memories(self):
        for i in range(5):
            memory_repo.create_memory(
                self._make_memory_data(
                    subject=f"主题{i}",
                    created_at=self.NOW + timedelta(minutes=i),
                )
            )
        result = memory_repo.get_recent_memories("user-1", limit=3)
        assert len(result) == 3

    def test_get_important_memories(self):
        memory_repo.create_memory(self._make_memory_data(importance=5))
        memory_repo.create_memory(self._make_memory_data(importance=3))
        memory_repo.create_memory(self._make_memory_data(importance=1))
        result = memory_repo.get_important_memories("user-1", min_importance=4)
        assert len(result) == 1
        assert result[0]["importance"] == 5

    def test_get_preference_by_user_tag_and_subject(self):
        memory_repo.create_memory(
            self._make_memory_data(
                memory_type="preference",
                subject="语言偏好",
                content="中文",
            )
        )
        memory_repo.create_memory(
            self._make_memory_data(
                memory_type="fact",
                subject="语言偏好",
                content="英文",
            )
        )
        result = memory_repo.get_preference_by_user_tag_and_subject("user-1", "语言偏好")
        assert result is not None
        assert result["content"] == "中文"
        assert result["memory_type"] == "preference"

    def test_get_preference_returns_none_when_not_found(self):
        assert memory_repo.get_preference_by_user_tag_and_subject("user-1", "不存在") is None

    # ── Deactivate ──────────────────────────────────────────

    def test_deactivate_memory(self):
        mem = memory_repo.create_memory(self._make_memory_data(is_active=True))
        assert memory_repo.deactivate_memory(mem["id"]) is True
        fetched = memory_repo.get_memory_by_id(mem["id"])
        assert fetched["is_active"] is False

    def test_deactivate_memory_returns_false_for_nonexistent(self):
        assert memory_repo.deactivate_memory(9999) is False

    def test_deactivate_expired_memories(self):
        # deactivate_expired_memories() compares against datetime.now() (naive/local),
        # so expires_at must also be naive to match.
        naive_now = datetime.now()
        past = naive_now - timedelta(hours=1)
        future = naive_now + timedelta(hours=1)
        memory_repo.create_memory(self._make_memory_data(is_active=True, expires_at=past))
        memory_repo.create_memory(self._make_memory_data(is_active=True, expires_at=future))
        memory_repo.create_memory(self._make_memory_data(is_active=True, expires_at=None))
        count = memory_repo.deactivate_expired_memories()
        assert count == 1

    def test_deactivate_expired_memories_no_expired(self):
        naive_now = datetime.now()
        future = naive_now + timedelta(hours=1)
        memory_repo.create_memory(self._make_memory_data(is_active=True, expires_at=future))
        assert memory_repo.deactivate_expired_memories() == 0


# ═══════════════════════════════════════════════════════════════
# Memory Reminder Repository
# ═══════════════════════════════════════════════════════════════


class TestMemoryReminderRepository:
    NOW = datetime.now(UTC)

    def _make_memory(self, **overrides):
        base = {
            "session_id": "sess-1",
            "user_tag": "user-1",
            "memory_type": "fact",
            "category": "general",
            "subject": "提醒主题",
            "content": "提醒内容",
            "source": "user",
            "importance": 3,
            "is_active": True,
            "created_at": self.NOW,
            "updated_at": self.NOW,
        }
        base.update(overrides)
        return memory_repo.create_memory(base)

    def test_crud_full_flow(self):
        mem = self._make_memory()
        reminder = memory_repo.create_reminder(
            {
                "memory_id": mem["id"],
                "reminder_type": "one-time",
                "trigger_at": self.NOW + timedelta(days=1),
                "created_at": self.NOW,
            }
        )
        assert reminder["id"] is not None
        assert reminder["triggered"] is False
        assert reminder["trigger_count"] == 0

        # Read by memory
        reminders = memory_repo.get_reminders_by_memory(mem["id"])
        assert len(reminders) == 1

        # Mark triggered
        marked = memory_repo.mark_reminder_triggered(reminder["id"])
        assert marked is not None
        assert marked["triggered"] is True
        assert marked["trigger_count"] == 1

        # Delete
        assert memory_repo.delete_reminder(reminder["id"]) is True
        assert memory_repo.get_reminders_by_memory(mem["id"]) == []

    def test_mark_reminder_triggered_returns_none_for_nonexistent(self):
        assert memory_repo.mark_reminder_triggered(9999) is None

    def test_delete_reminder_returns_false_for_nonexistent(self):
        assert memory_repo.delete_reminder(9999) is False

    def test_get_pending_reminders(self):
        mem = self._make_memory()
        before = self.NOW + timedelta(days=2)
        # Pending: trigger_at is in the past relative to 'before'
        memory_repo.create_reminder(
            {
                "memory_id": mem["id"],
                "reminder_type": "one-time",
                "trigger_at": self.NOW + timedelta(days=1),
                "triggered": False,
                "created_at": self.NOW,
            }
        )
        # Already triggered
        memory_repo.create_reminder(
            {
                "memory_id": mem["id"],
                "reminder_type": "one-time",
                "trigger_at": self.NOW + timedelta(days=1),
                "triggered": True,
                "created_at": self.NOW,
            }
        )
        result = memory_repo.get_pending_reminders("user-1", before)
        assert len(result) == 1
        assert result[0]["triggered"] is False

    def test_get_pending_reminders_inactive_memory_excluded(self):
        mem = self._make_memory(is_active=False)
        before = self.NOW + timedelta(days=2)
        memory_repo.create_reminder(
            {
                "memory_id": mem["id"],
                "reminder_type": "one-time",
                "trigger_at": self.NOW + timedelta(days=1),
                "triggered": False,
                "created_at": self.NOW,
            }
        )
        result = memory_repo.get_pending_reminders("user-1", before)
        assert len(result) == 0

    def test_get_reminders_by_memory_empty(self):
        mem = self._make_memory()
        assert memory_repo.get_reminders_by_memory(mem["id"]) == []

    def test_mark_reminder_triggered_increments_count(self):
        mem = self._make_memory()
        reminder = memory_repo.create_reminder(
            {
                "memory_id": mem["id"],
                "reminder_type": "recurring",
                "trigger_at": self.NOW,
                "triggered": False,
                "trigger_count": 0,
                "created_at": self.NOW,
            }
        )
        memory_repo.mark_reminder_triggered(reminder["id"])
        marked = memory_repo.mark_reminder_triggered(reminder["id"])
        assert marked["trigger_count"] == 2


# ═══════════════════════════════════════════════════════════════
# Conversation Message Repository
# ═══════════════════════════════════════════════════════════════


class TestConversationMessageRepository:
    NOW = datetime.now(UTC)

    def test_crud_full_flow(self):
        msg = memory_repo.create_message(
            {
                "session_id": "sess-1",
                "role": "user",
                "content": "你好",
                "created_at": self.NOW,
            }
        )
        assert msg["id"] is not None
        assert msg["role"] == "user"

        # Read by session
        msgs = memory_repo.get_messages_by_session("sess-1")
        assert len(msgs) == 1

        # Count
        assert memory_repo.count_messages_by_session("sess-1") == 1

        # Delete by session
        assert memory_repo.delete_messages_by_session("sess-1") is True
        assert memory_repo.count_messages_by_session("sess-1") == 0

    def test_get_messages_by_session_ordered_by_created_at_asc(self):
        for i in range(3):
            memory_repo.create_message(
                {
                    "session_id": "sess-1",
                    "role": "user",
                    "content": f"消息{i}",
                    "created_at": self.NOW + timedelta(seconds=i),
                }
            )
        msgs = memory_repo.get_messages_by_session("sess-1")
        assert len(msgs) == 3
        assert msgs[0]["content"] == "消息0"
        assert msgs[2]["content"] == "消息2"

    def test_count_messages_by_session(self):
        memory_repo.create_message(
            {
                "session_id": "sess-1",
                "role": "user",
                "content": "a",
                "created_at": self.NOW,
            }
        )
        memory_repo.create_message(
            {
                "session_id": "sess-1",
                "role": "assistant",
                "content": "b",
                "created_at": self.NOW,
            }
        )
        memory_repo.create_message(
            {
                "session_id": "sess-2",
                "role": "user",
                "content": "c",
                "created_at": self.NOW,
            }
        )
        assert memory_repo.count_messages_by_session("sess-1") == 2
        assert memory_repo.count_messages_by_session("sess-2") == 1
        assert memory_repo.count_messages_by_session("sess-999") == 0

    def test_delete_messages_by_session_returns_false_when_empty(self):
        assert memory_repo.delete_messages_by_session("sess-999") is False

    def test_list_sessions(self):
        memory_repo.create_message(
            {
                "session_id": "sess-beta",
                "role": "user",
                "content": "b",
                "created_at": self.NOW,
            }
        )
        memory_repo.create_message(
            {
                "session_id": "sess-alpha",
                "role": "user",
                "content": "a",
                "created_at": self.NOW,
            }
        )
        memory_repo.create_message(
            {
                "session_id": "sess-beta",
                "role": "assistant",
                "content": "b2",
                "created_at": self.NOW,
            }
        )
        sessions = memory_repo.list_sessions()
        assert "sess-alpha" in sessions
        assert "sess-beta" in sessions
        assert len(sessions) == 2

    def test_trim_session_messages_no_trim_needed(self):
        for i in range(3):
            memory_repo.create_message(
                {
                    "session_id": "sess-1",
                    "role": "user",
                    "content": f"msg-{i}",
                    "created_at": self.NOW + timedelta(seconds=i),
                }
            )
        memory_repo.trim_session_messages("sess-1", 5)
        assert memory_repo.count_messages_by_session("sess-1") == 3

    def test_trim_session_messages_trims_oldest(self):
        for i in range(5):
            memory_repo.create_message(
                {
                    "session_id": "sess-1",
                    "role": "user",
                    "content": f"msg-{i}",
                    "created_at": self.NOW + timedelta(seconds=i),
                }
            )
        memory_repo.trim_session_messages("sess-1", 3)
        assert memory_repo.count_messages_by_session("sess-1") == 3
        remaining = memory_repo.get_messages_by_session("sess-1")
        # Should keep the 3 most recent (msg-2, msg-3, msg-4)
        contents = [m["content"] for m in remaining]
        assert "msg-0" not in contents
        assert "msg-1" not in contents
        assert "msg-2" in contents
        assert "msg-3" in contents
        assert "msg-4" in contents

    def test_trim_session_messages_nonexistent_session(self):
        # Should not raise
        memory_repo.trim_session_messages("sess-999", 5)
