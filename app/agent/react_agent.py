"""LangGraph-backed agent runtime."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field
from typing import Any

from openai import APIError, APITimeoutError, RateLimitError

from app.agent.onboarding_orchestrator import OnboardingOrchestrator
from app.agent.orchestrator_manager import OrchestratorManager, ResolvedOrchestrator
from app.agent.protocol import (
    AgentTool,
    BaseAgent,
    BaseHistoryStore,
    SkillMatch,
    ToolExecutionContext,
    ToolResultEnvelope,
)
from app.agent.skill_registry import SkillRegistry
from app.agent.skill_router import SkillRouter
from app.config import settings

try:
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
    from langgraph.errors import GraphRecursionError
    from langgraph.graph import END, START, MessagesState, StateGraph

    from app.agent.deepseek_chat import DeepSeekChatOpenAI

    _LANGGRAPH_IMPORT_ERROR: ImportError | None = None
except ImportError as exc:  # pragma: no cover - handled gracefully at runtime
    AIMessage = Any
    BaseMessage = Any
    HumanMessage = Any
    SystemMessage = Any
    ToolMessage = Any
    DeepSeekChatOpenAI = None
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

ALLOWED_ENVELOPE_STATUSES = {"success", "needs_input", "blocked", "error"}
RECENT_HISTORY_WINDOW = 12


@dataclass(slots=True)
class TurnTrace:
    session_id: str
    user_tag: str
    selected_skills: list[dict[str, Any]] = field(default_factory=list)
    selected_tools: list[str] = field(default_factory=list)
    orchestrators: list[str] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    tool_failures: list[dict[str, str]] = field(default_factory=list)
    stopped_reason: str = "completed"
    recursion_limit_hit: bool = False

    def as_log_payload(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_tag": self.user_tag,
            "selected_skills": self.selected_skills,
            "selected_tools": self.selected_tools,
            "orchestrators": self.orchestrators,
            "tool_calls": self.tool_calls,
            "tool_failures": self.tool_failures,
            "stopped_reason": self.stopped_reason,
            "recursion_limit_hit": self.recursion_limit_hit,
        }


@dataclass(slots=True)
class TurnPlan:
    session_id: str
    user_tag: str
    message: str
    context: ToolExecutionContext
    skill_matches: list[SkillMatch]
    tools: list[AgentTool]
    runtime_messages: list[dict[str, str]]
    orchestrators: list[ResolvedOrchestrator]
    trace: TurnTrace


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
        self._orchestrators = OrchestratorManager([OnboardingOrchestrator()])
        self._use_routing = use_routing
        self._client = None

        if DeepSeekChatOpenAI is not None and settings.deepseek_api_key:
            self._client = DeepSeekChatOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                model=settings.deepseek_model,
                temperature=0,
                max_retries=2,
            )

    def chat(self, session_id: str, message: str, user_tag: str | None = None) -> str:
        resolved_user_tag = user_tag or settings.default_user_tag
        plan = self._prepare_turn(session_id, message, resolved_user_tag)

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

        messages = self._load_langchain_messages(session_id, plan.runtime_messages)
        graph = self._build_graph(plan.tools, plan.context, plan.orchestrators, plan.trace)

        final_reply = ""
        try:
            for update in graph.stream(
                {"messages": messages},
                config={"recursion_limit": self._recursion_limit()},
                stream_mode="updates",
            ):
                final_reply = self._persist_graph_update(session_id, resolved_user_tag, update, final_reply)
        except GraphRecursionError:
            plan.trace.recursion_limit_hit = True
            plan.trace.stopped_reason = "recursion_limit"
            final_reply = "The agent reached the maximum tool-iteration limit before finishing the request."
            self._add_history_message(session_id, "assistant", user_tag=resolved_user_tag, content=final_reply)
        except (APITimeoutError, RateLimitError, APIError) as exc:
            logger.warning("Agent model call failed: %s", exc)
            plan.trace.stopped_reason = "model_error"
            final_reply = f"Model call failed: {exc}"
            self._add_history_message(session_id, "assistant", user_tag=resolved_user_tag, content=final_reply)
        except Exception:
            plan.trace.stopped_reason = "runtime_error"
            logger.exception("Unexpected agent runtime error")
            raise
        finally:
            self._log_turn_trace(plan.trace)

        return final_reply

    async def chat_stream(
        self,
        session_id: str,
        message: str,
        user_tag: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        resolved_user_tag = user_tag or settings.default_user_tag
        plan = self._prepare_turn(session_id, message, resolved_user_tag)

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

        messages = self._load_langchain_messages(session_id, plan.runtime_messages)
        graph = self._build_graph(plan.tools, plan.context, plan.orchestrators, plan.trace)
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
            plan.trace.recursion_limit_hit = True
            plan.trace.stopped_reason = "recursion_limit"
            reply = "The agent reached the maximum tool-iteration limit before finishing the request."
            self._add_history_message(session_id, "assistant", user_tag=resolved_user_tag, content=reply)
            yield {"event": "message", "data": reply}
        except (APITimeoutError, RateLimitError, APIError) as exc:
            logger.warning("Agent model stream failed: %s", exc)
            plan.trace.stopped_reason = "model_error"
            yield {"event": "error", "data": f"Model call failed: {exc}"}
            return
        except Exception as exc:
            plan.trace.stopped_reason = "runtime_error"
            logger.exception("Unexpected agent runtime error")
            yield {"event": "error", "data": str(exc)}
            return
        finally:
            self._log_turn_trace(plan.trace)

        yield {"event": "done", "data": ""}

    def _dependency_error_message(self) -> str | None:
        if _LANGGRAPH_IMPORT_ERROR is None:
            return None
        return "LangGraph runtime dependencies are not installed. Run `uv sync` to install project dependencies."

    def _initialize_session(self, session_id: str, user_tag: str) -> None:
        if not self._history.get_messages(session_id):
            self._add_history_message(session_id, "system", user_tag=user_tag, content=SYSTEM_PROMPT)

    def _prepare_turn(self, session_id: str, message: str, user_tag: str) -> TurnPlan:
        self._initialize_session(session_id, user_tag)
        self._add_history_message(session_id, "user", user_tag=user_tag, content=message)

        orchestrators = self._orchestrators.resolve(session_id, user_tag, message)
        self._orchestrators.prepare_turn(orchestrators, session_id, user_tag, message)
        skill_matches = self._resolve_skill_matches(session_id, user_tag, message, orchestrators)
        tools = (
            self._skill_registry.get_tools_for_matches(skill_matches)
            if self._use_routing
            else self._skill_registry.get_all_tools()
        )
        runtime_messages = self._orchestrators.build_runtime_messages(orchestrators, session_id, user_tag)
        trace = TurnTrace(
            session_id=session_id,
            user_tag=user_tag,
            selected_skills=[match.to_dict() for match in skill_matches],
            selected_tools=[tool.name for tool in tools],
            orchestrators=[resolved.orchestrator.name for resolved in orchestrators],
        )
        return TurnPlan(
            session_id=session_id,
            user_tag=user_tag,
            message=message,
            context=ToolExecutionContext(session_id=session_id, user_tag=user_tag),
            skill_matches=skill_matches,
            tools=tools,
            runtime_messages=runtime_messages,
            orchestrators=orchestrators,
            trace=trace,
        )

    def _resolve_skill_matches(
        self,
        session_id: str,
        user_tag: str,
        message: str,
        orchestrators: list[ResolvedOrchestrator],
    ) -> list[SkillMatch]:
        enabled_skills = self._skill_registry.get_enabled_skills()
        if not self._use_routing:
            return [
                SkillMatch(
                    skill_name=skill.name,
                    reason="routing_disabled",
                    priority=int(skill.metadata.get("priority", 50)),
                    match_type="strong",
                )
                for skill in enabled_skills
            ]

        forced_skills = self._orchestrators.collect_forced_skills(orchestrators)
        matches = self._router.route(message, enabled_skills, forced_skill_names=forced_skills)
        logger.debug(
            "Resolved skill routing",
            extra={
                "session_id": session_id,
                "user_tag": user_tag,
                "routing_matches": [match.to_dict() for match in matches],
            },
        )
        return matches

    def _recursion_limit(self) -> int:
        return max(4, settings.agent_max_iterations * 2 + 2)

    def _build_graph(
        self,
        tools: Sequence[AgentTool],
        context: ToolExecutionContext,
        orchestrators: list[ResolvedOrchestrator],
        trace: TurnTrace,
    ):
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
                trace.tool_calls.append(tool_name)
                tool = tool_map.get(tool_name)
                if tool is None:
                    envelope = ToolResultEnvelope(
                        status="error",
                        summary=f"Tool '{tool_name}' is not available in the current skill set.",
                        data=None,
                        error_type="tool_not_available",
                    )
                else:
                    arguments = self._normalize_tool_arguments(tool_call.get("args"))
                    envelope = self._invoke_tool(tool, arguments, context)
                    self._orchestrators.handle_tool_result(
                        orchestrators,
                        context.session_id,
                        context.user_tag,
                        tool_name,
                        arguments,
                        envelope,
                    )
                    if envelope.status == "error":
                        trace.tool_failures.append(
                            {"tool_name": tool_name, "error_type": envelope.error_type or "tool_error"}
                        )
                results.append(
                    ToolMessage(
                        content=json.dumps(envelope.to_dict(), ensure_ascii=False, default=str),
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

    def _invoke_tool(
        self,
        tool: AgentTool,
        arguments: dict[str, Any],
        context: ToolExecutionContext,
    ) -> ToolResultEnvelope:
        if self._requires_confirmation(tool) and not bool(arguments.get(tool.confirmation_argument)):
            return ToolResultEnvelope(
                status="blocked",
                summary=tool.metadata.get(
                    "confirmation_summary",
                    f"Tool '{tool.name}' requires explicit user confirmation before making changes.",
                ),
                data={"arguments": arguments},
                next_action_hint="Ask the user to confirm before retrying the write action.",
                requires_confirmation=True,
                error_type="confirmation_required",
            )
        try:
            raw_result = tool.invoke(arguments, context)
        except TypeError as exc:
            return ToolResultEnvelope(
                status="error",
                summary=f"Tool '{tool.name}' received invalid arguments.",
                data={"arguments": arguments, "error": str(exc)},
                next_action_hint="Check tool arguments and retry with the required fields.",
                error_type="invalid_arguments",
            )
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            logger.exception("Unexpected tool runtime failure: %s", tool.name)
            return ToolResultEnvelope(
                status="error",
                summary=f"Tool '{tool.name}' failed unexpectedly.",
                data={"error": str(exc)},
                next_action_hint="Try a different tool strategy or inspect the underlying service.",
                error_type="tool_runtime_error",
            )
        return self._normalize_tool_result(tool, raw_result)

    @staticmethod
    def _requires_confirmation(tool: AgentTool) -> bool:
        if tool.requires_confirmation:
            return True
        properties = tool.parameters.get("properties", {}) if isinstance(tool.parameters, dict) else {}
        return tool.name.startswith("update_") and tool.confirmation_argument in properties

    def _normalize_tool_result(self, tool: AgentTool, raw_result: Any) -> ToolResultEnvelope:
        if isinstance(raw_result, ToolResultEnvelope):
            return raw_result

        if isinstance(raw_result, dict):
            if raw_result.get("error"):
                summary = str(raw_result.get("message") or raw_result.get("error"))
                error_type = "business_error"
                if raw_result.get("error") == "confirmation_required":
                    return ToolResultEnvelope(
                        status="blocked",
                        summary=summary,
                        data=raw_result,
                        next_action_hint="Ask the user to confirm before retrying this action.",
                        requires_confirmation=True,
                        error_type="confirmation_required",
                    )
                return ToolResultEnvelope(
                    status="error",
                    summary=summary,
                    data=raw_result,
                    next_action_hint="Inspect the blocker and adjust the next action.",
                    error_type=error_type,
                )

            domain_status = raw_result.get("status")
            normalized_status = "success"
            if domain_status == "blocked":
                normalized_status = "blocked"
            elif domain_status in {"warning", "needs_input"}:
                normalized_status = "needs_input"
            elif isinstance(domain_status, str) and domain_status in ALLOWED_ENVELOPE_STATUSES:
                normalized_status = domain_status

            summary = str(
                raw_result.get("summary")
                or raw_result.get("summary_reason")
                or raw_result.get("message")
                or tool.metadata.get("success_summary")
                or f"Tool '{tool.name}' completed."
            )
            next_action_hint = tool.metadata.get("next_action_hint")
            if normalized_status == "blocked" and next_action_hint is None:
                next_action_hint = "Resolve the blocker or ask for the missing confirmation or data."
            if normalized_status == "needs_input" and next_action_hint is None:
                next_action_hint = "Ask the user for the missing information or follow-up decision."
            return ToolResultEnvelope(
                status=normalized_status,
                summary=summary,
                data=raw_result,
                next_action_hint=next_action_hint,
                requires_confirmation=bool(raw_result.get("requires_confirmation", False)),
                error_type=None,
            )

        summary = tool.metadata.get("success_summary") or f"Tool '{tool.name}' completed."
        return ToolResultEnvelope(status="success", summary=summary, data=raw_result)

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

    def _load_langchain_messages(
        self,
        session_id: str,
        runtime_messages: Sequence[dict[str, Any]] | None = None,
    ) -> list[BaseMessage]:
        messages: list[BaseMessage] = []
        compatible_history = self._load_compatible_history(session_id)
        system_messages = [message for message in compatible_history if message.get("role") == "system"]
        recent_messages = [
            message for message in compatible_history if message.get("role") != "system"
        ][-RECENT_HISTORY_WINDOW:]

        for message in system_messages:
            converted = self._history_to_langchain_message(message)
            if converted is not None:
                messages.append(converted)
        for runtime_message in runtime_messages or []:
            converted = self._history_to_langchain_message(runtime_message)
            if converted is not None:
                messages.append(converted)
        for message in recent_messages:
            converted = self._history_to_langchain_message(message)
            if converted is not None:
                messages.append(converted)
        return messages

    def _load_compatible_history(self, session_id: str) -> list[dict[str, Any]]:
        compatible_messages: list[dict[str, Any]] = []
        skip_legacy_tool_results = False
        for message in self._history.get_messages(session_id):
            role = message.get("role")
            if role == "assistant" and message.get("tool_calls") and not message.get("reasoning_content"):
                skip_legacy_tool_results = True
                logger.warning(
                    "Skipping legacy assistant tool trace without reasoning_content for session %s",
                    session_id,
                )
                continue
            if role == "tool" and skip_legacy_tool_results:
                continue
            if role != "tool":
                skip_legacy_tool_results = False
            compatible_messages.append(message)
        return compatible_messages

    def _history_to_langchain_message(self, message: dict[str, Any]) -> BaseMessage | None:
        role = message.get("role")
        content = message.get("content") or ""
        if role == "system":
            return SystemMessage(content=content)
        if role == "user":
            return HumanMessage(content=content)
        if role == "assistant":
            additional_kwargs: dict[str, Any] = {}
            reasoning_content = message.get("reasoning_content")
            if isinstance(reasoning_content, str) and reasoning_content:
                additional_kwargs["reasoning_content"] = reasoning_content
            return AIMessage(
                content=content,
                additional_kwargs=additional_kwargs,
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
            payload = {
                "role": "assistant",
                "content": self._content_to_text(message.content),
                "tool_calls": self._langchain_tool_calls_to_history(message.tool_calls),
            }
            reasoning_content = self._extract_reasoning_content(message)
            if reasoning_content is not None:
                payload["reasoning_content"] = reasoning_content
            return payload
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
    def _extract_reasoning_content(message: AIMessage) -> str | None:
        reasoning_content = getattr(message, "additional_kwargs", {}).get("reasoning_content")
        return reasoning_content if isinstance(reasoning_content, str) and reasoning_content else None

    @staticmethod
    def _extract_tool_names(message: AIMessage) -> list[str]:
        tool_calls = getattr(message, "tool_calls", []) or []
        return [str(tool_call.get("name", "")) for tool_call in tool_calls if tool_call.get("name")]

    @staticmethod
    def _log_turn_trace(trace: TurnTrace) -> None:
        logger.info("Agent turn completed", extra={"agent_turn": trace.as_log_payload()})


ReActAgent = LangGraphAgent

__all__ = ["LangGraphAgent", "ReActAgent"]
