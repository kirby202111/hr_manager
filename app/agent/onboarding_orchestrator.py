"""Heuristics and runtime context for agent-led worker onboarding."""

from __future__ import annotations

from typing import Any

from app.agent.schemas.onboarding import OnboardingCasePatch
from app.agent.services import onboarding as onboarding_service

ONBOARDING_KEYWORDS = (
    "入职",
    "新员工",
    "新工人",
    "办理上岗",
    "上岗",
    "工位",
    "onboarding",
    "new hire",
    "workstation",
)

FIELD_LABELS = {
    "worker_code": "工号",
    "worker_name": "姓名",
    "employment_type": "用工类型",
    "organization_unit_id": "组织单元",
    "production_line_id": "产线",
    "production_team_id": "班组",
    "role_title": "岗位名称",
    "hire_date": "入职日期",
    "target_workstation_id": "目标工位",
}

TOOL_ACTIONS = {
    "create_worker_profile": "已创建员工档案",
    "update_worker_profile": "已更新员工档案",
    "create_primary_assignment": "已创建任职归属",
    "update_primary_assignment": "已更新任职归属",
    "record_worker_skill": "已登记技能",
    "record_worker_certification": "已登记证书",
    "record_worker_training": "已登记培训",
    "record_equipment_authorization": "已登记设备授权",
}


