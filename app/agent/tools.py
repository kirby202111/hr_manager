from __future__ import annotations

from datetime import date as date_type
from typing import Any

from fastapi import HTTPException

from app.agent.protocol import AgentTool
from app.services import employee as employee_service
from app.services import department as department_service
from app.services import attendance as attendance_service
from app.services import leave as leave_service
from app.services import payroll as payroll_service
from app.services import performance as performance_service
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.schemas.leave import LeaveCreate, LeaveApproval
from app.schemas.attendance import AttendanceCheckIn, AttendanceCheckOut
from app.schemas.payroll import PayrollCreate, PayrollUpdate
from app.schemas.performance import PerformanceReviewCreate, PerformanceReviewUpdate, ReviewCycleCreate, ReviewCycleUpdate


def _safe(fn, *args, **kwargs) -> dict:
    try:
        result = fn(*args, **kwargs)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        if isinstance(result, list):
            return [r.model_dump() if hasattr(r, "model_dump") else r for r in result]
        return result
    except HTTPException as e:
        return {"error": e.detail}
    except Exception as e:
        return {"error": str(e)}


# ---- Phase 1: Query Tools ----

query_employees = AgentTool(
    name="query_employees",
    description="查询所有员工列表，返回员工ID、姓名、部门、薪资等信息",
    parameters={"type": "object", "properties": {}, "required": []},
    fn=lambda: _safe(employee_service.list_employees),
)

query_employee = AgentTool(
    name="query_employee",
    description="根据员工ID查询单个员工的详细信息",
    parameters={
        "type": "object",
        "properties": {"employee_id": {"type": "integer", "description": "员工ID"}},
        "required": ["employee_id"],
    },
    fn=lambda employee_id: _safe(employee_service.get_employee, employee_id),
)

query_departments = AgentTool(
    name="query_departments",
    description="查询所有部门列表，返回部门ID、名称、人数等信息",
    parameters={"type": "object", "properties": {}, "required": []},
    fn=lambda: _safe(department_service.list_departments),
)

query_department = AgentTool(
    name="query_department",
    description="根据部门ID查询部门详情，包括部门人数",
    parameters={
        "type": "object",
        "properties": {"department_id": {"type": "integer", "description": "部门ID"}},
        "required": ["department_id"],
    },
    fn=lambda department_id: _safe(department_service.get_department, department_id),
)

query_department_employees = AgentTool(
    name="query_department_employees",
    description="查询指定部门下的所有员工",
    parameters={
        "type": "object",
        "properties": {"department_id": {"type": "integer", "description": "部门ID"}},
        "required": ["department_id"],
    },
    fn=lambda department_id: _safe(department_service.get_department_employees, department_id),
)

query_attendance = AgentTool(
    name="query_attendance",
    description="查询考勤记录，可按员工ID、起止日期筛选",
    parameters={
        "type": "object",
        "properties": {
            "employee_id": {"type": "integer", "description": "员工ID（可选）"},
            "start_date": {"type": "string", "description": "起始日期，格式YYYY-MM-DD（可选）"},
            "end_date": {"type": "string", "description": "结束日期，格式YYYY-MM-DD（可选）"},
        },
        "required": [],
    },
    fn=lambda employee_id=None, start_date=None, end_date=None: _safe(
        attendance_service.list_attendance,
        employee_id,
        date_type.fromisoformat(start_date) if start_date else None,
        date_type.fromisoformat(end_date) if end_date else None,
    ),
)

query_attendance_stats = AgentTool(
    name="query_attendance_stats",
    description="查询指定员工在指定时间段的考勤统计（正常、迟到、早退、缺勤天数）",
    parameters={
        "type": "object",
        "properties": {
            "employee_id": {"type": "integer", "description": "员工ID"},
            "start_date": {"type": "string", "description": "起始日期，格式YYYY-MM-DD"},
            "end_date": {"type": "string", "description": "结束日期，格式YYYY-MM-DD"},
        },
        "required": ["employee_id", "start_date", "end_date"],
    },
    fn=lambda employee_id, start_date, end_date: _safe(
        attendance_service.get_employee_stats,
        employee_id,
        date_type.fromisoformat(start_date),
        date_type.fromisoformat(end_date),
    ),
)

