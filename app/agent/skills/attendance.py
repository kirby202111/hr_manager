from datetime import date as date_type

from app.agent.protocol import AgentTool, Skill, _safe
from app.schemas.attendance import AttendanceCheckIn, AttendanceCheckOut
from app.services import attendance as attendance_service

skill = Skill(
    name="attendance_management",
    description="考勤记录与签到签退管理",
    applicability="用户询问考勤记录、签到签退、考勤统计时使用",
    tools=[
        AgentTool(
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
        ),
        AgentTool(
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
        ),
        AgentTool(
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
        ),
        AgentTool(
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
        ),
    ],
)
