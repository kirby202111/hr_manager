"""LangGraph-backed agent runtime."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Sequence
from typing import Any

from openai import APIError, APITimeoutError, RateLimitError

from app.agent.protocol import AgentTool, BaseAgent, BaseHistoryStore, ToolExecutionContext
from app.agent.skill_registry import SkillRegistry
from app.agent.skill_router import SkillRouter
from app.config import settings

try:
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
    from langchain_openai import ChatOpenAI
    from langgraph.errors import GraphRecursionError
    from langgraph.graph import END, START, MessagesState, StateGraph

    _LANGGRAPH_IMPORT_ERROR: ImportError | None = None
except ImportError as exc:  # pragma: no cover - handled gracefully at runtime
    AIMessage = Any
    BaseMessage = Any
    HumanMessage = Any
    SystemMessage = Any
    ToolMessage = Any
    ChatOpenAI = None
    GraphRecursionError = RuntimeError
    MessagesState = dict[str, Any]
    StateGraph = None
    START = "__start__"
    END = "__end__"
    _LANGGRAPH_IMPORT_ERROR = exc


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are WorkforceOps Copilot for a manufacturing workforce operations system.

Use the available tools whenever the user asks about real business data
or wants you to create, update, or validate records.
Key business flows include:
- worker master data and assignments
- skills, certifications, trainings, and equipment authorizations
- attendance, leave, and payroll
- production lines, workstations, orders, operations, and shift plans
- eligibility checks before staffing or assignment decisions
- SOP and safety lookup through the local knowledge base

Rules:
- Never invent IDs, dates, or business records when a tool can verify them.
- Before proposing staffing changes, prefer checking eligibility when workstation or assignment risk is involved.
- Summarize tool results clearly and mention blockers directly.
- Use memory only for durable user context, preferences, or reminders.
""".strip()


