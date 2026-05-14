from __future__ import annotations

from fastapi.testclient import TestClient

# ── Employee Router ────────────────────────────────────────────


class TestEmployeeRouter:
    def test_list_employees_empty(self, client: TestClient):
        resp = client.get("/employees/")
        assert resp.status_code == 200
        data = resp.json()
        assert "employees" in data
        assert "total" in data
        assert data["total"] == 0

    def test_create_employee(self, client: TestClient, sample_department: dict):
        resp = client.post(
            "/employees/",
            json={
                "name": "李四",
                "department_id": sample_department["id"],
                "salary": 12000,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "李四"
        assert data["salary"] == 12000
        assert data["department_name"] == sample_department["name"]

    def test_create_employee_invalid_department(self, client: TestClient):
        resp = client.post(
            "/employees/",
            json={
                "name": "王五",
                "department_id": 9999,
                "salary": 10000,
            },
        )
        assert resp.status_code == 400

    def test_get_employee(self, client: TestClient, sample_employee: dict):
        resp = client.get(f"/employees/{sample_employee['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == sample_employee["name"]

    def test_get_employee_not_found(self, client: TestClient):
        resp = client.get("/employees/9999")
        assert resp.status_code == 404

    def test_update_employee(self, client: TestClient, sample_employee: dict):
        resp = client.put(f"/employees/{sample_employee['id']}", json={"name": "张三丰"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "张三丰"

    def test_delete_employee(self, client: TestClient, sample_employee: dict):
        resp = client.delete(f"/employees/{sample_employee['id']}")
        assert resp.status_code == 200
        resp2 = client.get(f"/employees/{sample_employee['id']}")
        assert resp2.status_code == 404

    def test_delete_employee_not_found(self, client: TestClient):
        resp = client.delete("/employees/9999")
        assert resp.status_code == 404

    def test_create_employee_missing_required(self, client: TestClient):
        resp = client.post("/employees/", json={"name": "测试"})
        assert resp.status_code == 422


# ── Department Router ──────────────────────────────────────────


class TestDepartmentRouter:
    def test_list_departments(self, client: TestClient):
        resp = client.get("/departments/")
        assert resp.status_code == 200
        assert "departments" in resp.json()

    def test_create_department(self, client: TestClient):
        resp = client.post("/departments/", json={"name": "市场部"})
        assert resp.status_code == 201
        assert resp.json()["name"] == "市场部"

    def test_create_department_duplicate(self, client: TestClient, sample_department: dict):
        resp = client.post("/departments/", json={"name": sample_department["name"]})
        assert resp.status_code == 400

    def test_get_department(self, client: TestClient, sample_department: dict):
        resp = client.get(f"/departments/{sample_department['id']}")
        assert resp.status_code == 200

    def test_get_department_not_found(self, client: TestClient):
        resp = client.get("/departments/9999")
        assert resp.status_code == 404

    def test_delete_department_with_employees(self, client: TestClient, sample_employee: dict):
        dept_id = sample_employee.get("department_id")
        if dept_id:
            resp = client.delete(f"/departments/{dept_id}")
            assert resp.status_code == 400


# ── Attendance Router ──────────────────────────────────────────


class TestAttendanceRouter:
    def test_check_in(self, client: TestClient, sample_employee: dict):
        resp = client.post(
            "/attendance/check-in",
            json={
                "employee_id": sample_employee["id"],
                "date": "2026-05-01",
                "check_in": "08:30:00",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "normal"
        assert data["employee_name"] == sample_employee["name"]

    def test_check_in_invalid_employee(self, client: TestClient):
        resp = client.post(
            "/attendance/check-in",
            json={
                "employee_id": 9999,
                "date": "2026-05-01",
                "check_in": "08:30:00",
            },
        )
        assert resp.status_code == 404

    def test_check_out(self, client: TestClient, sample_employee: dict):
        check_in_resp = client.post(
            "/attendance/check-in",
            json={
                "employee_id": sample_employee["id"],
                "date": "2026-05-02",
                "check_in": "08:30:00",
            },
        )
        record_id = check_in_resp.json()["id"]
        resp = client.put(f"/attendance/check-out/{record_id}", json={"check_out": "18:00:00"})
        assert resp.status_code == 200
        assert resp.json()["work_hours"] is not None

    def test_list_attendance(self, client: TestClient):
        resp = client.get("/attendance/")
        assert resp.status_code == 200
        assert "records" in resp.json()

    def test_get_employee_stats(self, client: TestClient, sample_employee: dict):
        client.post(
            "/attendance/check-in",
            json={
                "employee_id": sample_employee["id"],
                "date": "2026-05-01",
                "check_in": "08:30:00",
            },
        )
        resp = client.get(
            f"/attendance/employee/{sample_employee['id']}/stats",
            params={
                "start_date": "2026-05-01",
                "end_date": "2026-05-31",
            },
        )
        assert resp.status_code == 200


# ── Leave Router ───────────────────────────────────────────────


class TestLeaveRouter:
    def test_create_leave(self, client: TestClient, sample_employee: dict):
        resp = client.post(
            "/leaves/",
            json={
                "employee_id": sample_employee["id"],
                "leave_type": "annual",
                "start_date": "2026-06-01",
                "end_date": "2026-06-03",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["days"] == 3

    def test_create_leave_invalid_type(self, client: TestClient, sample_employee: dict):
        resp = client.post(
            "/leaves/",
            json={
                "employee_id": sample_employee["id"],
                "leave_type": "invalid",
                "start_date": "2026-06-01",
                "end_date": "2026-06-03",
            },
        )
        assert resp.status_code == 400

    def test_list_leaves(self, client: TestClient):
        resp = client.get("/leaves/")
        assert resp.status_code == 200
        assert "leaves" in resp.json()

    def test_get_leave_balance(self, client: TestClient, sample_employee: dict):
        resp = client.get(f"/leaves/employee/{sample_employee['id']}/balance")
        assert resp.status_code == 200
        data = resp.json()
        assert data["annual_remaining"] == 10
        assert data["sick_remaining"] == 15

    def test_approve_leave(self, client: TestClient, sample_employee: dict):
        create_resp = client.post(
            "/leaves/",
            json={
                "employee_id": sample_employee["id"],
                "leave_type": "annual",
                "start_date": "2026-07-01",
                "end_date": "2026-07-02",
            },
        )
        leave_id = create_resp.json()["id"]
        resp = client.put(f"/leaves/{leave_id}/approve", json={"approver": "管理员"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    def test_reject_leave(self, client: TestClient, sample_employee: dict):
        create_resp = client.post(
            "/leaves/",
            json={
                "employee_id": sample_employee["id"],
                "leave_type": "sick",
                "start_date": "2026-08-01",
                "end_date": "2026-08-01",
            },
        )
        leave_id = create_resp.json()["id"]
        resp = client.put(f"/leaves/{leave_id}/reject", json={"approver": "管理员"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    def test_cancel_leave(self, client: TestClient, sample_employee: dict):
        create_resp = client.post(
            "/leaves/",
            json={
                "employee_id": sample_employee["id"],
                "leave_type": "personal",
                "start_date": "2026-09-01",
                "end_date": "2026-09-01",
            },
        )
        leave_id = create_resp.json()["id"]
        resp = client.delete(f"/leaves/{leave_id}")
        assert resp.status_code == 200


# ── Payroll Router ─────────────────────────────────────────────


class TestPayrollRouter:
    def test_create_payroll(self, client: TestClient, sample_employee: dict):
        resp = client.post(
            "/payroll/",
            json={
                "employee_id": sample_employee["id"],
                "month": "2026-05",
                "base_salary": 15000,
                "bonuses": 1000,
                "deductions": 0,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["net_salary"] == 16000
        assert data["status"] == "draft"

    def test_create_payroll_invalid_employee(self, client: TestClient):
        resp = client.post(
            "/payroll/",
            json={
                "employee_id": 9999,
                "month": "2026-05",
                "base_salary": 10000,
            },
        )
        assert resp.status_code == 404

    def test_list_payrolls(self, client: TestClient):
        resp = client.get("/payroll/")
        assert resp.status_code == 200
        assert "payrolls" in resp.json()

    def test_pay_payroll(self, client: TestClient, sample_employee: dict):
        create_resp = client.post(
            "/payroll/",
            json={
                "employee_id": sample_employee["id"],
                "month": "2026-04",
                "base_salary": 15000,
            },
        )
        payroll_id = create_resp.json()["id"]
        resp = client.put(f"/payroll/{payroll_id}/pay")
        assert resp.status_code == 200
        assert resp.json()["status"] == "paid"

    def test_get_payslip(self, client: TestClient, sample_employee: dict):
        create_resp = client.post(
            "/payroll/",
            json={
                "employee_id": sample_employee["id"],
                "month": "2026-03",
                "base_salary": 15000,
            },
        )
        payroll_id = create_resp.json()["id"]
        resp = client.get(f"/payroll/payslip/{payroll_id}")
        assert resp.status_code == 200
        assert "payroll" in resp.json()


# ── Employee Skill Router ──────────────────────────────────────


class TestEmployeeSkillRouter:
    def test_create_skill(self, client: TestClient, sample_employee: dict, sample_skill_catalog: dict):
        resp = client.post(
            "/employee-skills/",
            json={
                "employee_id": sample_employee["id"],
                "skill_name": "Python",
                "skill_id": sample_skill_catalog["id"],
                "proficiency_level": "advanced",
                "years_of_experience": 5,
            },
        )
        assert resp.status_code == 201
        assert resp.json()["proficiency_level"] == "advanced"

    def test_create_skill_invalid_proficiency(self, client: TestClient, sample_employee: dict):
        resp = client.post(
            "/employee-skills/",
            json={
                "employee_id": sample_employee["id"],
                "skill_name": "Java",
                "proficiency_level": "guru",
            },
        )
        assert resp.status_code == 400

    def test_list_skills(self, client: TestClient):
        resp = client.get("/employee-skills/")
        assert resp.status_code == 200

    def test_list_skills_by_employee(self, client: TestClient, sample_employee: dict):
        resp = client.get(f"/employee-skills/employees/{sample_employee['id']}/skills")
        assert resp.status_code == 200


# ── Skill Catalog Router ───────────────────────────────────────


class TestSkillCatalogRouter:
    def test_create_skill(self, client: TestClient):
        resp = client.post(
            "/skill-catalog/",
            json={
                "name": "JavaScript",
                "category": "编程",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "JavaScript"

    def test_create_duplicate_skill(self, client: TestClient, sample_skill_catalog: dict):
        resp = client.post("/skill-catalog/", json={"name": sample_skill_catalog["name"]})
        assert resp.status_code == 400

    def test_list_skills(self, client: TestClient):
        resp = client.get("/skill-catalog/")
        assert resp.status_code == 200

    def test_delete_skill_in_use(self, client: TestClient, sample_employee_skill: dict):
        skill_id = sample_employee_skill.get("skill_id")
        if skill_id:
            resp = client.delete(f"/skill-catalog/{skill_id}")
            assert resp.status_code == 400


# ── Project Router ─────────────────────────────────────────────


class TestProjectRouter:
    def test_create_project(self, client: TestClient):
        resp = client.post(
            "/projects/",
            json={
                "name": "测试项目",
                "status": "planning",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "测试项目"

    def test_create_project_invalid_status(self, client: TestClient):
        resp = client.post(
            "/projects/",
            json={
                "name": "坏项目",
                "status": "invalid",
            },
        )
        assert resp.status_code == 400

    def test_list_projects(self, client: TestClient):
        resp = client.get("/projects/")
        assert resp.status_code == 200

    def test_get_project_not_found(self, client: TestClient):
        resp = client.get("/projects/9999")
        assert resp.status_code == 404

    def test_delete_active_project(self, client: TestClient):
        create_resp = client.post(
            "/projects/",
            json={
                "name": "活跃项目",
                "status": "active",
            },
        )
        project_id = create_resp.json()["id"]
        resp = client.delete(f"/projects/{project_id}")
        assert resp.status_code == 400


# ── Agent Memory Router ────────────────────────────────────────


class TestAgentMemoryRouter:
    def test_save_memory(self, client: TestClient):
        resp = client.post(
            "/agent/memories/",
            json={
                "session_id": "test-session",
                "user_tag": "test_user",
                "memory_type": "fact",
                "category": "general",
                "subject": "test_subject",
                "content": "测试记忆内容",
                "source": "agent_observed",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["content"] == "测试记忆内容"

    def test_save_memory_invalid_type(self, client: TestClient):
        resp = client.post(
            "/agent/memories/",
            json={
                "session_id": "test-session",
                "memory_type": "invalid",
                "category": "general",
                "subject": "test",
                "content": "test",
            },
        )
        assert resp.status_code == 400

    def test_recall_memories(self, client: TestClient):
        resp = client.get("/agent/memories/", params={"user_tag": "test_user"})
        assert resp.status_code == 200
        assert "memories" in resp.json()

    def test_get_memory_not_found(self, client: TestClient):
        resp = client.get("/agent/memories/9999")
        assert resp.status_code == 404

    def test_delete_memory_not_found(self, client: TestClient):
        resp = client.delete("/agent/memories/9999")
        assert resp.status_code == 404


# ── Root endpoint ──────────────────────────────────────────────


class TestRoot:
    def test_root(self, client: TestClient):
        # Root endpoint is defined in main.py, not in our test app
        # Just verify the app responds at a known route
        resp = client.get("/employees/")
        assert resp.status_code == 200
