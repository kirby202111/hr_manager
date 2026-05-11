from __future__ import annotations

import calendar
from datetime import date as date_type

from app.agent.protocol import AgentTool, Skill, _safe
from app.repositories import employee as employee_repo
from app.repositories import department as department_repo
from app.services import department as department_service
from app.services import attendance as attendance_service
from app.services import leave as leave_service
from app.services import performance as performance_service


def _analyze_department_salary() -> dict:
    try:
        depts = department_service.list_departments()
        result = []
        for dept in depts.departments:
            employees = employee_repo.get_employees_by_department(dept.id)
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
        parts = month.split("-")
        year, m = int(parts[0]), int(parts[1])
        start = date_type(year, m, 1)
        end = date_type(year, m, calendar.monthrange(year, m)[1])
        anomalies = []
        for emp in employee_repo.get_all_employees():
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
        type_count: dict[str, int] = {}
        type_days: dict[str, int] = {}
        dept_count: dict[str, int] = {}
        for leave in leaves.leaves:
            lt = leave.leave_type
            type_count[lt] = type_count.get(lt, 0) + 1
            type_days[lt] = type_days.get(lt, 0) + leave.days
            emp = employee_repo.get_employee_by_id(leave.employee_id)
            if emp and emp.get("department_id"):
                dept = department_repo.get_department_by_id(emp["department_id"])
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


skill = Skill(
    name="analytics",
    description="HR数据分析与统计",
    applicability="用户询问分析、趋势、分布、异常等跨领域数据统计时使用",
    tools=[
        AgentTool(
            name="analyze_department_salary_distribution",
            description="分析各部门薪资分布情况，包括平均薪资、最高最低薪资、人数",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: _analyze_department_salary(),
        ),
        AgentTool(
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
        ),
        AgentTool(
            name="analyze_leave_trends",
            description="分析请假趋势，按类型、部门统计请假情况",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: _analyze_leave_trends(),
        ),
        AgentTool(
            name="analyze_performance_distribution",
            description="分析绩效评分分布，按等级统计人数和占比",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: _analyze_performance_distribution(),
        ),
    ],
)