class LangGraphAgent(BaseAgent):
    """Agent runtime implemented with a LangGraph message loop."""

    def __init__(
        self,
        history_store: BaseHistoryStore,
        skill_registry: SkillRegistry,
        *,
        use_routing: bool = True,
    ) -> None:
        self._skill_registry = skill_registry
        self._history = history_store
        self._router = SkillRouter()
        self._use_routing = use_routing
        self._client = None

        if ChatOpenAI is not None and settings.deepseek_api_key:
            self._client = ChatOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                model=settings.deepseek_model,
                temperature=0,
                max_retries=2,
            )

    def chat(self, session_id: str, message: str, user_tag: str | None = None) -> str:
        resolved_user_tag = user_tag or settings.default_user_tag
        self._initialize_session(session_id, resolved_user_tag)
        self._add_history_message(session_id, "user", user_tag=resolved_user_tag, content=message)

        dependency_message = self._dependency_error_message()
        if dependency_message is not None:
            self._add_history_message(
                session_id,
                "assistant",
                user_tag=resolved_user_tag,
                content=dependency_message,
            )
            return dependency_message

        if self._client is None:
            reply = "DeepSeek API key is not configured. Set DEEPSEEK_API_KEY in .env."
            self._add_history_message(session_id, "assistant", user_tag=resolved_user_tag, content=reply)
            return reply

        tools = self._resolve_tools(message)
        context = ToolExecutionContext(session_id=session_id, user_tag=resolved_user_tag)
        messages = self._load_langchain_messages(session_id)
        graph = self._build_graph(tools, context)

        final_reply = ""
        try:
            for update in graph.stream(
                {"messages": messages},
                config={"recursion_limit": self._recursion_limit()},
                stream_mode="updates",
            ):
                final_reply = self._persist_graph_update(session_id, resolved_user_tag, update, final_reply)
        except GraphRecursionError:
            final_reply = "The agent reached the maximum tool-iteration limit before finishing the request."
            self._add_history_message(session_id, "assistant", user_tag=resolved_user_tag, content=final_reply)
        except (APITimeoutError, RateLimitError, APIError) as exc:
            logger.warning("Agent model call failed: %s", exc)
            final_reply = f"Model call failed: {exc}"
            self._add_history_message(session_id, "assistant", user_tag=resolved_user_tag, content=final_reply)
        except Exception:
            logger.exception("Unexpected agent runtime error")
            raise

        return final_reply

    async def chat_stream(
        self,
        session_id: str,
        message: str,
        user_tag: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        resolved_user_tag = user_tag or settings.default_user_tag
        self._initialize_session(session_id, resolved_user_tag)
        self._add_history_message(session_id, "user", user_tag=resolved_user_tag, content=message)

        dependency_message = self._dependency_error_message()
        if dependency_message is not None:
            self._add_history_message(
                session_id,
                "assistant",
                user_tag=resolved_user_tag,
                content=dependency_message,
            )
            yield {"event": "message", "data": dependency_message}
            yield {"event": "done", "data": ""}
            return

        if self._client is None:
            reply = "DeepSeek API key is not configured. Set DEEPSEEK_API_KEY in .env."
            self._add_history_message(session_id, "assistant", user_tag=resolved_user_tag, content=reply)
            yield {"event": "message", "data": reply}
            yield {"event": "done", "data": ""}
            return

        tools = self._resolve_tools(message)
        context = ToolExecutionContext(session_id=session_id, user_tag=resolved_user_tag)
        messages = self._load_langchain_messages(session_id)
        graph = self._build_graph(tools, context)
        pending_tool_names: list[str] = []

        try:
            async for update in graph.astream(
                {"messages": messages},
                config={"recursion_limit": self._recursion_limit()},
                stream_mode="updates",
            ):
                for node_name, payload in update.items():
                    node_messages = payload.get("messages", [])
                    for node_message in node_messages:
                        history_payload = self._message_to_history_payload(node_message)
                        if history_payload is not None:
                            self._history.add_message(session_id, history_payload, user_tag=resolved_user_tag)

                        if node_name == "agent" and isinstance(node_message, AIMessage):
                            text = self._content_to_text(node_message.content)
                            if text:
                                yield {"event": "message", "data": text}
                            tool_names = self._extract_tool_names(node_message)
                            if tool_names:
                                pending_tool_names = tool_names
                                yield {"event": "tool_call", "data": json.dumps(tool_names, ensure_ascii=False)}
                        elif node_name == "tools" and pending_tool_names:
                            yield {"event": "tool_result", "data": json.dumps(pending_tool_names, ensure_ascii=False)}
                            pending_tool_names = []
        except GraphRecursionError:
            reply = "The agent reached the maximum tool-iteration limit before finishing the request."
            self._add_history_message(session_id, "assistant", user_tag=resolved_user_tag, content=reply)
            yield {"event": "message", "data": reply}
        except (APITimeoutError, RateLimitError, APIError) as exc:
            logger.warning("Agent model stream failed: %s", exc)
            yield {"event": "error", "data": f"Model call failed: {exc}"}
            return
        except Exception as exc:
            logger.exception("Unexpected agent runtime error")
            yield {"event": "error", "data": str(exc)}
            return

        yield {"event": "done", "data": ""}

    def _dependency_error_message(self) -> str | None:
        if _LANGGRAPH_IMPORT_ERROR is None:
            return None
        return "LangGraph runtime dependencies are not installed. Run `uv sync` to install project dependencies."

    def _initialize_session(self, session_id: str, user_tag: str) -> None:
        if not self._history.get_messages(session_id):
            self._add_history_message(session_id, "system", user_tag=user_tag, content=SYSTEM_PROMPT)

    def _resolve_tools(self, message: str) -> list[AgentTool]:
        enabled_skills = self._skill_registry.get_enabled_skills()
        if not self._use_routing:
            return self._skill_registry.get_all_tools()
        skill_names = self._router.route(message, enabled_skills)
        return self._skill_registry.get_tools_for_skills(skill_names)

    def _recursion_limit(self) -> int:
        return max(4, settings.agent_max_iterations * 2 + 2)

    def _build_graph(self, tools: Sequence[AgentTool], context: ToolExecutionContext):
        if StateGraph is None or self._client is None:
            raise RuntimeError(self._dependency_error_message() or "Model client is not configured")

        tool_schemas = [tool.to_openai_tool() for tool in tools]
        tool_map = {tool.name: tool for tool in tools}
        model = self._client.bind_tools(tool_schemas) if tool_schemas else self._client

        def call_model(state: MessagesState) -> dict[str, list[BaseMessage]]:
            response = model.invoke(state["messages"])
            return {"messages": [response]}

        def execute_tools(state: MessagesState) -> dict[str, list[BaseMessage]]:
            last_message = state["messages"][-1]
            tool_calls = getattr(last_message, "tool_calls", []) or []
            results: list[BaseMessage] = []
            for tool_call in tool_calls:
                tool_name = str(tool_call.get("name", ""))
                tool = tool_map.get(tool_name)
                if tool is None:
                    result = {"error": f"Tool '{tool_name}' is not available in the current skill set."}
                else:
                    arguments = self._normalize_tool_arguments(tool_call.get("args"))
                    result = tool.invoke(arguments, context)
                results.append(
                    ToolMessage(
                        content=json.dumps(result, ensure_ascii=False, default=str),
                        tool_call_id=str(tool_call.get("id", "")),
                    )
                )
            return {"messages": results}

        def should_continue(state: MessagesState) -> str:
            last_message = state["messages"][-1]
            if isinstance(last_message, AIMessage) and getattr(last_message, "tool_calls", None):
                return "tools"
            return "end"

        graph = StateGraph(MessagesState)
        graph.add_node("agent", call_model)
        graph.add_node("tools", execute_tools)
        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
        graph.add_edge("tools", "agent")
        return graph.compile()

    def _persist_graph_update(
        self,
        session_id: str,
        user_tag: str,
        update: dict[str, Any],
        current_reply: str,
    ) -> str:
        final_reply = current_reply
        for payload in update.values():
            for node_message in payload.get("messages", []):
                history_payload = self._message_to_history_payload(node_message)
                if history_payload is not None:
                    self._history.add_message(session_id, history_payload, user_tag=user_tag)
                if isinstance(node_message, AIMessage) and not self._extract_tool_names(node_message):
                    final_reply = self._content_to_text(node_message.content) or final_reply
        return final_reply

    def _add_history_message(
        self,
        session_id: str,
        role: str,
        *,
        user_tag: str,
        content: str | None = None,
        tool_call_id: str | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> None:
        message: dict[str, Any] = {"role": role}
        if content is not None:
            message["content"] = content
        if tool_call_id is not None:
            message["tool_call_id"] = tool_call_id
        if tool_calls is not None:
            message["tool_calls"] = tool_calls
        self._history.add_message(session_id, message, user_tag=user_tag)

    def _load_langchain_messages(self, session_id: str) -> list[BaseMessage]:
        messages: list[BaseMessage] = []
        for message in self._history.get_messages(session_id):
            converted = self._history_to_langchain_message(message)
            if converted is not None:
                messages.append(converted)
        return messages

    def _history_to_langchain_message(self, message: dict[str, Any]) -> BaseMessage | None:
        role = message.get("role")
        content = message.get("content") or ""
        if role == "system":
            return SystemMessage(content=content)
        if role == "user":
            return HumanMessage(content=content)
        if role == "assistant":
            return AIMessage(
                content=content,
                tool_calls=self._history_tool_calls_to_langchain(message.get("tool_calls")),
            )
        if role == "tool":
            return ToolMessage(content=content, tool_call_id=message.get("tool_call_id") or "")
        return None

    def _history_tool_calls_to_langchain(self, raw_tool_calls: Any) -> list[dict[str, Any]]:
        if raw_tool_calls is None:
            return []
        tool_calls = raw_tool_calls
        if isinstance(tool_calls, str):
            try:
                tool_calls = json.loads(tool_calls)
            except json.JSONDecodeError:
                return []
        normalized: list[dict[str, Any]] = []
        if not isinstance(tool_calls, list):
            return normalized
        for tool_call in tool_calls:
            if not isinstance(tool_call, dict):
                continue
            function_payload = tool_call.get("function", {})
            arguments = function_payload.get("arguments", {})
            normalized.append(
                {
                    "id": tool_call.get("id", ""),
                    "name": function_payload.get("name", ""),
                    "args": self._normalize_tool_arguments(arguments),
                    "type": "tool_call",
                }
            )
        return normalized

    def _message_to_history_payload(self, message: BaseMessage) -> dict[str, Any] | None:
        if isinstance(message, SystemMessage):
            return {"role": "system", "content": self._content_to_text(message.content)}
        if isinstance(message, HumanMessage):
            return {"role": "user", "content": self._content_to_text(message.content)}
        if isinstance(message, AIMessage):
            return {
                "role": "assistant",
                "content": self._content_to_text(message.content),
                "tool_calls": self._langchain_tool_calls_to_history(message.tool_calls),
            }
        if isinstance(message, ToolMessage):
            return {
                "role": "tool",
                "content": self._content_to_text(message.content),
                "tool_call_id": getattr(message, "tool_call_id", None),
            }
        return None

    @staticmethod
    def _normalize_tool_arguments(arguments: Any) -> dict[str, Any]:
        if arguments is None:
            return {}
        if isinstance(arguments, str):
            try:
                loaded = json.loads(arguments)
            except json.JSONDecodeError:
                return {}
            return loaded if isinstance(loaded, dict) else {}
        return arguments if isinstance(arguments, dict) else {}

    @staticmethod
    def _content_to_text(content: Any) -> str:
        if isinstance(content, str):
            return content
        if not isinstance(content, list):
            return str(content or "")

        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
                continue
            if not isinstance(block, dict):
                parts.append(str(block))
                continue
            text = block.get("text")
            if isinstance(text, str):
                parts.append(text)
                continue
            if isinstance(text, dict) and isinstance(text.get("value"), str):
                parts.append(text["value"])
        return "".join(parts)

    @staticmethod
    def _langchain_tool_calls_to_history(tool_calls: Any) -> list[dict[str, Any]] | None:
        if not tool_calls:
            return None
        normalized: list[dict[str, Any]] = []
        for tool_call in tool_calls:
            if not isinstance(tool_call, dict):
                continue
            normalized.append(
                {
                    "id": tool_call.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": tool_call.get("name", ""),
                        "arguments": json.dumps(tool_call.get("args", {}), ensure_ascii=False),
                    },
                }
            )
        return normalized or None

    @staticmethod
    def _extract_tool_names(message: AIMessage) -> list[str]:
        tool_calls = getattr(message, "tool_calls", []) or []
        return [str(tool_call.get("name", "")) for tool_call in tool_calls if tool_call.get("name")]


ReActAgent = LangGraphAgent

__all__ = ["LangGraphAgent", "ReActAgent"]
