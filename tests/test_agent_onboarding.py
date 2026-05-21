from __future__ import annotations

from types import SimpleNamespace

from app.agent.history import InMemoryHistoryStore
from app.agent.onboarding_orchestrator import OnboardingOrchestrator
from app.agent.protocol import AgentSkill, AgentTool, ToolExecutionContext
from app.agent.react_agent import LangGraphAgent
from app.agent.schemas.onboarding import OnboardingCasePatch, OnboardingCaseResponse
from app.agent.services import onboarding as onboarding_service
from app.agent.skill_registry import SkillRegistry
from app.agent.skill_router import SkillRouter


def test_prepare_turn_initializes_onboarding_case(monkeypatch):
    captured: dict[str, object] = {}

    monkeypatch.setattr(onboarding_service, "get_active_case", lambda session_id, user_tag: None)

    def fake_upsert(session_id, user_tag, patch, db=None):
        captured["session_id"] = session_id
        captured["user_tag"] = user_tag
        captured["patch"] = patch
        return None

    monkeypatch.setattr(onboarding_service, "upsert_case", fake_upsert)

    orchestrator = OnboardingOrchestrator()
    orchestrator.prepare_turn("s-1", "u-1", "帮我办理新员工入职")

    assert captured["session_id"] == "s-1"
    assert captured["user_tag"] == "u-1"
    patch = captured["patch"]
    assert isinstance(patch, OnboardingCasePatch)
    assert patch.is_active is True
    assert patch.pending_actions == ["查重并收集建档信息", "确认目标工位", "完成上岗资格复核"]


def test_build_runtime_messages_include_working_memory(monkeypatch):
    monkeypatch.setattr(
        onboarding_service,
        "get_active_case",
        lambda session_id, user_tag: SimpleNamespace(
            worker_id=12,
            worker_code="W-001",
            worker_name="张三",
            employment_type="full_time",
            organization_unit_id=3,
            production_line_id=7,
            production_team_id=9,
            role_title="装配工",
            hire_date="2026-05-21",
            target_workstation_id=21,
            latest_eligibility={"status": "blocked", "summary_reason": "缺安全培训"},
            missing_fields=["target_workstation_id"],
            completed_actions=["已创建员工档案"],
            pending_actions=["补齐安全培训"],
            last_agent_summary="等待补齐安全培训",
            is_active=True,
        ),
    )

    messages = OnboardingOrchestrator().build_runtime_messages("s-1", "u-1")

    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert "Onboarding working memory" in messages[0]["content"]
    assert "worker_code: W-001" in messages[0]["content"]
    assert "Always check for worker duplicates" in messages[0]["content"]


def test_handle_tool_result_marks_eligible_case_complete(monkeypatch):
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        onboarding_service,
        "get_active_case",
        lambda session_id, user_tag: SimpleNamespace(is_active=True, latest_eligibility=None),
    )

    def fake_upsert(session_id, user_tag, patch, db=None):
        captured["patch"] = patch
        return None

    monkeypatch.setattr(onboarding_service, "upsert_case", fake_upsert)

    OnboardingOrchestrator().handle_tool_result(
        "s-1",
        "u-1",
        "check_worker_workstation_eligibility",
        {"worker_id": 12, "workstation_id": 21},
        SimpleNamespace(
            status="success",
            summary="eligible",
            data={
                "worker_id": 12,
                "workstation_id": 21,
                "status": "eligible",
                "summary_reason": "全部要求已满足",
                "details": [],
                "checked_at": "2026-05-21T09:00:00Z",
            },
            next_action_hint=None,
            requires_confirmation=False,
            error_type=None,
        ),
    )

    patch = captured["patch"]
    assert isinstance(patch, OnboardingCasePatch)
    assert patch.worker_id == 12
    assert patch.target_workstation_id == 21
    assert patch.is_active is False
    assert patch.pending_actions == []
    assert patch.last_agent_summary == "目标工位资格校验已通过，员工可上岗。"


def test_get_session_state_uses_latest_case(monkeypatch):
    latest_case = OnboardingCaseResponse.model_validate(
        {
            "id": 1,
            "session_id": "s-1",
            "user_tag": "u-1",
            "intent": "worker_onboarding",
            "collected_fields": [],
            "missing_fields": [],
            "pending_actions": [],
            "completed_actions": [],
            "risk_flags": [],
            "is_active": False,
            "created_at": "2026-05-21T00:00:00Z",
            "updated_at": "2026-05-21T00:00:00Z",
        }
    )
    monkeypatch.setattr(onboarding_service, "get_latest_case", lambda session_id, user_tag, db=None: latest_case)

    state = onboarding_service.get_session_state("s-1", "u-1")

    assert state.session_id == "s-1"
    assert state.onboarding_case is latest_case


