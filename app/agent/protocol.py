from __future__ import annotations

from dataclasses import dataclass, field
from typing import AsyncIterator, Callable, Protocol, runtime_checkable

from fastapi import HTTPException


@runtime_checkable
class BaseAgent(Protocol):
    def chat(self, session_id: str, message: str) -> str: ...
    async def chat_stream(self, session_id: str, message: str) -> AsyncIterator[dict]: ...


@runtime_checkable
class BaseHistoryStore(Protocol):
    def get_messages(self, session_id: str) -> list[dict]: ...
    def add_message(self, session_id: str, message: dict) -> None: ...
    def clear(self, session_id: str) -> None: ...
    def list_sessions(self) -> list[str]: ...


@dataclass
class AgentTool:
    name: str
    description: str
    parameters: dict
    fn: Callable[..., dict]

    def to_openai_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


def _safe(fn, *args, **kwargs) -> dict:
    try:
        result = fn(*args, **kwargs)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        if isinstance(result, list):
            return [r.model_dump() if hasattr(r, "model_dump") else r for r in result]
        return result
    except HTTPException as e:
        return {"error": e.detail}
    except Exception as e:
        return {"error": str(e)}


@dataclass
class Skill:
    name: str
    description: str
    applicability: str
    tools: list[AgentTool]
    workflows: dict[str, Callable[..., dict]] = field(default_factory=dict)
    enabled: bool = True

    def to_openai_skill_summary(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "applicability": self.applicability,
        }

    def get_openai_tools(self) -> list[dict]:
        if not self.enabled:
            return []
        return [t.to_openai_tool() for t in self.tools]

    def get_tool_map(self) -> dict[str, AgentTool]:
        if not self.enabled:
            return {}
        return {t.name: t for t in self.tools}