query_leaves = AgentTool(
    name="query_leaves",
    description="查询请假记录，可按员工ID和状态筛选",
    parameters={
        "type": "object",
        "properties": {
            "employee_id": {"type": "integer", "description": "员工ID（可选）"},
            "status": {"type": "string", "description": "状态：pending/approved/rejected/cancelled（可选）"},
        },
        "required": [],
    },
    fn=lambda employee_id=None, status=None: _safe(
        leave_service.list_leaves, employee_id, status
    ),
)

query_leave_balance = AgentTool(
    name="query_leave_balance",
    description="查询员工的请假余额（年假、病假、事假的总额、已用、剩余）",
    parameters={
        "type": "object",
        "properties": {"employee_id": {"type": "integer", "description": "员工ID"}},
        "required": ["employee_id"],
    },
    fn=lambda employee_id: _safe(leave_service.get_leave_balance, employee_id),
)

query_payrolls = AgentTool(
    name="query_payrolls",
    description="查询薪资记录，可按员工ID、月份、状态筛选",
    parameters={
        "type": "object",
        "properties": {
            "employee_id": {"type": "integer", "description": "员工ID（可选）"},
            "month": {"type": "string", "description": "月份，格式YYYY-MM（可选）"},
            "status": {"type": "string", "description": "状态：draft/paid（可选）"},
        },
        "required": [],
    },
    fn=lambda employee_id=None, month=None, status=None: _safe(
        payroll_service.list_payrolls, employee_id, month, status
    ),
)

query_payslip = AgentTool(
    name="query_payslip",
    description="查询薪资条详情，包含考勤摘要、请假摘要、扣款明细、奖金明细",
    parameters={
        "type": "object",
        "properties": {"payroll_id": {"type": "integer", "description": "薪资记录ID"}},
        "required": ["payroll_id"],
    },
    fn=lambda payroll_id: _safe(payroll_service.get_payslip, payroll_id),
)

query_performance_reviews = AgentTool(
    name="query_performance_reviews",
    description="查询绩效评审记录，可按员工ID和考核周期ID筛选",
    parameters={
        "type": "object",
        "properties": {
            "employee_id": {"type": "integer", "description": "员工ID（可选）"},
            "cycle_id": {"type": "integer", "description": "考核周期ID（可选）"},
        },
        "required": [],
    },
    fn=lambda employee_id=None, cycle_id=None: _safe(
        performance_service.list_reviews, employee_id, cycle_id
    ),
)

query_employee_performance = AgentTool(
    name="query_employee_performance",
    description="查询员工的绩效摘要，包含平均评分、评审次数、最新评分、评分分布",
    parameters={
        "type": "object",
        "properties": {"employee_id": {"type": "integer", "description": "员工ID"}},
        "required": ["employee_id"],
    },
    fn=lambda employee_id: _safe(performance_service.get_employee_summary, employee_id),
)

query_performance_cycles = AgentTool(
    name="query_performance_cycles",
    description="查询所有绩效考核周期列表",
    parameters={"type": "object", "properties": {}, "required": []},
    fn=lambda: _safe(performance_service.list_cycles),
)

# ---- Phase 2: Workflow Automation Tools ----

create_employee_tool = AgentTool(
    name="create_employee",
    description="创建新员工，需要提供姓名和薪资",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "员工姓名"},
            "department_id": {"type": "integer", "description": "部门ID（可选）"},
            "salary": {"type": "number", "description": "月薪"},
        },
        "required": ["name", "salary"],
    },
    fn=lambda name, salary, department_id=None: _safe(
        employee_service.create_employee,
        EmployeeCreate(name=name, department_id=department_id, salary=salary),
    ),
)

update_employee_tool = AgentTool(
    name="update_employee",
    description="更新员工信息，只需提供要修改的字段",
    parameters={
        "type": "object",
        "properties": {
            "employee_id": {"type": "integer", "description": "员工ID"},
            "name": {"type": "string", "description": "新姓名（可选）"},
            "department_id": {"type": "integer", "description": "新部门ID（可选）"},
            "salary": {"type": "number", "description": "新月薪（可选）"},
        },
        "required": ["employee_id"],
    },
    fn=lambda employee_id, name=None, department_id=None, salary=None: _safe(
        employee_service.update_employee,
        employee_id,
        EmployeeUpdate(name=name, department_id=department_id, salary=salary),
    ),
)