def test_skill_router_returns_structured_matches():
    router = SkillRouter(default_skill="memory", max_selected_skills=2)
    skills = [
        AgentSkill(
            name="memory",
            description="memory",
            applicability="memory",
            tools=[],
            metadata={"priority": 10, "default": True},
        ),
        AgentSkill(
            name="onboarding",
            description="onboarding",
            applicability="onboarding",
            tools=[],
            keywords=("入职",),
            metadata={"priority": 90},
        ),
        AgentSkill(
            name="qualification",
            description="qualification",
            applicability="qualification",
            tools=[],
            keywords=("资格",),
            metadata={"priority": 60},
        ),
    ]

    matches = router.route("帮我处理入职资格问题", skills, forced_skill_names=["onboarding"])

    assert [match.skill_name for match in matches] == ["onboarding", "qualification"]
    assert matches[0].match_type == "forced"
    assert matches[1].match_type == "strong"
    assert matches[1].reason.startswith("keyword:")


def test_react_agent_load_messages_uses_runtime_summary_and_recent_history():
    registry = SkillRegistry()
    agent = LangGraphAgent(history_store=InMemoryHistoryStore(), skill_registry=registry, use_routing=True)
    history = agent._history

    history.add_message("s-1", {"role": "system", "content": "SYSTEM"}, user_tag="u-1")
    for idx in range(15):
        history.add_message("s-1", {"role": "user", "content": f"user-{idx}"}, user_tag="u-1")
        history.add_message("s-1", {"role": "assistant", "content": f"assistant-{idx}"}, user_tag="u-1")

    messages = agent._load_langchain_messages("s-1", [{"role": "system", "content": "RUNTIME"}])
    rendered = [agent._content_to_text(message.content) for message in messages]

    assert rendered[0] == "SYSTEM"
    assert rendered[1] == "RUNTIME"
    assert "user-0" not in rendered
    assert "assistant-14" in rendered


def test_react_agent_normalizes_tool_results_and_blocks_unconfirmed_updates():
    registry = SkillRegistry()
    agent = LangGraphAgent(history_store=InMemoryHistoryStore(), skill_registry=registry, use_routing=True)
    context = ToolExecutionContext(session_id="s-1", user_tag="u-1")

    tool = AgentTool(
        name="update_worker_profile",
        description="update worker",
        parameters={"type": "object", "properties": {"worker_id": {"type": "integer"}, "confirm": {"type": "boolean"}}},
        fn=lambda worker_id, confirm=False: {"id": worker_id},
    )

    blocked = agent._invoke_tool(tool, {"worker_id": 7}, context)
    allowed = agent._invoke_tool(tool, {"worker_id": 7, "confirm": True}, context)

    assert blocked.status == "blocked"
    assert blocked.requires_confirmation is True
    assert allowed.status == "success"
    assert allowed.data == {"id": 7}


def test_react_agent_prepare_turn_uses_orchestrator_forced_skills(monkeypatch):
    registry = SkillRegistry()
    registry.register(
        AgentSkill(
            name="memory",
            description="memory",
            applicability="memory",
            tools=[AgentTool(name="remember", description="remember", parameters={"type": "object"}, fn=lambda: None)],
        )
    )
    registry.register(
        AgentSkill(
            name="onboarding",
            description="onboarding",
            applicability="onboarding",
            tools=[
                AgentTool(
                    name="create_worker_profile",
                    description="create worker",
                    parameters={"type": "object"},
                    fn=lambda: None,
                )
            ],
        )
    )

    agent = LangGraphAgent(history_store=InMemoryHistoryStore(), skill_registry=registry, use_routing=True)
    monkeypatch.setattr(
        agent._orchestrators,
        "resolve",
        lambda session_id, user_tag, message: [
            SimpleNamespace(orchestrator=SimpleNamespace(name="onboarding"), forced_skills=["onboarding"])
        ],
    )
    monkeypatch.setattr(agent._orchestrators, "prepare_turn", lambda orchestrators, session_id, user_tag, message: None)
    monkeypatch.setattr(
        agent._orchestrators,
        "build_runtime_messages",
        lambda orchestrators, session_id, user_tag: [{"role": "system", "content": "runtime"}],
    )

    plan = agent._prepare_turn("s-1", "继续刚才的流程", "u-1")

    assert [match.skill_name for match in plan.skill_matches] == ["onboarding"]
    assert [tool.name for tool in plan.tools] == ["create_worker_profile"]
    assert plan.trace.orchestrators == ["onboarding"]
