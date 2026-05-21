"""Agent runtime shared protocols and data contracts."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from dataclasses import asdict, dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

from fastapi import HTTPException

from app.errors import AppError


@runtime_checkable
class BaseAgent(Protocol):
    """Agent runtime protocol."""

    def chat(self, session_id: str, message: str, user_tag: str | None = None) -> str: ...

    async def chat_stream(
        self,
        session_id: str,
        message: str,
        user_tag: str | None = None,
    ) -> AsyncIterator[dict[str, str]]: ...


@runtime_checkable
class BaseHistoryStore(Protocol):
    """Conversation history storage protocol."""

    def get_messages(self, session_id: str) -> list[dict[str, Any]]: ...

    def add_message(self, session_id: str, message: dict[str, Any], user_tag: str = "default") -> None: ...

    def clear(self, session_id: str) -> None: ...

    def list_sessions(self, user_tag: str | None = None) -> list[str]: ...


@dataclass(slots=True)
class ToolExecutionContext:
    """Tool execution context for agent tools."""

    session_id: str
    user_tag: str


ToolMatchType = Literal["forced", "strong", "fallback"]
ToolResultStatus = Literal["success", "needs_input", "blocked", "error"]


@dataclass(slots=True)
class SkillMatch:
    """Structured routing decision for a skill."""

    skill_name: str
    reason: str
    priority: int
    match_type: ToolMatchType

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ToolResultEnvelope:
    """Normalized tool result passed back to the model and orchestrators."""

    status: ToolResultStatus
    summary: str
    data: Any
    next_action_hint: str | None = None
    requires_confirmation: bool = False
    error_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgentTool:
    """Function-callable agent tool."""

    name: str
    description: str
    parameters: dict[str, Any]
    fn: Callable[..., Any]
    context_defaults: dict[str, str] = field(default_factory=dict)
    requires_confirmation: bool = False
    confirmation_argument: str = "confirm"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def invoke(self, arguments: dict[str, Any], context: ToolExecutionContext) -> Any:
        payload = dict(arguments)
        for argument_name, context_field in self.context_defaults.items():
            payload.setdefault(argument_name, getattr(context, context_field))
        properties = self.parameters.get("properties", {}) if isinstance(self.parameters, dict) else {}
        if "session_id" in properties:
            payload.setdefault("session_id", context.session_id)
        if "user_tag" in properties:
            payload.setdefault("user_tag", context.user_tag)
        return self.fn(**payload)


@dataclass(slots=True)
class AgentSkill:
    """Skill definition used by registry and router."""

    name: str
    description: str
    applicability: str
    tools: list[AgentTool]
    keywords: tuple[str, ...] = ()
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "applicability": self.applicability,
            "enabled": self.enabled,
            "metadata": self.metadata,
        }


@runtime_checkable
class BaseOrchestrator(Protocol):
    """Runtime hook interface for multi-step task orchestration."""

    name: str
    priority: int

    def should_handle(self, message: str, session_id: str, user_tag: str) -> bool: ...

    def forced_skills(self, session_id: str, user_tag: str, message: str) -> list[str]: ...

    def prepare_turn(self, session_id: str, user_tag: str, message: str) -> None: ...

    def build_runtime_summary(self, session_id: str, user_tag: str) -> str | None: ...

    def handle_tool_result(
        self,
        session_id: str,
        user_tag: str,
        tool_name: str,
        arguments: dict[str, Any],
        result: ToolResultEnvelope,
    ) -> None: ...


def safe_call(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Normalize service responses and application errors for tool calls."""

    try:
        result = fn(*args, **kwargs)
    except HTTPException as exc:
        return {"error": exc.detail}
    except AppError as exc:
        return {"error": exc.message, "error_code": exc.error_code}
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        return {"error": str(exc)}

    if hasattr(result, "model_dump"):
        return result.model_dump()
    if isinstance(result, list):
        return [item.model_dump() if hasattr(item, "model_dump") else item for item in result]
    return result


__all__ = [
    "AgentSkill",
    "AgentTool",
    "BaseAgent",
    "BaseHistoryStore",
    "BaseOrchestrator",
    "SkillMatch",
    "ToolExecutionContext",
    "ToolResultEnvelope",
    "safe_call",
]