delete_employee_tool = AgentTool(
    name="delete_employee",
    description="删除指定员工",
    parameters={
        "type": "object",
        "properties": {"employee_id": {"type": "integer", "description": "员工ID"}},
        "required": ["employee_id"],
    },
    fn=lambda employee_id: _safe(employee_service.delete_employee, employee_id),
)

create_leave_tool = AgentTool(
    name="create_leave",
    description="提交请假申请",
    parameters={
        "type": "object",
        "properties": {
            "employee_id": {"type": "integer", "description": "员工ID"},
            "leave_type": {"type": "string", "description": "请假类型：sick(病假)/annual(年假)/personal(事假)/other(其他)"},
            "start_date": {"type": "string", "description": "起始日期，格式YYYY-MM-DD"},
            "end_date": {"type": "string", "description": "结束日期，格式YYYY-MM-DD"},
            "reason": {"type": "string", "description": "请假原因（可选）"},
        },
        "required": ["employee_id", "leave_type", "start_date", "end_date"],
    },
    fn=lambda employee_id, leave_type, start_date, end_date, reason=None: _safe(
        leave_service.create_leave,
        LeaveCreate(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=date_type.fromisoformat(start_date),
            end_date=date_type.fromisoformat(end_date),
            reason=reason,
        ),
    ),
)

approve_leave_tool = AgentTool(
    name="approve_leave",
    description="审批通过请假申请",
    parameters={
        "type": "object",
        "properties": {
            "leave_id": {"type": "integer", "description": "请假记录ID"},
            "approver": {"type": "string", "description": "审批人姓名"},
            "comment": {"type": "string", "description": "审批意见（可选）"},
        },
        "required": ["leave_id", "approver"],
    },
    fn=lambda leave_id, approver, comment=None: _safe(
        leave_service.approve_leave,
        leave_id,
        LeaveApproval(approver=approver, comment=comment),
    ),
)

reject_leave_tool = AgentTool(
    name="reject_leave",
    description="驳回请假申请",
    parameters={
        "type": "object",
        "properties": {
            "leave_id": {"type": "integer", "description": "请假记录ID"},
            "approver": {"type": "string", "description": "审批人姓名"},
            "comment": {"type": "string", "description": "驳回原因（可选）"},
        },
        "required": ["leave_id", "approver"],
    },
    fn=lambda leave_id, approver, comment=None: _safe(
        leave_service.reject_leave,
        leave_id,
        LeaveApproval(approver=approver, comment=comment),
    ),
)

check_in_tool = AgentTool(
    name="check_in",
    description="员工签到打卡",
    parameters={
        "type": "object",
        "properties": {
            "employee_id": {"type": "integer", "description": "员工ID"},
            "date": {"type": "string", "description": "日期，格式YYYY-MM-DD"},
            "check_in": {"type": "string", "description": "签到时间，格式HH:MM:SS"},
        },
        "required": ["employee_id", "date", "check_in"],
    },
    fn=lambda employee_id, date, check_in: _safe(
        attendance_service.check_in,
        AttendanceCheckIn(
            employee_id=employee_id,
            date=date_type.fromisoformat(date),
            check_in=check_in,
        ),
    ),
)

check_out_tool = AgentTool(
    name="check_out",
    description="员工签退打卡",
    parameters={
        "type": "object",
        "properties": {
            "record_id": {"type": "integer", "description": "考勤记录ID"},
            "check_out": {"type": "string", "description": "签退时间，格式HH:MM:SS"},
        },
        "required": ["record_id", "check_out"],
    },
    fn=lambda record_id, check_out: _safe(
        attendance_service.check_out,
        record_id,
        AttendanceCheckOut(check_out=check_out),
    ),
)

