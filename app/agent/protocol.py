"""Agent runtime shared protocols and data contracts."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

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


@dataclass(slots=True)
class AgentTool:
    """Function-callable agent tool."""

    name: str
    description: str
    parameters: dict[str, Any]
    fn: Callable[..., Any]

    def to_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


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
        }


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
    "ToolExecutionContext",
    "safe_call",
]
