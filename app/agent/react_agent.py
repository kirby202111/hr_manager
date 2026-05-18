"""ReAct-style agent runtime."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from openai import APIError, APITimeoutError, OpenAI, RateLimitError

from app.agent.protocol import AgentTool, BaseHistoryStore
from app.agent.skill_registry import SkillRegistry
from app.agent.skill_router import SkillRouter
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Workforce Ops assistant.

You help users inspect workforce, attendance, skill, qualification, shopfloor, staffing, and knowledge-base data.
Use tools whenever they help you answer accurately.
When information is missing, say so plainly.
Do not invent business data.
"""


class ReActAgent:
    """Simple function-calling agent with pluggable history and skills."""

    def __init__(
        self,
        history_store: BaseHistoryStore,
        skill_registry: SkillRegistry,
        use_routing: bool = True,
    ) -> None:
        self._history = history_store
        self._registry = skill_registry
        self._router = SkillRouter()
        self._use_routing = use_routing
        self._client: OpenAI | None = None
        if settings.deepseek_api_key:
            self._client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )

    def chat(self, session_id: str, message: str, user_tag: str | None = None) -> str:
        effective_tag = user_tag or settings.default_user_tag
        self._init_session(session_id, effective_tag)
        self._history.add_message(session_id, {"role": "user", "content": message}, user_tag=effective_tag)

        if self._client is None:
            reply = "Agent model is not configured. Set DEEPSEEK_API_KEY before using chat."
            self._history.add_message(session_id, {"role": "assistant", "content": reply}, user_tag=effective_tag)
            return reply

        tools, tool_map = self._resolve_tools(message)
        messages = self._history.get_messages(session_id)
        final_reply = ""

        for _ in range(settings.agent_max_iterations):
            response = self._create_completion(messages, tools)
            choice = response.choices[0]
            assistant_message = choice.message.model_dump()
            self._history.add_message(session_id, assistant_message, user_tag=effective_tag)

            if not assistant_message.get("tool_calls"):
                final_reply = assistant_message.get("content") or ""
                break

            self._execute_tool_calls(session_id, effective_tag, assistant_message["tool_calls"], tool_map)
            messages = self._history.get_messages(session_id)
        else:
            final_reply = "The assistant reached the maximum number of tool iterations."
            self._history.add_message(session_id, {"role": "assistant", "content": final_reply}, user_tag=effective_tag)

        return final_reply

    async def chat_stream(
        self,
        session_id: str,
        message: str,
        user_tag: str | None = None,
    ) -> AsyncIterator[dict[str, str]]:
        effective_tag = user_tag or settings.default_user_tag
        self._init_session(session_id, effective_tag)
        self._history.add_message(session_id, {"role": "user", "content": message}, user_tag=effective_tag)

        if self._client is None:
            reply = "Agent model is not configured. Set DEEPSEEK_API_KEY before using chat."
            self._history.add_message(session_id, {"role": "assistant", "content": reply}, user_tag=effective_tag)
            yield {"event": "message", "data": reply}
            yield {"event": "done", "data": ""}
            return

        tools, tool_map = self._resolve_tools(message)

        for _ in range(settings.agent_max_iterations):
            messages = self._history.get_messages(session_id)
            response = self._create_completion(messages, tools)
            choice = response.choices[0]
            assistant_message = choice.message.model_dump()
            self._history.add_message(session_id, assistant_message, user_tag=effective_tag)

            content = assistant_message.get("content") or ""
            if content:
                yield {"event": "message", "data": content}

            tool_calls = assistant_message.get("tool_calls") or []
            if not tool_calls:
                yield {"event": "done", "data": ""}
                return

            yield {
                "event": "tool_call",
                "data": json.dumps([tool_call["function"]["name"] for tool_call in tool_calls], ensure_ascii=False),
            }
            self._execute_tool_calls(session_id, effective_tag, tool_calls, tool_map)
            yield {
                "event": "tool_result",
                "data": json.dumps([tool_call["function"]["name"] for tool_call in tool_calls], ensure_ascii=False),
            }

        yield {"event": "error", "data": "The assistant reached the maximum number of tool iterations."}

    def _init_session(self, session_id: str, user_tag: str) -> None:
        if self._history.get_messages(session_id):
            return
        self._history.add_message(session_id, {"role": "system", "content": SYSTEM_PROMPT}, user_tag=user_tag)

    def _resolve_tools(self, message: str) -> tuple[list[dict[str, Any]], dict[str, AgentTool]]:
        enabled_skills = self._registry.get_enabled_skills()
        if not self._use_routing:
            tools = self._registry.get_all_tools()
        else:
            skill_names = self._router.route(message, enabled_skills)
            memory_skill = self._registry.get_skill("memory")
            if "memory" not in skill_names and memory_skill and memory_skill.enabled:
                skill_names.append("memory")
            tools = self._registry.get_tools_for_skills(skill_names)
        tool_map = {tool.name: tool for tool in tools}
        return [tool.to_openai_tool() for tool in tools], tool_map

    def _create_completion(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> Any:
        assert self._client is not None
        try:
            return self._client.chat.completions.create(
                model=settings.deepseek_model,
                messages=messages,
                tools=tools or None,
                temperature=0.2,
            )
        except RateLimitError as exc:
            raise RuntimeError("Agent model rate limit exceeded.") from exc
        except APITimeoutError as exc:
            raise RuntimeError("Agent model request timed out.") from exc
        except APIError as exc:
            raise RuntimeError(f"Agent model API error: {exc.message}") from exc

    def _execute_tool_calls(
        self,
        session_id: str,
        user_tag: str,
        tool_calls: list[dict[str, Any]],
        tool_map: dict[str, AgentTool],
    ) -> None:
        for tool_call in tool_calls:
            name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]
            try:
                parsed_arguments = json.loads(arguments) if arguments else {}
            except json.JSONDecodeError:
                parsed_arguments = {}

            tool = tool_map.get(name)
            if tool is None:
                result: Any = {"error": f"Unknown tool: {name}"}
            else:
                try:
                    result = tool.fn(**parsed_arguments)
                except Exception as exc:  # pragma: no cover - defensive runtime guard
                    logger.warning("Tool execution failed for %s", name, exc_info=True)
                    result = {"error": str(exc)}

            self._history.add_message(
                session_id,
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                },
                user_tag=user_tag,
            )


__all__ = ["ReActAgent"]