generate_monthly_payroll_tool = AgentTool(
    name="generate_monthly_payroll",
    description="为所有员工生成指定月份的薪资，自动计算考勤扣款和请假扣款",
    parameters={
        "type": "object",
        "properties": {"month": {"type": "string", "description": "月份，格式YYYY-MM"}},
        "required": ["month"],
    },
    fn=lambda month: _safe(payroll_service.generate_monthly_payroll, month),
)

pay_payroll_tool = AgentTool(
    name="pay_payroll",
    description="将薪资记录标记为已支付",
    parameters={
        "type": "object",
        "properties": {"payroll_id": {"type": "integer", "description": "薪资记录ID"}},
        "required": ["payroll_id"],
    },
    fn=lambda payroll_id: _safe(payroll_service.pay_payroll, payroll_id),
)

create_performance_review_tool = AgentTool(
    name="create_performance_review",
    description="提交绩效评审评分",
    parameters={
        "type": "object",
        "properties": {
            "employee_id": {"type": "integer", "description": "员工ID"},
            "cycle_id": {"type": "integer", "description": "考核周期ID"},
            "rating": {"type": "number", "description": "评分，1.0-5.0"},
            "reviewer": {"type": "string", "description": "评审人姓名"},
            "comments": {"type": "string", "description": "评审意见（可选）"},
        },
        "required": ["employee_id", "cycle_id", "rating", "reviewer"],
    },
    fn=lambda employee_id, cycle_id, rating, reviewer, comments=None: _safe(
        performance_service.create_review,
        PerformanceReviewCreate(
            employee_id=employee_id,
            cycle_id=cycle_id,
            rating=rating,
            reviewer=reviewer,
            comments=comments,
        ),
    ),
)

# ---- Phase 3: Analysis Tools ----

analyze_department_salary_tool = AgentTool(
    name="analyze_department_salary_distribution",
    description="分析各部门薪资分布情况，包括平均薪资、最高最低薪资、人数",
    parameters={"type": "object", "properties": {}, "required": []},
    fn=lambda: _analyze_department_salary(),
)

analyze_attendance_anomalies_tool = AgentTool(
    name="analyze_attendance_anomalies",
    description="分析指定月份的考勤异常情况，找出迟到、早退、缺勤较多的员工",
    parameters={
        "type": "object",
        "properties": {
            "month": {"type": "string", "description": "月份，格式YYYY-MM"},
        },
        "required": ["month"],
    },
    fn=lambda month: _analyze_attendance_anomalies(month),
)

analyze_leave_trends_tool = AgentTool(
    name="analyze_leave_trends",
    description="分析请假趋势，按类型、部门统计请假情况",
    parameters={"type": "object", "properties": {}, "required": []},
    fn=lambda: _analyze_leave_trends(),
)

analyze_performance_distribution_tool = AgentTool(
    name="analyze_performance_distribution",
    description="分析绩效评分分布，按等级统计人数和占比",
    parameters={"type": "object", "properties": {}, "required": []},
    fn=lambda: _analyze_performance_distribution(),
)


def _analyze_department_salary() -> dict:
    try:
        depts = department_service.list_departments()
        from app.models import employee as employee_model
        result = []
        for dept in depts.departments:
            employees = employee_model.get_employees_by_department(dept.id)
            if not employees:
                result.append({
                    "department": dept.name,
                    "employee_count": 0,
                    "avg_salary": 0,
                    "min_salary": 0,
                    "max_salary": 0,
                })
                continue
            salaries = [e["salary"] for e in employees]
            result.append({
                "department": dept.name,
                "employee_count": len(salaries),
                "avg_salary": round(sum(salaries) / len(salaries), 2),
                "min_salary": min(salaries),
                "max_salary": max(salaries),
            })
        return {"departments": result}
    except Exception as e:
        return {"error": str(e)}