class OnboardingOrchestrator:
    """Lightweight runtime helper for onboarding-focused conversations."""

    def should_handle(self, message: str, session_id: str, user_tag: str) -> bool:
        if any(keyword.lower() in message.lower() for keyword in ONBOARDING_KEYWORDS):
            return True
        return onboarding_service.get_active_case(session_id, user_tag) is not None

    def prepare_turn(self, session_id: str, user_tag: str, message: str) -> None:
        if not self.should_handle(message, session_id, user_tag):
            return
        existing = onboarding_service.get_active_case(session_id, user_tag)
        patch = OnboardingCasePatch(is_active=True)
        if existing is None:
            patch.pending_actions = ["收集员工建档信息", "确认目标工位", "完成资格复核"]
            patch.last_agent_summary = "已识别为工人入职会话，准备先查重、再建档、再做上岗资格校验。"
        onboarding_service.upsert_case(session_id, user_tag, patch)

    def build_runtime_messages(self, session_id: str, user_tag: str) -> list[dict[str, str]]:
        case = onboarding_service.get_active_case(session_id, user_tag)
        if case is None:
            return []
        latest = case.latest_eligibility or {}
        latest_status = latest.get("status") or "unknown"
        latest_reason = latest.get("summary_reason") or "not_checked"
        missing = ", ".join(FIELD_LABELS.get(item, item) for item in case.missing_fields) or "none"
        completed = ", ".join(case.completed_actions[-5:]) or "none"
        pending = ", ".join(case.pending_actions) or "none"
        current_result = self._current_result(case)
        summary_lines = [
            "Current onboarding case context:",
            f"- worker_id: {case.worker_id}",
            f"- worker_code: {case.worker_code}",
            f"- worker_name: {case.worker_name}",
            f"- employment_type: {case.employment_type}",
            f"- organization_unit_id: {case.organization_unit_id}",
            f"- production_line_id: {case.production_line_id}",
            f"- production_team_id: {case.production_team_id}",
            f"- role_title: {case.role_title}",
            f"- hire_date: {case.hire_date}",
            f"- target_workstation_id: {case.target_workstation_id}",
            f"- current_result: {current_result}",
            f"- latest_eligibility_status: {latest_status}",
            f"- latest_eligibility_reason: {latest_reason}",
            f"- missing_fields: {missing}",
            f"- completed_actions: {completed}",
            f"- pending_actions: {pending}",
        ]
        guidance_lines = [
            "Onboarding operating rules:",
            "1. Always check for worker duplicates before creating a new worker profile.",
            "2. Ask only for the smallest missing set of fields needed to unlock the next action.",
            "3. Use list_shopfloor_targets and get_workstation_requirements when the target workstation is ambiguous.",
            "4. After each write action, update save_onboarding_case with progress and missing items.",
            (
                "5. After qualification updates, run check_worker_workstation_eligibility "
                "and summarize blockers or readiness."
            ),
            "6. Do not call update_worker_profile or update_primary_assignment without explicit user confirmation.",
        ]
        return [
            {"role": "system", "content": "\n".join(summary_lines)},
            {"role": "system", "content": "\n".join(guidance_lines)},
        ]

    def handle_tool_result(
        self,
        session_id: str,
        user_tag: str,
        tool_name: str,
        arguments: dict[str, Any],
        result: Any,
    ) -> None:
        if onboarding_service.get_active_case(session_id, user_tag) is None and tool_name != "save_onboarding_case":
            return
        if not isinstance(result, dict) or result.get("error"):
            if tool_name in {"find_worker_candidates", "create_primary_assignment"}:
                self._append_risk(session_id, user_tag, f"{tool_name}_attention")
            return
        patch = OnboardingCasePatch()
        if tool_name == "create_worker_profile":
            patch.worker_id = result.get("id")
            patch.worker_code = result.get("worker_code")
            patch.worker_name = result.get("full_name")
            patch.employment_type = result.get("employment_type")
            patch.completed_actions = [TOOL_ACTIONS[tool_name]]
            patch.last_agent_summary = "员工档案已创建，下一步应确认归属与目标工位。"
        elif tool_name == "update_worker_profile":
            patch.worker_id = result.get("id")
            patch.worker_code = result.get("worker_code")
            patch.worker_name = result.get("full_name")
            patch.employment_type = result.get("employment_type")
            patch.completed_actions = [TOOL_ACTIONS[tool_name]]
        elif tool_name in {"create_primary_assignment", "update_primary_assignment"}:
            patch.organization_unit_id = result.get("organization_unit_id")
            patch.production_line_id = result.get("production_line_id")
            patch.production_team_id = result.get("production_team_id")
            patch.role_title = result.get("role_title")
            patch.completed_actions = [TOOL_ACTIONS[tool_name]]
            patch.last_agent_summary = "任职归属已登记，下一步应核对目标工位要求并补齐资质。"
        elif tool_name == "save_onboarding_case":
            return
        elif tool_name in TOOL_ACTIONS:
            patch.completed_actions = [TOOL_ACTIONS[tool_name]]
        elif tool_name == "check_worker_workstation_eligibility":
            patch.worker_id = result.get("worker_id")
            patch.target_workstation_id = result.get("workstation_id")
            patch.latest_eligibility = {
                "status": result.get("status"),
                "summary_reason": result.get("summary_reason"),
                "details": result.get("details", []),
                "checked_at": result.get("checked_at"),
            }
            patch.completed_actions = [
                "上岗资格已通过" if result.get("status") == "eligible" else "已完成上岗资格复核"
            ]
            patch.pending_actions = self._pending_actions_from_eligibility(result)
            patch.last_agent_summary = self._summary_from_eligibility(result)
            if result.get("status") == "eligible":
                patch.is_active = False
        onboarding_service.upsert_case(session_id, user_tag, patch)

    @staticmethod
    def _summary_from_eligibility(result: dict[str, Any]) -> str:
        status = result.get("status")
        if status == "eligible":
            return "目标工位资格校验已通过，员工可上岗。"
        if status == "warning":
            return f"资格校验通过但存在提醒：{result.get('summary_reason')}"
        return f"资格校验未通过：{result.get('summary_reason')}"

    @staticmethod
    def _pending_actions_from_eligibility(result: dict[str, Any]) -> list[str]:
        if result.get("status") == "eligible":
            return []
        details = result.get("details") or []
        blocked = [detail.get("message") for detail in details if detail.get("status") == "blocked"]
        warnings = [detail.get("message") for detail in details if detail.get("status") == "warning"]
        return [str(item) for item in [*blocked, *warnings] if item]

    @staticmethod
    def _current_result(case) -> str:
        latest = case.latest_eligibility or {}
        if latest.get("status") == "eligible":
            return "ready_for_work"
        return "blocked" if case.is_active else "unknown"

    def _append_risk(self, session_id: str, user_tag: str, risk_flag: str) -> None:
        onboarding_service.upsert_case(
            session_id,
            user_tag,
            OnboardingCasePatch(risk_flags=[risk_flag]),
        )


__all__ = ["OnboardingOrchestrator"]
