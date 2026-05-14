"""Unit tests for the Agent system: protocol, skill_registry, skill_router,
history, and react_agent modules."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from pydantic import BaseModel

from app.agent.history import InMemoryHistoryStore
from app.agent.protocol import AgentTool, Skill, _safe
from app.agent.react_agent import ReActAgent, _build_hook_memory
from app.agent.skill_registry import SkillRegistry
from app.agent.skill_router import SkillRouter

# ── Helpers ────────────────────────────────────────────────────


def _make_tool(name: str = "test_tool", fn=None) -> AgentTool:
    return AgentTool(
        name=name,
        description=f"{name} description",
        parameters={"type": "object", "properties": {}},
        fn=fn or (lambda: {"ok": True}),
    )


def _make_skill(
    name: str = "test_skill",
    tools: list[AgentTool] | None = None,
    enabled: bool = True,
    workflows: dict | None = None,
) -> Skill:
    return Skill(
        name=name,
        description=f"{name} description",
        applicability=f"{name} applicability",
        tools=tools or [_make_tool(f"{name}_tool")],
        enabled=enabled,
        workflows=workflows or {},
    )


# ── protocol.py: AgentTool ─────────────────────────────────────


class TestAgentTool:
    def test_to_openai_tool_returns_correct_format(self):
        tool = AgentTool(
            name="search_employee",
            description="Search for employees",
            parameters={"type": "object", "properties": {"name": {"type": "string"}}},
            fn=lambda: {},
        )
        result = tool.to_openai_tool()
        assert result == {
            "type": "function",
            "function": {
                "name": "search_employee",
                "description": "Search for employees",
                "parameters": {"type": "object", "properties": {"name": {"type": "string"}}},
            },
        }


# ── protocol.py: Skill ─────────────────────────────────────────


class TestSkill:
    def test_to_openai_skill_summary(self):
        skill = _make_skill("emp_mgmt")
        summary = skill.to_openai_skill_summary()
        assert summary == {
            "name": "emp_mgmt",
            "description": "emp_mgmt description",
            "applicability": "emp_mgmt applicability",
        }

    def test_get_openai_tools_enabled(self):
        tool = _make_tool("t1")
        skill = Skill(
            name="s",
            description="d",
            applicability="a",
            tools=[tool],
            enabled=True,
        )
        tools = skill.get_openai_tools()
        assert len(tools) == 1
        assert tools[0] == tool.to_openai_tool()

    def test_get_openai_tools_disabled(self):
        tool = _make_tool("t1")
        skill = Skill(
            name="s",
            description="d",
            applicability="a",
            tools=[tool],
            enabled=False,
        )
        assert skill.get_openai_tools() == []

    def test_get_tool_map_enabled(self):
        t1 = _make_tool("t1")
        t2 = _make_tool("t2")
        skill = Skill(
            name="s",
            description="d",
            applicability="a",
            tools=[t1, t2],
            enabled=True,
        )
        result = skill.get_tool_map()
        assert result == {"t1": t1, "t2": t2}

    def test_get_tool_map_disabled(self):
        tool = _make_tool("t1")
        skill = Skill(
            name="s",
            description="d",
            applicability="a",
            tools=[tool],
            enabled=False,
        )
        assert skill.get_tool_map() == {}


# ── protocol.py: _safe ─────────────────────────────────────────


class TestSafe:
    def test_normal_dict_return(self):
        result = _safe(lambda: {"key": "value"})
        assert result == {"key": "value"}

    def test_pydantic_model_return(self):
        class MyModel(BaseModel):
            name: str
            age: int

        result = _safe(lambda: MyModel(name="Alice", age=30))
        assert result == {"name": "Alice", "age": 30}

    def test_list_of_pydantic_models(self):
        class Item(BaseModel):
            x: int

        items = [Item(x=1), Item(x=2)]
        result = _safe(lambda: items)
        assert result == [{"x": 1}, {"x": 2}]

    def test_list_mixed_with_dicts(self):
        data = [{"x": 1}, {"x": 2}]
        result = _safe(lambda: data)
        assert result == [{"x": 1}, {"x": 2}]

    def test_http_exception_caught(self):
        def raise_http():
            raise HTTPException(status_code=404, detail="Not found")

        result = _safe(raise_http)
        assert result == {"error": "Not found"}

    def test_generic_exception_caught(self):
        def raise_err():
            raise ValueError("bad value")

        result = _safe(raise_err)
        assert result == {"error": "bad value"}

    def test_safe_passes_args(self):
        def add(a, b):
            return {"sum": a + b}

        result = _safe(add, 3, 4)
        assert result == {"sum": 7}

    def test_safe_passes_kwargs(self):
        def greet(name="world"):
            return {"msg": f"hello {name}"}

        result = _safe(greet, name="test")
        assert result == {"msg": "hello test"}


# ── skill_registry.py ──────────────────────────────────────────


class TestSkillRegistry:
    def test_register_and_get_skill(self):
        reg = SkillRegistry()
        skill = _make_skill("hr_ops")
        reg.register(skill)
        assert reg.get_skill("hr_ops") is skill

    def test_register_duplicate_skill_name_raises(self):
        reg = SkillRegistry()
        reg.register(_make_skill("dup"))
        with pytest.raises(ValueError, match="already registered"):
            reg.register(_make_skill("dup"))

    def test_register_duplicate_tool_name_raises(self):
        reg = SkillRegistry()
        shared_tool = _make_tool("shared_tool")
        reg.register(
            Skill(
                name="s1",
                description="d",
                applicability="a",
                tools=[shared_tool],
            )
        )
        with pytest.raises(ValueError, match="already belongs to skill"):
            reg.register(
                Skill(
                    name="s2",
                    description="d",
                    applicability="a",
                    tools=[_make_tool("shared_tool")],
                )
            )

    def test_unregister_removes_skill_and_tools(self):
        reg = SkillRegistry()
        tool = _make_tool("my_tool")
        skill = Skill(
            name="gone",
            description="d",
            applicability="a",
            tools=[tool],
            workflows={"wf1": lambda: {}},
        )
        reg.register(skill)
        assert reg.get_skill("gone") is not None
        reg.unregister("gone")
        assert reg.get_skill("gone") is None
        assert reg.get_skill_for_tool("my_tool") is None

    def test_unregister_nonexistent_is_noop(self):
        reg = SkillRegistry()
        reg.unregister("no_such")  # should not raise

    def test_get_skill_for_tool(self):
        reg = SkillRegistry()
        tool = _make_tool("find_emp")
        skill = _make_skill("emp", tools=[tool])
        reg.register(skill)
        assert reg.get_skill_for_tool("find_emp") is skill

    def test_get_all_tools_enabled_only(self):
        reg = SkillRegistry()
        t1 = _make_tool("t1")
        t2 = _make_tool("t2")
        reg.register(Skill(name="on", description="d", applicability="a", tools=[t1], enabled=True))
        reg.register(Skill(name="off", description="d", applicability="a", tools=[t2], enabled=False))
        all_tools = reg.get_all_tools()
        assert t1 in all_tools
        assert t2 not in all_tools

    def test_get_tool_map(self):
        reg = SkillRegistry()
        t1 = _make_tool("t1")
        t2 = _make_tool("t2")
        reg.register(Skill(name="s1", description="d", applicability="a", tools=[t1], enabled=True))
        reg.register(Skill(name="s2", description="d", applicability="a", tools=[t2], enabled=False))
        tool_map = reg.get_tool_map()
        assert "t1" in tool_map
        assert "t2" not in tool_map

    def test_get_skill_summaries(self):
        reg = SkillRegistry()
        reg.register(Skill(name="on", description="d1", applicability="a1", tools=[_make_tool("x")], enabled=True))
        reg.register(Skill(name="off", description="d2", applicability="a2", tools=[_make_tool("y")], enabled=False))
        summaries = reg.get_skill_summaries()
        assert len(summaries) == 1
        assert summaries[0]["name"] == "on"

    def test_get_tools_for_skills(self):
        reg = SkillRegistry()
        t1 = _make_tool("t1")
        t2 = _make_tool("t2")
        reg.register(Skill(name="s1", description="d", applicability="a", tools=[t1], enabled=True))
        reg.register(Skill(name="s2", description="d", applicability="a", tools=[t2], enabled=False))
        tools = reg.get_tools_for_skills(["s1", "s2"])
        assert t1 in tools
        assert t2 not in tools  # disabled

    def test_get_workflows_for_skills(self):
        def wf_fn():
            return {"done": True}

        reg = SkillRegistry()
        reg.register(
            Skill(
                name="s1",
                description="d",
                applicability="a",
                tools=[_make_tool("t1")],
                enabled=True,
                workflows={"onboard_employee": wf_fn},
            )
        )
        wf_map = reg.get_workflows_for_skills(["s1"])
        assert "onboard_employee" in wf_map
        assert wf_map["onboard_employee"] is reg.get_skill("s1")

    def test_enable_disable_skill(self):
        reg = SkillRegistry()
        skill = Skill(name="toggle", description="d", applicability="a", tools=[_make_tool("tg")], enabled=True)
        reg.register(skill)

        reg.disable("toggle")
        assert skill.enabled is False
        assert reg.get_all_tools() == []

        reg.enable("toggle")
        assert skill.enabled is True
        assert len(reg.get_all_tools()) == 1

    def test_enable_nonexistent_returns_false(self):
        reg = SkillRegistry()
        assert reg.enable("nope") is False
        assert reg.disable("nope") is False

    def test_list_skills(self):
        reg = SkillRegistry()
        reg.register(
            Skill(
                name="s1",
                description="desc1",
                applicability="a",
                tools=[_make_tool("t1"), _make_tool("t2")],
                workflows={"wf1": lambda: {}},
            )
        )
        info = reg.list_skills()
        assert len(info) == 1
        assert info[0] == {
            "name": "s1",
            "description": "desc1",
            "enabled": True,
            "tool_count": 2,
            "workflow_count": 1,
        }


# ── skill_router.py ────────────────────────────────────────────


class TestSkillRouter:
    def test_route_empty_summaries(self):
        client = MagicMock()
        router = SkillRouter(client, model="test-model")
        result = router.route("hello", [])
        assert result == []

    def test_route_with_mock_client(self):
        client = MagicMock()
        tool_call = MagicMock()
        tool_call.function.arguments = json.dumps({"skills": ["emp_mgmt", "payroll"]})
        message = MagicMock()
        message.tool_calls = [tool_call]
        client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=message)])

        router = SkillRouter(client, model="test-model")
        summaries = [
            {"name": "emp_mgmt", "description": "Employee management", "applicability": "employee ops"},
            {"name": "payroll", "description": "Payroll processing", "applicability": "salary ops"},
        ]
        result = router.route("Calculate salary", summaries)
        assert result == ["emp_mgmt", "payroll"]

    def test_route_fallback_on_api_failure(self):
        client = MagicMock()
        client.chat.completions.create.side_effect = Exception("API down")

        router = SkillRouter(client, model="test-model")
        summaries = [
            {"name": "emp_mgmt", "description": "Employee management", "applicability": "employee ops"},
            {"name": "payroll", "description": "Payroll processing", "applicability": "salary ops"},
        ]
        result = router.route("Calculate salary", summaries)
        assert result == ["emp_mgmt", "payroll"]


# ── history.py: InMemoryHistoryStore ───────────────────────────


class TestInMemoryHistoryStore:
    def test_get_messages_new_session_empty(self):
        store = InMemoryHistoryStore()
        assert store.get_messages("new-session") == []

    def test_add_and_get_messages(self):
        store = InMemoryHistoryStore()
        store.add_message("s1", {"role": "system", "content": "prompt"})
        store.add_message("s1", {"role": "user", "content": "hi"})
        msgs = store.get_messages("s1")
        assert len(msgs) == 2
        assert msgs[0]["role"] == "system"
        assert msgs[1]["content"] == "hi"

    def test_max_history_messages_trims(self):
        store = InMemoryHistoryStore()
        session_id = "trim-test"
        # Add system message first, then many user messages
        store.add_message(session_id, {"role": "system", "content": "system prompt"})
        # settings.agent_max_history_messages defaults to 50
        # We add 60 user messages to exceed the limit
        for i in range(60):
            store.add_message(session_id, {"role": "user", "content": f"msg {i}"})

        msgs = store.get_messages(session_id)
        # Should be capped; system message should be preserved
        assert msgs[0]["role"] == "system"
        assert msgs[0]["content"] == "system prompt"
        # Total should be at most agent_max_history_messages
        from app.config import settings

        assert len(msgs) <= settings.agent_max_history_messages

    def test_clear_removes_session(self):
        store = InMemoryHistoryStore()
        store.add_message("s1", {"role": "user", "content": "hello"})
        store.clear("s1")
        assert store.get_messages("s1") == []

    def test_list_sessions(self):
        store = InMemoryHistoryStore()
        store.add_message("s1", {"role": "user", "content": "a"})
        store.add_message("s2", {"role": "user", "content": "b"})
        sessions = store.list_sessions()
        assert set(sessions) == {"s1", "s2"}


# ── react_agent.py: _build_hook_memory ────────────────────────


class TestBuildHookMemory:
    def test_onboard_employee_success(self):
        result = {"employee": {"name": "Alice", "id": 42}}
        ctx = {"session_id": "sess1", "user_tag": "user1"}
        mem = _build_hook_memory("onboard_employee", result, ctx)
        assert mem is not None
        assert mem["memory_type"] == "fact"
        assert mem["category"] == "onboarding"
        assert "Alice" in mem["content"]
        assert mem["session_id"] == "sess1"

    def test_onboard_employee_error_returns_none(self):
        result = {"error": "Something went wrong"}
        ctx = {"session_id": "sess1", "user_tag": "user1"}
        assert _build_hook_memory("onboard_employee", result, ctx) is None

    def test_analyze_function_success(self):
        result = {"summary": "Salary distribution normal"}
        ctx = {"session_id": "sess1", "user_tag": "user1"}
        mem = _build_hook_memory("analyze_salary", result, ctx)
        assert mem is not None
        assert mem["memory_type"] == "observation"
        assert mem["category"] == "analytics"

    def test_analyze_function_error_returns_none(self):
        result = {"error": "Analysis failed"}
        ctx = {"session_id": "sess1", "user_tag": "user1"}
        assert _build_hook_memory("analyze_salary", result, ctx) is None

    def test_unknown_function_returns_none(self):
        result = {"data": "whatever"}
        ctx = {"session_id": "sess1", "user_tag": "user1"}
        assert _build_hook_memory("unknown_func", result, ctx) is None

    def test_query_project_progress_success(self):
        result = {"project": "HR V2", "progress": 60}
        ctx = {"session_id": "sess1", "user_tag": "user1"}
        mem = _build_hook_memory("query_project_progress", result, ctx)
        assert mem is not None
        assert mem["memory_type"] == "observation"
        assert mem["category"] == "project"


# ── react_agent.py: ReActAgent.chat ────────────────────────────


def _make_mock_message(content=None, tool_calls=None, reasoning_content=None):
    """Build a mock ChatCompletionMessage for OpenAI response."""
    msg = MagicMock()
    msg.content = content
    msg.tool_calls = tool_calls
    msg.reasoning_content = reasoning_content
    msg.model_dump.return_value = {
        "role": "assistant",
        "content": content,
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in (tool_calls or [])
        ]
        if tool_calls
        else None,
    }
    return msg


def _make_mock_tool_call(call_id, name, arguments):
    tc = MagicMock()
    tc.id = call_id
    tc.function = MagicMock()
    tc.function.name = name
    tc.function.arguments = arguments
    return tc


class TestReActAgentChat:
    @patch("app.agent.react_agent.OpenAI")
    @patch("app.agent.react_agent.SkillRouter")
    @patch("app.agent.react_agent.settings")
    def test_chat_direct_answer(self, mock_settings, mock_router_cls, mock_openai_cls):
        """LLM returns a direct answer with no tool calls."""
        # Setup
        mock_settings.deepseek_api_key = "fake-key"
        mock_settings.deepseek_base_url = "https://fake.api"
        mock_settings.deepseek_model = "fake-model"
        mock_settings.agent_max_iterations = 10
        mock_settings.agent_max_history_messages = 50
        mock_settings.default_user_tag = "default"
        mock_settings.use_skill_routing = False

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        # Direct answer — no tool_calls
        direct_msg = _make_mock_message(content="You have 5 employees.")
        mock_client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=direct_msg)])

        history = InMemoryHistoryStore()
        registry = SkillRegistry()
        registry.register(_make_skill("test_skill"))

        agent = ReActAgent(
            history_store=history,
            skill_registry=registry,
            use_routing=False,
        )
        # Override the client/router that __init__ created
        agent._client = mock_client

        reply = agent.chat("sess1", "How many employees?")
        assert reply == "You have 5 employees."

    @patch("app.agent.react_agent.OpenAI")
    @patch("app.agent.react_agent.SkillRouter")
    @patch("app.agent.react_agent.settings")
    def test_chat_with_tool_call_then_answer(self, mock_settings, mock_router_cls, mock_openai_cls):
        """LLM first returns a tool call, then on the second call returns a final answer."""
        mock_settings.deepseek_api_key = "fake-key"
        mock_settings.deepseek_base_url = "https://fake.api"
        mock_settings.deepseek_model = "fake-model"
        mock_settings.agent_max_iterations = 10
        mock_settings.agent_max_history_messages = 50
        mock_settings.default_user_tag = "default"
        mock_settings.use_skill_routing = False

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        # First response: tool call
        tc = _make_mock_tool_call("call_1", "test_tool", "{}")
        tool_msg = _make_mock_message(content=None, tool_calls=[tc])
        # Second response: direct answer
        answer_msg = _make_mock_message(content="Found: Alice, Bob")
        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=tool_msg)]),
            MagicMock(choices=[MagicMock(message=answer_msg)]),
        ]

        tool_fn = MagicMock(return_value={"result": "Alice, Bob"})
        tool = _make_tool("test_tool", fn=tool_fn)
        skill = _make_skill("test_skill", tools=[tool])

        history = InMemoryHistoryStore()
        registry = SkillRegistry()
        registry.register(skill)

        agent = ReActAgent(
            history_store=history,
            skill_registry=registry,
            use_routing=False,
        )
        agent._client = mock_client

        reply = agent.chat("sess2", "Find employees")
        assert reply == "Found: Alice, Bob"
        tool_fn.assert_called_once()

    @patch("app.agent.react_agent.OpenAI")
    @patch("app.agent.react_agent.SkillRouter")
    @patch("app.agent.react_agent.settings")
    def test_chat_respects_max_iterations(self, mock_settings, mock_router_cls, mock_openai_cls):
        """Agent stops after max_iterations and returns the fallback message."""
        mock_settings.deepseek_api_key = "fake-key"
        mock_settings.deepseek_base_url = "https://fake.api"
        mock_settings.deepseek_model = "fake-model"
        mock_settings.agent_max_iterations = 2
        mock_settings.agent_max_history_messages = 50
        mock_settings.default_user_tag = "default"
        mock_settings.use_skill_routing = False

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        # Always return tool calls so the loop never exits naturally
        tc = _make_mock_tool_call("call_loop", "test_tool", "{}")
        loop_msg = _make_mock_message(content=None, tool_calls=[tc])
        mock_client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=loop_msg)])

        tool = _make_tool("test_tool", fn=lambda: {"data": "looping"})
        skill = _make_skill("test_skill", tools=[tool])

        history = InMemoryHistoryStore()
        registry = SkillRegistry()
        registry.register(skill)

        agent = ReActAgent(
            history_store=history,
            skill_registry=registry,
            use_routing=False,
        )
        agent._client = mock_client

        reply = agent.chat("sess3", "Loop test")
        assert "最大迭代次数" in reply