def _analyze_attendance_anomalies(month: str) -> dict:
    try:
        from app.config import settings as _s
        from app.models import employee as employee_model
        import calendar
        parts = month.split("-")
        year, m = int(parts[0]), int(parts[1])
        start = date_type(year, m, 1)
        end = date_type(year, m, calendar.monthrange(year, m)[1])
        anomalies = []
        for emp in employee_model.get_all_employees():
            stats = attendance_service.get_employee_stats(emp["id"], start, end)
            if stats.late_days > 0 or stats.early_leave_days > 0 or stats.absent_days > 0:
                anomalies.append({
                    "employee_id": emp["id"],
                    "employee_name": emp["name"],
                    "late_days": stats.late_days,
                    "early_leave_days": stats.early_leave_days,
                    "absent_days": stats.absent_days,
                })
        anomalies.sort(key=lambda x: x["late_days"] + x["early_leave_days"] + x["absent_days"], reverse=True)
        return {"month": month, "anomaly_count": len(anomalies), "anomalies": anomalies}
    except Exception as e:
        return {"error": str(e)}


def _analyze_leave_trends() -> dict:
    try:
        leaves = leave_service.list_leaves()
        from app.models import employee as employee_model
        type_count: dict[str, int] = {}
        type_days: dict[str, int] = {}
        dept_count: dict[str, int] = {}
        for leave in leaves.leaves:
            lt = leave.leave_type
            type_count[lt] = type_count.get(lt, 0) + 1
            type_days[lt] = type_days.get(lt, 0) + leave.days
            emp = employee_model.get_employee_by_id(leave.employee_id)
            if emp and emp.get("department_id"):
                from app.models import department as dept_model
                dept = dept_model.get_department_by_id(emp["department_id"])
                if dept:
                    dept_count[dept["name"]] = dept_count.get(dept["name"], 0) + 1
        return {
            "by_type": {k: {"count": type_count[k], "days": type_days[k]} for k in type_count},
            "by_department": dept_count,
            "total_requests": leaves.total,
        }
    except Exception as e:
        return {"error": str(e)}


def _analyze_performance_distribution() -> dict:
    try:
        reviews = performance_service.list_reviews()
        dist: dict[str, int] = {}
        for r in reviews.reviews:
            level = r.rating_level
            dist[level] = dist.get(level, 0) + 1
        total = reviews.total
        return {
            "distribution": {k: {"count": v, "percentage": round(v / total * 100, 1)} for k, v in dist.items()},
            "total_reviews": total,
        }
    except Exception as e:
        return {"error": str(e)}


# ---- Tool Registry ----

ALL_TOOLS: list[AgentTool] = [
    # Phase 1: Query
    query_employees,
    query_employee,
    query_departments,
    query_department,
    query_department_employees,
    query_attendance,
    query_attendance_stats,
    query_leaves,
    query_leave_balance,
    query_payrolls,
    query_payslip,
    query_performance_reviews,
    query_employee_performance,
    query_performance_cycles,
    # Phase 2: Workflow
    create_employee_tool,
    update_employee_tool,
    delete_employee_tool,
    create_leave_tool,
    approve_leave_tool,
    reject_leave_tool,
    check_in_tool,
    check_out_tool,
    generate_monthly_payroll_tool,
    pay_payroll_tool,
    create_performance_review_tool,
    # Phase 3: Analysis
    analyze_department_salary_tool,
    analyze_attendance_anomalies_tool,
    analyze_leave_trends_tool,
    analyze_performance_distribution_tool,
]

TOOL_MAP: dict[str, AgentTool] = {t.name: t for t in ALL_TOOLS}

SYSTEM_PROMPT = """你是一个专业的HR管理助手。你可以帮助用户查询员工信息、考勤记录、请假情况、薪资数据和绩效评估等。

你的职责：
1. 理解用户用自然语言提出的问题
2. 调用相应的工具获取数据
3. 用清晰、专业的中文回答用户的问题

你可以执行以下操作：
- 查询：员工、部门、考勤、请假、薪资、绩效等各类数据
- 操作：创建员工、提交/审批请假、签到签退、生成/支付薪资、提交绩效评分等
- 分析：薪资分布、考勤异常、请假趋势、绩效分布等

注意事项：
- 回答时使用中文
- 如果数据量很大，只展示摘要和关键信息
- 如果工具返回错误信息，向用户解释错误原因
- 执行操作前请确认用户意图，避免误操作
- 对于多步骤操作，先查询数据再逐个操作
- 不要编造数据，只使用工具返回的真实数据
"""
